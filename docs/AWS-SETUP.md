# Configuración Inicial de AWS

## 📋 Prerrequisitos para AWS (Si nunca has usado AWS)

### 1. Crear una Cuenta de AWS

1. **Regístrate en AWS**:
   - Ve a [aws.amazon.com](https://aws.amazon.com)
   - Haz clic en "Crear una cuenta de AWS"
   - Necesitarás:
     - Email
     - Tarjeta de crédito (AWS Free Tier es gratuito el primer año)
     - Número de teléfono para verificación

2. **Nivel Gratuito (Free Tier)**:
   - ✅ S3: 5 GB de almacenamiento
   - ✅ Systems Manager Parameter Store: Gratis
   - ✅ IAM: Completamente gratuito
   - Este proyecto se mantiene dentro del Free Tier

### 2. Crear un Usuario IAM (NO uses el usuario root)

**⚠️ IMPORTANTE**: Nunca uses las credenciales del usuario root para desarrollo.

1. **Accede a la consola de AWS**:
   ```
   https://console.aws.amazon.com
   ```

2. **Ve al servicio IAM**:
   - En la barra de búsqueda superior, escribe "IAM"
   - Haz clic en "IAM"

3. **Crea un usuario con acceso programático**:
   ```
   IAM > Usuarios > Añadir usuarios
   ```
   
   - **Nombre de usuario**: `terraform-user` (o el que prefieras)
   - **Tipo de acceso**: Marca "Acceso programático"
   - Haz clic en "Siguiente: Permisos"

4. **Asigna permisos al usuario**:
   
   **Opción A - Permisos Administrativos (más fácil para empezar)**:
   - Selecciona "Asociar políticas existentes directamente"
   - Busca y marca: `AdministratorAccess`
   - ⚠️ Solo para desarrollo/aprendizaje

   **Opción B - Permisos Mínimos (recomendado para producción)**:
   - Crea una política personalizada con estos permisos:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:*",
           "ssm:*",
           "iam:*",
           "sts:*",
           "ecr:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

5. **Descarga las credenciales**:
   - Al finalizar, AWS mostrará:
     - **Access Key ID**: `AKIA...`
     - **Secret Access Key**: `wJalrXUtn...`
   - ⚠️ **GUÁRDALAS AHORA** - No podrás verlas de nuevo
   - Descarga el archivo CSV como respaldo

### 3. Configurar AWS CLI en tu Mac

1. **Instalar AWS CLI**:
   ```bash
   # Usando Homebrew
   brew install awscli
   
   # O descargar directamente
   curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
   sudo installer -pkg AWSCLIV2.pkg -target /
   ```

2. **Verificar instalación**:
   ```bash
   aws --version
   # Debe mostrar: aws-cli/2.x.x Python/3.x.x Darwin/...
   ```

3. **Configurar credenciales**:
   ```bash
   aws configure
   ```
   
   Te pedirá:
   ```
   AWS Access Key ID [None]: AKIA................
   AWS Secret Access Key [None]: wJalrXUtn................
   Default region name [None]: eu-west-1
   Default output format [None]: json
   ```

4. **Verificar configuración**:
   ```bash
   # Ver tu identidad
   aws sts get-caller-identity
   
   # Debe mostrar algo como:
   # {
   #     "UserId": "AIDA...",
   #     "Account": "123456789012",
   #     "Arn": "arn:aws:iam::123456789012:user/terraform-user"
   # }
   ```

### 4. Elegir una Región de AWS

Las regiones más comunes en Europa:
- `eu-west-1` - Irlanda (recomendada, menor latencia desde España)
- `eu-west-3` - París
- `eu-south-2` - España (Madrid) - ⚠️ Más nueva, puede tener limitaciones

**Configurar la región en este proyecto**:

Edita `terraform/environments/dev/terraform.tfvars`:
```hcl
aws_region = "eu-west-1"  # Cambia según tu preferencia
```

### 5. Configurar Backend de Terraform (Opcional pero recomendado)

Para guardar el estado de Terraform en S3:

1. **Crear bucket manualmente (primera vez)**:
   ```bash
   # Cambia el nombre - debe ser único globalmente
   aws s3 mb s3://tu-nombre-terraform-state-bucket --region eu-west-1
   
   # Activar versionado
   aws s3api put-bucket-versioning \
     --bucket tu-nombre-terraform-state-bucket \
     --versioning-configuration Status=Enabled
   
   # Activar encriptación
   aws s3api put-bucket-encryption \
     --bucket tu-nombre-terraform-state-bucket \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'
   ```

2. **Actualizar configuración de Terraform**:
   
   En `terraform/environments/dev/backend.tf`:
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "tu-nombre-terraform-state-bucket"
       key            = "dev/terraform.tfstate"
       region         = "eu-west-1"
       encrypt        = true
     }
   }
   ```

### 6. Variables de Entorno (Alternativa a aws configure)

Si prefieres usar variables de entorno en lugar de `aws configure`:

```bash
# Añade a tu ~/.zshrc
export AWS_ACCESS_KEY_ID="AKIA................"
export AWS_SECRET_ACCESS_KEY="wJalrXUtn................"
export AWS_DEFAULT_REGION="eu-west-1"

# Recarga el shell
source ~/.zshrc
```

## 🚀 Verificación Final Antes de Empezar

Ejecuta estos comandos para verificar que todo está listo:

```bash
# 1. AWS CLI instalado
aws --version

# 2. Credenciales configuradas
aws sts get-caller-identity

# 3. Terraform instalado (deberías tenerlo)
terraform version

# 4. Docker instalado y corriendo (deberías tenerlo)
docker version

# 5. Listar regiones disponibles
aws ec2 describe-regions --output table
```

Si todos estos comandos funcionan, **¡estás listo para continuar!**

## 📝 Resumen: ¿Qué necesitas crear en AWS?

### ✅ ANTES de ejecutar Terraform:

1. ✅ Cuenta de AWS (gratis)
2. ✅ Usuario IAM con credenciales programáticas
3. ✅ AWS CLI instalado y configurado
4. ✅ (Opcional) Bucket S3 para Terraform state

### ❌ NO necesitas crear manualmente:

- ❌ Buckets S3 → Terraform los creará
- ❌ Parámetros en Parameter Store → Terraform los creará
- ❌ Roles IAM → Terraform los creará
- ❌ Políticas IAM → Terraform las creará
- ❌ OIDC Provider → Terraform lo creará

## 🎯 Siguiente Paso

Una vez completados los pasos 1-3 anteriores, continúa con:

```bash
# Ver el inicio rápido
cat INICIO-RAPIDO.md

# O ir directamente a desplegar
cd terraform/environments/dev
terraform init
terraform plan
```

## 🆘 Problemas Comunes

### "Unable to locate credentials"
```bash
# Verifica que las credenciales están configuradas
cat ~/.aws/credentials
cat ~/.aws/config

# O reconfigura
aws configure
```

### "Access Denied" al ejecutar comandos
- Verifica que tu usuario IAM tiene los permisos necesarios
- Para desarrollo rápido, usa `AdministratorAccess`
- Para producción, usa permisos mínimos

### "Region not found"
```bash
# Lista todas las regiones disponibles
aws ec2 describe-regions --query 'Regions[].RegionName' --output table

# Configura una región válida
aws configure set region eu-west-1
```

### Error con Terraform backend S3
```bash
# Si no quieres usar S3 backend por ahora, comenta el bloque backend
# en terraform/environments/dev/backend.tf
# Terraform usará estado local (archivo terraform.tfstate)
```

## 💡 Consejos para Principiantes en AWS

1. **Free Tier Alert**: Configura alertas de facturación
   - AWS Console > Billing > Budgets
   - Crea un presupuesto de $1-5 para recibir alertas

2. **Limpieza**: Siempre ejecuta `terraform destroy` cuando termines
   ```bash
   cd terraform/environments/dev
   terraform destroy
   ```

3. **Costos**: Este proyecto cuesta ~$0 dentro del Free Tier
   - S3: < 5GB = Gratis
   - Parameter Store (Standard): Gratis
   - IAM: Siempre gratis

4. **Seguridad**:
   - ✅ Nunca subas credenciales a Git
   - ✅ Usa `.gitignore` (ya incluido)
   - ✅ Rota credenciales cada 90 días
   - ✅ Activa MFA en tu cuenta root

## 📚 Recursos Adicionales

- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS CLI Guía](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
