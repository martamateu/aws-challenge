# 🚀 Inicio Rápido - AWS Challenge

Esta guía te ayudará a poner en marcha el proyecto en **menos de 30 minutos**.

## ⚡ Quick Start (5 comandos)

```bash
# 1. Crear cluster Kubernetes
kind create cluster --name aws-challenge --config kind-config.yaml

# 2. Aplicar infraestructura AWS
cd terraform && terraform init && terraform apply -auto-approve && cd ..

# 3. Construir y publicar imágenes Docker
docker build -t TU_USUARIO/main-api:latest services/main-api/ && docker push TU_USUARIO/main-api:latest
docker build -t TU_USUARIO/auxiliary-service:latest services/auxiliary-service/ && docker push TU_USUARIO/auxiliary-service:latest

# 4. Instalar Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 5. Desplegar aplicaciones
kubectl apply -f kubernetes/base/namespaces/
kubectl apply -f kubernetes/base/main-api/
kubectl apply -f kubernetes/base/auxiliary-service/
```

## 📝 Paso a Paso Detallado

### Antes de Empezar

**Requisitos previos:**
```bash
# Verificar herramientas instaladas
docker --version
kubectl version --client
terraform version
kind version
aws --version

# Si falta alguna (macOS):
brew install docker kubectl terraform kind awscli
```

**Configurar AWS:**
```bash
aws configure
# AWS Access Key ID: [tu-key]
# AWS Secret Access Key: [tu-secret]
# Default region: us-east-1
# Default output format: json

# Verificar
aws sts get-caller-identity
```

### Paso 1: Personalizar Configuración (5 min)

Actualiza los siguientes archivos con tu información:

**1. Variables de Terraform** (`terraform/variables.tf`):
```hcl
variable "github_org" {
  default = "tu-usuario-github"  # ← CAMBIAR
}
```

**2. Imágenes Docker** (en `kubernetes/base/*/deployment.yaml`):
```yaml
# main-api/deployment.yaml
image: tu-dockerhub-user/main-api:latest  # ← CAMBIAR

# auxiliary-service/deployment.yaml
image: tu-dockerhub-user/auxiliary-service:latest  # ← CAMBIAR
```

**3. Repositorio Git** (en `kubernetes/argocd/applications/*.yaml`):
```yaml
source:
  repoURL: https://github.com/tu-usuario/aws-challenge.git  # ← CAMBIAR
```

### Paso 2: Crear Cluster Kubernetes (3 min)

```bash
# Crear cluster con Kind
kind create cluster --name aws-challenge --config kind-config.yaml

# Verificar
kubectl cluster-info
kubectl get nodes
# Debe mostrar 1 control-plane y 2 workers
```

**Solución de problemas:**
```bash
# Si el cluster ya existe:
kind delete cluster --name aws-challenge
kind create cluster --name aws-challenge --config kind-config.yaml
```

### Paso 3: Desplegar Infraestructura AWS (5 min)

```bash
cd terraform

# Inicializar Terraform
terraform init

# Revisar plan
terraform plan \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=tu-usuario"

# Aplicar (escribir 'yes' cuando pregunte)
terraform apply \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=tu-usuario"

# Guardar outputs
terraform output -json > terraform-outputs.json

# Volver al directorio raíz
cd ..
```

**Verificar recursos creados:**
```bash
# S3 buckets
aws s3 ls | grep aws-challenge

# Parámetros
aws ssm describe-parameters --query "Parameters[?contains(Name, 'aws-challenge')].Name"

# IAM roles
aws iam list-roles --query "Roles[?contains(RoleName, 'aws-challenge')].RoleName"
```

### Paso 4: Construir y Publicar Imágenes Docker (7 min)

```bash
# Login a Docker Hub
docker login
# Usuario: tu-usuario
# Password: tu-password (o token)

# Construir Main API
cd services/main-api
docker build -t tu-dockerhub-user/main-api:latest .
docker push tu-dockerhub-user/main-api:latest
cd ../..

# Construir Auxiliary Service
cd services/auxiliary-service
docker build -t tu-dockerhub-user/auxiliary-service:latest .
docker push tu-dockerhub-user/auxiliary-service:latest
cd ../..
```

**Verificar imágenes:**
```bash
# Localmente
docker images | grep main-api
docker images | grep auxiliary-service

# En Docker Hub (navegador)
# https://hub.docker.com/r/tu-usuario/main-api
# https://hub.docker.com/r/tu-usuario/auxiliary-service
```

### Paso 5: Crear Namespaces (1 min)

```bash
# Crear todos los namespaces
kubectl apply -f kubernetes/base/namespaces/

# Verificar
kubectl get namespaces
# Debe mostrar: main-api, auxiliary-service, monitoring
```

### Paso 6: Instalar Argo CD (5 min)

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que esté listo (puede tomar 2-3 minutos)
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=5m

# Obtener password inicial
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
# GUARDAR ESTE PASSWORD
```

**Acceder a Argo CD UI:**
```bash
# En un terminal separado
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Abrir navegador: https://localhost:8080
# Usuario: admin
# Password: (el obtenido arriba)
```

### Paso 7: Desplegar Aplicaciones (2 min)

**Opción A: Despliegue Manual (para testing local)**
```bash
# Aplicar manifests directamente
kubectl apply -f kubernetes/base/main-api/
kubectl apply -f kubernetes/base/auxiliary-service/

# Verificar
kubectl get pods -n main-api
kubectl get pods -n auxiliary-service
```

**Opción B: Despliegue con Argo CD (recomendado)**
```bash
# Aplicar Argo CD Applications
kubectl apply -f kubernetes/argocd/applications/

# Verificar en UI de Argo CD
# O desde CLI:
kubectl get applications -n argocd

# Sincronizar manualmente si no auto-sync
kubectl patch application main-api -n argocd --type merge -p '{"operation": {"initiatedBy": {"username": "admin"}}}'
kubectl patch application auxiliary-service -n argocd --type merge -p '{"operation": {"initiatedBy": {"username": "admin"}}}'
```

### Paso 8: Verificar Despliegue (5 min)

```bash
# Ver todos los recursos
kubectl get all -n main-api
kubectl get all -n auxiliary-service

# Ver logs
kubectl logs -n main-api -l app=main-api --tail=50
kubectl logs -n auxiliary-service -l app=auxiliary-service --tail=50

# Verificar health
kubectl get pods -n main-api
kubectl get pods -n auxiliary-service
# Todos deben estar Running y Ready 1/1
```

**Esperar a que los pods estén listos:**
```bash
# Esto puede tomar 1-2 minutos
kubectl wait --for=condition=Ready pods --all -n main-api --timeout=3m
kubectl wait --for=condition=Ready pods --all -n auxiliary-service --timeout=3m
```

### Paso 9: Probar las APIs (3 min)

```bash
# Port forward Main API
kubectl port-forward -n main-api svc/main-api-service 8000:80

# En otro terminal, probar endpoints:

# 1. Health check
curl http://localhost:8000/health | jq

# 2. Listar S3 buckets
curl http://localhost:8000/api/v1/s3/buckets | jq

# 3. Listar parámetros
curl http://localhost:8000/api/v1/parameters | jq

# 4. Obtener valor de parámetro
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq
```

**Respuestas esperadas:**
```json
// Health check
{
  "status": "healthy",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0",
  "auxiliary_service_healthy": true,
  "timestamp": "2025-10-24T10:30:00Z"
}

// S3 buckets
{
  "buckets": [...],
  "count": 3,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

## ✅ Checklist Final

Antes de dar por completado:

- [ ] Cluster Kubernetes creado y funcionando
- [ ] Infraestructura AWS desplegada (S3, Parameter Store, IAM)
- [ ] Imágenes Docker construidas y publicadas
- [ ] Namespaces creados
- [ ] Argo CD instalado y accesible
- [ ] Aplicaciones desplegadas
- [ ] Pods en estado Running
- [ ] APIs respondiendo correctamente
- [ ] Versionado funcionando (visible en responses)

## 🐛 Problemas Comunes

### Pods en CrashLoopBackOff

```bash
# Ver logs
kubectl logs -n main-api <pod-name>

# Común: Variable de entorno faltante
kubectl get configmap -n main-api main-api-config -o yaml

# Común: Imagen incorrecta
kubectl describe pod -n main-api <pod-name> | grep Image
```

### Auxiliary Service no puede acceder AWS

```bash
# Verificar credenciales AWS
aws sts get-caller-identity

# Verificar que los permisos existen
aws s3 ls
aws ssm describe-parameters

# Si usas Kind local, los pods usan las credenciales de tu AWS CLI
# Para EKS, necesitas configurar IRSA correctamente
```

### Main API no puede conectar con Auxiliary Service

```bash
# Verificar que Auxiliary Service está running
kubectl get pods -n auxiliary-service

# Verificar service
kubectl get svc -n auxiliary-service

# Probar conectividad desde Main API pod
kubectl exec -it -n main-api <pod-name> -- sh
wget -O- http://auxiliary-service.auxiliary-service.svc.cluster.local:8001/health
```

## 🎓 Siguientes Pasos

1. **Configurar GitHub Actions:**
   - Agregar secrets en GitHub
   - Hacer push para trigger pipeline

2. **Instalar Prometheus:**
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack \
     -n monitoring -f monitoring/prometheus/values.yaml
   ```

3. **Explorar Argo CD:**
   - Sync applications
   - Ver history
   - Rollback changes

4. **Personalizar:**
   - Agregar nuevos endpoints
   - Modificar configuración
   - Agregar tests

## 📚 Documentación Adicional

- [SETUP.md](docs/SETUP.md) - Guía completa paso a paso
- [API.md](docs/API.md) - Documentación de APIs
- [TERRAFORM.md](docs/TERRAFORM.md) - Documentación de infraestructura
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Solución de problemas
- [COMANDOS.md](COMANDOS.md) - Referencia rápida de comandos

## 🎉 ¡Listo!

Si llegaste hasta aquí, tu proyecto está funcionando correctamente.

**Total time:** ~30 minutos

**Next:** Explora las APIs, personaliza la configuración, y prepara tu presentación para Kantox.

---

**Tip:** Usa el script automatizado para setup más rápido:
```bash
chmod +x quick-start.sh
./quick-start.sh
```
