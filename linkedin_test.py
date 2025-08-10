#!/usr/bin/env python3
"""
LinkedIn Direct Access Test - See what LinkedIn returns
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_linkedin_direct():
    """Test direct LinkedIn access to see what's happening"""
    driver = None
    try:
        print("🔧 Setting up WebDriver...")
        
        # Setup Chrome options (similar to our scraper)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Create driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver created successfully")
        
        # Test 1: Access LinkedIn homepage
        print("\n🔍 Test 1: Accessing LinkedIn homepage...")
        driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Test 2: Try to access a job search directly (without login)
        print("\n🔍 Test 2: Accessing job search page...")
        search_url = "https://www.linkedin.com/jobs/search/?keywords=Java%20Developer&location=India&f_TPR=r86400&sortBy=DD"
        print(f"Navigating to: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        print(f"Current URL after search: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Test 3: Check for job elements with different selectors
        print("\n🔍 Test 3: Looking for job elements...")
        
        job_selectors = [
            ".job-search-card",
            ".jobs-search-card", 
            ".base-search-card",
            ".job-result-card",
            "[data-entity-urn*='job']",
            ".job-card",
            ".result-card",
            "a[href*='/jobs/view/']"
        ]
        
        found_elements = False
        for selector in job_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Selector '{selector}': Found {len(elements)} elements")
                if elements:
                    found_elements = True
                    # Get href from first few elements
                    for i, element in enumerate(elements[:3]):
                        try:
                            href = element.get_attribute('href')
                            if href:
                                print(f"  Element {i+1} href: {href}")
                        except:
                            print(f"  Element {i+1}: No href attribute")
            except Exception as e:
                print(f"Error with selector '{selector}': {e}")
        
        # Test 4: Check page source for indicators
        print("\n🔍 Test 4: Analyzing page content...")
        page_source = driver.page_source
        
        indicators = {
            "Sign in required": "sign in" in page_source.lower() or "login" in page_source.lower(),
            "Bot detected": "bot" in page_source.lower() or "automation" in page_source.lower(),
            "CAPTCHA present": "captcha" in page_source.lower() or "recaptcha" in page_source.lower(),
            "Jobs content": "jobs" in page_source.lower(),
            "Search results": "results" in page_source.lower(),
            "Access denied": "access denied" in page_source.lower() or "forbidden" in page_source.lower()
        }
        
        for indicator, present in indicators.items():
            status = "✅ YES" if present else "❌ NO"
            print(f"{indicator}: {status}")
        
        # Test 5: Look for specific job-related content
        print("\n🔍 Test 5: Looking for job-specific content...")
        
        job_indicators = [
            "view job",
            "apply now",
            "job details",
            "company",
            "location",
            "posted",
            "ago"
        ]
        
        for indicator in job_indicators:
            count = page_source.lower().count(indicator)
            print(f"'{indicator}': Found {count} times")
        
        # Test 6: Save page source for manual inspection
        print("\n💾 Saving page source for inspection...")
        filename = "linkedin_search_debug.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"Page source saved to {filename}")
        
        # Test 7: Check if we're getting redirected or blocked
        print("\n🔍 Test 7: Checking for redirects or blocks...")
        
        if "linkedin.com/jobs" not in driver.current_url:
            print("⚠️ Possible redirect detected!")
        
        if "challenge" in driver.current_url or "security" in driver.current_url:
            print("🚫 Security challenge detected!")
        
        if not found_elements:
            print("❌ No job elements found - this is the issue!")
        else:
            print("✅ Job elements found - scraper should work")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        logger.exception("Full error details:")
    
    finally:
        if driver:
            driver.quit()
            print("\n🔚 WebDriver closed")

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 LINKEDIN DIRECT ACCESS TEST")
    print("=" * 60)
    test_linkedin_direct()
    print("=" * 60)
