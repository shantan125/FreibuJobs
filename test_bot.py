#!/usr/bin/env python3
"""
Quick test script to verify bot functionality
"""

import requests
import time

# Bot token from environment
BOT_TOKEN = "8422798837:AAFhcis3PaHKqz1EgnBce34xtfYC0oaSJ_A"
AZURE_URL = "https://linkedin-bot-app.livelyfield-aae26b29.eastasia.azurecontainerapps.io"

def test_telegram_api():
    """Test if Telegram API is accessible"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Telegram API: Bot '{data['result']['username']}' is active")
            return True
        else:
            print(f"❌ Telegram API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram API Error: {e}")
        return False

def test_azure_health():
    """Test Azure Container App health"""
    try:
        health_url = f"{AZURE_URL}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Azure Health: Container App is healthy")
            return True
        else:
            print(f"❌ Azure Health: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Azure Health Error: {e}")
        return False

def test_bot_updates():
    """Test if bot is receiving updates"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bot Updates: {len(data['result'])} updates received")
            return True
        else:
            print(f"❌ Bot Updates: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bot Updates Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing LinkedIn Bot Status...")
    print("=" * 50)
    
    # Test Telegram API
    telegram_ok = test_telegram_api()
    time.sleep(1)
    
    # Test Azure health
    azure_ok = test_azure_health()
    time.sleep(1)
    
    # Test bot updates
    updates_ok = test_bot_updates()
    
    print("=" * 50)
    
    if telegram_ok and azure_ok:
        print("🎉 Bot is operational! ChromeDriver fix should be working.")
    elif telegram_ok:
        print("⚠️  Bot API works, but Azure health check failed. Container may be updating.")
    else:
        print("❌ Bot has issues. Check logs for details.")
    
    print("\n📝 To test job search, send a message to your bot:")
    print("   1. Open Telegram")
    print("   2. Search for your bot")
    print("   3. Send: /start")
    print("   4. Try searching for: python developer")

if __name__ == "__main__":
    main()
