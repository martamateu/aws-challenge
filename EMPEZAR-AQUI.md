# Guía Rápida: Primeros Pasos con AWS y Terraform

## 🎯 Resumen: Qué hacer ahora

Como tienes experiencia con Terraform y Docker pero no con AWS, estos son los pasos esenciales:

## Paso 1: Crear Cuenta de AWS (15 min)

1. **Regístrate**: Ve a [aws.amazon.com](https://aws.amazon.com) y crea una cuenta
   - Necesitas email, tarjeta de crédito (no se cobrará nada en Free Tier), y teléfono
   - El primer año es gratis para los servicios que usaremos

## Paso 2: Crear Usuario IAM (10 min)

⚠️ **MUY IMPORTANTE**: No uses el usuario "root" para desarrollo

1. **Accede a AWS Console**: [console.aws.amazon.com](https://console.aws.amazon.com)

2. **Busca "IAM"** en la barra de búsqueda superior

3. **Usuarios → Crear usuario**:
   - Nombre: `terraform-user`
   - Marca: ✅ "Proporcionar acceso a la consola de administración de AWS" (opcional)
   - Marca: ✅ "Crear clave de acceso" → Selecciona "CLI"

4. **Permisos**:
   - Para empezar: Asigna `AdministratorAccess` (política predefinida)
   - Para producción: Usa permisos mínimos (ver docs/AWS-SETUP.md)

5. **IMPORTANTE - Guardar Credenciales**:
   Al finalizar verás:
   ```
   Access Key ID: AKIA...
   Secret Access Key: wJalrXUtn...
   ```
   ⚠️ **¡CÓPIALAS AHORA!** No podrás verlas después
   - Descarga el CSV como respaldo

## Paso 3: Configurar AWS CLI (5 min)

```bash
# Instalar (si no lo tienes)
brew install awscli

# Verificar instalación
aws --version

# Configurar con tus credenciales
aws configure
```

Te pedirá:
```
AWS Access Key ID [None]: AKIA................  (del paso 2)
AWS Secret Access Key [None]: wJalr............ (del paso 2)
Default region name [None]: eu-west-1          (Irlanda, más cercano a España)
Default output format [None]: json             (recomendado)
```

**Verificar que funciona**:
```bash
aws sts get-caller-identity
```

Deberías ver algo como:
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/terraform-user"
}
```

## Paso 4: Personalizar Terraform (2 min)

Edita `terraform/environments/dev/terraform.tfvars`:

```bash
# Opción 1: Editar manualmente
code terraform/environments/dev/terraform.tfvars

# O usar el script automático
./aws-setup.sh
```

**Cambiar esta línea**:
```hcl
github_org  = "TU_USUARIO_GITHUB"  # 👈 Cambia esto
```

## Paso 5: Desplegar Infraestructura (5 min)

```bash
# Ir al directorio de Terraform
cd terraform/environments/dev

# Inicializar (ya está hecho)
terraform init

# Ver qué se va a crear (NO crea nada todavía)
terraform plan

# Si todo se ve bien, créalo
terraform apply
# Te pedirá confirmación, escribe: yes
```

### ¿Qué creará Terraform?

✅ **3 Buckets S3**:
- `aws-challenge-dev-data` - Para datos de aplicación
- `aws-challenge-dev-logs` - Para logs
- `aws-challenge-dev-backups` - Para backups

✅ **8 Parámetros SSM** (configuración de aplicación):
- Database URL, password
- API secret key
- Redis URL
- Configuración de app

✅ **IAM Roles y Políticas**:
- GitHub Actions OIDC provider
- Role para GitHub Actions (CI/CD sin credenciales)

### Costo: **$0** (todo dentro del Free Tier)

## Paso 6: Verificar Recursos Creados (2 min)

```bash
# Ver outputs de Terraform
terraform output

# Listar buckets S3 creados
aws s3 ls | grep aws-challenge

# Listar parámetros SSM
aws ssm describe-parameters --filters "Key=Name,Values=/aws-challenge/dev/"

# Ver detalles de un bucket
aws s3 ls s3://aws-challenge-dev-data
```

## 🎉 ¡Listo!

Ya tienes la infraestructura de AWS creada. Próximos pasos:

### Opción A: Continuar con Docker (recomendado)

```bash
# Volver al directorio raíz
cd ../../..

# Ver la guía de Docker
cat INICIO-RAPIDO.md

# Construir imágenes
docker compose build
```

### Opción B: Crear repositorios ECR para imágenes

```bash
# Crear repositorios en AWS ECR
aws ecr create-repository --repository-name main-api --region eu-west-1
aws ecr create-repository --repository-name auxiliary-service --region eu-west-1

# Obtener URL de login
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.eu-west-1.amazonaws.com
```

## 🆘 Si algo falla

### Error: "Unable to locate credentials"
```bash
# Verifica configuración
cat ~/.aws/credentials
cat ~/.aws/config

# Reconfigura si es necesario
aws configure
```

### Error: "Access Denied"
- Tu usuario IAM no tiene permisos suficientes
- Ve a IAM Console → Usuarios → tu usuario → Agregar permisos
- Añade `AdministratorAccess` para desarrollo

### Error: "BucketAlreadyExists" al crear buckets
Los nombres de S3 son globalmente únicos. Cambia en `terraform.tfvars`:
```hcl
project_name = "aws-challenge-tunombre"
```

### Terraform plan falla con timeout
A veces el plugin de AWS tarda. Intenta de nuevo:
```bash
terraform plan
```

## 🧹 Limpieza (cuando termines)

Para evitar cargos, destruye todo:

```bash
cd terraform/environments/dev
terraform destroy
# Escribe: yes
```

Esto eliminará:
- Todos los buckets S3 (deben estar vacíos)
- Parámetros SSM
- Roles IAM
- OIDC provider

## 📚 Más información

- **Guía completa de AWS**: `docs/AWS-SETUP.md`
- **Inicio rápido del proyecto**: `INICIO-RAPIDO.md`
- **Comandos útiles**: `COMANDOS.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

## ⏱️ Tiempo total: ~40 minutos

- Crear cuenta AWS: 15 min
- Crear usuario IAM: 10 min
- Configurar AWS CLI: 5 min
- Personalizar Terraform: 2 min
- Aplicar Terraform: 5 min
- Verificar: 2 min

¡Empieza por el Paso 1 y estarás listo en menos de una hora! 🚀
