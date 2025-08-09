@echo off
REM Azure Deployment Script for LinkedIn Bot (Windows)
REM This script automates the deployment process to Azure Container Apps

setlocal enabledelayedexpansion

REM Configuration
set RESOURCE_GROUP=linkedin-bot-rg
set LOCATION=East US
set CONTAINER_APP_NAME=linkedin-bot-app
set CONTAINER_APP_ENV=linkedin-bot-env
set CONTAINER_REGISTRY=linkedinbotacr
set KEY_VAULT_NAME=linkedin-bot-kv
set IMAGE_NAME=linkedin-bot
set IMAGE_TAG=latest

REM Check if Azure CLI is installed
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure CLI not found. Please install Azure CLI first.
    echo Download from: https://aka.ms/installazurecliwindows
    exit /b 1
)

REM Check if user is logged in to Azure
echo [INFO] Checking Azure login status...
az account show >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Not logged in to Azure. Please run 'az login' first.
    exit /b 1
)
echo [SUCCESS] Azure login verified

if "%1"=="cleanup" goto cleanup
if "%1"=="status" goto status
if "%1"=="logs" goto logs
if "%1"=="scale" goto scale
if "%1"=="help" goto help
if "%1"=="" goto deploy
goto help

:deploy
echo [INFO] Starting Azure deployment for LinkedIn Bot...

REM Check for Telegram bot token
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo [ERROR] TELEGRAM_BOT_TOKEN environment variable is not set
    echo Please set it: set TELEGRAM_BOT_TOKEN=your-token
    exit /b 1
)

REM Create resource group
echo [INFO] Creating resource group: %RESOURCE_GROUP%
az group create --name "%RESOURCE_GROUP%" --location "%LOCATION%" --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Resource group created

REM Create Azure Container Registry
echo [INFO] Creating Azure Container Registry: %CONTAINER_REGISTRY%
az acr create --resource-group "%RESOURCE_GROUP%" --name "%CONTAINER_REGISTRY%" --sku Basic --admin-enabled false --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Container Registry created

REM Create Key Vault
echo [INFO] Creating Azure Key Vault: %KEY_VAULT_NAME%
az keyvault create --name "%KEY_VAULT_NAME%" --resource-group "%RESOURCE_GROUP%" --location "%LOCATION%" --enable-rbac-authorization true --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Key Vault created

REM Set Telegram bot token in Key Vault
echo [INFO] Setting Telegram bot token in Key Vault
az keyvault secret set --vault-name "%KEY_VAULT_NAME%" --name "telegram-bot-token" --value "%TELEGRAM_BOT_TOKEN%" --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Telegram bot token stored in Key Vault

REM Build and push Docker image
echo [INFO] Building and pushing Docker image to ACR
az acr build --registry "%CONTAINER_REGISTRY%" --image "%IMAGE_NAME%:%IMAGE_TAG%" --file Dockerfile . --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Docker image built and pushed

REM Create Container App Environment
echo [INFO] Creating Container App Environment: %CONTAINER_APP_ENV%
az containerapp env create --name "%CONTAINER_APP_ENV%" --resource-group "%RESOURCE_GROUP%" --location "%LOCATION%" --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Container App Environment created

REM Get ACR login server
for /f "tokens=*" %%a in ('az acr show --name "%CONTAINER_REGISTRY%" --resource-group "%RESOURCE_GROUP%" --query loginServer --output tsv') do set ACR_LOGIN_SERVER=%%a

REM Deploy Container App
echo [INFO] Deploying Container App: %CONTAINER_APP_NAME%
az containerapp create ^
    --name "%CONTAINER_APP_NAME%" ^
    --resource-group "%RESOURCE_GROUP%" ^
    --environment "%CONTAINER_APP_ENV%" ^
    --image "%ACR_LOGIN_SERVER%/%IMAGE_NAME%:%IMAGE_TAG%" ^
    --target-port 8080 ^
    --ingress external ^
    --min-replicas 0 ^
    --max-replicas 3 ^
    --cpu 0.5 ^
    --memory 1.0Gi ^
    --registry-server "%ACR_LOGIN_SERVER%" ^
    --registry-identity system ^
    --env-vars AZURE_ENVIRONMENT=production LOG_LEVEL=INFO ENABLE_METRICS=true HEALTH_CHECK_ENABLED=true MAX_RESULTS_PER_SEARCH=10 DEFAULT_LOCATION=India ^
    --secrets telegram-bot-token="keyvaultref:https://%KEY_VAULT_NAME%.vault.azure.net/secrets/telegram-bot-token,identityref:system" ^
    --output table
if %errorlevel% neq 0 goto error
echo [SUCCESS] Container App deployed

REM Get the Container App's system-assigned identity
for /f "tokens=*" %%a in ('az containerapp show --name "%CONTAINER_APP_NAME%" --resource-group "%RESOURCE_GROUP%" --query identity.principalId --output tsv') do set PRINCIPAL_ID=%%a

REM Get subscription ID
for /f "tokens=*" %%a in ('az account show --query id --output tsv') do set SUBSCRIPTION_ID=%%a

REM Assign AcrPull role to Container App identity
echo [INFO] Assigning AcrPull permissions...
az role assignment create --assignee "%PRINCIPAL_ID%" --role "AcrPull" --scope "/subscriptions/%SUBSCRIPTION_ID%/resourceGroups/%RESOURCE_GROUP%/providers/Microsoft.ContainerRegistry/registries/%CONTAINER_REGISTRY%"

REM Assign Key Vault Secrets User role to Container App identity
echo [INFO] Assigning Key Vault permissions...
az role assignment create --assignee "%PRINCIPAL_ID%" --role "Key Vault Secrets User" --scope "/subscriptions/%SUBSCRIPTION_ID%/resourceGroups/%RESOURCE_GROUP%/providers/Microsoft.KeyVault/vaults/%KEY_VAULT_NAME%"

echo [SUCCESS] Permissions assigned

REM Get deployment information
for /f "tokens=*" %%a in ('az containerapp show --name "%CONTAINER_APP_NAME%" --resource-group "%RESOURCE_GROUP%" --query properties.configuration.ingress.fqdn --output tsv') do set FQDN=%%a

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo Deployment Details:
echo   Resource Group: %RESOURCE_GROUP%
echo   Container App: %CONTAINER_APP_NAME%
echo   FQDN: https://!FQDN!
echo   Health Check: https://!FQDN!/health
echo.
echo Management Commands:
echo   View logs: az containerapp logs show --name %CONTAINER_APP_NAME% --resource-group %RESOURCE_GROUP% --follow
echo   Scale app: az containerapp update --name %CONTAINER_APP_NAME% --resource-group %RESOURCE_GROUP% --min-replicas 1
echo   Stop app: az containerapp update --name %CONTAINER_APP_NAME% --resource-group %RESOURCE_GROUP% --min-replicas 0 --max-replicas 0
echo.
goto end

:cleanup
echo [WARNING] Deleting resource group: %RESOURCE_GROUP%
set /p confirm="Are you sure? This will delete all resources. (y/N): "
if /i "%confirm%"=="y" (
    az group delete --name "%RESOURCE_GROUP%" --yes --no-wait
    echo [SUCCESS] Cleanup initiated
) else (
    echo [INFO] Cleanup cancelled
)
goto end

:status
echo [INFO] Checking deployment status...
az containerapp show --name "%CONTAINER_APP_NAME%" --resource-group "%RESOURCE_GROUP%" --output table
goto end

:logs
echo [INFO] Showing container logs...
az containerapp logs show --name "%CONTAINER_APP_NAME%" --resource-group "%RESOURCE_GROUP%" --follow
goto end

:scale
set REPLICAS=%2
if "%REPLICAS%"=="" set REPLICAS=1
echo [INFO] Scaling to %REPLICAS% replicas...
az containerapp update --name "%CONTAINER_APP_NAME%" --resource-group "%RESOURCE_GROUP%" --min-replicas "%REPLICAS%" --max-replicas "%REPLICAS%"
goto end

:help
echo.
echo Usage: %0 [command]
echo.
echo Commands:
echo   deploy  - Deploy the LinkedIn Bot to Azure (default)
echo   cleanup - Delete all Azure resources
echo   status  - Show deployment status
echo   logs    - Show container logs
echo   scale   - Scale the application (usage: %0 scale [replicas])
echo   help    - Show this help message
echo.
echo Before deployment, set your Telegram bot token:
echo   set TELEGRAM_BOT_TOKEN=your-token-here
goto end

:error
echo [ERROR] Deployment failed. Check the error messages above.
exit /b 1

:end
