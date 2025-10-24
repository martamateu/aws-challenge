output "parameter_names" {
  description = "Names of created SSM parameters"
  value = [
    aws_ssm_parameter.database_host.name,
    aws_ssm_parameter.database_port.name,
    aws_ssm_parameter.database_name.name,
    aws_ssm_parameter.api_key.name,
    aws_ssm_parameter.api_secret.name,
    aws_ssm_parameter.app_log_level.name,
    aws_ssm_parameter.app_timeout.name,
    aws_ssm_parameter.aws_region.name
  ]
}

output "parameter_arns" {
  description = "ARNs of created SSM parameters"
  value = [
    aws_ssm_parameter.database_host.arn,
    aws_ssm_parameter.database_port.arn,
    aws_ssm_parameter.database_name.arn,
    aws_ssm_parameter.api_key.arn,
    aws_ssm_parameter.api_secret.arn,
    aws_ssm_parameter.app_log_level.arn,
    aws_ssm_parameter.app_timeout.arn,
    aws_ssm_parameter.aws_region.arn
  ]
}

output "database_host_arn" {
  description = "ARN of database host parameter"
  value       = aws_ssm_parameter.database_host.arn
}

output "api_key_arn" {
  description = "ARN of API key parameter"
  value       = aws_ssm_parameter.api_key.arn
  sensitive   = true
}
