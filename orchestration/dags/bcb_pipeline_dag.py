from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime

from ingestion.extract_bcb import main


with DAG(
    dag_id="bcb_pipeline",
    start_date=datetime(2026, 5, 1),
    schedule="@daily",
    catchup=False,
    tags=["bcb", "dbt", "pipeline"]
) as dag:

    ingest_bcb = PythonOperator(
        task_id="ingest_bcb",
        python_callable=main
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/pipeline-bcb/transformation/dbt_bcb && dbt run"
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/pipeline-bcb/transformation/dbt_bcb && dbt test"
    )

    ingest_bcb >> dbt_run >> dbt_test