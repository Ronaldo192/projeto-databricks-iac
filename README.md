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
