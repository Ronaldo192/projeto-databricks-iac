resource "databricks_directory" "base_dir" {
  path = var.workspace_base_path
}

locals {
  notebook_files = fileset("${path.module}/../notebooks", "**/*.py")
}

resource "databricks_notebook" "notebooks" {
  for_each = local.notebook_files

  source   = "${path.module}/../notebooks/${each.value}"
  path     = "${var.workspace_base_path}/${trimsuffix(each.value, ".py")}"
  language = "PYTHON"
  format   = "SOURCE"

  depends_on = [databricks_directory.base_dir]
}
