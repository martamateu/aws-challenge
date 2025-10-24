#!/bin/bash

# Script de inicio rápido para AWS (primera vez)
# Este script te guía paso a paso en la configuración inicial

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AWS Challenge - Setup Inicial para Principiantes        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar comandos
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 está instalado"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NO está instalado"
        return 1
    fi
}

# Función para verificar AWS credentials
check_aws_credentials() {
    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✓${NC} AWS CLI está configurado correctamente"
        echo ""
        echo "Tu identidad AWS:"
        aws sts get-caller-identity
        return 0
    else
        echo -e "${RED}✗${NC} AWS CLI no está configurado o las credenciales son inválidas"
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo " Paso 1: Verificar herramientas instaladas"
echo "═══════════════════════════════════════════════════════════"
echo ""

MISSING_TOOLS=0

if ! check_command aws; then
    echo -e "${YELLOW}   → Instala AWS CLI:${NC} brew install awscli"
    MISSING_TOOLS=1
fi

if ! check_command terraform; then
    echo -e "${YELLOW}   → Instala Terraform:${NC} brew install terraform"
    MISSING_TOOLS=1
fi

if ! check_command docker; then
    echo -e "${YELLOW}   → Instala Docker:${NC} brew install --cask docker"
    MISSING_TOOLS=1
fi

echo ""

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}⚠ Instala las herramientas faltantes y vuelve a ejecutar este script${NC}"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo " Paso 2: Verificar configuración de AWS"
echo "═══════════════════════════════════════════════════════════"
echo ""

if ! check_aws_credentials; then
    echo ""
    echo -e "${YELLOW}Necesitas configurar AWS CLI con tus credenciales${NC}"
    echo ""
    echo "Pasos:"
    echo "1. Ve a AWS Console → IAM → Usuarios"
    echo "2. Crea un usuario o selecciona uno existente"
    echo "3. Crea 'Access Key' (credenciales programáticas)"
    echo "4. Descarga el Access Key ID y Secret Access Key"
    echo "5. Ejecuta: aws configure"
    echo ""
    read -p "¿Ya tienes las credenciales y quieres configurarlas ahora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        aws configure
        echo ""
        if check_aws_credentials; then
            echo -e "${GREEN}✓ Configuración exitosa${NC}"
        else
            echo -e "${RED}✗ La configuración falló. Verifica tus credenciales.${NC}"
            exit 1
        fi
    else
        echo ""
        echo -e "${YELLOW}Configura AWS CLI y vuelve a ejecutar este script${NC}"
        echo "Comando: aws configure"
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " Paso 3: Personalizar configuración de Terraform"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Obtener el nombre de usuario de Git como sugerencia
GIT_USER=$(git config user.name 2>/dev/null || echo "")
GITHUB_USER=""

echo "Necesitas actualizar tu usuario de GitHub en terraform.tfvars"
echo ""

if [ -n "$GIT_USER" ]; then
    echo -e "Tu usuario de Git es: ${GREEN}$GIT_USER${NC}"
    read -p "¿Es este tu usuario de GitHub? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        GITHUB_USER=$GIT_USER
    fi
fi

if [ -z "$GITHUB_USER" ]; then
    read -p "Ingresa tu usuario de GitHub: " GITHUB_USER
fi

echo ""
echo -e "Configurando terraform.tfvars con usuario: ${GREEN}$GITHUB_USER${NC}"

# Actualizar terraform.tfvars
TFVARS_FILE="terraform/environments/dev/terraform.tfvars"
if [ -f "$TFVARS_FILE" ]; then
    sed -i.bak "s/YOUR_GITHUB_USERNAME/$GITHUB_USER/g" "$TFVARS_FILE"
    rm -f "$TFVARS_FILE.bak"
    echo -e "${GREEN}✓${NC} terraform.tfvars actualizado"
else
    echo -e "${RED}✗${NC} No se encontró $TFVARS_FILE"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " Paso 4: Inicializar y planificar Terraform"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd terraform/environments/dev

echo "Inicializando Terraform..."
terraform init

echo ""
echo "Verificando configuración (terraform plan)..."
echo ""
terraform plan

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " ✅ Configuración completada"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Terraform está listo para crear recursos en AWS."
echo ""
echo "Qué se va a crear:"
echo "  • 3 buckets S3 (data, logs, backups)"
echo "  • 8 parámetros en SSM Parameter Store"
echo "  • 1 OIDC provider para GitHub Actions"
echo "  • 1 rol IAM para GitHub Actions"
echo ""
echo "Costo estimado: \$0 (dentro del Free Tier)"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Revisar el plan de Terraform arriba"
echo "2. Si todo se ve bien, aplicar los cambios:"
echo -e "   ${GREEN}terraform apply${NC}"
echo ""
echo "3. Después de aplicar, ver los recursos creados:"
echo -e "   ${GREEN}terraform output${NC}"
echo ""
echo "4. Para destruir todos los recursos más tarde:"
echo -e "   ${YELLOW}terraform destroy${NC}"
echo ""
echo "📚 Para más información, consulta: docs/AWS-SETUP.md"
echo ""
