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

    # Writing to CSV
    file_path = f'/tmp/postgres_{table_name}.csv'
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([desc[0] for desc in cursor.description])  # Column headers
        writer.writerows(data)

    print(f"PostgreSQL data from table {table_name} have written to file: {file_path}")
    return file_path

def replicate_mongo_collection_to_hive(collection_name, hive_table_name):
    mongo_hook = MongoHook(mongo_conn_id='mongo_default_2')
    collection = mongo_hook.get_collection(collection_name)
    data = collection.find()

    # Writing to CSV
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

    for pg_task, hive_pg_task in zip(postgres_tasks, hive_postgres_tasks):
        pg_task >> hive_pg_task

    for mongo_task, hive_mongo_task in zip(mongo_tasks, hive_mongo_tasks):
        mongo_task >> hive_mongo_task
