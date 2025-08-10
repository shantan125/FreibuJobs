#!/usr/bin/env python3
"""
Simple LinkedIn Scraper Test - Debug Version
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if imports work."""
    print("🔧 Testing imports...")
    
    try:
        from dotenv import load_dotenv
        print("✅ dotenv imported")
        
        # Load environment
        load_dotenv()
        print("✅ Environment loaded")
        
        # Check variables
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        linkedin_email = os.getenv("LINKEDIN_EMAIL")
        
        print(f"📧 LinkedIn email: {linkedin_email[:10]}..." if linkedin_email else "❌ LinkedIn email not found")
        print(f"🤖 Telegram token: {telegram_token[:10]}..." if telegram_token else "❌ Telegram token not found")
        
        from src.utils.config import ConfigurationManager
        print("✅ ConfigurationManager imported")
        
        config = ConfigurationManager()
        print("✅ Configuration created")
        print(f"📍 Default location: {config.search_config.default_location}")
        print(f"📊 Max results: {config.search_config.max_results}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webdriver():
    """Test WebDriver setup."""
    print("\n🚗 Testing WebDriver setup...")
    
    try:
        from src.scraper.linkedin import LinkedInScraper
        from src.utils.config import ConfigurationManager
        
        config = ConfigurationManager()
        scraper = LinkedInScraper(config)
        
        print("✅ Scraper created")
        
        # Try to setup driver
        driver = scraper._get_driver()
        print("✅ WebDriver initialized")
        
        # Test basic navigation
        driver.get("https://www.google.com")
        print(f"✅ Navigation successful - Title: {driver.title}")
        
        # Close driver
        driver.quit()
        print("✅ WebDriver closed")
        
        return True
        
    except Exception as e:
        print(f"❌ WebDriver error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_linkedin_url():
    """Test LinkedIn URL building."""
    print("\n🔗 Testing LinkedIn URL building...")
    
    try:
        from src.scraper.linkedin import LinkedInScraper
        from src.utils.config import ConfigurationManager
        
        config = ConfigurationManager()
        scraper = LinkedInScraper(config)
        
        # Test URL building
        url = scraper._build_search_url(
            keyword="Java Developer",
            location="India",
            time_filter="r86400"
        )
        
        print(f"✅ URL built: {url}")
        
        # Expected format check
        if "linkedin.com/jobs/search" in url and "Java%20Developer" in url:
            print("✅ URL format looks correct")
        else:
            print("⚠️ URL format might be incorrect")
        
        return True
        
    except Exception as e:
        print(f"❌ URL building error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔬 SIMPLE LINKEDIN SCRAPER DEBUG")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_webdriver()
    success &= test_linkedin_url()
    
    if success:
        print("\n✅ All basic tests passed! Ready for full LinkedIn search test.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    print("=" * 50)
