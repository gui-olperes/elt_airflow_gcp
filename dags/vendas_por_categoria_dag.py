from airflow.decorators import task, dag
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.sdk import Variable
from pendulum import datetime
import requests
import pandas as pd
import io

@dag(
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["GCP", "Business Rules Data", "Gold"],   
)
def vendas_por_categoria_dag():

    sensor = GCSObjectsWithPrefixExistenceSensor(
        task_id="aguarda_produtos_silver",
        bucket=Variable.get("bucket_name"),
        prefix="silver/products.parquet",
        google_cloud_conn_id="google_cloud_default",
        poke_interval=30,
        timeout=60
    )


    @task
    def transform_and_move_data():
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        bucket = Variable.get("bucket_name")
        arquivo = "silver/products.parquet"

        print(f"Processando {arquivo}")
        file_bytes = hook.download(bucket, arquivo)
        df = pd.read_parquet(io.BytesIO(file_bytes))
        df1 = df.groupby('category').agg(
            total_vendas=('price', 'sum'),
            quantidade_vendida=('id', 'count')
        ).reset_index()
        df1['media_preco'] = (df1['total_vendas'] / df1['quantidade_vendida']).round(2)
        df1['categoria'] = df1['category']
        df1 = df1[['categoria', 'total_vendas', 'quantidade_vendida', 'media_preco']]
        df1 = df1.sort_values(by='total_vendas', ascending=False)
        print(df1)
        
        buffer = io.BytesIO()
        df1.to_parquet(buffer, index=False)
        buffer.seek(0)

        nome_saida = "gold/produtos.parquet"
        hook.upload(
            bucket_name=bucket,
            object_name=nome_saida,
            data=buffer.read(),
        )


    sensor >> transform_and_move_data()

vendas_por_categoria_dag()    