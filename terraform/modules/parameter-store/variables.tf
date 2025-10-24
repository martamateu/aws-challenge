variable "project_name" {
  description = "Project name for parameter naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all parameters"
  type        = map(string)
  default     = {}
}
