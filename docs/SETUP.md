# Guía de Configuración Detallada

Esta guía te llevará paso a paso por la configuración completa del proyecto aws-challenge.

## 📋 Requisitos Previos

### Software Necesario

Asegúrate de tener instalado:

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

### Instalación de Herramientas (macOS)

```bash
# Usando Homebrew
brew install docker kubectl terraform helm awscli kind

# Verificar instalaciones
docker --version
kubectl version --client
terraform version
helm version
aws --version
kind version
```

## 🔧 Paso 1: Configuración Inicial

### 1.1 Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/aws-challenge.git
cd aws-challenge
```

### 1.2 Configurar AWS Credentials

```bash
# Configurar AWS CLI
aws configure

# Ingresa:
# AWS Access Key ID: [tu-access-key]
# AWS Secret Access Key: [tu-secret-key]
# Default region name: us-east-1
# Default output format: json

# Verificar
aws sts get-caller-identity
```

### 1.3 Actualizar Configuraciones

Actualiza los siguientes archivos con tu información:

**En `terraform/variables.tf`**:
```hcl
variable "github_org" {
  default     = "tu-usuario-github"  # ← Cambiar
}

variable "github_repo" {
  default     = "aws-challenge"
}
```

**En `kubernetes/argocd/applications/*.yaml`**:
```yaml
source:
  repoURL: https://github.com/TU_USUARIO/aws-challenge.git  # ← Cambiar
```

**En `kubernetes/base/*/deployment.yaml`**:
```yaml
image: TU_DOCKERHUB_USERNAME/main-api:latest  # ← Cambiar
```

## 🏗️ Paso 2: Infraestructura con Terraform

### 2.1 Inicializar y Aplicar Terraform

```bash
cd terraform

# Inicializar
terraform init

# Planificar (revisar cambios)
terraform plan \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=tu-usuario"

# Aplicar
terraform apply \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=tu-usuario"

# Cuando pregunte, escribe 'yes'
```

### 2.2 Guardar Outputs

```bash
# Guardar outputs en archivo
terraform output -json > terraform-outputs.json

# Ver outputs importantes
terraform output s3_bucket_names
terraform output github_actions_role_arn
terraform output auxiliary_service_role_arn
```

### 2.3 Verificar Recursos Creados

```bash
# Verificar S3 buckets
aws s3 ls | grep aws-challenge

# Verificar parámetros
aws ssm describe-parameters --query "Parameters[?contains(Name, 'aws-challenge')].[Name,Type]" --output table

# Verificar IAM roles
aws iam list-roles --query "Roles[?contains(RoleName, 'aws-challenge')].RoleName" --output table
```

## ⚓ Paso 3: Crear Cluster Kubernetes

### 3.1 Crear Cluster con Kind

```bash
# Volver al directorio raíz
cd ..

# Crear cluster
kind create cluster --name aws-challenge --config kind-config.yaml

# Verificar
kubectl cluster-info --context kind-aws-challenge
kubectl get nodes
```

### 3.2 Crear Namespaces

```bash
# Crear namespaces
kubectl apply -f kubernetes/base/namespaces/

# Verificar
kubectl get namespaces
```

## 🎯 Paso 4: Instalar Argo CD

### 4.1 Instalar Argo CD

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que esté listo
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=5m
```

### 4.2 Acceder a Argo CD

```bash
# Obtener password inicial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
# Guardar este password

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# En otro terminal, abrir: https://localhost:8080
# Usuario: admin
# Password: (el obtenido arriba)
```

### 4.3 (Opcional) Instalar CLI de Argo CD

```bash
# macOS
brew install argocd

# Login
argocd login localhost:8080 --insecure --username admin --password <password>

# Cambiar password
argocd account update-password
```

## 🐳 Paso 5: Construir y Publicar Imágenes Docker

### 5.1 Login a Docker Hub

```bash
docker login
# Ingresa tu usuario y password de Docker Hub
```

### 5.2 Construir y Publicar Main API

```bash
# Ir al directorio
cd services/main-api

# Construir imagen
docker build -t TU_DOCKERHUB_USERNAME/main-api:latest .

# Publicar
docker push TU_DOCKERHUB_USERNAME/main-api:latest

# Volver
cd ../..
```

### 5.3 Construir y Publicar Auxiliary Service

```bash
# Ir al directorio
cd services/auxiliary-service

# Construir imagen
docker build -t TU_DOCKERHUB_USERNAME/auxiliary-service:latest .

# Publicar
docker push TU_DOCKERHUB_USERNAME/auxiliary-service:latest

# Volver
cd ../..
```

## 🚀 Paso 6: Desplegar Aplicaciones

### 6.1 Configurar Service Account (si usas EKS)

Si estás usando EKS con IRSA, actualiza:

```bash
# Obtener ARN del role
ROLE_ARN=$(cd terraform && terraform output -raw auxiliary_service_role_arn)

# Actualizar ServiceAccount
kubectl annotate serviceaccount auxiliary-service-sa \
  -n auxiliary-service \
  eks.amazonaws.com/role-arn=$ROLE_ARN
```

### 6.2 Desplegar con Argo CD

```bash
# Aplicar Applications
kubectl apply -f kubernetes/argocd/applications/

# Verificar
kubectl get applications -n argocd

# Sincronizar (manual si auto-sync está deshabilitado)
argocd app sync main-api
argocd app sync auxiliary-service

# Ver estado
argocd app list
```

### 6.3 Verificar Despliegue

```bash
# Verificar pods Main API
kubectl get pods -n main-api
kubectl logs -n main-api -l app=main-api

# Verificar pods Auxiliary Service
kubectl get pods -n auxiliary-service
kubectl logs -n auxiliary-service -l app=auxiliary-service

# Verificar servicios
kubectl get svc -n main-api
kubectl get svc -n auxiliary-service
```

## 🧪 Paso 7: Testing

### 7.1 Port Forward para Testing Local

```bash
# Main API
kubectl port-forward -n main-api svc/main-api-service 8000:80

# En otro terminal, probar
curl http://localhost:8000/health
```

### 7.2 Probar Endpoints

```bash
# Health check
curl http://localhost:8000/health | jq

# Listar S3 buckets
curl http://localhost:8000/api/v1/s3/buckets | jq

# Listar parámetros
curl http://localhost:8000/api/v1/parameters | jq

# Obtener parámetro específico
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq
```

## 📊 Paso 8: Configurar Monitoreo (Opcional)

### 8.1 Agregar Helm Repos

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 8.2 Instalar Prometheus Stack

```bash
# Instalar
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  -f monitoring/prometheus/values.yaml

# Verificar
kubectl get pods -n monitoring
```

### 8.3 Acceder a Grafana

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Abrir http://localhost:3000
# Usuario: admin
# Password: admin123 (o el definido en values.yaml)
```

## 🔐 Paso 9: Configurar GitHub Actions

### 9.1 Configurar Secrets en GitHub

Ve a tu repositorio en GitHub:
1. Settings > Secrets and variables > Actions
2. Click "New repository secret"

Agrega los siguientes secrets:

```
AWS_REGION = us-east-1
AWS_ACCOUNT_ID = (tu account ID, obtener con: aws sts get-caller-identity)
DOCKER_USERNAME = (tu usuario de Docker Hub)
DOCKER_PASSWORD = (tu password o token de Docker Hub)
```

### 9.2 Obtener Role ARN para GitHub Actions

```bash
cd terraform
terraform output -raw github_actions_role_arn
# Copiar este ARN
```

Agregar como secret:
```
AWS_ROLE_ARN = (el ARN obtenido)
```

### 9.3 Probar Pipeline

```bash
# Hacer un cambio pequeño
echo "# Test change" >> README.md

# Commit y push
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# Ver en GitHub Actions
# Ve a: https://github.com/TU_USUARIO/aws-challenge/actions
```

## ✅ Verificación Final

### Checklist de Verificación

- [ ] Terraform aplicado correctamente
- [ ] S3 buckets creados
- [ ] Parámetros en Parameter Store
- [ ] Cluster Kubernetes funcionando
- [ ] Argo CD instalado y accesible
- [ ] Imágenes Docker publicadas
- [ ] Main API desplegada y saludable
- [ ] Auxiliary Service desplegado y saludable
- [ ] Endpoints respondiendo correctamente
- [ ] GitHub Actions configurado
- [ ] (Opcional) Prometheus y Grafana funcionando

### Comandos de Verificación Rápida

```bash
# Ver todo el stack
kubectl get all -n main-api
kubectl get all -n auxiliary-service

# Ver aplicaciones de Argo CD
kubectl get applications -n argocd

# Ver health de todo
kubectl get pods --all-namespaces | grep -v Running
# (no debería mostrar nada)
```

## 🎓 Próximos Pasos

1. Personaliza los dashboards de Grafana
2. Agrega tests unitarios y de integración
3. Implementa staging environment
4. Configura alertas en Prometheus
5. Optimiza recursos de Kubernetes

## 📞 Soporte

Si encuentras problemas, consulta:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [Documentación de Terraform](TERRAFORM.md)
- [Documentación de API](API.md)
