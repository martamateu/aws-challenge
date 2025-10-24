# Terraform Documentation

Este documento explica la infraestructura como código (IaC) definida con Terraform para el proyecto aws-challenge.

## 📑 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Módulos](#módulos)
- [Variables](#variables)
- [Outputs](#outputs)
- [Uso](#uso)

## 🏗️ Descripción General

La infraestructura está organizada en módulos reutilizables que siguen las mejores prácticas de Terraform:

- **Modularidad**: Cada componente (S3, Parameter Store, IAM, GitHub OIDC) está en su propio módulo
- **Reutilización**: Los módulos pueden ser reutilizados en diferentes entornos
- **Seguridad**: Implementa principio de mínimo privilegio y cifrado por defecto
- **Escalabilidad**: Fácil de extender y modificar

## 📦 Módulos

### 1. Módulo S3 (`modules/s3`)

**Propósito**: Crear y gestionar buckets de S3 para almacenamiento de datos, logs y backups.

**Recursos creados**:
- 3 S3 buckets:
  - `{project}-data-{env}-{account_id}`: Almacenamiento de datos
  - `{project}-logs-{env}-{account_id}`: Almacenamiento de logs
  - `{project}-backups-{env}-{account_id}`: Almacenamiento de backups

**Características**:
- ✅ Versionado habilitado en buckets de data y backups
- ✅ Cifrado AES256 por defecto en todos los buckets
- ✅ Bloqueo de acceso público
- ✅ Política de ciclo de vida para logs (retención de 90 días)
- ✅ Transición a STANDARD_IA después de 30 días para logs

**Variables**:
```hcl
variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "environment" {
  description = "Entorno (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "Región de AWS"
  type        = string
}

variable "tags" {
  description = "Tags adicionales"
  type        = map(string)
  default     = {}
}
```

**Outputs**:
- `bucket_names`: Mapa con nombres de los buckets
- `bucket_arns`: Lista de ARNs de los buckets
- `data_bucket_id`, `logs_bucket_id`, `backups_bucket_id`: IDs individuales

### 2. Módulo Parameter Store (`modules/parameter-store`)

**Propósito**: Gestionar parámetros de configuración en AWS Systems Manager Parameter Store.

**Parámetros creados**:

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `/{project}/{env}/database/host` | String | Hostname de la base de datos |
| `/{project}/{env}/database/port` | String | Puerto de la base de datos |
| `/{project}/{env}/database/name` | String | Nombre de la base de datos |
| `/{project}/{env}/api/key` | SecureString | API Key (cifrada) |
| `/{project}/{env}/api/secret` | SecureString | API Secret (cifrado) |
| `/{project}/{env}/app/log-level` | String | Nivel de logging |
| `/{project}/{env}/app/timeout` | String | Timeout de aplicación |
| `/{project}/{env}/aws/region` | String | Región de AWS |

**Características**:
- ✅ Parámetros sensibles usan tipo `SecureString` (cifrado con KMS)
- ✅ Lifecycle `ignore_changes` en valores sensibles para prevenir sobrescritura
- ✅ Nomenclatura jerárquica para fácil filtrado
- ✅ Tags descriptivos para categorización

**Variables**:
```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {}
}
```

**Outputs**:
- `parameter_names`: Lista de nombres de parámetros
- `parameter_arns`: Lista de ARNs de parámetros
- `database_host_arn`, `api_key_arn`: ARNs específicos

### 3. Módulo IAM (`modules/iam`)

**Propósito**: Crear roles y políticas de IAM para Kubernetes Service Accounts (IRSA - IAM Roles for Service Accounts).

**Recursos creados**:

1. **IAM Role para Auxiliary Service**
   - Permite al pod asumir el rol mediante OIDC
   - Trust policy vinculado al OIDC provider de EKS
   - Condición: solo el ServiceAccount específico puede asumir el rol

2. **Política de acceso a S3**
   - `ListBucket`, `GetBucketLocation`, `ListBucketVersions`
   - `GetObject`, `PutObject`, `DeleteObject`, `GetObjectVersion`
   - `ListAllMyBuckets` (para listar todos los buckets de la cuenta)

3. **Política de acceso a Parameter Store**
   - `GetParameter`, `GetParameters`, `GetParameterHistory`
   - `GetParametersByPath`, `DescribeParameters`
   - Permiso de `kms:Decrypt` para SecureStrings

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/OIDC_URL"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "OIDC_URL:sub": "system:serviceaccount:auxiliary-service:auxiliary-service-sa",
        "OIDC_URL:aud": "sts.amazonaws.com"
      }
    }
  }]
}
```

**Variables**:
```hcl
variable "eks_oidc_provider_arn" {
  description = "ARN del OIDC provider de EKS"
  type        = string
  default     = ""
}

variable "eks_oidc_provider_url" {
  description = "URL del OIDC provider de EKS"
  type        = string
  default     = ""
}

variable "s3_bucket_arns" {
  description = "ARNs de buckets S3"
  type        = list(string)
  default     = []
}

variable "parameter_arns" {
  description = "ARNs de parámetros SSM"
  type        = list(string)
  default     = []
}
```

**Nota**: Si no estás usando EKS (por ejemplo, con Kind local), el módulo no creará recursos (count = 0).

### 4. Módulo GitHub OIDC (`modules/github-oidc`)

**Propósito**: Configurar autenticación segura entre GitHub Actions y AWS sin credenciales estáticas.

**Recursos creados**:

1. **OIDC Provider para GitHub**
   - URL: `https://token.actions.githubusercontent.com`
   - Thumbprints de GitHub (valores conocidos públicamente)
   - Client ID: `sts.amazonaws.com`

2. **IAM Role para GitHub Actions**
   - Permite a GitHub Actions asumir el rol
   - Trust policy limita acceso a repositorio específico
   - Condición: solo workflows del repositorio especificado

3. **Política ECR**
   - `ecr:GetAuthorizationToken` (global)
   - Push/pull de imágenes a ECR
   - Crear repositorios si no existen

4. **Política S3**
   - Acceso a buckets para artefactos

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:ORG/REPO:*"
      }
    }
  }]
}
```

**Variables**:
```hcl
variable "github_org" {
  description = "Organización o usuario de GitHub"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "Nombre del repositorio"
  type        = string
}
```

## 🔧 Variables Principales

Variables definidas en `variables.tf`:

```hcl
# Obligatorias
variable "region" {
  default = "us-east-1"
}

variable "environment" {
  default = "dev"
}

variable "project_name" {
  default = "aws-challenge"
}

# Para GitHub OIDC
variable "github_org" {
  description = "Tu usuario/org de GitHub"
  default     = ""
}

variable "github_repo" {
  default = "aws-challenge"
}

# Para IRSA (solo si usas EKS)
variable "eks_cluster_name" {
  default = "aws-challenge-cluster"
}

variable "eks_oidc_provider_arn" {
  description = "ARN del OIDC provider (obtener de EKS)"
  default     = ""
}

variable "eks_oidc_provider_url" {
  description = "URL del OIDC provider (obtener de EKS)"
  default     = ""
}
```

## 📤 Outputs

Outputs principales disponibles:

```hcl
# S3
output "s3_bucket_names"
output "s3_bucket_arns"

# Parameter Store
output "parameter_store_names"
output "parameter_store_arns"

# IAM (solo si eks_oidc_provider_arn está configurado)
output "auxiliary_service_role_arn"
output "auxiliary_service_role_name"

# GitHub OIDC
output "github_actions_role_arn"
output "github_actions_role_name"
output "github_oidc_provider_arn"
```

## 🚀 Uso

### Inicialización

```bash
cd terraform

# Inicializar Terraform (descargar providers)
terraform init
```

### Planificación

```bash
# Ver qué recursos se crearán
terraform plan

# Con variables personalizadas
terraform plan \
  -var="region=eu-west-1" \
  -var="environment=prod" \
  -var="github_org=mi-usuario"
```

### Aplicación

```bash
# Crear infraestructura
terraform apply

# O con auto-approve (no recomendado en prod)
terraform apply -auto-approve

# Con variables
terraform apply \
  -var="region=us-east-1" \
  -var="environment=dev" \
  -var="github_org=marta-mateu"
```

### Outputs

```bash
# Ver todos los outputs
terraform output

# Output específico
terraform output s3_bucket_names

# En formato JSON (útil para scripts)
terraform output -json > terraform-outputs.json
```

### Destrucción

```bash
# Eliminar toda la infraestructura
terraform destroy

# Con variables
terraform destroy -var="environment=dev"
```

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. **Cifrado**:
   - S3: AES256 por defecto
   - Parameter Store: SecureString con KMS

2. **Acceso Mínimo**:
   - Políticas IAM con permisos específicos
   - No se usan wildcards innecesarios

3. **Bloqueo Público**:
   - Todos los buckets S3 bloquean acceso público

4. **OIDC en lugar de credenciales**:
   - GitHub Actions usa OIDC
   - Kubernetes usa IRSA (si EKS)

5. **Versionado**:
   - Buckets importantes tienen versionado

6. **Tags**:
   - Todos los recursos están etiquetados para auditoría

### State Management

Para producción, configura backend remoto en `versions.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "tu-bucket-terraform-state"
    key            = "aws-challenge/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## 🐛 Troubleshooting

### Error: "No valid credential sources"

**Solución**: Configura AWS CLI:
```bash
aws configure
```

### Error: "Bucket name already exists"

**Causa**: Los nombres de S3 buckets son globales

**Solución**: El código usa account ID para hacerlos únicos, pero si persiste:
```bash
# Cambia el project_name
terraform apply -var="project_name=aws-challenge-unique-name"
```

### Error: OIDC provider no encontrado

**Causa**: `eks_oidc_provider_arn` no configurado

**Solución**: Si usas EKS local (Kind/Minikube), deja vacío. Si usas EKS real:
```bash
# Obtener OIDC provider ARN
aws eks describe-cluster --name tu-cluster --query "cluster.identity.oidc.issuer" --output text

# Usar en Terraform
terraform apply -var="eks_oidc_provider_arn=arn:aws:iam::..."
```

## 📚 Referencias

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
