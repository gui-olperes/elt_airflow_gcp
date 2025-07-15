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
    tags=["GCP", "Data Transform", "Silver"],   
)
def transform_dag():

    sensor = GCSObjectsWithPrefixExistenceSensor(
        task_id="aguarda_qualquer_csv_bronze",
        bucket=Variable.get("bucket_name"),
        prefix="bronze/new/",
        google_cloud_conn_id="google_cloud_default",
        poke_interval=30,
        timeout=60
    )


    @task
    def transform_and_move_data():
        """
        transform data from the bronze layer.
        """

        hook = GCSHook(gcp_conn_id="google_cloud_default")
        bucket = Variable.get("bucket_name")

        arquivos = hook.list(bucket_name=bucket, prefix="bronze/new")

        for arquivo in arquivos:
            if arquivo.endswith(".csv"):
                print(f"Processando {arquivo}")
                file_bytes = hook.download(bucket, arquivo)
                df = pd.read_csv(io.BytesIO(file_bytes))

                df = df.drop_duplicates()
                df = df.dropna()
                df["processado"] = True

                buffer = io.BytesIO()
                df.to_parquet(buffer, index=False)
                buffer.seek(0)

                nome_saida = "silver/" + arquivo.split("/")[-1].replace(".csv", ".parquet")
                hook.upload(
                    bucket_name=bucket,
                    object_name=nome_saida,
                    data=buffer.read(),
                )
        
        hook.copy(
            source_bucket=bucket,
            source_object=arquivo,
            destination_bucket=bucket,
            destination_object="bronze/processed/" + arquivo.split("/")[-1]
        )
        hook.delete(bucket, arquivo)

    sensor >> transform_and_move_data()

transform_dag()    