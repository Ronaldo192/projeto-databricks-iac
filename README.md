# Data Pipeline CI/CD & IaC no Databricks Community Edition

Projeto acadêmico e prático de Engenharia de Dados aplicando conceitos de **Infrastructure as Code (IaC)** com Terraform e automação de **CI/CD** com GitHub Actions para deploy de notebooks com Arquitetura Medalhão no Databricks Community Edition.

---

## 🏛️ Arquitetura da Solução

<p align="center">
  <img src="docs/images/projeto_iac_git_databricks.jfif" alt="Arquitetura Data Pipeline Databricks IaC & CI/CD" width="100%">
</p>

```text
[ Developer ]
   │ (git push / PR)
   ▼
[ GitHub Repository ] (branch: dev / master)
   │ (trigger workflow)
   ▼
[ GitHub Actions Runner ]
   ├── 1. Checkout do código
   ├── 2. Setup Terraform CLI (1.8.x)
   ├── 3. Injeção de Secrets (DATABRICKS_HOST, DATABRICKS_TOKEN)
   ├── 4. terraform fmt, init, validate, plan
   └── 5. terraform apply (auto-approve em master/main)
   ▼
[ Databricks Terraform Provider ]
   ▼
[ Databricks Community Edition Workspace ]
   └── /Shared/projeto_faculdade/
         ├── 00.config/
         ├── 01.bronze/
         ├── 02.silver/
         └── 03.gold/
```

---

## 📂 Estrutura do Repositório

```text
projeto-databricks-iac/
├── .github/
│   └── workflows/
│       └── deploy.yml            # Pipeline de automação CI/CD
├── terraform/
│   ├── versions.tf               # Provider Databricks e constraints de versão
│   ├── variables.tf              # Variáveis parametrizáveis
│   ├── main.tf                   # Recursos: diretórios e mapeamento dinâmico de notebooks
│   ├── outputs.tf                # Outputs com caminhos implantados
│   └── terraform.tfvars.example  # Exemplo de variáveis para teste local
├── docs/
│   └── images/
│       └── projeto_iac_git_databricks.jfif # Diagrama de arquitetura
├── notebooks/
│   ├── 00.config/
│   │   └── config.py             # Configurações e caminhos
│   ├── 01.bronze/
│   │   ├── boi_gordo_bronze.py   # Ingestão de cotações Boi Gordo
│   │   └── ipca_bronze.py        # Ingestão de dados IPCA
│   ├── 02.silver/
│   │   └── economia_silver.py    # Tratamento, padronização e tipagem
│   └── 03.gold/
│       └── gold_insights.py      # Agregações analíticas e regras de negócio
├── .gitignore                    # Arquivos ignorados (tfstate, secrets, caches)
├── spec.md                       # Especificação técnica do projeto
└── README.md                     # Documentação do projeto
```

---

## ⚙️ Pré-requisitos e Configuração

### 1. Secrets no GitHub
Configure no GitHub em **Settings > Secrets and variables > Actions**:

| Secret | Descrição | Exemplo |
| :--- | :--- | :--- |
| `DATABRICKS_HOST` | URL do seu workspace | `https://community.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | Personal Access Token gerado no Databricks | `dapi...` |

### 2. Fluxo de Trabalho (GitFlow)
- **Branch `dev`**: Branch para desenvolvimento e teste de novas funcionalidades.
- **Branch `master`**: Branch de produção. Ao abrir Pull Request ou fazer push, a esteira executa o lint, plano e apply automático dos notebooks no Databricks.

---

## 🌐 Origem dos Dados (Data Sources)

A esteira de dados integra duas fontes do cenário macroeconômico e agropecuário brasileiro:

| Fonte | Indicador | Tipo de Coleta | Destino Bronze | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **CEPEA / ESALQ** | Cotação do Boi Gordo | Upload de arquivo (`boi_gordo.csv`) | `workspace.bronze_economia.boi_gordo_aula` | Dados históricos de cotações obtidos no [Banco de Dados do CEPEA](https://www.cepea.org.br/br/consultas-ao-banco-de-dados-do-site.aspx). O arquivo CSV foi carregado manualmente via interface do Databricks no Unity Catalog para originar a tabela bruta. |
| **Banco Central (BACEN)** | IPCA (Série 433) | API REST (HTTP GET) | `workspace.bronze_economia.ipca` | Dados oficiais de inflação consumidos diretamente da API pública do SGS do Banco Central (`https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados`). |

---

## 📓 Descrição dos Notebooks (Arquitetura Medalhão)

A lógica de processamento distribuído segue a convenção de camadas do Lakehouse:

### ⚙️ `00.config/config.py`
* **Objetivo:** Inicialização de ambiente e governança de dados.
* **Ações:**
  * Define o Unity Catalog (`workspace`) e os schemas das camadas: `bronze_economia`, `silver_economia` e `gold_economia`.
  * Cria automaticamente os schemas caso não existam (`CREATE SCHEMA IF NOT EXISTS`).
  * Define o catálogo ativo para a sessão Spark (`USE CATALOG workspace`).

### 🥉 Camada Bronze (Ingestão Bruta)
* **`01.bronze/boi_gordo_bronze.py`**:
  * Lê a tabela bruta `workspace.bronze_economia.boi_gordo_aula` (criada a partir do upload do `boi_gordo.csv`).
  * Adiciona carimbo de data/hora de controle de auditoria (`data_coleta = current_timestamp()`).
  * Persiste os dados brutos versionados em formato Delta Lake na tabela `workspace.bronze_economia.boi_gordo`.
* **`01.bronze/ipca_bronze.py`**:
  * Realiza requisição HTTP na API do Banco Central (SGS 433) com parâmetros de intervalo de datas.
  * Converte os dados brutos em DataFrame Spark, higieniza separadores decimais (vírgula por ponto).
  * Adiciona coluna de auditoria (`data_coleta`) e persiste em Delta Lake na tabela `workspace.bronze_economia.ipca`.

### 🥈 Camada Silver (Limpeza, Tipagem e Enriquecimento)
* **`02.silver/economia_silver.py`**:
  * Lê as tabelas Delta `ipca` e `boi_gordo` da camada Bronze.
  * Padroniza nomes de colunas (`Data/Valor` -> `data/boi_gordo`).
  * Converte e harmoniza os formatos de datas (`MM/yyyy` e `dd/MM/yyyy`) para granularidade temporal mensal padronizada (`yyyy-MM` e data `yyyy-MM-01`).
  * Realiza o **Inner Join** entre os conjuntos de dados de inflação e cotação do boi gordo pela chave temporal (`data`).
  * Garante tipagem estrita (`DoubleType`) para valores numéricos e `DateType` para competência temporal.
  * Salva o dataset unificado na tabela Delta `workspace.silver_economia.economia` com suporte a `overwriteSchema`.

### 🥇 Camada Gold (Regras de Negócio e Agregações Analíticas)
* **`03.gold/gold_insights.py`**:
  * Lê os dados limpos de `workspace.silver_economia.economia`.
  * Aplica **Window Functions** (`F.lag`) ordenadas pela data para calcular a taxa de variação percentual mensal do IPCA (`variacao_ipca`) e da arroba do boi gordo (`variacao_boi`).
  * Persiste os indicadores calculados na tabela Delta `workspace.gold_economia.insights`.
  * Executa transformações analíticas em SQL para categorização de negócio:
    * Criação da tabela `workspace.gold_economia.gold_analitico` com cálculo de média de variações, identificação do indicador predominante (`destaque`) e estratificação de divergência (`classe_impacto`).
    * Criação da View `workspace.gold_economia.vw_gold_dashboard` para consumo direto em dashboards analíticos e ferramentas de BI (Power BI, Metabase, Tableau).
