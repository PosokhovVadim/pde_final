FROM apache/airflow:2.5.1-python3.9

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && apt-get clean

USER airflow

RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
    apache-airflow-providers-postgres \
    apache-airflow-providers-mongo \
    apache-airflow-providers-apache-hive \
    apache-airflow-providers-apache-spark \
    pyspark pyopenssl boto3 azure-datalake-store

RUN pip install protobuf==3.20.*

WORKDIR /opt/airflow

USER airflow

COPY dags /opt/airflow/dags
COPY plugins /opt/airflow/plugins
COPY logs /opt/airflow/logs

ENTRYPOINT ["bash", "-c", "airflow db migrate && airflow users create --username admin --firstname Admin --lastname User --role Admin --email posokhovvadyusha@gmail.com --password admin && airflow webserver"]
