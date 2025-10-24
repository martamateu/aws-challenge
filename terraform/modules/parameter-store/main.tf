# Parameter Store Module - Creates SSM parameters

# Database configuration parameters
resource "aws_ssm_parameter" "database_host" {
  name        = "/app/${var.project_name}/${var.environment}/database/host"
  description = "Database host for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = "db.${var.environment}.example.com"

  tags = merge(
    var.tags,
    {
      Name        = "database-host"
      Description = "Database hostname"
      Category    = "Database"
    }
  )
}

resource "aws_ssm_parameter" "database_port" {
  name        = "/app/${var.project_name}/${var.environment}/database/port"
  description = "Database port for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = "5432"

  tags = merge(
    var.tags,
    {
      Name        = "database-port"
      Description = "Database port number"
      Category    = "Database"
    }
  )
}

resource "aws_ssm_parameter" "database_name" {
  name        = "/app/${var.project_name}/${var.environment}/database/name"
  description = "Database name for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = "${var.project_name}_${var.environment}"

  tags = merge(
    var.tags,
    {
      Name        = "database-name"
      Description = "Database name"
      Category    = "Database"
    }
  )
}

# API configuration parameters
resource "aws_ssm_parameter" "api_key" {
  name        = "/app/${var.project_name}/${var.environment}/api/key"
  description = "API key for ${var.project_name} ${var.environment}"
  type        = "SecureString"
  value       = "dummy-api-key-change-me"

  tags = merge(
    var.tags,
    {
      Name        = "api-key"
      Description = "API authentication key"
      Category    = "API"
      Sensitive   = "true"
    }
  )

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "api_secret" {
  name        = "/app/${var.project_name}/${var.environment}/api/secret"
  description = "API secret for ${var.project_name} ${var.environment}"
  type        = "SecureString"
  value       = "dummy-api-secret-change-me"

  tags = merge(
    var.tags,
    {
      Name        = "api-secret"
      Description = "API secret"
      Category    = "API"
      Sensitive   = "true"
    }
  )

  lifecycle {
    ignore_changes = [value]
  }
}

# Application configuration
resource "aws_ssm_parameter" "app_log_level" {
  name        = "/app/${var.project_name}/${var.environment}/config/log-level"
  description = "Application log level for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = var.environment == "prod" ? "INFO" : "DEBUG"

  tags = merge(
    var.tags,
    {
      Name        = "app-log-level"
      Description = "Application logging level"
      Category    = "Application"
    }
  )
}

resource "aws_ssm_parameter" "app_timeout" {
  name        = "/app/${var.project_name}/${var.environment}/config/timeout"
  description = "Application timeout in seconds for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = "30"

  tags = merge(
    var.tags,
    {
      Name        = "app-timeout"
      Description = "Application request timeout"
      Category    = "Application"
    }
  )
}

# AWS Region configuration
resource "aws_ssm_parameter" "aws_region" {
  name        = "/app/${var.project_name}/${var.environment}/config/region"
  description = "AWS region for ${var.project_name} ${var.environment}"
  type        = "String"
  value       = data.aws_region.current.name

  tags = merge(
    var.tags,
    {
      Name        = "aws-region"
      Description = "AWS region"
      Category    = "AWS"
    }
  )
}

# Data sources
data "aws_region" "current" {}
