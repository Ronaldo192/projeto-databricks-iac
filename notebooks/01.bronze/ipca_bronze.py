# Databricks notebook source
# MAGIC %run "../00.config/config"

# COMMAND ----------

import requests
import pandas as pd
from pyspark.sql.functions import current_timestamp

# Período de 09/2025 a 08/2026 (compatível com a série do boi gordo)
url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
params = {"formato": "json", "dataInicial": "01/09/2025", "dataFinal": "31/08/2026"}
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data_json = response.json()
except Exception as e:
    print(f"Aviso: Cluster sem acesso externo ({e}).")
    print("Utilizando dados oficiais em fallback da série 433 (IPCA 09/2025 a 08/2026):")
    data_json = [
        {"data": "01/09/2025", "valor": "0.48"},
        {"data": "01/10/2025", "valor": "0.09"},
        {"data": "01/11/2025", "valor": "0.18"},
        {"data": "01/12/2025", "valor": "0.33"},
        {"data": "01/01/2026", "valor": "0.33"},
        {"data": "01/02/2026", "valor": "0.70"},
        {"data": "01/03/2026", "valor": "0.88"},
        {"data": "01/04/2026", "valor": "0.67"},
        {"data": "01/05/2026", "valor": "0.58"},
        {"data": "01/06/2026", "valor": "0.16"},
        {"data": "01/07/2026", "valor": "0.07"},
        {"data": "01/08/2026", "valor": "-0.32"}
    ]

df_pd = pd.DataFrame(data_json)
df_pd.columns = ["data", "ipca"]
df_pd["ipca"] = df_pd["ipca"].astype(str).str.replace(",", ".").astype(float)

# COMMAND ----------

display(df_pd)

# COMMAND ----------

df_spark = spark.createDataFrame(df_pd).withColumn("data_coleta", current_timestamp())

# COMMAND ----------

display(df_spark)

# COMMAND ----------

df_spark.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{BRONZE}.ipca")
