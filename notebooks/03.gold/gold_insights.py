# Databricks notebook source
# MAGIC %run "/Users/thiagoazro@gmail.com/ETL_arquitetura_medalhao/00.config/config"

# COMMAND ----------

from pyspark.sql import functions as F, Window

df = spark.table(f"{CATALOG}.{SILVER}.economia")


df.display()


# COMMAND ----------

from pyspark.sql import functions as F, Window

df = spark.table(f"{CATALOG}.{SILVER}.economia")

w = Window.orderBy("data")

gold = (df
    .withColumn("ipca_ant", F.lag("ipca").over(w))
    .withColumn("boi_ant", F.lag("boi_gordo").over(w))
    .withColumn("variacao_ipca", (F.col("ipca") - F.col("ipca_ant")) / F.col("ipca_ant") * 100)
    .withColumn("variacao_boi", (F.col("boi_gordo") - F.col("boi_ant")) / F.col("boi_ant") * 100)
    .drop("ipca_ant", "boi_ant")
)

gold.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{GOLD}.insights")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.gold_economia.insights LIMIT 20;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE workspace.gold_economia.gold_analitico AS
# MAGIC WITH base AS (
# MAGIC     SELECT
# MAGIC         data,
# MAGIC         variacao_ipca,
# MAGIC         variacao_boi,
# MAGIC         ROUND((variacao_ipca + variacao_boi) / 2, 2) AS media_variacoes,
# MAGIC         CASE
# MAGIC             WHEN variacao_boi > variacao_ipca THEN 'Preço do boi cresce mais'
# MAGIC             WHEN variacao_ipca > variacao_boi THEN 'Inflação cresce mais'
# MAGIC             ELSE 'Empate'
# MAGIC         END AS destaque,
# MAGIC         CASE
# MAGIC             WHEN ABS(variacao_boi - variacao_ipca) > 5 THEN 'Alta divergência'
# MAGIC             WHEN ABS(variacao_boi - variacao_ipca) BETWEEN 2 AND 5 THEN 'Média divergência'
# MAGIC             ELSE 'Baixa divergência'
# MAGIC         END AS classe_impacto
# MAGIC     FROM workspace.gold_economia.insights
# MAGIC )
# MAGIC SELECT * FROM base;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW workspace.gold_economia.vw_gold_dashboard AS
# MAGIC SELECT *
# MAGIC FROM workspace.gold_economia.gold_analitico;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT data, variacao_ipca, variacao_boi
# MAGIC FROM workspace.gold_economia.vw_gold_dashboard;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT variacao_ipca, variacao_boi
# MAGIC FROM workspace.gold_economia.vw_gold_dashboard;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT correlacao_global 
# MAGIC FROM workspace.gold_economia.vw_gold_dashboard LIMIT 1;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT media_ipca_global, media_boi_global, media_combinada_global 
# MAGIC FROM workspace.gold_economia.vw_gold_dashboard LIMIT 1;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT data, destaque, classe_impacto
# MAGIC FROM workspace.gold_economia.vw_gold_dashboard;
# MAGIC