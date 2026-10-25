variable "databricks_host" {
  description = "Databricks Workspace URL (ex: https://community.cloud.databricks.com)"
  type        = string
  default     = null
}

variable "databricks_token" {
  description = "Databricks Personal Access Token"
  type        = string
  sensitive   = true
  default     = null
}

variable "workspace_base_path" {
  description = "Caminho base dentro do Databricks onde os notebooks serão criados"
  type        = string
  default     = "/Shared/projeto_faculdade"
}
