from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
        dag_id='crawl_readtoolead_dynamic',
        default_args=default_args,
        start_date=datetime(2026, 4, 10),
        schedule_interval='@weekly',
        catchup=False,
        max_active_tasks=5,
) as dag:
    @task
    def task_get_total_pages() -> list:
        import sys
        DATA_SRC_PATH = "/opt/airflow/data/src"
        if DATA_SRC_PATH not in sys.path:
            sys.path.append(DATA_SRC_PATH)
        from raw.read_to_lead import ReadToLeadScraper

        BASE_URL = "https://readtoolead.com"
        scraper = ReadToLeadScraper(headless=True)

        max_page = scraper.get_total_pages(BASE_URL)
        return list(range(1, max_page + 1))

    @task(max_active_tis_per_dag=5)
    def task_scrape_and_save(page_num: int):
        import sys

        DATA_SRC_PATH = "/opt/airflow/data/src"
        if DATA_SRC_PATH not in sys.path:
            sys.path.append(DATA_SRC_PATH)

        AIRFLOW_ROOT = "/opt/airflow"
        if AIRFLOW_ROOT not in sys.path:
            sys.path.append(AIRFLOW_ROOT)

        import pandas as pd

        from raw.read_to_lead import ReadToLeadScraper
        from utils.bucket_manager import BucketManager

        BASE_URL = "https://readtoolead.com"
        BUCKET_NAME = "bronze"
        PREFIX = "readtoolead_data"

        bm = BucketManager()
        scraper = ReadToLeadScraper(headless=True)

        p_num, data = scraper.scrape_page(page_num, BASE_URL, processed_links=set())

        if data:
            df = pd.DataFrame(data)
            folder_path = f"{PREFIX}/page_{p_num}"
            file_name = f"dataset_page_{p_num}"

            bm.save_dataframe(
                df=df, bucket=BUCKET_NAME, folder=folder_path,
                file_name=file_name, file_format="json"
            )
            return f"COMPLETELY SAVING PAGE {p_num}"

        return f"--PAGE {p_num} is empty or error--"


    pages_array = task_get_total_pages()
    task_scrape_and_save.expand(page_num=pages_array)