from airflow.decorators import task, dag
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import Variable
from pendulum import datetime
import requests
import pandas as pd
import io

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["API", "GCP", "Data Ingestion", "Bronze"],   
)
def ingestion_dag():

    @task       
    def testar_conexao():
        print(Variable.get("bucket_name"))
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        arquivos = hook.list(bucket_name=Variable.get("bucket_name"))
        print(arquivos)

    @task
    def extract_data():
        """
        Fetch data from the API and return it.
        """
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            data = response.json()
            df  = pd.DataFrame(data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return df
        else:
            raise Exception("Failed to fetch data from API")
        
    @task
    def load_data(data):
        """
        Process the fetched data.
        """
        try:
            hook = GCSHook(gcp_conn_id='google_cloud_default')
            hook.upload(
                bucket_name=Variable.get("bucket_name"),
                object_name='bronze/new/products.csv',
                data=data.to_csv(index=False),
                mime_type='text/csv'
            )
        except Exception as e:
            print(f"Error uploading data to GCS: {e}")
            raise    

    conexao = testar_conexao()
    dados = extract_data()
    salvar = load_data(dados)

    conexao >> dados >> salvar

ingestion_dag()    