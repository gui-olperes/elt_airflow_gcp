Este projeto implementa um pipeline de ELT (Extract, Load, Transform) utilizando o Apache Airflow (Astronomer), com armazenamento de dados em Google Cloud Storage (GCS), aplicando uma arquitetura em camadas: bronze, silver e gold.

📂 Estrutura do Projeto
makefile
Copiar
Editar
├── dags/
│   ├── bronze_ingest_dag.py          # Sensor + transformação bronze → silver
│   ├── silver_transform_dag.py       # Sensor + transformação silver → gold
│   └── gold_business_dag.py          # Regras de negócio finais (gold)
├── include/
│   └── gcp_key.json                  # Chave de autenticação (não subir no Git!)
├── README.md
└── requirements.txt
🔗 Conexão com GCP
A conexão com o Google Cloud é feita via uma chave de serviço (gcp_key.json).

Gerar chave JSON em IAM > Service Accounts > Create Key.

Escapar a private_key com \\n e gerar o extra JSON no formato:

json
Copiar
Editar
{
  "keyfile_dict": {
    "type": "service_account",
    "...": "...",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nABC...\\n-----END PRIVATE KEY-----\\n"
  },
  "scope": "https://www.googleapis.com/auth/cloud-platform"
}
Adicionar esse conteúdo no Airflow UI > Admin → Connections > google_cloud_default.

🧱 Camadas de Dados
Bronze: dados brutos recebidos (.csv)

Silver: dados limpos e transformados (.parquet)

Gold: dados prontos para análise com regras de negócio aplicadas

🌀 Fluxo ELT com DAGs
🔍 1. Bronze → Silver
Sensor: aguarda qualquer .csv na pasta bronze/

Tarefa:

Lê os arquivos .csv

Remove duplicatas e valores nulos

Adiciona coluna processado = True

Salva como .parquet em silver/

Move original para bronze/processed/

✨ 2. Silver → Gold
Sensor: aguarda silver/produtos.parquet

Tarefa:

Lê o .parquet

Aplica regra de negócio (ex: agregações)

Exporta como .parquet para gold/

📦 Operadores e Sensores usados
GCSHook: leitura e escrita em buckets

GCSObjectsWithPrefixExistenceSensor: aguarda arquivos em GCS

@dag e @task: estrutura moderna com Airflow 2.x+

Variable.get(): para parametrizar o nome do bucket

✅ Benefícios do projeto
Automatiza o ciclo de ingestão, transformação e entrega de dados.

Evita retrabalho com sensores e controle de arquivos processados.

Usa camadas bem definidas para organização e rastreabilidade.

Pode ser expandido facilmente para múltiplas fontes e regras de negócio.
