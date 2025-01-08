from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import csv
import os


def replicate_postgres_table_to_hive(table_name, hive_table_name):
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default_2')
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()

    # Fetching data
    cursor.execute(f'SELECT * FROM {table_name}')  
    data = cursor.fetchall()

    file_path = f'/tmp/postgres_{table_name}.csv'
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([desc[0] for desc in cursor.description]) 
        writer.writerows(data)

    print(f"PostgreSQL data from table {table_name} have written to file: {file_path}")
    return file_path

def replicate_mongo_collection_to_hive(collection_name, hive_table_name):
    mongo_hook = MongoHook(mongo_conn_id='mongo_default_2')
    collection = mongo_hook.get_collection(collection_name)
    data = collection.find()

    file_path = f'/tmp/mongo_{collection_name}.csv'
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        headers = set()
        documents = list(data)
        for doc in documents:
            headers.update(doc.keys())
        headers = list(headers)

        writer.writerow(headers) 
        for doc in documents:
            writer.writerow([doc.get(header, None) for header in headers])

    print(f"MongoDB data from collection {collection_name} have written to file: {file_path}")
    return file_path

with DAG(
    'replicate_data_to_hive',
    default_args={'owner': 'airflow'},
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    postgres_tasks = []
    mongo_tasks = []
    hive_postgres_tasks = []
    hive_mongo_tasks = []

    postgres_tables = {
        'Users': 'users_hive',
        'Orders': 'orders_hive',
        'Products': 'products_hive',
        'OrderDetails': 'order_details_hive',
        'ProductReviews': 'product_reviews_hive',
        'SupportChats': 'support_chats_hive',
        'Cashback': 'cashback_hive',
        'Warehouse': 'warehouse_hive',
        'Promotions': 'promotions_hive'
    }

    for table_name, hive_table_name in postgres_tables.items():
        file_task_id = f"replicate_postgres_{table_name}_to_hive"
        hive_task_id = f"load_postgres_{table_name}_to_hive"

        postgres_task = PythonOperator(
            task_id=file_task_id,
            python_callable=replicate_postgres_table_to_hive,
            op_args=[table_name, hive_table_name],
        )

        hive_task = HiveOperator(
            task_id=hive_task_id,
            hql=f"LOAD DATA LOCAL INPATH '/tmp/postgres_{table_name}.csv' INTO TABLE {hive_table_name}",
            hive_cli_conn_id='hive_default',
        )

        postgres_task >> hive_task
        postgres_tasks.append(postgres_task)
        hive_postgres_tasks.append(hive_task)

        mongo_collections = {
        'ProductPriceHistory': 'product_price_history_hive',
        'SupportTickets': 'support_tickets_hive',
        'ModerationQueue': 'moderation_queue_hive',
        'ProductRecommendations': 'product_recommendations_hive',
        'SearchQueries': 'search_queries_hive'
    }


    for collection_name, hive_table_name in mongo_collections.items():
        file_task_id = f"replicate_mongo_{collection_name}_to_hive"
        hive_task_id = f"load_mongo_{collection_name}_to_hive"

        mongo_task = PythonOperator(
            task_id=file_task_id,
            python_callable=replicate_mongo_collection_to_hive,
            op_args=[collection_name, hive_table_name],
        )

        hive_task = HiveOperator(
            task_id=hive_task_id,
            hql=f"LOAD DATA LOCAL INPATH '/tmp/mongo_{collection_name}.csv' INTO TABLE {hive_table_name}",
            hive_cli_conn_id='hive_default',
        )

        mongo_task >> hive_task
        mongo_tasks.append(mongo_task)
        hive_mongo_tasks.append(hive_task)

    # Tasks
    for pg_task, hive_pg_task in zip(postgres_tasks, hive_postgres_tasks):
        pg_task >> hive_pg_task

    for mongo_task, hive_mongo_task in zip(mongo_tasks, hive_mongo_tasks):
        mongo_task >> hive_mongo_task

    # Metrics
    ## 1.User activity metrics
    create_user_activity_summary = HiveOperator(
        task_id='create_user_activity_summary',
        hql="""
        CREATE TABLE user_activity_summary AS
        SELECT
            u.user_id,
            COUNT(DISTINCT o.order_id) AS total_orders,
            AVG(o.total_amount) AS avg_order_value,
            COUNT(DISTINCT r.review_id) AS total_reviews,
            MAX(o.order_date) AS last_activity
        FROM users_hive u
        LEFT JOIN orders_hive o ON u.user_id = o.user_id
        LEFT JOIN product_reviews_hive r ON u.user_id = r.user_id
        GROUP BY u.user_id;
        """,
        hive_cli_conn_id='hive_default'
    )

    ## 2.Promotion Effectiveness metrics
    create_promotion_effectiveness = HiveOperator(
        task_id='create_promotion_effectiveness',
        hql="""
        CREATE TABLE promotion_effectiveness AS
        SELECT
            p.promotion_id,
            SUM(od.quantity * od.unit_price) AS total_sales,
            COUNT(DISTINCT od.order_id) AS total_orders,
            AVG(od.quantity * od.unit_price) AS avg_order_value,
            p.start_date,
            p.end_date
        FROM promotions_hive p
        LEFT JOIN order_details_hive od ON p.product_id = od.product_id
        GROUP BY p.promotion_id, p.start_date, p.end_date;
        """,
        hive_cli_conn_id='hive_default'
    )

    ## 3.Support quality metrics
    create_support_quality_metrics = HiveOperator(
        task_id='create_support_quality_metrics',
        hql="""
        CREATE TABLE support_quality_metrics AS
        SELECT
            s.support_agent_id AS agent_id,
            COUNT(DISTINCT s.chat_id) AS total_chats,
            AVG(UNIX_TIMESTAMP(s.end_time) - UNIX_TIMESTAMP(s.start_time)) / 60 AS avg_response_time,
            AVG(s.satisfaction_score) AS satisfaction_score,
            SUM(CASE WHEN s.chat_status = 'Closed' THEN 1 ELSE 0 END) AS resolved_chats
        FROM support_chats_hive s
        GROUP BY s.support_agent_id;
        """,
        hive_cli_conn_id='hive_default'
    )

    for hive_task in hive_postgres_tasks + hive_mongo_tasks:
        hive_task >> create_user_activity_summary
        hive_task >> create_promotion_effectiveness
        hive_task >> create_support_quality_metrics