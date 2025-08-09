# Azure Deployment Guide for LinkedIn Bot

## 🏗️ Prerequisites

### 1. Azure Account Setup

- **Azure Subscription**: Active Azure subscription with billing enabled
- **Resource Group**: Create or use existing resource group
- **Service Principal**: For automated deployments (optional but recommended)

### 2. Azure CLI Installation

```bash
# Install Azure CLI
# Windows (PowerShell)
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'

# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 3. Required Azure Services

- **Azure Container Instances (ACI)** - For simple container deployment
- **Azure Container Apps** - For advanced container orchestration (recommended)
- **Azure App Service** - For web app deployment
- **Azure Key Vault** - For secure secret management
- **Azure Container Registry (ACR)** - For private container images
- **Azure Log Analytics** - For monitoring and logging

## 🚀 Deployment Options

### Option 1: Azure Container Apps (Recommended)

**Best for**: Production workloads, auto-scaling, advanced features

**Features**:

- Auto-scaling based on demand
- Built-in load balancing
- Integrated monitoring
- Managed certificates
- Blue-green deployments

### Option 2: Azure Container Instances (ACI)

**Best for**: Simple deployments, development/testing

**Features**:

- Simple container deployment
- Per-second billing
- Quick startup
- Basic monitoring

### Option 3: Azure App Service

**Best for**: Web-based bots with HTTP endpoints

**Features**:

- Integrated deployment slots
- Custom domains
- SSL certificates
- Application insights

## 💰 Cost Estimation

### Container Apps (Recommended)

- **Consumption Plan**: $0.000024/vCPU-second + $0.000004/GiB-second
- **Estimated Monthly Cost**: $15-30 for typical bot usage
- **Free Tier**: 180,000 vCPU-seconds + 360,000 GiB-seconds per month

### Container Instances

- **Standard**: $0.0000012/second per vCPU + $0.00000017/second per GB
- **Estimated Monthly Cost**: $20-40 for typical bot usage

### App Service

- **Basic B1**: $12.41/month (1 core, 1.75 GB RAM)
- **Standard S1**: $56.94/month (1 core, 1.75 GB RAM, staging slots)

## 🔐 Security Requirements

### 1. Service Principal (for CI/CD)

```bash
# Create service principal
az ad sp create-for-rbac --name "linkedin-bot-sp" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}
```

### 2. Required Secrets

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `TELEGRAM_BOT_TOKEN`

### 3. Azure Key Vault Setup

```bash
# Create Key Vault
az keyvault create --name "linkedin-bot-kv" --resource-group "linkedin-bot-rg" --location "East US"

# Add secrets
az keyvault secret set --vault-name "linkedin-bot-kv" --name "telegram-bot-token" --value "your-token"
```

## 📋 Step-by-Step Deployment

### Step 1: Azure Resource Setup

```bash
# Login to Azure
az login

# Create resource group
az group create --name linkedin-bot-rg --location "East US"

# Create container registry (optional, for private images)
az acr create --resource-group linkedin-bot-rg --name linkedinbotacr --sku Basic
```

### Step 2: GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_CLIENT_SECRET=your-service-principal-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=linkedin-bot-rg
AZURE_CONTAINER_APP_NAME=linkedin-bot-app
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### Step 3: Deploy using GitHub Actions

The deployment will be automated once you push to the main branch.

### Step 4: Manual Deployment (Alternative)

```bash
# Build and push to Azure Container Registry
az acr build --registry linkedinbotacr --image linkedin-bot:latest .

# Create container app environment
az containerapp env create --name linkedin-bot-env --resource-group linkedin-bot-rg --location "East US"

# Deploy container app
az containerapp create \
  --name linkedin-bot-app \
  --resource-group linkedin-bot-rg \
  --environment linkedin-bot-env \
  --image linkedinbotacr.azurecr.io/linkedin-bot:latest \
  --target-port 8080 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 1 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars TELEGRAM_BOT_TOKEN=secretref:telegram-bot-token
```

## 🔧 Configuration Management

### Environment Variables

```yaml
# Required for Azure deployment
AZURE_ENVIRONMENT=production
TELEGRAM_BOT_TOKEN=from-key-vault
LOG_LEVEL=INFO
ENABLE_METRICS=true
HEALTH_CHECK_ENABLED=true
```

### Resource Limits

```yaml
# Recommended resource allocation
CPU: 0.5 cores
Memory: 1 GB
Storage: 10 GB (temporary)
Network: Standard
```

## 📊 Monitoring Setup

### Azure Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app linkedin-bot-insights \
  --location "East US" \
  --resource-group linkedin-bot-rg \
  --application-type web
```

### Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --workspace-name linkedin-bot-logs \
  --resource-group linkedin-bot-rg \
  --location "East US"
```

## 🚨 Common Issues & Solutions

### Issue 1: Container Startup Failures

**Solution**: Check container logs and ensure all environment variables are set

```bash
az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg
```

### Issue 2: Chrome/Selenium Issues

**Solution**: Ensure the Docker image includes Chrome and ChromeDriver

- Use the provided Dockerfile which installs Chrome
- Set appropriate Chrome options for headless mode

### Issue 3: Network Connectivity

**Solution**: Configure proper network security groups and firewall rules

```bash
# Check container app status
az containerapp show --name linkedin-bot-app --resource-group linkedin-bot-rg
```

### Issue 4: Secret Management

**Solution**: Use Azure Key Vault integration

```bash
# Link Key Vault to Container App
az containerapp secret set \
  --name linkedin-bot-app \
  --resource-group linkedin-bot-rg \
  --secrets telegram-bot-token=keyvaultref:https://linkedin-bot-kv.vault.azure.net/secrets/telegram-bot-token,identityref:system
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline will:

1. Build Docker image
2. Push to Azure Container Registry
3. Deploy to Azure Container Apps
4. Run health checks
5. Send deployment notifications

## 📈 Scaling Configuration

### Auto-scaling Rules

```yaml
# Container Apps auto-scaling
minReplicas: 0 # Scale to zero when idle
maxReplicas: 3 # Maximum instances
rules:
  - name: "http-scaling"
    http:
      metadata:
        concurrentRequests: 10
```

## 💡 Best Practices

1. **Use Container Apps** for production deployments
2. **Store secrets** in Azure Key Vault
3. **Enable monitoring** with Application Insights
4. **Set up alerts** for failures and performance issues
5. **Use managed identity** instead of service principals when possible
6. **Implement health checks** for container readiness
7. **Configure proper resource limits** to control costs
8. **Use Azure Front Door** for global distribution (if needed)

## 📞 Support & Troubleshooting

### Azure CLI Commands for Debugging

```bash
# Check container app status
az containerapp show --name linkedin-bot-app --resource-group linkedin-bot-rg

# View logs
az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg --follow

# Check revisions
az containerapp revision list --name linkedin-bot-app --resource-group linkedin-bot-rg

# Scale manually
az containerapp update --name linkedin-bot-app --resource-group linkedin-bot-rg --min-replicas 1 --max-replicas 2
```

### Cost Optimization

- Use **consumption-based** pricing for Container Apps
- Set **scale-to-zero** for development environments
- Monitor **resource usage** with Azure Cost Management
- Use **reserved instances** for predictable workloads

---

**Next Steps**: Choose your deployment option and follow the corresponding setup guide!
