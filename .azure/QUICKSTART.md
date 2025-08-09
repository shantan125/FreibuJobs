# Azure Setup Guide - Quick Start

## 🚀 Quick Setup Checklist

### ✅ **Step 1: Azure Account & CLI**

- [ ] Azure subscription with billing enabled
- [ ] Azure CLI installed and logged in
- [ ] PowerShell/Bash terminal access

### ✅ **Step 2: Get Your Telegram Bot Token**

- [ ] Message @BotFather on Telegram
- [ ] Create new bot: `/newbot`
- [ ] Save the bot token securely

### ✅ **Step 3: One-Command Deployment**

**Windows:**

```cmd
# Set your bot token
set TELEGRAM_BOT_TOKEN=your_bot_token_here

# Run deployment
.\.azure\deploy.bat
```

**Linux/Mac:**

```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN=your_bot_token_here

# Make script executable and run
chmod +x .azure/deploy.sh
./.azure/deploy.sh
```

### ✅ **Step 4: Verify Deployment**

- [ ] Check the output for your bot URL
- [ ] Test health check: `https://your-app-url/health`
- [ ] Message your bot on Telegram

## 🔧 Manual Setup (If Needed)

### Prerequisites Installation

**Install Azure CLI:**

```powershell
# Windows PowerShell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

**Login to Azure:**

```bash
az login
az account set --subscription "your-subscription-name-or-id"
```

### GitHub Actions Setup (Optional)

If you want automated deployments:

1. **Create Service Principal:**

```bash
az ad sp create-for-rbac --name "linkedin-bot-sp" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth
```

2. **Add GitHub Secrets:**
   Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

```
AZURE_CREDENTIALS=<entire JSON output from service principal>
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
AZURE_SUBSCRIPTION_ID=your_subscription_id
```

## 💰 **Cost Estimate**

### Free Tier Included:

- ✅ 180,000 vCPU-seconds per month
- ✅ 360,000 GiB-seconds per month
- ✅ Enough for small to medium bot usage

### Paid Usage:

- **Light usage**: $10-20/month
- **Medium usage**: $20-40/month
- **Heavy usage**: $40-80/month

## 🔍 **Management Commands**

### View Logs:

```bash
az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg --follow
```

### Scale App:

```bash
# Scale up
az containerapp update --name linkedin-bot-app --resource-group linkedin-bot-rg --min-replicas 1

# Scale down (save costs)
az containerapp update --name linkedin-bot-app --resource-group linkedin-bot-rg --min-replicas 0 --max-replicas 0
```

### Check Status:

```bash
az containerapp show --name linkedin-bot-app --resource-group linkedin-bot-rg --output table
```

### Update Bot:

```bash
# Push new code to main branch (if using GitHub Actions)
# OR run deployment script again
.\.azure\deploy.bat  # Windows
./.azure/deploy.sh   # Linux/Mac
```

## 🚨 **Troubleshooting**

### Common Issues:

**1. "Command not found: az"**

- Install Azure CLI from https://aka.ms/installazurecliwindows

**2. "Not logged in to Azure"**

- Run: `az login`

**3. "Telegram bot not responding"**

- Check bot token is correct
- Verify deployment completed successfully
- Check logs: `az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg`

**4. "Container fails to start"**

- Check environment variables are set correctly
- Verify image was built successfully
- Check resource limits

### Get Help:

```bash
# Deployment script help
.\.azure\deploy.bat help     # Windows
./.azure/deploy.sh help      # Linux/Mac

# Azure CLI help
az containerapp --help
```

## 🧹 **Cleanup (Delete Everything)**

**⚠️ Warning: This deletes all Azure resources**

```bash
# Windows
.\.azure\deploy.bat cleanup

# Linux/Mac
./.azure/deploy.sh cleanup
```

## 🎉 **Success!**

After successful deployment, you'll see:

```
✅ Deployment completed successfully!

📋 Deployment Details:
  Resource Group: linkedin-bot-rg
  Container App: linkedin-bot-app
  FQDN: https://linkedin-bot-app.azurecontainerapps.io
  Health Check: https://linkedin-bot-app.azurecontainerapps.io/health
```

Your bot is now running on Azure! 🚀

---

**Need help?** Check the full [Azure Deployment Guide](AZURE_DEPLOYMENT.md) for detailed instructions.
