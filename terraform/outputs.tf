output "base_directory" {
  description = "Diretório base criado no Databricks Workspace"
  value       = databricks_directory.base_dir.path
}

output "deployed_notebooks" {
  description = "Lista de notebooks implantados no Databricks"
  value       = [for nb in databricks_notebook.notebooks : nb.path]
}
