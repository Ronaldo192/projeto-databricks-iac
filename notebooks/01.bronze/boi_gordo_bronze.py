# Databricks notebook source
# MAGIC %run "../00.config/config"

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, col, split

# Lê a tabela recém-carregada no schema default
df = spark.table("workspace.default.boi_gordo")

# Tratamento defensivo: caso o CSV venha com coluna agrupada 'Data;Valor'
if "Data;Valor" in df.columns:
    df = (
        df
        .withColumn("Data", split(col("`Data;Valor`"), ";")[0])
        .withColumn("Valor", split(col("`Data;Valor`"), ";")[1])
        .drop("`Data;Valor`")
    )

# COMMAND ----------

df.display()

# COMMAND ----------

# Adiciona metadados de auditoria
df = df.withColumn("data_coleta", current_timestamp())

# COMMAND ----------

df.display()

# COMMAND ----------

# Persiste com Delta Lake no schema bronze com overwriteSchema
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{BRONZE}.boi_gordo")
