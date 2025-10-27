# Terraform Documentation

This document explains the Infrastructure as Code (IaC) defined with Terraform for the aws-challenge project.

## 📑 Table of Contents

- [Overview](#overview)
- [Modules](#modules)
- [Variables](#variables)
- [Outputs](#outputs)
- [Usage](#usage)

## 🏗️ Overview

The infrastructure is organized into reusable modules that follow Terraform best practices:

- **Modularity**: Each component (S3, Parameter Store, IAM, GitHub OIDC) is in its own module
- **Reusability**: Modules can be reused in different environments
- **Security**: Implements principle of least privilege and encryption by default
- **Scalability**: Easy to extend and modify

## 📦 Modules

### 1. S3 Module (`modules/s3`)

**Purpose**: Create and manage S3 buckets for data, logs, and backups storage.

**Created resources**:
- 3 S3 buckets:
  - `{project}-data-{env}-{account_id}`: Data storage
  - `{project}-logs-{env}-{account_id}`: Logs storage
  - `{project}-backups-{env}-{account_id}`: Backups storage

**Features**:
- ✅ Versioning enabled on data and backups buckets
- ✅ AES256 encryption by default on all buckets
- ✅ Public access block
- ✅ Lifecycle policy for logs (90 days retention)
- ✅ Transition to STANDARD_IA after 30 days for logs

**Variables**:
```hcl
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "AWS Region"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

**Outputs**:
- `bucket_names`: Map with bucket names
- `bucket_arns`: List of bucket ARNs
- `data_bucket_id`, `logs_bucket_id`, `backups_bucket_id`: Individual IDs

### 2. Parameter Store Module (`modules/parameter-store`)

**Purpose**: Manage configuration parameters in AWS Systems Manager Parameter Store.

**Created parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `/{project}/{env}/database/host` | String | Database hostname |
| `/{project}/{env}/database/port` | String | Database port |
| `/{project}/{env}/database/name` | String | Database name |
| `/{project}/{env}/api/key` | SecureString | API Key (encrypted) |
| `/{project}/{env}/api/secret` | SecureString | API Secret (encrypted) |
| `/{project}/{env}/app/log-level` | String | Logging level |
| `/{project}/{env}/app/timeout` | String | Application timeout |
| `/{project}/{env}/aws/region` | String | AWS Region |

**Features**:
- ✅ Sensitive parameters use `SecureString` type (encrypted with KMS)
- ✅ Lifecycle `ignore_changes` on sensitive values to prevent overwrite
- ✅ Hierarchical naming for easy filtering
- ✅ Descriptive tags for categorization

**Variables**:
```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {}
}
```

**Outputs**:
- `parameter_names`: List of parameter names
- `parameter_arns`: List of parameter ARNs
- `database_host_arn`, `api_key_arn`: Specific ARNs

### 3. IAM Module (`modules/iam`)

**Purpose**: Create IAM roles and policies for Kubernetes Service Accounts (IRSA - IAM Roles for Service Accounts).

**Created resources**:

1. **IAM Role for Auxiliary Service**
   - Allows pod to assume role via OIDC
   - Trust policy bound to EKS OIDC provider
   - Condition: only specific ServiceAccount can assume the role

2. **S3 Access Policy**
   - `ListBucket`, `GetBucketLocation`, `ListBucketVersions`
   - `GetObject`, `PutObject`, `DeleteObject`, `GetObjectVersion`
   - `ListAllMyBuckets` (to list all account buckets)

3. **Parameter Store Access Policy**
   - `GetParameter`, `GetParameters`, `GetParameterHistory`
   - `GetParametersByPath`, `DescribeParameters`
   - `kms:Decrypt` permission for SecureStrings

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/OIDC_URL"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "OIDC_URL:sub": "system:serviceaccount:auxiliary-service:auxiliary-service-sa",
        "OIDC_URL:aud": "sts.amazonaws.com"
      }
    }
  }]
}
```

**Variables**:
```hcl
variable "eks_oidc_provider_arn" {
  description = "EKS OIDC provider ARN"
  type        = string
  default     = ""
}

variable "eks_oidc_provider_url" {
  description = "EKS OIDC provider URL"
  type        = string
  default     = ""
}

variable "s3_bucket_arns" {
  description = "S3 bucket ARNs"
  type        = list(string)
  default     = []
}

variable "parameter_arns" {
  description = "SSM parameter ARNs"
  type        = list(string)
  default     = []
}
```

**Note**: If you're not using EKS (e.g., with Kind locally), the module won't create resources (count = 0).

### 4. GitHub OIDC Module (`modules/github-oidc`)

**Purpose**: Configure secure authentication between GitHub Actions and AWS without static credentials.

**Created resources**:

1. **OIDC Provider for GitHub**
   - URL: `https://token.actions.githubusercontent.com`
   - GitHub thumbprints (publicly known values)
   - Client ID: `sts.amazonaws.com`

2. **IAM Role for GitHub Actions**
   - Allows GitHub Actions to assume role
   - Trust policy limits access to specific repository
   - Condition: only workflows from specified repository

3. **ECR Policy**
   - `ecr:GetAuthorizationToken` (global)
   - Push/pull images to ECR
   - Create repositories if they don't exist

4. **S3 Policy**
   - Access to buckets for artifacts

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:ORG/REPO:*"
      }
    }
  }]
}
```

**Variables**:
```hcl
variable "github_org" {
  description = "GitHub organization or user"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "Repository name"
  type        = string
}
```

## 🔧 Main Variables

Variables defined in `variables.tf`:

```hcl
# Required
variable "region" {
  default = "us-east-1"
}

variable "environment" {
  default = "dev"
}

variable "project_name" {
  default = "aws-challenge"
}

# For GitHub OIDC
variable "github_org" {
  description = "Your GitHub user/org"
  default     = ""
}

variable "github_repo" {
  default = "aws-challenge"
}

# For IRSA (only if using EKS)
variable "eks_cluster_name" {
  default = "aws-challenge-cluster"
}

variable "eks_oidc_provider_arn" {
  description = "OIDC provider ARN (get from EKS)"
  default     = ""
}

variable "eks_oidc_provider_url" {
  description = "OIDC provider URL (get from EKS)"
  default     = ""
}
```

## 📤 Outputs

Main available outputs:

```hcl
# S3
output "s3_bucket_names"
output "s3_bucket_arns"

# Parameter Store
output "parameter_store_names"
output "parameter_store_arns"

# IAM (only if eks_oidc_provider_arn is configured)
output "auxiliary_service_role_arn"
output "auxiliary_service_role_name"

# GitHub OIDC
output "github_actions_role_arn"
output "github_actions_role_name"
output "github_oidc_provider_arn"
```

## 🚀 Usage

### Initialization

```bash
cd terraform

# Initialize Terraform (download providers)
terraform init
```

### Planning

```bash
# See what resources will be created
terraform plan

# With custom variables
terraform plan \
  -var="region=your-aws-region" \
  -var="environment=prod" \
  -var="github_org=your-github-username"
```

### Application

```bash
# Create infrastructure
terraform apply

# Or with auto-approve (not recommended in prod)
terraform apply -auto-approve

# With variables
terraform apply \
  -var="region=your-aws-region" \
  -var="environment=dev" \
  -var="github_org=your-github-username"
```

### Outputs

```bash
# View all outputs
terraform output

# Specific output
terraform output s3_bucket_names

# In JSON format (useful for scripts)
terraform output -json > terraform-outputs.json
```

### Destruction

```bash
# Delete all infrastructure
terraform destroy

# With variables
terraform destroy -var="environment=dev"
```

## 🔒 Security

### Implemented Best Practices

1. **Encryption**:
   - S3: AES256 by default
   - Parameter Store: SecureString with KMS

2. **Minimum Access**:
   - IAM policies with specific permissions
   - No unnecessary wildcards

3. **Public Block**:
   - All S3 buckets block public access

4. **OIDC instead of credentials**:
   - GitHub Actions uses OIDC
   - Kubernetes uses IRSA (if EKS)

5. **Versioning**:
   - Important buckets have versioning enabled

6. **Tags**:
   - All resources are tagged for auditing

### State Management

For production, configure remote backend in `versions.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "aws-challenge/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## 🐛 Troubleshooting

### Error: "No valid credential sources"

**Solution**: Configure AWS CLI:
```bash
aws configure
```

### Error: "Bucket name already exists"

**Cause**: S3 bucket names are global

**Solution**: Code uses account ID to make them unique, but if it persists:
```bash
# Change the project_name
terraform apply -var="project_name=aws-challenge-unique-name"
```

### Error: OIDC provider not found

**Cause**: `eks_oidc_provider_arn` not configured

**Solution**: If using local EKS (Kind/Minikube), leave empty. If using real EKS:
```bash
# Get OIDC provider ARN
aws eks describe-cluster --name your-cluster --query "cluster.identity.oidc.issuer" --output text

# Use in Terraform
terraform apply -var="eks_oidc_provider_arn=arn:aws:iam::..."
```

## 📚 References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
