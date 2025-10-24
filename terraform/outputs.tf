output "s3_bucket_names" {
  description = "Names of created S3 buckets"
  value       = module.s3.bucket_names
}

output "s3_bucket_arns" {
  description = "ARNs of created S3 buckets"
  value       = module.s3.bucket_arns
}

output "parameter_store_names" {
  description = "Names of created SSM parameters"
  value       = module.parameter_store.parameter_names
}

output "parameter_store_arns" {
  description = "ARNs of created SSM parameters"
  value       = module.parameter_store.parameter_arns
}

output "auxiliary_service_role_arn" {
  description = "ARN of IAM role for Auxiliary Service"
  value       = module.iam.auxiliary_service_role_arn
}

output "auxiliary_service_role_name" {
  description = "Name of IAM role for Auxiliary Service"
  value       = module.iam.auxiliary_service_role_name
}

output "github_actions_role_arn" {
  description = "ARN of IAM role for GitHub Actions"
  value       = module.github_oidc.github_actions_role_arn
}

output "github_actions_role_name" {
  description = "Name of IAM role for GitHub Actions"
  value       = module.github_oidc.github_actions_role_name
}

output "github_oidc_provider_arn" {
  description = "ARN of GitHub OIDC provider"
  value       = module.github_oidc.oidc_provider_arn
}

output "region" {
  description = "AWS region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}
