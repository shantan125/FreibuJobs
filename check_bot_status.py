#!/usr/bin/env python3
"""
Quick Telegram Bot Status Checker
"""

import requests
import json

def check_telegram_bot_status():
    """Check if the Telegram bot is responding."""
    
    # Your bot token from .env
    bot_token = "8422798837:AAFhcis3PaHKqz1EgnBce34xtfYC0oaSJ_A"
    
    # Telegram API URL
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        print("🤖 Checking Telegram bot status...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Bot is active!")
                print(f"   👤 Bot Name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   🔗 Username: @{bot_info.get('username', 'Unknown')}")
                print(f"   🆔 Bot ID: {bot_info.get('id', 'Unknown')}")
                return True
            else:
                print(f"❌ Bot API error: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def check_bot_updates():
    """Check recent updates/messages to the bot."""
    
    bot_token = "8422798837:AAFhcis3PaHKqz1EgnBce34xtfYC0oaSJ_A"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        print("\n📨 Checking recent bot activity...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                updates = data.get("result", [])
                print(f"📊 Found {len(updates)} recent updates")
                
                if updates:
                    latest = updates[-1]
                    print(f"🕐 Latest update ID: {latest.get('update_id')}")
                    message = latest.get("message", {})
                    if message:
                        user = message.get("from", {})
                        print(f"👤 Last user: {user.get('first_name', 'Unknown')}")
                        print(f"💬 Last message: {message.get('text', 'No text')[:50]}...")
                
                return True
            else:
                print(f"❌ Updates API error: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 TELEGRAM BOT STATUS CHECKER")
    print("=" * 50)
    
    bot_active = check_telegram_bot_status()
    updates_available = check_bot_updates()
    
    print("\n" + "=" * 50)
    if bot_active:
        print("✅ RESULT: Your Telegram bot is ACTIVE and responding!")
        print("💡 You can now test it by sending a message to your bot.")
    else:
        print("❌ RESULT: Your Telegram bot is NOT responding.")
        print("🔧 Check your Azure Container App logs for issues.")
    
    print("=" * 50)
