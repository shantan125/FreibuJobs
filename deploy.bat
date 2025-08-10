@echo off
echo 🚀 LinkedIn Bot Deployment Script
echo ================================

echo.
echo 📦 Building Docker image...
docker build -t linkedin-bot:latest .

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

echo.
echo ✅ Docker image built successfully!

echo.
echo 🔍 Available images:
docker images | findstr linkedin-bot

echo.
echo 🚀 Deployment options:
echo 1. Push to Azure Container Registry (ACR)
echo 2. Run locally for testing
echo 3. Push to GitHub (triggers Azure deployment)
echo.

set /p choice="Enter your choice (1/2/3): "

if "%choice%"=="1" goto azure_deploy
if "%choice%"=="2" goto local_run
if "%choice%"=="3" goto github_push
goto invalid_choice

:azure_deploy
echo.
echo 📤 Pushing to Azure Container Registry...
echo Note: Make sure you're logged in with 'az acr login --name linkedinbotacr'

docker tag linkedin-bot:latest linkedinbotacr.azurecr.io/linkedin-bot:latest
docker push linkedinbotacr.azurecr.io/linkedin-bot:latest

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Azure push failed! Make sure you're logged in:
    echo az acr login --name linkedinbotacr
    pause
    exit /b 1
)

echo ✅ Pushed to Azure Container Registry!
echo 🔄 Manually update the Azure Container App to use the new image
goto end

:local_run
echo.
echo 🏃 Running locally for testing...
echo Note: Make sure you have TELEGRAM_BOT_TOKEN set in your environment

docker run -it --rm ^
    -e TELEGRAM_BOT_TOKEN=%TELEGRAM_BOT_TOKEN% ^
    -e LOG_LEVEL=DEBUG ^
    -e AZURE_ENVIRONMENT=local ^
    linkedin-bot:latest

goto end

:github_push
echo.
echo 📤 Pushing to GitHub (will trigger Azure deployment)...

git add -A
git status

echo.
set /p commit_msg="Enter commit message: "
git commit -m "%commit_msg%"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Nothing to commit or commit failed
)

git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git push failed!
    pause
    exit /b 1
)

echo ✅ Pushed to GitHub! Check GitHub Actions for deployment status.
echo 🔗 https://github.com/shantan125/FreibuJobs/actions
goto end

:invalid_choice
echo ❌ Invalid choice! Please enter 1, 2, or 3.
pause
exit /b 1

:end
echo.
echo 🎉 Deployment process completed!
echo.
echo 📋 Quick commands:
echo   • Check logs: docker logs [container-id]
echo   • Azure logs: az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg --follow
echo   • Test bot: Open Telegram and message your bot
echo.
pause
