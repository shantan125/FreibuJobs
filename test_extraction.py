#!/usr/bin/env python3
"""
Test the actual URL extraction from LinkedIn
"""

import os
import sys
sys.path.insert(0, "src")

from src.utils.config import ConfigurationManager
from src.scraper.linkedin import LinkedInScraper

def test_url_extraction():
    """Test actual URL extraction to see what's happening"""
    try:
        config = ConfigurationManager()
        scraper = LinkedInScraper(config)
        
        print("🔍 Testing URL extraction for Java Developer...")
        
        # Test the exact search that's failing
        results = scraper.search_jobs(
            keyword="Java Developer",
            max_results=5,
            time_filter="r604800"  # 7 days
        )
        
        print(f"📊 Results: {len(results)} URLs found")
        
        if results:
            print("✅ URLs found:")
            for i, url in enumerate(results, 1):
                print(f"{i}. {url}")
        else:
            print("❌ No URLs extracted - this is the core issue!")
            print("🔧 The page has job-search-card elements but URL extraction is failing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_extraction()
