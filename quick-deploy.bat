@echo off
echo 🔧 LinkedIn Bot - Quick Deploy to Azure
echo =====================================

echo.
echo 📦 Step 1: Building Docker image...
docker build -t linkedin-bot:latest .

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Build successful!

echo.
echo 📤 Step 2: Pushing to GitHub (triggers Azure deployment)...

git add -A
git commit -m "🚀 Deploy: Streaming bot with enhanced logging and forced restart"
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git push failed!
    pause
    exit /b 1
)

echo.
echo 🎉 Deployment initiated!
echo 📊 Monitor deployment: https://github.com/shantan125/FreibuJobs/actions
echo 🤖 Test bot in Telegram once deployment completes
echo.

echo ⏳ Waiting for deployment to complete (checking every 30 seconds)...

:check_loop
timeout /t 30 > nul
echo 🔍 Checking deployment status...

REM You can add Azure CLI commands here to check deployment status
REM For now, we'll just wait and let user check manually

set /p continue="Check GitHub Actions. Continue waiting? (y/n): "
if /i "%continue%"=="y" goto check_loop

echo.
echo 🚀 Deployment process completed!
echo 💡 Test your bot in Telegram to verify streaming functionality
pause
