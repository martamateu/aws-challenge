# IAM Module - Creates IAM roles for Kubernetes Service Accounts (IRSA)
# This module sets up IAM roles that Kubernetes pods can assume

locals {
  # Extract OIDC provider ID from ARN or URL
  oidc_provider_id = var.eks_oidc_provider_arn != "" ? split("/", var.eks_oidc_provider_arn)[length(split("/", var.eks_oidc_provider_arn)) - 1] : ""
  oidc_provider_url_clean = var.eks_oidc_provider_url != "" ? replace(var.eks_oidc_provider_url, "https://", "") : ""
  
  namespace = "auxiliary-service"
  service_account_name = "auxiliary-service-sa"
}

# IAM Role for Auxiliary Service (IRSA - IAM Roles for Service Accounts)
resource "aws_iam_role" "auxiliary_service" {
  count = var.eks_oidc_provider_arn != "" ? 1 : 0
  
  name        = "${var.project_name}-auxiliary-service-${var.environment}"
  description = "IAM role for Auxiliary Service in ${var.environment} environment"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.eks_oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${local.oidc_provider_url_clean}:sub" = "system:serviceaccount:${local.namespace}:${local.service_account_name}"
            "${local.oidc_provider_url_clean}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-auxiliary-service-${var.environment}"
      Description = "IAM role for Auxiliary Service"
      Service     = "auxiliary-service"
    }
  )
}

# IAM Policy for S3 access
resource "aws_iam_policy" "s3_access" {
  count = var.eks_oidc_provider_arn != "" ? 1 : 0
  
  name        = "${var.project_name}-s3-access-${var.environment}"
  description = "Policy for S3 bucket access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:ListBucketVersions"
        ]
        Resource = var.s3_bucket_arns
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion"
        ]
        Resource = [
          for arn in var.s3_bucket_arns : "${arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-s3-access-${var.environment}"
    }
  )
}

# IAM Policy for SSM Parameter Store access
resource "aws_iam_policy" "parameter_store_access" {
  count = var.eks_oidc_provider_arn != "" ? 1 : 0
  
  name        = "${var.project_name}-parameter-store-access-${var.environment}"
  description = "Policy for SSM Parameter Store access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParameterHistory",
          "ssm:GetParametersByPath",
          "ssm:DescribeParameters"
        ]
        Resource = var.parameter_arns
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:DescribeParameters"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "ssm.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-parameter-store-access-${var.environment}"
    }
  )
}

# Attach S3 policy to role
resource "aws_iam_role_policy_attachment" "auxiliary_s3" {
  count = var.eks_oidc_provider_arn != "" ? 1 : 0
  
  role       = aws_iam_role.auxiliary_service[0].name
  policy_arn = aws_iam_policy.s3_access[0].arn
}

# Attach Parameter Store policy to role
resource "aws_iam_role_policy_attachment" "auxiliary_parameter_store" {
  count = var.eks_oidc_provider_arn != "" ? 1 : 0
  
  role       = aws_iam_role.auxiliary_service[0].name
  policy_arn = aws_iam_policy.parameter_store_access[0].arn
}

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
