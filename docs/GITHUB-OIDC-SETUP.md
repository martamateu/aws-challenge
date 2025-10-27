# GitHub OIDC Setup for AWS

This guide explains how to configure GitHub Actions to connect to AWS using OIDC (OpenID Connect) instead of static credentials.

## Why OIDC Instead of Static Credentials?

✅ **Security Best Practice**: No long-lived credentials stored in GitHub  
✅ **Automatic Rotation**: Temporary credentials expire automatically  
✅ **Audit Trail**: Better tracking of who accessed what  
✅ **Compliance**: Meets security requirements for production systems

## Prerequisites

1. AWS account with admin access
2. Terraform already deployed (creates OIDC provider and IAM role)
3. GitHub repository with Actions enabled

## Step 1: Deploy Terraform Infrastructure

The Terraform code already creates:
- AWS OIDC provider for GitHub Actions
- IAM role with trust policy for your repository
- Necessary permissions for S3, SSM, ECR

```bash
cd terraform
terraform init
terraform apply
```

After deployment, note the output:
```bash
terraform output github_actions_role_arn
# Output: arn:aws:iam::your-account-id:role/aws-challenge-github-actions-dev
```

## Step 2: Configure GitHub Secrets

Go to your repository settings: `Settings` → `Secrets and variables` → `Actions`

### Required Secrets for OIDC

Add the following repository secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ROLE_ARN` | ARN of the IAM role from Terraform output | `arn:aws:iam::123456789012:role/aws-challenge-github-actions-dev` |
| `AWS_DEFAULT_REGION` | Your AWS region | `eu-west-1` |
| `DOCKER_USERNAME` | Your Docker Hub username | `your-dockerhub-username` |
| `DOCKER_PASSWORD` | Your Docker Hub password or token | `dckr_pat_xxxxx` |

### ⚠️ Remove Old Secrets

**Delete these old static credential secrets** (if they exist):
- ❌ `AWS_ACCESS_KEY_ID` (no longer needed)
- ❌ `AWS_SECRET_ACCESS_KEY` (no longer needed)

## Step 3: Verify Terraform Configuration

Check that your `terraform/main.tf` includes the GitHub OIDC module:

```hcl
module "github_oidc" {
  source = "./modules/github-oidc"
  
  project_name = var.project_name
  environment  = var.environment
  github_org   = var.github_org      # Your GitHub username/org
  github_repo  = "aws-challenge"     # Your repository name
  
  tags = local.common_tags
}
```

Ensure variables are set in `terraform/terraform.tfvars`:

```hcl
github_org = "your-github-username"  # Change this to your GitHub username
```

## Step 4: How OIDC Works in the Workflow

The updated `.github/workflows/ci-cd.yml` now uses:

```yaml
permissions:
  id-token: write  # Required for OIDC
  contents: read

steps:
  - name: Configure AWS credentials via OIDC
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: ${{ secrets.AWS_DEFAULT_REGION }}
      role-session-name: GitHubActions-AuxiliaryService
```

**What happens:**
1. GitHub Actions requests a token from GitHub OIDC provider
2. Token includes repository information (`repo:owner/repo:ref:refs/heads/main`)
3. AWS STS validates the token against the OIDC provider
4. If trust policy matches, AWS issues temporary credentials (valid for 1 hour)
5. Workflow uses temporary credentials to access AWS resources

## Step 5: Test the OIDC Connection

### 5.1 Trigger a GitHub Actions Workflow

```bash
# Make a small change to trigger the workflow
git commit --allow-empty -m "test: verify OIDC connection"
git push origin main
```

### 5.2 Check the Workflow

Go to: `https://github.com/your-username/aws-challenge/actions`

Look for the "Configure AWS credentials via OIDC" step. It should show:
```
✓ Assuming role with OIDC
✓ Role assumed successfully
```

### 5.3 Verify AWS Access

In the workflow logs, you should see successful AWS operations:
```
✓ Running tests with AWS access
✓ Pytest completed successfully
```

## Troubleshooting

### Error: "Not authorized to perform sts:AssumeRoleWithWebIdentity"

**Cause**: GitHub repository doesn't match the trust policy

**Solution**: Check your Terraform variables:
```bash
cd terraform
terraform console
> var.github_org
> var.github_repo
```

Update `terraform.tfvars`:
```hcl
github_org = "your-actual-github-username"
```

Then reapply:
```bash
terraform apply
```

### Error: "AssumeRole Session Policy size exceeds"

**Cause**: Too many inline policies

**Solution**: The module uses managed policies - check `modules/github-oidc/main.tf`

### Error: "Signature expired"

**Cause**: Clock skew or token already used

**Solution**: Re-run the workflow. Tokens are short-lived (15 minutes) and can only be used once.

### Verify Trust Policy

Check the IAM role trust policy:
```bash
aws iam get-role --role-name aws-challenge-github-actions-dev \
  --query 'Role.AssumeRolePolicyDocument'
```

Should include:
```json
{
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:your-username/aws-challenge:*"
    }
  }
}
```

## Security Benefits

### Before (Static Credentials)
```yaml
- name: Configure AWS
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}      # ❌ Long-lived
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }} # ❌ Stored in GitHub
    aws-region: us-east-1
```

**Risks:**
- ❌ Credentials never expire
- ❌ If leaked, attacker has permanent access
- ❌ Hard to rotate
- ❌ Shared across all workflows

### After (OIDC)
```yaml
permissions:
  id-token: write  # ✅ Request temporary token

- name: Configure AWS via OIDC
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}  # ✅ Role ARN only
    aws-region: eu-west-1
```

**Benefits:**
- ✅ Credentials expire in 1 hour
- ✅ No secrets to leak
- ✅ Automatic rotation
- ✅ Per-workflow, per-run credentials
- ✅ Full AWS CloudTrail audit logs

## AWS CloudTrail Logs

View who accessed AWS and when:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=GitHubActions-AuxiliaryService \
  --max-results 10
```

You'll see entries like:
```json
{
  "Username": "GitHubActions-AuxiliaryService",
  "AssumedRole": "aws-challenge-github-actions-dev",
  "SourceIPAddress": "github.com",
  "EventTime": "2025-10-27T10:30:00Z"
}
```

## Migration Checklist

- [x] Deploy Terraform with OIDC module
- [x] Get IAM role ARN from Terraform output
- [x] Add `AWS_ROLE_ARN` to GitHub Secrets
- [x] Add `AWS_DEFAULT_REGION` to GitHub Secrets
- [x] Update workflow to use `role-to-assume` instead of static credentials
- [x] Add `permissions: id-token: write` to jobs
- [x] Delete old `AWS_ACCESS_KEY_ID` secret
- [x] Delete old `AWS_SECRET_ACCESS_KEY` secret
- [x] Test workflow runs successfully
- [x] Verify AWS access in workflow logs

## Additional Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS IAM OIDC Provider](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [configure-aws-credentials Action](https://github.com/aws-actions/configure-aws-credentials)

---

**Note**: This is a one-time setup. Once configured, all future workflows automatically use OIDC without any changes needed.
