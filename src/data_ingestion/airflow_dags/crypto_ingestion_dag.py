from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data_ingestion.kafka_producer.crypto_producer import CryptoProducer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_crypto_producer():
    """Task to run the crypto producer."""
    producer = CryptoProducer(
        bootstrap_servers=['localhost:9092'],
        topic='crypto_prices',
        crypto_symbols=['BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'SOL-USD']
    )
    producer.publish_messages()

with DAG(
    'crypto_price_ingestion',
    default_args=default_args,
    description='DAG for ingesting cryptocurrency price data',
    schedule_interval=timedelta(minutes=1),
    start_date=datetime(2023, 12, 1),
    catchup=False,
    tags=['crypto'],
) as dag:

    # Task to ensure Kafka is running
    health_check = BashOperator(
        task_id='kafka_health_check',
        bash_command='echo "Checking Kafka connection..." && nc -zv localhost 9092',
        retries=3,
        retry_delay=timedelta(seconds=10),
    )

    # Task to run the crypto producer
    ingest_crypto_data = PythonOperator(
        task_id='ingest_crypto_data',
        python_callable=run_crypto_producer,
        retries=3,
    )

    health_check >> ingest_crypto_data 