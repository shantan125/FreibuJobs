#!/usr/bin/env python3
"""
Local LinkedIn Scraper Test

Test LinkedIn scraping functionality locally to debug issues.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import ConfigurationManager
from src.scraper.linkedin import LinkedInScraper

def setup_logging():
    """Setup detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('test_linkedin.log')
        ]
    )

def test_basic_search():
    """Test basic LinkedIn search functionality."""
    print("🚀 Starting local LinkedIn scraper test...")
    
    try:
        # Initialize configuration
        config_manager = ConfigurationManager()
        
        # Create scraper
        scraper = LinkedInScraper(config_manager)
        
        # Test search
        print("\n🔍 Testing search for 'Java Developer'...")
        job_urls = scraper.search_jobs(
            keyword="Java Developer",
            max_results=5,
            time_filter="r86400"  # Last 24 hours
        )
        
        print(f"\n📊 Results:")
        print(f"Found {len(job_urls)} job entries")
        
        if job_urls:
            print("\n📋 Job entries found:")
            for i, url in enumerate(job_urls[:3], 1):  # Show first 3
                print(f"{i}. {url[:100]}...")
        else:
            print("❌ No job entries found")
            
            # Try a broader search
            print("\n🔄 Trying broader search...")
            job_urls = scraper.search_jobs(
                keyword="Software Developer",
                max_results=5,
                time_filter="r604800"  # Last 7 days
            )
            
            print(f"Broader search found {len(job_urls)} job entries")
            if job_urls:
                for i, url in enumerate(job_urls[:2], 1):
                    print(f"{i}. {url[:100]}...")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_internship_search():
    """Test internship search functionality."""
    print("\n🎓 Testing internship search...")
    
    try:
        config_manager = ConfigurationManager()
        scraper = LinkedInScraper(config_manager)
        
        internship_urls = scraper.search_internships(
            keyword="Software Engineering",
            max_results=3,
            time_filter="r86400"
        )
        
        print(f"Found {len(internship_urls)} internship entries")
        
        if internship_urls:
            for i, url in enumerate(internship_urls, 1):
                print(f"{i}. {url[:100]}...")
                
    except Exception as e:
        print(f"❌ Internship test failed: {e}")

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    print("=" * 60)
    print("🔧 LOCAL LINKEDIN SCRAPER DEBUG TEST")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("LINKEDIN_EMAIL"):
            print("✅ LinkedIn email configured")
        else:
            print("❌ LinkedIn email not configured")
            
        if os.getenv("TELEGRAM_TOKEN"):
            print("✅ Telegram token configured")
        else:
            print("❌ Telegram token not configured")
    else:
        print("❌ .env file not found")
    
    # Run tests
    test_basic_search()
    test_internship_search()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed! Check 'test_linkedin.log' for detailed logs.")
    print("=" * 60)
