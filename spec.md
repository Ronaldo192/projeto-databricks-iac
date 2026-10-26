```markdown
# SPEC-001: Data Pipeline CI/CD & IaC no Databricks Community Edition

## 1. Visão Geral (Overview)
Implementar uma esteira automatizada de Engenharia de Dados para fins acadêmicos integrando GitHub, GitHub Actions, Terraform e Databricks Community Edition. O foco do projeto é aplicar os conceitos de **Infrastructure as Code (IaC)** e **CI/CD** no gerenciamento do ciclo de vida de diretórios, notebooks e orquestração de pipelines no Databricks Free.

---

## 2. Objetivos e Escopo
- **IaC Declarativo:** Versionar e gerenciar recursos internos do workspace Databricks via Terraform Provider.
- **Automação CI/CD:** Realizar lint, validação, planejamento e deploy contínuo via GitHub Actions a cada push na branch principal.
- **Arquitetura de Dados:** Organizar a camada de scripts/notebooks seguindo os princípios de Medallion Architecture (Ingestão/Raw -> Silver -> Gold).
- **Abstração Cloud Free:** Operar dentro dos limites de cota e escopo do Databricks Community Edition (sem custos de cloud provider).

---

## 3. Arquitetura da Solução


```

[ Developer ]
│  (git push)
▼
[ GitHub Repository ]
│  (trigger workflow)
▼
[ GitHub Actions Runner ]
│  1. Checkout code
│  2. Setup Terraform CLI
│  3. Injetar secrets (DATABRICKS_HOST, DATABRICKS_TOKEN)
│  4. terraform init / plan / apply
▼
[ Databricks Terraform Provider ]
│  (Databricks REST API / PAT Authentication)
▼
[ Databricks Community Edition Workspace ]
├── /Shared/projeto_faculdade/
│     ├── 01_ingestao
│     ├── 02_silver
│     └── 03_gold
└── (Optional) databricks_job (Orquestração)

```

---

## 4. Estrutura do Repositório

```text
projeto-databricks-iac/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pipeline de automação CI/CD
├── terraform/
│   ├── versions.tf             # Declaração de providers e constraints
│   ├── variables.tf            # Definição de variáveis
│   ├── main.tf                 # Recursos do Databricks (diretórios, notebooks)
│   ├── outputs.tf              # Outputs pós-deploy
│   └── terraform.tfvars.example# Template para variáveis locais (ignorado no git)
├── notebooks/
│   ├── 00.config/
│   │   └── config.py           # Configurações do catálogo e schemas Unity Catalog
│   ├── 01.bronze/
│   │   ├── boi_gordo_bronze.py # Ingestão e versionamento da cotação do Boi Gordo (CEPEA)
│   │   └── ipca_bronze.py      # Ingestão via API REST do IPCA (BACEN)
│   ├── 02.silver/
│   │   └── economia_silver.py  # Higienização, tipagem e cruzamento temporal (Inner Join)
│   └── 03.gold/
│       └── gold_insights.py    # Métricas analíticas, window functions e views BI
├── docs/
│   └── images/
│       └── projeto_iac_git_databricks.jfif
├── .gitignore
└── README.md
```

---

## 5. Especificação dos Componentes

### 5.1. Terraform (`terraform/versions.tf` e `terraform/main.tf`)

* **Provider:** `databricks/databricks` versão `~> 1.0`.
* **Autenticação:** Via variáveis de ambiente injetadas no runner (`DATABRICKS_HOST` e `DATABRICKS_TOKEN`).
* **Recursos Obrigatórios:**
* `databricks_directory`: Cria o caminho base `/Shared/projeto_faculdade`.
* `databricks_notebook`: Mapeia cada script local em `notebooks/*.py` para um notebook tipo `SOURCE`/`PYTHON` no workspace remoto.



### 5.2. GitHub Actions (`.github/workflows/deploy.yml`)

* **Triggers:**
* `push` na branch `main` com filtros em caminhos (`terraform/**`, `notebooks/**`).
* `workflow_dispatch` (execução manual para testes).


* **Passos do Job:**
1. `actions/checkout@v4`
2. `hashicorp/setup-terraform@v3` (versão fixada: `1.8.0`+)
3. `terraform fmt -check` (garantia de conformidade de código)
4. `terraform init`
5. `terraform plan -no-color`
6. `terraform apply -auto-approve`



### 5.3. Gerenciamento de Secrets

Configurar no GitHub em **Settings > Secrets and variables > Actions**:

* `DATABRICKS_HOST`: URL do workspace (ex: `https://community.cloud.databricks.com`).
* `DATABRICKS_TOKEN`: Personal Access Token gerado no Databricks.

---

## 6. Critérios de Aceite (Definition of Done)

1. **Validação Estática:** `terraform fmt -check` e `terraform validate` executados com sucesso no CI.
2. **Deploy Automatizado:** Ao fazer merge/push para `main`, os notebooks locais devem ser sincronizados automaticamente no Databricks sob a pasta `/Shared/projeto_faculdade`.
3. **Idempotência:** Múltiplas execuções consecutivas do pipeline sem alterações de código devem reportar `No changes. Your infrastructure matches the configuration.`
4. **Segurança:** Nenhum token ou credencial privada versionada em texto puro nos commits (`.gitignore` validado).

```

---

### Como aplicar no seu Antigravity:
1. Crie ou salve este conteúdo na raiz do projeto como `SPEC.md` ou `.antigravity/spec.md`.
2. Assim, o assistente de contexto do CLI consegue ler a especificação técnica e gerar os scripts de cada etapa (`main.tf`, `deploy.yml`, notebooks Spark) mantendo a rastreabilidade arquitetural.

```