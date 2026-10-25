# Databricks notebook source
# MAGIC %run "../00.config/config"

# COMMAND ----------


df = spark.table("workspace.bronze_economia.boi_gordo_aula")



# COMMAND ----------

df.display()

# COMMAND ----------

from pyspark.sql.functions import current_timestamp

df = df.withColumn("data_coleta", current_timestamp())

# COMMAND ----------

df.display()

# COMMAND ----------

df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{BRONZE}.boi_gordo")
