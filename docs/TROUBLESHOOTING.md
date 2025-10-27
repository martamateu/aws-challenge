# Troubleshooting Guide

Guía de solución de problemas comunes en el proyecto aws-challenge.

## 📑 Índice

- [Problemas con Terraform](#problemas-con-terraform)
- [Problemas con Docker](#problemas-con-docker)
- [Problemas con Kubernetes](#problemas-con-kubernetes)
- [Problemas con Argo CD](#problemas-con-argo-cd)
- [Problemas con AWS](#problemas-con-aws)
- [Problemas con las APIs](#problemas-con-las-apis)
- [Problemas con GitHub Actions](#problemas-con-github-actions)

## 🏗️ Problemas con Terraform

### Error: "No valid credential sources"

**Síntoma:**
```
Error: error configuring Terraform AWS Provider: no valid credential sources
```

**Solución:**
```bash
# Configurar AWS CLI
aws configure

# O exportar variables de entorno
export AWS_ACCESS_KEY_ID="tu-access-key"
export AWS_SECRET_ACCESS_KEY="tu-secret-key"
export AWS_REGION="your-aws-region"

# Verificar
aws sts get-caller-identity
```

### Error: "Bucket name already exists"

**Síntoma:**
```
Error: error creating S3 Bucket: BucketAlreadyExists: The requested bucket name is not available
```

**Causa:** Los nombres de S3 buckets son globalmente únicos.

**Solución:**
```bash
# El código usa account ID para hacer nombres únicos, pero si persiste:
terraform apply -var="project_name=aws-challenge-unique-$(date +%s)"
```

### Error: "Backend initialization required"

**Síntoma:**
```
Error: Backend initialization required: please run "terraform init"
```

**Solución:**
```bash
cd terraform
terraform init
# Si cambias providers o módulos:
terraform init -upgrade
```

### State Lock Issues

**Síntoma:**
```
Error: Error acquiring the state lock
```

**Solución:**
```bash
# Si estás seguro que no hay otra operación en curso:
terraform force-unlock <LOCK_ID>

# O elimina el archivo de lock local
rm -rf .terraform/
terraform init
```

## 🐳 Problemas con Docker

### Error: "Cannot connect to Docker daemon"

**Síntoma:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solución:**
```bash
# Iniciar Docker Desktop (macOS)
open -a Docker

# Esperar a que Docker esté listo
docker ps

# Verificar
docker version
```

### Error: "denied: requested access to the resource is denied"

**Síntoma:**
```
denied: requested access to the resource is denied
```

**Solución:**
```bash
# Login a Docker Hub
docker login

# Verificar que el nombre de imagen es correcto
docker images
docker tag local-image:tag username/image:tag
docker push username/image:tag
```

### Imagen no se actualiza en Kubernetes

**Síntoma:** Los cambios no se reflejan después de hacer push.

**Solución:**
```bash
# Usar tags específicos en lugar de :latest
docker build -t username/main-api:v1.0.1 .
docker push username/main-api:v1.0.1

# Actualizar deployment
kubectl set image deployment/main-api main-api=username/main-api:v1.0.1 -n main-api

# O forzar pull
kubectl rollout restart deployment/main-api -n main-api
```

## ⚓ Problemas con Kubernetes

### Error: "connection refused"

**Síntoma:**
```
Unable to connect to the server: dial tcp 127.0.0.1:6443: connect: connection refused
```

**Solución:**
```bash
# Verificar que el cluster está corriendo
kind get clusters

# Si no existe, crearlo
kind create cluster --name aws-challenge --config kind-config.yaml

# Verificar contexto
kubectl config current-context
kubectl config use-context kind-aws-challenge
```

### Pods en estado CrashLoopBackOff

**Síntoma:**
```
NAME                     READY   STATUS             RESTARTS   AGE
main-api-xxx             0/1     CrashLoopBackOff   5          5m
```

**Diagnóstico:**
```bash
# Ver logs del pod
kubectl logs -n main-api main-api-xxx

# Ver logs del pod anterior (si crasheó)
kubectl logs -n main-api main-api-xxx --previous

# Ver eventos
kubectl describe pod -n main-api main-api-xxx
kubectl get events -n main-api --sort-by='.lastTimestamp'
```

**Soluciones comunes:**
1. Error en código → Revisar logs
2. Variables de entorno faltantes → Verificar ConfigMap
3. Problemas de permisos AWS → Verificar ServiceAccount e IAM role
4. Health checks fallando → Ajustar tiempos en deployment

### Pods en estado Pending

**Síntoma:**
```
NAME                     READY   STATUS    RESTARTS   AGE
main-api-xxx             0/1     Pending   0          2m
```

**Diagnóstico:**
```bash
kubectl describe pod -n main-api main-api-xxx
```

**Causas comunes:**
1. **Recursos insuficientes:**
   ```yaml
   # Reducir requests en deployment
   resources:
     requests:
       memory: "64Mi"
       cpu: "50m"
   ```

2. **Imagen no disponible:**
   ```bash
   # Verificar que la imagen existe
   docker pull username/main-api:latest
   ```

3. **PersistentVolumeClaim pendiente:**
   ```bash
   kubectl get pvc -n main-api
   ```

### Service no accesible

**Síntoma:** No se puede acceder al servicio.

**Diagnóstico:**
```bash
# Verificar service
kubectl get svc -n main-api
kubectl describe svc -n main-api main-api-service

# Verificar endpoints
kubectl get endpoints -n main-api

# Verificar que los pods están Running
kubectl get pods -n main-api
```

**Soluciones:**
```bash
# Port forward directo al pod
kubectl port-forward -n main-api <pod-name> 8000:8000

# Si funciona el pod pero no el service:
# Verificar labels en deployment y selector en service
kubectl get pods -n main-api --show-labels
```

### ImagePullBackOff

**Síntoma:**
```
main-api-xxx   0/1   ImagePullBackOff   0   2m
```

**Diagnóstico:**
```bash
kubectl describe pod -n main-api main-api-xxx
# Buscar: "Failed to pull image"
```

**Soluciones:**
1. **Imagen no existe:**
   ```bash
   docker push username/main-api:latest
   ```

2. **Nombre incorrecto:**
   ```yaml
   # Verificar en deployment.yaml
   image: username/main-api:latest  # ← Debe coincidir exactamente
   ```

3. **Imagen privada sin secret:**
   ```bash
   kubectl create secret docker-registry regcred \
     --docker-server=https://index.docker.io/v1/ \
     --docker-username=username \
     --docker-password=password \
     -n main-api
   
   # Agregar a deployment:
   imagePullSecrets:
   - name: regcred
   ```

## 🎯 Problemas con Argo CD

### No puedo acceder a Argo CD UI

**Solución:**
```bash
# Verificar que está corriendo
kubectl get pods -n argocd

# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Acceder a https://localhost:8080
# Usuario: admin
# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Application en estado "OutOfSync"

**Síntoma:** Application muestra OutOfSync pero no se sincroniza automáticamente.

**Solución:**
```bash
# Sincronizar manualmente
argocd app sync main-api

# O desde kubectl
kubectl patch application main-api -n argocd \
  --type merge \
  --patch '{"operation": {"initiatedBy": {"username": "admin"}, "sync": {"syncStrategy": {"hook": {}}}}}'

# Verificar auto-sync está habilitado
kubectl get application -n argocd main-api -o yaml | grep -A 5 syncPolicy
```

### Application en estado "Unknown"

**Causa:** Argo CD no puede acceder al repositorio Git.

**Solución:**
```bash
# Verificar la URL del repo en Application
kubectl get application -n argocd main-api -o yaml | grep repoURL

# Debe ser accesible públicamente o configurar credentials
argocd repo add https://github.com/username/aws-challenge.git
```

### Health check fallando

**Síntoma:** Argo CD muestra "Degraded" o "Progressing".

**Solución:**
```bash
# Ver detalles
argocd app get main-api

# Verificar que los pods están saludables
kubectl get pods -n main-api

# Ver health check en Argo CD
kubectl describe application -n argocd main-api
```

## ☁️ Problemas con AWS

### Error: "AccessDenied"

**Síntoma:**
```json
{
  "detail": "AWS Error: AccessDenied - User: ... is not authorized to perform: s3:ListAllMyBuckets"
}
```

**Soluciones:**

1. **Usando credentials locales (Kind/Minikube):**
   ```bash
   # Verificar credenciales
   aws sts get-caller-identity
   
   # Verificar permisos
   aws s3 ls
   aws ssm describe-parameters
   ```

2. **Usando IRSA (EKS):**
   ```bash
   # Verificar que el ServiceAccount tiene la anotación
   kubectl get sa -n auxiliary-service auxiliary-service-sa -o yaml
   
   # Debe tener:
   # annotations:
   #   eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/ROLE_NAME
   
   # Verificar trust policy del IAM role
   aws iam get-role --role-name aws-challenge-auxiliary-service-dev \
     --query 'Role.AssumeRolePolicyDocument'
   
   # Verificar políticas attachadas
   aws iam list-attached-role-policies \
     --role-name aws-challenge-auxiliary-service-dev
   ```

3. **Agregar permisos faltantes:**
   ```bash
   # Editar policy en Terraform
   # terraform/modules/iam/main.tf
   
   # Aplicar cambios
   cd terraform
   terraform apply
   ```

### Parámetro no encontrado

**Síntoma:**
```json
{
  "detail": "Parameter '/aws-challenge/dev/database/host' not found"
}
```

**Solución:**
```bash
# Verificar que existe
aws ssm get-parameter --name "/aws-challenge/dev/database/host"

# Listar todos los parámetros
aws ssm describe-parameters --query "Parameters[].Name"

# Si no existe, crear con Terraform
cd terraform
terraform apply
```

### Region mismatch

**Síntoma:** Recursos no se encuentran.

**Solución:**
```bash
# Verificar región configurada
aws configure get region

# Verificar región en deployment
kubectl get configmap -n auxiliary-service auxiliary-service-config -o yaml | grep AWS_REGION

# Deben coincidir
```

## 🐞 Problemas con las APIs

### Auxiliary Service retorna error 500

**Diagnóstico:**
```bash
# Ver logs del Auxiliary Service
kubectl logs -n auxiliary-service -l app=auxiliary-service --tail=50

# Port forward y probar directamente
kubectl port-forward -n auxiliary-service svc/auxiliary-service 8001:8001
curl http://localhost:8001/health
```

**Causas comunes:**
1. Credenciales AWS incorrectas
2. Región incorrecta
3. Permisos IAM insuficientes
4. Boto3 no instalado correctamente

### Main API no puede contactar Auxiliary Service

**Síntoma:**
```json
{
  "detail": "Cannot reach auxiliary service: ..."
}
```

**Diagnóstico:**
```bash
# Verificar que Auxiliary Service está corriendo
kubectl get pods -n auxiliary-service

# Verificar service
kubectl get svc -n auxiliary-service

# Probar conectividad desde Main API pod
kubectl exec -it -n main-api <main-api-pod> -- sh
# Dentro del pod:
wget -O- http://auxiliary-service.auxiliary-service.svc.cluster.local:8001/health
```

**Soluciones:**
1. **Service name incorrecto:**
   ```yaml
   # En configmap de main-api:
   AUXILIARY_SERVICE_URL: "http://auxiliary-service.auxiliary-service.svc.cluster.local:8001"
   #                               ↑ nombre      ↑ namespace
   ```

2. **Namespace incorrecto:**
   ```bash
   kubectl get svc --all-namespaces | grep auxiliary
   ```

3. **Puerto incorrecto:**
   ```bash
   kubectl get svc -n auxiliary-service auxiliary-service -o yaml | grep port
   ```

### Timeout errors

**Síntoma:**
```json
{
  "detail": "Auxiliary service timeout"
}
```

**Solución:**
```bash
# Aumentar timeout en Main API
# Editar kubernetes/base/main-api/configmap.yaml
# O aumentar en el código: app/config.py
# auxiliary_service_timeout: int = 60  # aumentar de 30 a 60
```

## 🚀 Problemas con GitHub Actions

### Workflow no se ejecuta

**Causas:**
1. **Branch incorrecto:**
   - Verificar que pusheaste a `main` o `develop`

2. **Path filters:**
   ```yaml
   # En .github/workflows/ci-cd.yml
   paths:
     - 'services/**'  # Solo se ejecuta si cambias archivos en services/
   ```

3. **Workflow deshabilitado:**
   - Ir a Actions tab en GitHub y verificar que está habilitado

### Error: "denied: requested access to the resource is denied"

**Causa:** Credenciales de Docker Hub incorrectas.

**Solución:**
```bash
# Verificar secrets en GitHub:
# Settings > Secrets and variables > Actions

# Deben existir:
# DOCKER_USERNAME
# DOCKER_PASSWORD (o token de acceso)

# Generar token en Docker Hub:
# https://hub.docker.com/settings/security
```

### OIDC authentication fails

**Síntoma:**
```
Error: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Solución:**
```bash
# Verificar que el role existe
aws iam get-role --role-name aws-challenge-github-actions-dev

# Verificar trust policy
aws iam get-role --role-name aws-challenge-github-actions-dev \
  --query 'Role.AssumeRolePolicyDocument'

# Debe incluir:
# "token.actions.githubusercontent.com:sub": "repo:your-github-org/your-repo-name:*"

# Verificar que github_org está configurado en Terraform
cd terraform
terraform output github_actions_role_arn

# Re-aplicar si es necesario
terraform apply -var="github_org=your-github-username"
```

## 🔧 Comandos Útiles de Debugging

### Ver todo lo que está mal

```bash
# Pods que no están Running
kubectl get pods --all-namespaces --field-selector=status.phase!=Running

# Eventos de error
kubectl get events --all-namespaces --field-selector type=Warning

# Logs de todos los pods de un deployment
kubectl logs -n main-api -l app=main-api --all-containers=true
```

### Reset completo

```bash
# Eliminar todo y empezar de nuevo
kubectl delete namespace main-api auxiliary-service monitoring

# Re-desplegar
kubectl apply -f kubernetes/base/namespaces/
kubectl apply -f kubernetes/base/main-api/
kubectl apply -f kubernetes/base/auxiliary-service/
```

### Debug de networking

```bash
# Desde un pod, probar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Dentro:
nslookup auxiliary-service.auxiliary-service.svc.cluster.local
wget -O- http://auxiliary-service.auxiliary-service.svc.cluster.local:8001/health
```

## 📞 ¿Todavía con problemas?

1. **Revisa los logs:** Siempre empieza por los logs
2. **Usa `kubectl describe`:** Da mucha información útil
3. **Comprueba los eventos:** `kubectl get events`
4. **Verifica configuración:** ConfigMaps, Secrets, ServiceAccounts
5. **Prueba manualmente:** Port forward y usa curl
6. **Revisa la documentación:** API.md, SETUP.md, TERRAFORM.md

## 🔍 Recursos Adicionales

- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug/)
- [Argo CD Troubleshooting](https://argo-cd.readthedocs.io/en/stable/operator-manual/troubleshooting/)
- [AWS IAM Troubleshooting](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot.html)
- [Docker Troubleshooting](https://docs.docker.com/config/daemon/troubleshoot/)
