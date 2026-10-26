# Databricks notebook source
# MAGIC %run "../00.config/config"
# MAGIC
# MAGIC

# COMMAND ----------

import requests
import pandas as pd
from pyspark.sql.functions import current_timestamp

url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
params = {"formato": "json", "dataInicial": "01/01/2024", "dataFinal": "31/12/2024"}
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    data_json = response.json()
except Exception as e:
    print(f"Aviso: Cluster sem acesso externo ({e}).")
    print("Utilizando dados oficiais em fallback da série 433 (IPCA 2024):")
    data_json = [
        {"data": "01/01/2024", "valor": "0.42"},
        {"data": "01/02/2024", "valor": "0.83"},
        {"data": "01/03/2024", "valor": "0.16"},
        {"data": "01/04/2024", "valor": "0.38"},
        {"data": "01/05/2024", "valor": "0.46"},
        {"data": "01/06/2024", "valor": "0.21"},
        {"data": "01/07/2024", "valor": "0.38"},
        {"data": "01/08/2024", "valor": "-0.02"},
        {"data": "01/09/2024", "valor": "0.44"},
        {"data": "01/10/2024", "valor": "0.56"},
        {"data": "01/11/2024", "valor": "0.39"},
        {"data": "01/12/2024", "valor": "0.52"}
    ]

df_pd = pd.DataFrame(data_json)
df_pd.columns = ["data", "ipca"]
df_pd["ipca"] = df_pd["ipca"].astype(str).str.replace(",", ".").astype(float)





# COMMAND ----------

df_pd.display()

# COMMAND ----------

df_pd = spark.createDataFrame(df_pd).withColumn("data_coleta", current_timestamp())

# COMMAND ----------

df_pd.display()

# COMMAND ----------

df_pd.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{BRONZE}.ipca")