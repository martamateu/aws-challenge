# Comandos Útiles - AWS Challenge

Este archivo contiene comandos útiles para trabajar con el proyecto.

## 🐳 Docker

### Build y Push de Imágenes

```bash
# Main API
docker build -t TU_USUARIO/main-api:latest services/main-api/
docker push TU_USUARIO/main-api:latest

# Auxiliary Service
docker build -t TU_USUARIO/auxiliary-service:latest services/auxiliary-service/
docker push TU_USUARIO/auxiliary-service:latest

# Build con tag específico
docker build -t TU_USUARIO/main-api:v1.0.0 services/main-api/
docker tag TU_USUARIO/main-api:v1.0.0 TU_USUARIO/main-api:latest

# Login a Docker Hub
docker login

# Ver imágenes locales
docker images | grep main-api
docker images | grep auxiliary-service
```

### Testing Local

```bash
# Correr Main API localmente
cd services/main-api
docker build -t main-api-test .
docker run -p 8000:8000 -e AUXILIARY_SERVICE_URL=http://host.docker.internal:8001 main-api-test

# Correr Auxiliary Service localmente (requiere AWS credentials)
cd services/auxiliary-service
docker build -t aux-service-test .
docker run -p 8001:8001 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-east-1 \
  aux-service-test
```

## ⚓ Kubernetes

### Cluster Management

```bash
# Crear cluster Kind
kind create cluster --name aws-challenge --config kind-config.yaml

# Ver clusters
kind get clusters

# Eliminar cluster
kind delete cluster --name aws-challenge

# Cambiar contexto
kubectl config use-context kind-aws-challenge

# Ver contextos
kubectl config get-contexts

# Ver nodos
kubectl get nodes
```

### Namespaces

```bash
# Crear todos los namespaces
kubectl apply -f kubernetes/base/namespaces/

# Ver namespaces
kubectl get namespaces

# Eliminar namespace
kubectl delete namespace main-api
```

### Deployments y Pods

```bash
# Ver todos los recursos en un namespace
kubectl get all -n main-api
kubectl get all -n auxiliary-service

# Ver pods
kubectl get pods -n main-api
kubectl get pods -n auxiliary-service --watch

# Ver detalles de un pod
kubectl describe pod -n main-api <pod-name>

# Ver logs
kubectl logs -n main-api -l app=main-api
kubectl logs -n main-api -l app=main-api --follow
kubectl logs -n main-api <pod-name>

# Logs de container específico
kubectl logs -n main-api <pod-name> -c main-api

# Ejecutar comando en pod
kubectl exec -it -n main-api <pod-name> -- /bin/sh
kubectl exec -it -n main-api <pod-name> -- python --version

# Port forward
kubectl port-forward -n main-api svc/main-api-service 8000:80
kubectl port-forward -n auxiliary-service svc/auxiliary-service 8001:8001
kubectl port-forward -n main-api <pod-name> 8000:8000
```

### Services

```bash
# Ver servicios
kubectl get svc -n main-api
kubectl get svc -n auxiliary-service

# Detalles de servicio
kubectl describe svc -n main-api main-api-service

# Ver endpoints
kubectl get endpoints -n main-api
```

### ConfigMaps

```bash
# Ver ConfigMaps
kubectl get configmap -n main-api
kubectl get configmap -n auxiliary-service

# Ver contenido
kubectl describe configmap -n main-api main-api-config
kubectl get configmap -n main-api main-api-config -o yaml

# Editar ConfigMap
kubectl edit configmap -n main-api main-api-config
```

### Aplicar Manifests

```bash
# Aplicar todo
kubectl apply -f kubernetes/base/namespaces/
kubectl apply -f kubernetes/base/main-api/
kubectl apply -f kubernetes/base/auxiliary-service/

# Aplicar archivo específico
kubectl apply -f kubernetes/base/main-api/deployment.yaml

# Eliminar recursos
kubectl delete -f kubernetes/base/main-api/

# Ver diferencias antes de aplicar
kubectl diff -f kubernetes/base/main-api/deployment.yaml
```

### Debugging

```bash
# Ver eventos
kubectl get events -n main-api --sort-by='.lastTimestamp'
kubectl get events -n main-api --watch

# Verificar salud de pods
kubectl get pods -n main-api -o wide
kubectl top pods -n main-api

# Restart deployment
kubectl rollout restart deployment/main-api -n main-api

# Ver historial de rollout
kubectl rollout history deployment/main-api -n main-api

# Rollback
kubectl rollout undo deployment/main-api -n main-api

# Scale
kubectl scale deployment/main-api -n main-api --replicas=3
```

## 🎯 Argo CD

### Instalación

```bash
# Crear namespace
kubectl create namespace argocd

# Instalar
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Esperar a que esté listo
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=5m

# Obtener password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

### Acceso

```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# CLI login
argocd login localhost:8080 --insecure --username admin

# Cambiar password
argocd account update-password
```

### Gestión de Applications

```bash
# Aplicar applications
kubectl apply -f kubernetes/argocd/applications/

# Ver applications
kubectl get applications -n argocd
argocd app list

# Ver detalles
argocd app get main-api
kubectl describe application -n argocd main-api

# Sincronizar manualmente
argocd app sync main-api
argocd app sync auxiliary-service

# Sincronizar todo
argocd app sync --all

# Ver logs de sync
argocd app logs main-api

# Ver diferencias
argocd app diff main-api

# Eliminar application
argocd app delete main-api
kubectl delete application -n argocd main-api
```

## 🏗️ Terraform

### Comandos Básicos

```bash
cd terraform

# Inicializar
terraform init

# Formatear código
terraform fmt -recursive

# Validar
terraform validate

# Planificar
terraform plan
terraform plan -out=tfplan

# Aplicar
terraform apply
terraform apply tfplan
terraform apply -auto-approve

# Destruir
terraform destroy
terraform destroy -target=module.s3
```

### Con Variables

```bash
# Pasar variables
terraform apply \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=mi-usuario"

# Usar archivo de variables
terraform apply -var-file="dev.tfvars"

# Variables de entorno
export TF_VAR_region=us-east-1
terraform apply
```

### Outputs

```bash
# Ver todos los outputs
terraform output

# Output específico
terraform output s3_bucket_names

# JSON format
terraform output -json
terraform output -json > outputs.json

# Raw (útil para scripts)
terraform output -raw github_actions_role_arn
```

### State Management

```bash
# Ver state
terraform show

# Listar recursos en state
terraform state list

# Ver recurso específico
terraform state show module.s3.aws_s3_bucket.data

# Refresh state
terraform refresh

# Import recurso existente
terraform import module.s3.aws_s3_bucket.data my-bucket-name
```

## 🐞 AWS CLI

### S3

```bash
# Listar buckets
aws s3 ls

# Listar contenido de bucket
aws s3 ls s3://bucket-name/

# Ver buckets del proyecto
aws s3api list-buckets --query "Buckets[?contains(Name, 'aws-challenge')].Name"
```

### Parameter Store

```bash
# Listar parámetros
aws ssm describe-parameters

# Listar parámetros del proyecto
aws ssm describe-parameters \
  --query "Parameters[?contains(Name, 'aws-challenge')].[Name,Type]" \
  --output table

# Obtener valor de parámetro
aws ssm get-parameter --name "/aws-challenge/dev/database/host"
aws ssm get-parameter --name "/aws-challenge/dev/api/key" --with-decryption

# Obtener parámetros por path
aws ssm get-parameters-by-path --path "/aws-challenge/dev/"
aws ssm get-parameters-by-path --path "/aws-challenge/dev/" --recursive --with-decryption
```

### IAM

```bash
# Ver roles
aws iam list-roles --query "Roles[?contains(RoleName, 'aws-challenge')].RoleName"

# Ver detalles de rol
aws iam get-role --role-name aws-challenge-auxiliary-service-dev

# Ver políticas de rol
aws iam list-attached-role-policies --role-name aws-challenge-auxiliary-service-dev

# Ver trust policy
aws iam get-role --role-name aws-challenge-auxiliary-service-dev \
  --query 'Role.AssumeRolePolicyDocument'
```

### General

```bash
# Obtener account ID
aws sts get-caller-identity

# Ver región configurada
aws configure get region

# Ver credenciales configuradas
aws configure list
```

## 📊 Monitoreo

### Prometheus

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Ver targets
curl http://localhost:9090/api/v1/targets | jq

# Query métricas
curl 'http://localhost:9090/api/v1/query?query=up'
```

### Grafana

```bash
# Port forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Usuario: admin
# Password: definido en values.yaml (default: admin123)
```

## 🧪 Testing APIs

### Main API

```bash
# Health check
curl http://localhost:8000/health | jq

# Version
curl http://localhost:8000/version | jq

# Listar S3 buckets
curl http://localhost:8000/api/v1/s3/buckets | jq

# Listar parámetros
curl http://localhost:8000/api/v1/parameters | jq

# Parámetros con filtro
curl "http://localhost:8000/api/v1/parameters?path_prefix=/aws-challenge/dev" | jq

# Obtener valor de parámetro
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq

# Ver headers
curl -I http://localhost:8000/health
```

### Auxiliary Service

```bash
# Port forward primero
kubectl port-forward -n auxiliary-service svc/auxiliary-service 8001:8001

# Health check
curl http://localhost:8001/health | jq

# Version
curl http://localhost:8001/version | jq

# S3 buckets
curl http://localhost:8001/aws/s3/buckets | jq

# Parámetros
curl http://localhost:8001/aws/parameters | jq

# Valor de parámetro
curl "http://localhost:8001/aws/parameters/value?name=/aws-challenge/dev/database/host" | jq
```

## 🔍 Helm

### Repositorios

```bash
# Agregar repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

# Actualizar repos
helm repo update

# Buscar charts
helm search repo prometheus
helm search repo grafana
```

### Releases

```bash
# Instalar
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  -f monitoring/prometheus/values.yaml

# Ver releases
helm list -n monitoring
helm list --all-namespaces

# Ver estado
helm status prometheus -n monitoring

# Ver valores
helm get values prometheus -n monitoring

# Upgrade
helm upgrade prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring/prometheus/values.yaml

# Rollback
helm rollback prometheus -n monitoring

# Uninstall
helm uninstall prometheus -n monitoring
```

## 🎓 Troubleshooting

### Ver todo lo que no está Running

```bash
kubectl get pods --all-namespaces --field-selector=status.phase!=Running
```

### Ver recursos que consumen más

```bash
kubectl top nodes
kubectl top pods -n main-api
kubectl top pods --all-namespaces --sort-by=memory
```

### Eventos de error

```bash
kubectl get events --all-namespaces --field-selector type=Warning
```

### Restart de todo

```bash
kubectl rollout restart deployment -n main-api
kubectl rollout restart deployment -n auxiliary-service
```
