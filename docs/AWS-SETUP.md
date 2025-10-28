# AWS Setup Guide

## Prerequisites

This project requires:
- AWS account with programmatic access
- AWS CLI configured
- IAM user with appropriate permissions

## Quick Setup

### 1. Install AWS CLI

```bash
# macOS
brew install awscli

# Verify installation
aws --version
```

### 2. Configure AWS Credentials

```bash
aws configure
```

You'll need:
- **Access Key ID**: Your IAM user access key
- **Secret Access Key**: Your IAM user secret key
- **Default region**: `eu-west-1` (recommended) or your preferred region
- **Output format**: `json`

### 3. Verify Configuration

```bash
# Check your identity
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "...",
#     "Account": "",
#     "Arn": ""
# }
```

## IAM Permissions Required

Your IAM user needs permissions for:
- **S3**: Full access (`s3:*`)
- **Systems Manager**: Parameter Store access (`ssm:*`)
- **IAM**: Role and policy management (`iam:*`)
- **STS**: AssumeRole operations (`sts:*`)

**For development/testing**: Attach the `AdministratorAccess` policy to your IAM user.

**For production**: Use the principle of least privilege with a custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "ssm:*",
        "iam:*",
        "sts:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## What Terraform Creates

Terraform will automatically provision:

- ✅ **S3 Buckets**: Data, logs, and backups
- ✅ **Parameter Store**: Configuration parameters
- ✅ **IAM Roles**: Service roles and GitHub OIDC role
- ✅ **IAM Policies**: Least-privilege access policies
- ✅ **OIDC Provider**: GitHub Actions authentication

You don't need to create any AWS resources manually.

## Region Configuration

Default region: `eu-west-1` (Ireland)

To change the region, edit `terraform/environments/dev/terraform.tfvars`:

```hcl
aws_region = "your-preferred-region"
```

## Verification Checklist

Before running Terraform, verify:

```bash
# 1. AWS CLI installed
aws --version

# 2. Credentials configured
aws sts get-caller-identity

# 3. Terraform installed
terraform version

# 4. Can list S3 buckets (permission check)
aws s3 ls
```

## Next Steps

Once AWS is configured:

```bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

## Troubleshooting

### "Unable to locate credentials"
```bash
aws configure  # Reconfigure credentials
```

### "Access Denied"
Verify your IAM user has the required permissions (see IAM Permissions section above).

### "Invalid region"
```bash
aws configure set region eu-west-1
```

## Cost Estimate

This project stays within AWS Free Tier:
- S3: Free for <5GB storage
- Parameter Store (Standard): Free
- IAM: Always free

**Estimated cost**: $0/month (within Free Tier limits)
