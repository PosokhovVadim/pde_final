from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import csv
import os

def replicate_postgres_to_hive():
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default_2')
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')  
    data = cursor.fetchall()

    file_path = '/tmp/postgres_users.csv'
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([desc[0] for desc in cursor.description])  
        writer.writerows(data)

    print(f"Данные PostgreSQL записаны в файл: {file_path}")

def replicate_mongo_to_hive():
    mongo_hook = MongoHook(mongo_conn_id='mongo_default_2')
    collection = mongo_hook.get_collection('ProductPriceHistory')
    data = collection.find()

    file_path = '/tmp/mongo_product_price_history.csv'
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['product_id', 'price_changes', 'current_price', 'currency'])  
        for document in data:
            writer.writerow([
                document.get('product_id'),
                str(document.get('price_changes', [])),
                document.get('current_price'),
                document.get('currency')
            ])

    print(f"Данные MongoDB записаны в файл: {file_path}")

with DAG(
    'replicate_data_to_hive',
    default_args={'owner': 'airflow'},
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    postgres_task = PythonOperator(
        task_id='replicate_postgres_to_hive',
        python_callable=replicate_postgres_to_hive,
    )

    mongo_task = PythonOperator(
        task_id='replicate_mongo_to_hive',
        python_callable=replicate_mongo_to_hive,
    )

    load_postgres_to_hive = HiveOperator(
        task_id='load_postgres_to_hive',
        hql="LOAD DATA LOCAL INPATH '/tmp/postgres_users.csv' INTO TABLE users_hive",
        hive_cli_conn_id='hive_default',
    )

    load_mongo_to_hive = HiveOperator(
        task_id='load_mongo_to_hive',
        hql="LOAD DATA LOCAL INPATH '/tmp/mongo_product_price_history.csv' INTO TABLE product_price_history_hive",
        hive_cli_conn_id='hive_default',
    )

    postgres_task >> load_postgres_to_hive
    mongo_task >> load_mongo_to_hive
