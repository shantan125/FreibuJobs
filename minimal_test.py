#!/usr/bin/env python3
"""
Minimal test - no WebDriver
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔧 Testing configuration only...")

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    print("✅ Environment loaded")
    
    # Check variables
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    
    print(f"📧 LinkedIn email: {'✅' if linkedin_email else '❌'}")
    print(f"🔑 LinkedIn password: {'✅' if linkedin_password else '❌'}")
    print(f"🤖 Telegram token: {'✅' if telegram_token else '❌'}")
    
    if linkedin_email:
        print(f"Email starts with: {linkedin_email[:5]}...")
    
    from src.utils.config import ConfigurationManager
    print("✅ Importing ConfigurationManager...")
    
    config = ConfigurationManager()
    print("✅ Configuration created")
    
    print(f"📍 Default location: {config.search_config.default_location}")
    print(f"📊 Max results: {config.search_config.max_results}")
    print(f"📧 LinkedIn email configured: {'✅' if config.linkedin_config.email else '❌'}")
    
    # Test URL building
    from src.scraper.linkedin import LinkedInScraper
    print("✅ Importing LinkedInScraper...")
    
    scraper = LinkedInScraper(config)
    print("✅ Scraper created (no WebDriver yet)")
    
    # Test URL building only
    url = scraper._build_search_url(
        keyword="Java Developer",
        location="India",
        time_filter="r86400"
    )
    
    print(f"✅ Search URL: {url}")
    
    print("\n🎉 Configuration test successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
