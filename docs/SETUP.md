# Detailed Setup Guide

This guide will walk you through the complete setup of the aws-challenge project step by step.

## 📋 Prerequisites

### Required Software

Make sure you have installed:

```bash
# Docker
docker --version  # >= 20.10

# kubectl
kubectl version --client  # >= 1.28

# Terraform
terraform version  # >= 1.5

# Helm
helm version  # >= 3.12

# AWS CLI
aws --version  # >= 2.13

# Kind (Kubernetes in Docker)
kind version  # >= 0.20
```

### Tools Installation (macOS)

```bash
# Using Homebrew
brew install docker kubectl terraform helm awscli kind

# Verify installations
docker --version
kubectl version --client
terraform version
helm version
aws --version
kind version
```

## 🔧 Step 1: Initial Setup

### 1.1 Clone the Repository

```bash
git clone https://github.com/your-github-username/aws-challenge.git
cd aws-challenge
```

### 1.2 Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Enter:
# AWS Access Key ID: your-access-key-id
# AWS Secret Access Key: your-secret-access-key
# Default region name: your-aws-region
# Default output format: json

# Verify
aws sts get-caller-identity
```

### 1.3 Update Configurations

Update the following files with your information:

**In `terraform/variables.tf`**:
```hcl
variable "github_org" {
  default     = "your-github-username"  # ← Change this
}

variable "github_repo" {
  default     = "aws-challenge"
}
```

**In `kubernetes/argocd/applications/*.yaml`**:
```yaml
source:
  repoURL: https://github.com/your-github-username/aws-challenge.git  # ← Change this
```

**In `kubernetes/base/*/deployment.yaml`**:
```yaml
image: your-dockerhub-username/main-api:latest  # ← Change this
```

## 🏗️ Step 2: Infrastructure with Terraform

### 2.1 Initialize and Apply Terraform

```bash
cd terraform

# Initialize
terraform init

# Plan (review changes)
terraform plan \
  -var="region=your-aws-region" \
  -var="environment=dev" \
  -var="github_org=your-github-username"

# Apply
terraform apply \
  -var="region=your-aws-region" \
  -var="environment=dev" \
  -var="github_org=your-github-username"

# When prompted, type 'yes'
```

### 2.2 Save Outputs

```bash
# Save outputs to file
terraform output -json > terraform-outputs.json

# View important outputs
terraform output s3_bucket_names
terraform output github_actions_role_arn
terraform output auxiliary_service_role_arn
```

### 2.3 Verify Created Resources

```bash
# Verify S3 buckets
aws s3 ls | grep aws-challenge

# Verify parameters
aws ssm describe-parameters --query "Parameters[?contains(Name, 'aws-challenge')].[Name,Type]" --output table

# Verify IAM roles
aws iam list-roles --query "Roles[?contains(RoleName, 'aws-challenge')].RoleName" --output table
```

## ⚓ Step 3: Create Kubernetes Cluster

### 3.1 Create Cluster with Kind

```bash
# Return to root directory
cd ..

# Create cluster
kind create cluster --name aws-challenge --config kind-config.yaml

# Verify
kubectl cluster-info --context kind-aws-challenge
kubectl get nodes
```

### 3.2 Create Namespaces

```bash
# Create namespaces
kubectl apply -f kubernetes/base/namespaces/

# Verify
kubectl get namespaces
```

## 🎯 Step 4: Install Argo CD

### 4.1 Install Argo CD

```bash
# Create namespace
kubectl create namespace argocd

# Install Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait until ready
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=5m
```

### 4.2 Access Argo CD

```bash
# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
# Save this password

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# In another terminal, open: https://localhost:8080
# Username: admin
# Password: (obtained above)
```

### 4.3 (Optional) Install Argo CD CLI

```bash
# macOS
brew install argocd

# Login
argocd login localhost:8080 --insecure --username admin --password <password>

# Change password
argocd account update-password
```

## 🐳 Step 5: Build and Publish Docker Images

### 5.1 Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### 5.2 Build and Publish Main API

```bash
# Go to directory
cd services/main-api

# Build image
docker build -t your-dockerhub-username/main-api:latest .

# Publish
docker push your-dockerhub-username/main-api:latest

# Return
cd ../..
```

### 5.3 Build and Publish Auxiliary Service

```bash
# Go to directory
cd services/auxiliary-service

# Build image
docker build -t your-dockerhub-username/auxiliary-service:latest .

# Publish
docker push your-dockerhub-username/auxiliary-service:latest

# Return
cd ../..
```

## 🚀 Step 6: Deploy Applications

### 6.1 Configure Service Account (if using EKS)

If you're using EKS with IRSA, update:

```bash
# Get role ARN
ROLE_ARN=$(cd terraform && terraform output -raw auxiliary_service_role_arn)

# Update ServiceAccount
kubectl annotate serviceaccount auxiliary-service-sa \
  -n auxiliary-service \
  eks.amazonaws.com/role-arn=$ROLE_ARN
```

### 6.2 Deploy with Argo CD

```bash
# Apply Applications
kubectl apply -f kubernetes/argocd/applications/

# Verify
kubectl get applications -n argocd

# Sync (manual if auto-sync is disabled)
argocd app sync main-api
argocd app sync auxiliary-service

# View status
argocd app list
```

### 6.3 Verify Deployment

```bash
# Verify Main API pods
kubectl get pods -n main-api
kubectl logs -n main-api -l app=main-api

# Verify Auxiliary Service pods
kubectl get pods -n auxiliary-service
kubectl logs -n auxiliary-service -l app=auxiliary-service

# Verify services
kubectl get svc -n main-api
kubectl get svc -n auxiliary-service
```

## 🧪 Step 7: Testing

### 7.1 Port Forward for Local Testing

```bash
# Main API
kubectl port-forward -n main-api svc/main-api-service 8000:80

# In another terminal, test
curl http://localhost:8000/health
```

### 7.2 Test Endpoints

```bash
# Health check
curl http://localhost:8000/health | jq

# List S3 buckets
curl http://localhost:8000/api/v1/s3/buckets | jq

# List parameters
curl http://localhost:8000/api/v1/parameters | jq

# Get specific parameter
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq
```

## 📊 Step 8: Configure Monitoring (Optional)

### 8.1 Add Helm Repos

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 8.2 Install Prometheus Stack

```bash
# Install
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  -f monitoring/prometheus/values.yaml

# Verify
kubectl get pods -n monitoring
```

### 8.3 Access Grafana

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open http://localhost:3000
# Username: admin
# Password: admin123 (or as defined in values.yaml)
```

## 🔐 Step 9: Configure GitHub Actions

### 9.1 Configure GitHub Secrets

Go to your GitHub repository:
1. Settings > Secrets and variables > Actions
2. Click "New repository secret"

Add the following secrets:

```
AWS_REGION=your-aws-region
AWS_ACCOUNT_ID=your-aws-account-id
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
```

### 9.2 Get Role ARN for GitHub Actions

```bash
cd terraform
terraform output -raw github_actions_role_arn
# Copy this ARN
```

Add as secret:
```
AWS_ROLE_ARN = (the ARN obtained)
```

### 9.3 Test Pipeline

```bash
# Make a small change
echo "# Test change" >> README.md

# Commit and push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# View in GitHub Actions
# Go to: https://github.com/your-github-username/aws-challenge/actions
```

## ✅ Final Verification

### Verification Checklist

- [ ] Terraform applied successfully
- [ ] S3 buckets created
- [ ] Parameters in Parameter Store
- [ ] Kubernetes cluster running
- [ ] Argo CD installed and accessible
- [ ] Docker images published
- [ ] Main API deployed and healthy
- [ ] Auxiliary Service deployed and healthy
- [ ] Endpoints responding correctly
- [ ] GitHub Actions configured
- [ ] (Optional) Prometheus and Grafana running

### Quick Verification Commands

```bash
# View entire stack
kubectl get all -n main-api
kubectl get all -n auxiliary-service

# View Argo CD applications
kubectl get applications -n argocd

# View health of everything
kubectl get pods --all-namespaces | grep -v Running
# (should not display anything)
```

## 🎓 Next Steps

1. Customize Grafana dashboards
2. Add unit and integration tests
3. Implement staging environment
4. Configure Prometheus alerts
5. Optimize Kubernetes resources

## 📞 Support

If you encounter problems, check:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [Terraform Documentation](TERRAFORM.md)
- [API Documentation](API.md)
