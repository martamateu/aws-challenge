output "auxiliary_service_role_arn" {
  description = "ARN of the IAM role for Auxiliary Service"
  value       = var.eks_oidc_provider_arn != "" ? aws_iam_role.auxiliary_service[0].arn : ""
}

output "auxiliary_service_role_name" {
  description = "Name of the IAM role for Auxiliary Service"
  value       = var.eks_oidc_provider_arn != "" ? aws_iam_role.auxiliary_service[0].name : ""
}

output "s3_access_policy_arn" {
  description = "ARN of the S3 access policy"
  value       = var.eks_oidc_provider_arn != "" ? aws_iam_policy.s3_access[0].arn : ""
}

output "parameter_store_access_policy_arn" {
  description = "ARN of the Parameter Store access policy"
  value       = var.eks_oidc_provider_arn != "" ? aws_iam_policy.parameter_store_access[0].arn : ""
}
