# Databricks notebook source
# MAGIC %run "../00.config/config"
# MAGIC
# MAGIC

# COMMAND ----------

import requests, pandas as pd
from pyspark.sql.functions import current_timestamp

url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
params = {"formato": "json", "dataInicial": "01/01/2024", "dataFinal": "31/12/2024"}

df_pd = pd.DataFrame(requests.get(url, params=params).json())
df_pd.columns = ["data", "ipca"]
df_pd["ipca"] = df_pd["ipca"].str.replace(",", ".").astype(float)





# COMMAND ----------

df_pd.display()

# COMMAND ----------

df_pd = spark.createDataFrame(df_pd).withColumn("data_coleta", current_timestamp())

# COMMAND ----------

df_pd.display()

# COMMAND ----------

df_pd.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{BRONZE}.ipca")
