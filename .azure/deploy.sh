#!/bin/bash

# Azure Deployment Script for LinkedIn Bot
# This script automates the deployment process to Azure Container Apps

set -e

# Configuration
RESOURCE_GROUP="linkedin-bot-rg"
LOCATION="East US"
CONTAINER_APP_NAME="linkedin-bot-app"
CONTAINER_APP_ENV="linkedin-bot-env"
CONTAINER_REGISTRY="linkedinbotacr"
KEY_VAULT_NAME="linkedin-bot-kv"
IMAGE_NAME="linkedin-bot"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if user is logged in to Azure
check_azure_login() {
    log_info "Checking Azure login status..."
    if ! az account show > /dev/null 2>&1; then
        log_error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi
    log_success "Azure login verified"
}

# Create resource group
create_resource_group() {
    log_info "Creating resource group: $RESOURCE_GROUP"
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output table
    log_success "Resource group created"
}

# Create Azure Container Registry
create_container_registry() {
    log_info "Creating Azure Container Registry: $CONTAINER_REGISTRY"
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$CONTAINER_REGISTRY" \
        --sku Basic \
        --admin-enabled false \
        --output table
    log_success "Container Registry created"
}

# Create Key Vault
create_key_vault() {
    log_info "Creating Azure Key Vault: $KEY_VAULT_NAME"
    az keyvault create \
        --name "$KEY_VAULT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --enable-rbac-authorization true \
        --output table
    log_success "Key Vault created"
}

# Set Telegram bot token in Key Vault
set_telegram_token() {
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        log_error "TELEGRAM_BOT_TOKEN environment variable is not set"
        log_info "Please set it: export TELEGRAM_BOT_TOKEN='your-token'"
        exit 1
    fi
    
    log_info "Setting Telegram bot token in Key Vault"
    az keyvault secret set \
        --vault-name "$KEY_VAULT_NAME" \
        --name "telegram-bot-token" \
        --value "$TELEGRAM_BOT_TOKEN" \
        --output table
    log_success "Telegram bot token stored in Key Vault"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image to ACR"
    az acr build \
        --registry "$CONTAINER_REGISTRY" \
        --image "$IMAGE_NAME:$IMAGE_TAG" \
        --file Dockerfile \
        . \
        --output table
    log_success "Docker image built and pushed"
}

# Create Container App Environment
create_container_app_environment() {
    log_info "Creating Container App Environment: $CONTAINER_APP_ENV"
    az containerapp env create \
        --name "$CONTAINER_APP_ENV" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output table
    log_success "Container App Environment created"
}

# Deploy Container App
deploy_container_app() {
    log_info "Deploying Container App: $CONTAINER_APP_NAME"
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name "$CONTAINER_REGISTRY" --resource-group "$RESOURCE_GROUP" --query loginServer --output tsv)
    
    az containerapp create \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --environment "$CONTAINER_APP_ENV" \
        --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
        --target-port 8080 \
        --ingress external \
        --min-replicas 0 \
        --max-replicas 3 \
        --cpu 0.5 \
        --memory 1.0Gi \
        --registry-server "$ACR_LOGIN_SERVER" \
        --registry-identity system \
        --env-vars \
            AZURE_ENVIRONMENT=production \
            LOG_LEVEL=INFO \
            ENABLE_METRICS=true \
            HEALTH_CHECK_ENABLED=true \
            MAX_RESULTS_PER_SEARCH=10 \
            DEFAULT_LOCATION=India \
        --secrets \
            telegram-bot-token="keyvaultref:https://$KEY_VAULT_NAME.vault.azure.net/secrets/telegram-bot-token,identityref:system" \
        --output table
    
    log_success "Container App deployed"
}

# Assign required permissions
assign_permissions() {
    log_info "Assigning required permissions..."
    
    # Get the Container App's system-assigned identity
    PRINCIPAL_ID=$(az containerapp show \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query identity.principalId \
        --output tsv)
    
    # Assign AcrPull role to Container App identity
    az role assignment create \
        --assignee "$PRINCIPAL_ID" \
        --role "AcrPull" \
        --scope "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/$CONTAINER_REGISTRY"
    
    # Assign Key Vault Secrets User role to Container App identity
    az role assignment create \
        --assignee "$PRINCIPAL_ID" \
        --role "Key Vault Secrets User" \
        --scope "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEY_VAULT_NAME"
    
    log_success "Permissions assigned"
}

# Get deployment information
get_deployment_info() {
    log_info "Getting deployment information..."
    
    FQDN=$(az containerapp show \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query properties.configuration.ingress.fqdn \
        --output tsv)
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    echo "📋 Deployment Details:"
    echo "  Resource Group: $RESOURCE_GROUP"
    echo "  Container App: $CONTAINER_APP_NAME"
    echo "  FQDN: https://$FQDN"
    echo "  Health Check: https://$FQDN/health"
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs: az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
    echo "  Scale app: az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 1"
    echo "  Stop app: az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --min-replicas 0 --max-replicas 0"
    echo ""
}

# Main deployment function
main() {
    log_info "Starting Azure deployment for LinkedIn Bot..."
    
    check_azure_login
    create_resource_group
    create_container_registry
    create_key_vault
    set_telegram_token
    build_and_push_image
    create_container_app_environment
    deploy_container_app
    assign_permissions
    get_deployment_info
    
    log_success "All deployment steps completed!"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "cleanup")
        log_warning "Deleting resource group: $RESOURCE_GROUP"
        read -p "Are you sure? This will delete all resources. (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            az group delete --name "$RESOURCE_GROUP" --yes --no-wait
            log_success "Cleanup initiated"
        else
            log_info "Cleanup cancelled"
        fi
        ;;
    "status")
        log_info "Checking deployment status..."
        az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --output table
        ;;
    "logs")
        log_info "Showing container logs..."
        az containerapp logs show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --follow
        ;;
    "scale")
        REPLICAS=${2:-1}
        log_info "Scaling to $REPLICAS replicas..."
        az containerapp update --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --min-replicas "$REPLICAS" --max-replicas "$REPLICAS"
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|status|logs|scale}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the LinkedIn Bot to Azure"
        echo "  cleanup - Delete all Azure resources"
        echo "  status  - Show deployment status"
        echo "  logs    - Show container logs"
        echo "  scale   - Scale the application (usage: $0 scale <replicas>)"
        exit 1
        ;;
esac
