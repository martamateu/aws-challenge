# Kubernetes Deployment with CI/CD & AWS Integration

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/aws-challenge/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/aws-challenge/actions)

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Configuración](#guía-de-configuración)
- [Despliegue](#despliegue)
- [Testing de APIs](#testing-de-apis)
- [Monitoreo](#monitoreo)
- [Troubleshooting](#troubleshooting)

## 📖 Descripción del Proyecto

Este proyecto implementa una arquitectura de microservicios en Kubernetes que interactúa con AWS, utilizando las mejores prácticas de Cloud Engineering, CI/CD y GitOps.

### Componentes Principales

1. **Main API**: API REST que expone endpoints para listar recursos de AWS
2. **Auxiliary Service**: Servicio backend que maneja las interacciones con AWS S3 y Parameter Store
3. **Infraestructura**: Definida como código usando Terraform
4. **CI/CD**: Automatización completa con GitHub Actions usando OIDC
5. **GitOps**: Despliegue declarativo con Argo CD
6. **Observabilidad**: Monitoreo con Prometheus y Grafana

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                               │
│  ┌──────────────┐          ┌─────────────────────┐          │
│  │  Source Code │──────────│  GitHub Actions     │          │
│  └──────────────┘          │  (CI/CD Pipeline)   │          │
│                            └──────────┬──────────┘          │
└───────────────────────────────────────┼──────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   ▼                   │
                    │     ┌─────────────────────────┐       │
                    │     │   Container Registry    │       │
                    │     │  (Docker Hub / ECR)     │       │
                    │     └──────────┬──────────────┘       │
                    │                │                       │
┌───────────────────┼────────────────┼───────────────────────┼──────────┐
│   Kubernetes      │                │                       │          │
│   Cluster         ▼                ▼                       │          │
│  ┌──────────────────────────────────────────┐              │          │
│  │            Argo CD                        │              │          │
│  │  (GitOps Deployment Management)          │              │          │
│  └────────────┬─────────────────────────────┘              │          │
│               │                                             │          │
│  ┌────────────┼─────────────────────────────────────┐      │          │
│  │ Namespace: main-api                              │      │          │
│  │  ┌─────────▼──────────┐    ┌─────────────────┐  │      │          │
│  │  │   Main API Pod     │    │   ConfigMap     │  │      │          │
│  │  │ ┌────────────────┐ │    │  - API Version  │  │      │          │
│  │  │ │  FastAPI App   │ │    └─────────────────┘  │      │          │
│  │  │ │  Port: 8000    │ │                          │      │          │
│  │  │ └────────────────┘ │    ┌─────────────────┐  │      │          │
│  │  └────────────────────┘    │    Service      │  │      │          │
│  │                             │  (LoadBalancer) │  │      │          │
│  │                             └─────────────────┘  │      │          │
│  └──────────────────────────────────────────────────┘      │          │
│                                                             │          │
│  ┌──────────────────────────────────────────────────┐      │          │
│  │ Namespace: auxiliary-service                     │      │          │
│  │  ┌────────────────────┐    ┌─────────────────┐  │      │          │
│  │  │ Auxiliary Service  │    │   ConfigMap     │  │      │          │
│  │  │ ┌────────────────┐ │    │ - Service Ver.  │  │      │          │
│  │  │ │  FastAPI App   │ │    └─────────────────┘  │      │          │
│  │  │ │  Port: 8001    │ │                          │      │          │
│  │  │ │  AWS SDK       │◄┼──────────────┐           │      │          │
│  │  │ └────────────────┘ │              │           │      │          │
│  │  └────────────────────┘    ┌─────────┴───────┐  │      │          │
│  │                             │    Service      │  │      │          │
│  │                             │  (ClusterIP)    │  │      │          │
│  │                             └─────────────────┘  │      │          │
│  └──────────────────────────────────────────────────┘      │          │
│                                                             │          │
│  ┌──────────────────────────────────────────────────┐      │          │
│  │ Namespace: monitoring                            │      │          │
│  │  ┌────────────────┐    ┌────────────────┐       │      │          │
│  │  │  Prometheus    │────│    Grafana     │       │      │          │
│  │  └────────────────┘    └────────────────┘       │      │          │
│  └──────────────────────────────────────────────────┘      │          │
└─────────────────────────────────────────────────────────────┘          │
                                                                          │
┌─────────────────────────────────────────────────────────────────────────┘
│                            AWS
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│  │   S3 Buckets    │  │ Parameter Store  │  │  IAM Roles/IRSA    │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘
└──────────────────────────────────────────────────────────────────────
```

## 🔧 Requisitos Previos

### Herramientas Necesarias

- **Docker**: v20.10+
- **kubectl**: v1.28+
- **Terraform**: v1.5+
- **Helm**: v3.12+
- **AWS CLI**: v2.13+
- **Kind/Minikube/K3s**: Para cluster Kubernetes local

### Cuentas y Accesos

- Cuenta de AWS con permisos de administrador
- Cuenta de GitHub
- (Opcional) Cuenta de Docker Hub o acceso a Amazon ECR

## 📁 Estructura del Proyecto

```
aws-challenge/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml                 # Pipeline CI/CD principal
│       └── terraform.yml             # Pipeline para infraestructura
├── services/
│   ├── main-api/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # FastAPI application
│   │   │   ├── config.py            # Configuración
│   │   │   └── routers/
│   │   │       └── aws_resources.py # Endpoints AWS
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── tests/
│   └── auxiliary-service/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py              # FastAPI application
│       │   ├── config.py
│       │   └── services/
│       │       └── aws_service.py   # AWS SDK interactions
│       ├── Dockerfile
│       ├── requirements.txt
│       └── tests/
├── terraform/
│   ├── main.tf                       # Configuración principal
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   └── modules/
│       ├── s3/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── parameter-store/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── iam/
│       │   ├── main.tf              # IAM roles, policies, IRSA
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── github-oidc/
│           ├── main.tf              # GitHub OIDC provider
│           ├── variables.tf
│           └── outputs.tf
├── kubernetes/
│   ├── base/
│   │   ├── namespaces/
│   │   │   ├── main-api.yaml
│   │   │   ├── auxiliary-service.yaml
│   │   │   └── monitoring.yaml
│   │   ├── main-api/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── serviceaccount.yaml
│   │   └── auxiliary-service/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── configmap.yaml
│   │       └── serviceaccount.yaml
│   ├── overlays/
│   │   ├── dev/
│   │   └── prod/
│   └── argocd/
│       ├── applications/
│       │   ├── main-api.yaml
│       │   └── auxiliary-service.yaml
│       └── argocd-install.yaml
├── monitoring/
│   ├── prometheus/
│   │   └── values.yaml
│   └── grafana/
│       ├── values.yaml
│       └── dashboards/
│           └── microservices-dashboard.json
├── docs/
│   ├── SETUP.md                      # Guía de configuración detallada
│   ├── API.md                        # Documentación de APIs
│   ├── TERRAFORM.md                  # Documentación Terraform
│   └── TROUBLESHOOTING.md
└── README.md
```

## 🚀 Guía de Configuración

### 1. Configuración del Entorno Local

#### Clonar el repositorio

```bash
git clone https://github.com/YOUR_USERNAME/aws-challenge.git
cd aws-challenge
```

#### Configurar AWS CLI

```bash
aws configure
# Ingresa tus credenciales de AWS
```

#### Crear cluster Kubernetes local (usando Kind)

```bash
# Instalar Kind
brew install kind  # macOS

# Crear cluster
kind create cluster --name aws-challenge --config kind-config.yaml

# Verificar
kubectl cluster-info
kubectl get nodes
```

### 2. Desplegar Infraestructura con Terraform

```bash
cd terraform

# Inicializar Terraform
terraform init

# Planificar cambios
terraform plan -var="region=us-east-1" -var="environment=dev"

# Aplicar infraestructura
terraform apply -auto-approve

# Guardar outputs importantes
terraform output -json > terraform-outputs.json
```

**Recursos creados:**
- 3 S3 buckets (data, logs, backups)
- Parámetros en AWS Systems Manager Parameter Store
- IAM roles y políticas para IRSA (IAM Roles for Service Accounts)
- GitHub OIDC provider para CI/CD seguro
- Service Accounts de Kubernetes

### 3. Configurar GitHub Secrets

Agrega los siguientes secrets en tu repositorio de GitHub (Settings > Secrets and variables > Actions):

```
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password (o token)
```

### 4. Instalar Argo CD

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que todos los pods estén listos
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s

# Obtener password inicial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port forward para acceder a la UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Acceder a https://localhost:8080
# Usuario: admin
# Password: (el obtenido arriba)
```

### 5. Desplegar Aplicaciones con Argo CD

```bash
# Aplicar las Applications de Argo CD
kubectl apply -f kubernetes/argocd/applications/

# Verificar el estado
kubectl get applications -n argocd

# Sincronizar aplicaciones
argocd app sync main-api
argocd app sync auxiliary-service
```

### 6. Instalar Stack de Monitoreo (Opcional)

```bash
# Agregar repos de Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Instalar Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  -f monitoring/prometheus/values.yaml

# Verificar instalación
kubectl get pods -n monitoring

# Acceder a Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Usuario: admin, Password: prom-operator (o el definido en values.yaml)
```

## 🧪 Testing de APIs

### Verificar que los servicios están corriendo

```bash
# Verificar pods
kubectl get pods -n main-api
kubectl get pods -n auxiliary-service

# Obtener servicios
kubectl get svc -n main-api
```

### Acceder a Main API

```bash
# Port forward
kubectl port-forward -n main-api svc/main-api-service 8000:80

# O si usas LoadBalancer
export MAIN_API_URL=$(kubectl get svc -n main-api main-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

### Ejemplos de Requests

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0",
  "timestamp": "2025-10-24T10:30:00Z"
}
```

#### 2. Listar todos los S3 Buckets

```bash
curl http://localhost:8000/api/v1/s3/buckets
```

**Respuesta esperada:**
```json
{
  "buckets": [
    {
      "name": "aws-challenge-data-dev",
      "creation_date": "2025-10-24T08:00:00Z"
    },
    {
      "name": "aws-challenge-logs-dev",
      "creation_date": "2025-10-24T08:00:00Z"
    },
    {
      "name": "aws-challenge-backups-dev",
      "creation_date": "2025-10-24T08:00:00Z"
    }
  ],
  "count": 3,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

#### 3. Listar todos los parámetros del Parameter Store

```bash
curl http://localhost:8000/api/v1/parameters
```

**Respuesta esperada:**
```json
{
  "parameters": [
    {
      "name": "/aws-challenge/dev/database/host",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00Z"
    },
    {
      "name": "/aws-challenge/dev/api/key",
      "type": "SecureString",
      "last_modified": "2025-10-24T08:00:00Z"
    }
  ],
  "count": 2,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

#### 4. Obtener valor de un parámetro específico

```bash
curl http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host
```

**Respuesta esperada:**
```json
{
  "name": "/aws-challenge/dev/database/host",
  "value": "db.example.com",
  "type": "String",
  "version": 1,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

### Testing con versiones en Headers

Todas las respuestas también incluyen headers personalizados:

```bash
curl -I http://localhost:8000/health
```

```
HTTP/1.1 200 OK
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
Content-Type: application/json
```

## 📊 Monitoreo

### Acceder a Prometheus

```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Abrir http://localhost:9090

### Acceder a Grafana

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Abrir http://localhost:3000

**Dashboards incluidos:**
- Kubernetes Cluster Monitoring
- Microservices Performance
- AWS API Calls Metrics
- Request/Response Times

## 🔒 Seguridad

### Autenticación con AWS

Este proyecto utiliza **IRSA (IAM Roles for Service Accounts)** para autenticación segura:

1. No hay credenciales hardcodeadas
2. Los pods asumen roles de IAM mediante service accounts de Kubernetes
3. GitHub Actions usa OIDC para evitar almacenar credenciales estáticas

### Secrets Management

- Secrets de AWS manejados por AWS Secrets Manager / Parameter Store
- ConfigMaps solo para configuración no sensible
- Service Accounts con permisos mínimos necesarios (Principle of Least Privilege)

## 🔄 CI/CD Pipeline

El pipeline de GitHub Actions realiza:

1. **Build**: Construye imágenes Docker para ambos servicios
2. **Test**: Ejecuta tests unitarios y de integración
3. **Push**: Sube imágenes al registry con tags semánticos
4. **Update**: Actualiza manifests de Kubernetes con nueva versión
5. **Deploy**: Argo CD detecta cambios y despliega automáticamente

### Trigger del Pipeline

```bash
# Cualquier push a main dispara el pipeline
git add .
git commit -m "feat: new feature"
git push origin main
```

## 🐛 Troubleshooting

Ver [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para soluciones a problemas comunes.

## 📝 Licencia

MIT License

## 👤 Autor

Marta Mateu - Cloud Engineer Challenge para Kantox

---

**¿Preguntas o sugerencias?** Abre un issue en este repositorio.
