#!/usr/bin/env python3
"""
Debug script to test LinkedIn scraping directly
"""

import os
import logging
from src.utils.config import ConfigurationManager
from src.scraper.linkedin import LinkedInScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_search():
    """Test the LinkedIn search functionality"""
    try:
        # Initialize configuration
        config = ConfigurationManager()
        
        # Create scraper
        scraper = LinkedInScraper(config)
        
        # Test search
        print("🔍 Testing Java Developer search...")
        results = scraper.search_jobs(
            keyword="Java Developer",
            max_results=5,
            time_filter="r604800"  # 7 days
        )
        
        print(f"✅ Found {len(results)} results:")
        for i, url in enumerate(results, 1):
            print(f"{i}. {url}")
        
        if not results:
            print("❌ No results found - this indicates the issue")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        logging.exception("Full error details:")

if __name__ == "__main__":
    test_search()
