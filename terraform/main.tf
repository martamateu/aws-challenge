# Main Terraform configuration
# This file orchestrates all modules

locals {
  common_tags = merge(
    var.tags,
    {
      Project     = var.project_name
      Environment = var.environment
    }
  )
}

# S3 Buckets Module
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
  region       = var.region
  tags         = local.common_tags
}

# Parameter Store Module
module "parameter_store" {
  source = "./modules/parameter-store"

  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}

# GitHub OIDC Provider Module
module "github_oidc" {
  source = "./modules/github-oidc"

  project_name = var.project_name
  environment  = var.environment
  github_org   = var.github_org
  github_repo  = var.github_repo
  s3_bucket_arns = module.s3.bucket_arns
  tags         = local.common_tags
}

# IAM Module (for Kubernetes Service Accounts - IRSA)
module "iam" {
  source = "./modules/iam"

  project_name          = var.project_name
  environment           = var.environment
  eks_cluster_name      = var.eks_cluster_name
  eks_oidc_provider_arn = var.eks_oidc_provider_arn
  eks_oidc_provider_url = var.eks_oidc_provider_url
  s3_bucket_arns        = module.s3.bucket_arns
  parameter_arns        = module.parameter_store.parameter_arns
  tags                  = local.common_tags
}
