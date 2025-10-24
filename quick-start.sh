#!/bin/bash

# Quick Start Script for AWS Challenge
# This script automates the initial setup

set -e

echo "🚀 AWS Challenge - Quick Start Script"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
    else
        echo -e "${RED}✗${NC} $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "Checking required tools..."
check_tool docker
check_tool kubectl
check_tool terraform
check_tool helm
check_tool kind
check_tool aws

echo ""
echo "All required tools are installed!"
echo ""

# Ask for user inputs
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your Docker Hub username: " DOCKER_USER
read -p "Enter AWS region [us-east-1]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

echo ""
echo "Configuration:"
echo "  GitHub User: $GITHUB_USER"
echo "  Docker User: $DOCKER_USER"
echo "  AWS Region: $AWS_REGION"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "📝 Step 1: Creating Kind cluster..."
kind create cluster --name aws-challenge --config kind-config.yaml || echo "Cluster may already exist"

echo ""
echo "📝 Step 2: Applying Terraform..."
cd terraform
terraform init
terraform apply -auto-approve \
    -var="region=$AWS_REGION" \
    -var="environment=dev" \
    -var="github_org=$GITHUB_USER"

echo ""
echo "📝 Step 3: Saving Terraform outputs..."
terraform output -json > terraform-outputs.json
cd ..

echo ""
echo "📝 Step 4: Creating Kubernetes namespaces..."
kubectl apply -f kubernetes/base/namespaces/

echo ""
echo "📝 Step 5: Installing Argo CD..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "Waiting for Argo CD to be ready..."
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=5m

echo ""
echo "📝 Step 6: Building Docker images..."
echo "Building Main API..."
docker build -t $DOCKER_USER/main-api:latest services/main-api/

echo "Building Auxiliary Service..."
docker build -t $DOCKER_USER/auxiliary-service:latest services/auxiliary-service/

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Push Docker images:"
echo "   docker login"
echo "   docker push $DOCKER_USER/main-api:latest"
echo "   docker push $DOCKER_USER/auxiliary-service:latest"
echo ""
echo "2. Update Kubernetes manifests with your Docker username"
echo ""
echo "3. Deploy applications:"
echo "   kubectl apply -f kubernetes/argocd/applications/"
echo ""
echo "4. Get Argo CD password:"
echo "   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo ""
echo "5. Access Argo CD:"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   Open: https://localhost:8080"
echo ""
echo "6. Access Main API:"
echo "   kubectl port-forward -n main-api svc/main-api-service 8000:80"
echo "   Test: curl http://localhost:8000/health"
echo ""
