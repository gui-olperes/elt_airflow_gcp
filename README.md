# 🛠️ ELT com Airflow + Google Cloud Storage

Este projeto implementa um pipeline de **ELT (Extract, Load, Transform)** utilizando o **Apache Airflow** (via Astronomer) e armazenamento de dados em **Google Cloud Storage (GCS)**. O pipeline segue uma arquitetura em camadas: **bronze → silver → gold**.

---

## 📂 Estrutura do Projeto

```
├── dags/
│   ├── transform_dag.py             # Bronze → Silver
│   ├── vendas_por_categoria_dag.py # Silver → Gold
├── include/
│   └── gcp_key.json                 # Chave GCP (não subir ao Git!)
├── README.md
└── requirements.txt
```

---

## 🔗 Conexão com GCP

A conexão com o Google Cloud é configurada por meio de uma chave de serviço (`gcp_key.json`).

1. Gere a chave JSON no painel do GCP (IAM → Service Accounts).
2. Rode este script localmente para preparar o campo `extra` para a conexão no Airflow:

```python
import json

with open(r"C:\caminho\para\gcp_key.json") as f:
    keyfile_dict = json.load(f)

keyfile_dict["private_key"] = keyfile_dict["private_key"].replace("\n", "\\n")

extra_json = {
    "keyfile_dict": keyfile_dict,
    "scope": "https://www.googleapis.com/auth/cloud-platform"
}

print(json.dumps(extra_json, indent=2))
```

3. Copie o JSON impresso e cole na UI do Airflow em:  
   `Admin → Connections → google_cloud_default → Extra`

---

## 🧱 Camadas de Dados

- **Bronze**: arquivos `.csv` brutos enviados ao GCS
- **Silver**: dados tratados (ex: remoção de duplicatas/nulos) em `.parquet`
- **Gold**: aplicação de regras de negócio e geração de datasets finais

---

## 🌀 Fluxo ELT com DAGs

### 🔍 Bronze → Silver (`transform_dag.py`)

- **Sensor**: espera por qualquer `.csv` na pasta `bronze/`
- **Transformação**:
  - Remove duplicatas
  - Remove valores nulos
  - Adiciona coluna `processado = True`
- **Saída**:
  - Exporta `.parquet` para `silver/`
  - Move `.csv` original para `bronze/processed/`

### ✨ Silver → Gold (`vendas_por_categoria_dag.py`)

- **Sensor**: espera pelo arquivo `silver/produtos.parquet`
- **Transformação**:
  - Aplica lógica de negócio (ex: vendas por categoria)
  - Exporta resultado em `.parquet` para `gold/`

---

## 🔧 Operadores e Sensores Utilizados

- `@dag`, `@task` — DAGs declarativas com Airflow moderno
- `GCSHook` — leitura e escrita em buckets GCS
- `GCSObjectsWithPrefixExistenceSensor` — sensor para aguardar arquivos
- `Variable.get()` — para parametrização do bucket via UI do Airflow

---

## ✅ Vantagens

- Evita reprocessamento com controle de arquivos
- Pipelines desacoplados e modulares por camada
- Escalável para múltiplas fontes de dados
- Permite lógica de negócio na camada Gold
- Integração nativa com GCP

---

## 🚀 Próximos Passos

- Versionamento de arquivos com timestamp no nome
- Upload dos dados finais para BigQuery
- Logs enriquecidos com metadados dos arquivos
- Monitoramento com alertas (Slack/Email)
- Deploy automatizado com CI/CD

---

> 💡 **Observação**: Não versionar nem subir `gcp_key.json` em repositórios públicos.
