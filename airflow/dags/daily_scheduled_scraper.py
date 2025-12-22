from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'daily_agoda_scraper',
    default_args=default_args,
    description='Runs Agoda scraper daily at 2 AM and ingests data',
    schedule_interval='0 2 * * *', # Daily at 2:00 AM
    catchup=False,
)

# Define paths (assuming running inside Docker container mapped at /app or similar)
# Since we are running local python commands, we need absolute paths or relative from project root
# But Airflow usually runs in its own environment.
# Assuming this DAG runs in the environment where `scraper` and `database` modules are available (e.g., via Docker volume mapping)

PROJECT_ROOT = "/opt/airflow/dags/.."  # If mapped as ./dags:/opt/airflow/dags, then project root is parent?
# Actually, typically we map the whole project. Let's assume standard structure.
# Command to run scraper
scrape_command = """
cd /app && \
python scraper/main.py \
    --mode multiple \
    --max-hotels 10 \
    --reviews 20 \
    --url "https://www.agoda.com/city/da-nang-vn.html" \
    --headless \
    --output "data/agoda_reviews_latest.json"
"""

# Command to ingest data
ingest_command = """
cd /app && \
python database/init_db.py --file "data/agoda_reviews_latest.json"
"""

t1 = BashOperator(
    task_id='run_scraper',
    bash_command=scrape_command,
    dag=dag,
)

t2 = BashOperator(
    task_id='ingest_data',
    bash_command=ingest_command,
    dag=dag,
)

t1 >> t2
