# Databricks notebook source
# Databricks notebook source
# ==============================================
# CONFIG DO ETL - UNITY CATALOG (FREE EDITION)
# ==============================================

CATALOG = "workspace"  # Seu catálogo REAL

# Define catálogo atual para a sessão
spark.sql(f"USE CATALOG {CATALOG}")

# SCHEMAS DA ARQUITETURA
BRONZE = "bronze_economia"
SILVER = "silver_economia"
GOLD = "gold_economia"

# Criar os schemas se não existirem (no catálogo workspace)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{GOLD}")

print("Catálogo:", CATALOG)
print("Schemas:", BRONZE, SILVER, GOLD)
