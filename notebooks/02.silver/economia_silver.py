# Databricks notebook source
# MAGIC %run "../00.config/config"

# COMMAND ----------

# 01 - Imports

from pyspark.sql import functions as F
from pyspark.sql.functions import to_date, regexp_replace, col, greatest


# COMMAND ----------

# 02 - Ler tabelas Bronze (IPCA e Boi Gordo)

ipca = spark.table(f"{CATALOG}.{BRONZE}.ipca")
boi  = spark.table(f"{CATALOG}.{BRONZE}.boi_gordo")

print("Schema IPCA:")
ipca.printSchema()

print("Schema Boi Gordo:")
boi.printSchema()


# COMMAND ----------

# 03 - (Opcional) Visualização inicial

display(ipca)
display(boi)


# COMMAND ----------

# 04 - Renomear colunas do boi gordo (Data/Valor -> data/boi_gordo)

from pyspark.sql.functions import col

boi = (
    boi
    .withColumnRenamed("Data", "data")
    .withColumnRenamed("Valor", "boi_gordo")
)

display(boi)
boi.printSchema()


# COMMAND ----------

# 05 - Ajuste de datas para boi gordo (MM/yyyy -> date -> yyyy-MM como string)

from pyspark.sql.functions import to_date, date_format

# 1) transforma string 'MM/yyyy' em date (com dia default)
boi = boi.withColumn("data", to_date("data", "MM/yyyy"))

# 2) formata essa date como string 'yyyy-MM'
boi = boi.withColumn("data", date_format("data", "yyyy-MM"))

display(boi)


# COMMAND ----------

# 06 - Ajuste de datas para IPCA (dd/MM/yyyy -> date -> yyyy-MM como string)

ipca = ipca.withColumn("data", to_date("data", "dd/MM/yyyy"))
ipca = ipca.withColumn("data", date_format("data", "yyyy-MM"))

display(ipca)


# COMMAND ----------

# 07 - Primeiro join simples por 'data' (como string yyyy-MM)

df_join = (
    ipca.join(boi, on="data", how="inner")
         .select("data", "ipca", "boi_gordo")
)

display(df_join)


# COMMAND ----------

# 08 - Join com alias, trazendo também data_coleta do IPCA

ip = ipca.alias("ip")
bo = boi.alias("bo")

df_join = (
    ip.join(bo, col("ip.data") == col("bo.data"), "inner")
      .select(
          col("ip.data").alias("data"),
          col("ip.ipca").alias("ipca"),
          col("bo.boi_gordo").alias("boi_gordo"),
          col("ip.data_coleta").alias("data_coleta")
      )
)

display(df_join)


# COMMAND ----------

# 09 - Correção de tipos: data como date yyyy-MM-01, números como double

from pyspark.sql.functions import regexp_replace

# 'data' está como string 'yyyy-MM' -> vira date assumindo dia '01'
df_join = df_join.withColumn("data", to_date(col("data"), "yyyy-MM"))

# ipca e boi_gordo: garantir double (se vier com vírgula, troca por ponto)
df_join = (
    df_join
    .withColumn("ipca",      regexp_replace("ipca",      ",", ".").cast("double"))
    .withColumn("boi_gordo", regexp_replace("boi_gordo", ",", ".").cast("double"))
)

df_join.printSchema()
display(df_join.orderBy("data").limit(50))


# COMMAND ----------

# 09 - Salvar em tabela Delta Silver (silver_etl.economia)

df_join.write.format("delta") \
      .mode("overwrite") \
      .option("overwriteSchema", "true") \
      .saveAsTable(f"{CATALOG}.{SILVER}.economia")

