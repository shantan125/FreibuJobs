#!/usr/bin/env python3
"""
Cross-Platform LinkedIn Bot Test

Tests WebDriver functionality across different platforms.
"""

import os
import sys
import platform
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_platform_detection():
    """Test platform detection."""
    current_platform = platform.system().lower()
    print(f"🖥️  Platform: {current_platform}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    return current_platform

def test_chrome_installation():
    """Test if Chrome is installed on the current platform."""
    current_platform = platform.system().lower()
    
    print("\n🔍 Testing Chrome installation...")
    
    if current_platform == "windows":
        # Windows Chrome locations
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    else:
        # Linux Chrome locations
        chrome_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("❌ Chrome not found in standard locations")
        print("📋 Expected locations:")
        for path in chrome_paths:
            print(f"   - {path}")
    
    return chrome_found

def test_webdriver_manager():
    """Test webdriver-manager functionality."""
    print("\n🚗 Testing webdriver-manager...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test driver download
        print("📥 Downloading ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ Driver downloaded: {driver_path}")
        
        # Check if it's executable
        if os.path.exists(driver_path):
            print(f"📁 Driver file exists: ✅")
            print(f"🔧 Driver executable: {'✅' if os.access(driver_path, os.X_OK) else '❌'}")
        else:
            print(f"❌ Driver file not found")
        
        return driver_path
        
    except Exception as e:
        print(f"❌ webdriver-manager error: {e}")
        return None

def test_selenium_basic():
    """Test basic Selenium functionality."""
    print("\n🔬 Testing Selenium WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Setup Chrome options for cross-platform compatibility
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        current_platform = platform.system().lower()
        if current_platform == "linux":
            chrome_options.add_argument("--single-process")
            chrome_options.add_argument("--disable-software-rasterizer")
        
        # Get driver path
        driver_path = ChromeDriverManager().install()
        print(f"📍 Using driver: {driver_path}")
        
        # Create service and driver
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        print("🌐 Testing basic navigation...")
        driver.get("data:,Hello World")
        title = driver.title
        print(f"✅ Page title: {title}")
        
        # Test Google access
        print("🔍 Testing Google access...")
        driver.get("https://www.google.com")
        google_title = driver.title
        print(f"✅ Google title: {google_title}")
        
        driver.quit()
        print("✅ WebDriver test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CROSS-PLATFORM LINKEDIN BOT TEST")
    print("=" * 60)
    
    # Test platform detection
    platform_name = test_platform_detection()
    
    # Test Chrome installation
    chrome_available = test_chrome_installation()
    
    # Test webdriver-manager
    driver_path = test_webdriver_manager()
    
    # Test Selenium if previous tests passed
    if chrome_available and driver_path:
        selenium_works = test_selenium_basic()
    else:
        selenium_works = False
        print("\n⚠️ Skipping Selenium test due to missing dependencies")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"🖥️  Platform: {platform_name}")
    print(f"🌐 Chrome Available: {'✅' if chrome_available else '❌'}")
    print(f"🚗 WebDriver Manager: {'✅' if driver_path else '❌'}")
    print(f"🔬 Selenium Works: {'✅' if selenium_works else '❌'}")
    
    if selenium_works:
        print("\n✅ All tests passed! Cross-platform compatibility verified.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("💡 This might be expected on Windows without Chrome installed.")
    
    print("=" * 60)
