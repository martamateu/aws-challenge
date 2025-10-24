#!/bin/bash

# Cleanup Script for AWS Challenge
# This script destroys all resources created

set -e

echo "🧹 AWS Challenge - Cleanup Script"
echo "=================================="
echo ""

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}WARNING: This will delete all resources!${NC}"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "📝 Step 1: Deleting Kubernetes resources..."
kubectl delete -f kubernetes/argocd/applications/ --ignore-not-found=true
kubectl delete namespace main-api --ignore-not-found=true
kubectl delete namespace auxiliary-service --ignore-not-found=true
kubectl delete namespace monitoring --ignore-not-found=true
kubectl delete namespace argocd --ignore-not-found=true

echo ""
echo "📝 Step 2: Deleting Kind cluster..."
kind delete cluster --name aws-challenge || echo "Cluster may not exist"

echo ""
echo "📝 Step 3: Destroying Terraform resources..."
cd terraform
terraform destroy -auto-approve
cd ..

echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "All resources have been deleted."
