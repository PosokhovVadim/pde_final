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
    pyspark

WORKDIR /opt/airflow

USER airflow

COPY . /opt/airflow

ENTRYPOINT ["bash", "-c", "airflow db init && airflow webserver"]
