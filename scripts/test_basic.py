#!/usr/bin/env python3
"""
Simple test runner for the LinkedIn Job Bot

Run basic functionality tests without external dependencies.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("🔍 Testing module imports...")
    
    try:
        from src.utils.config import ConfigurationManager
        from src.bot.messages import MessageTemplates, JobType
        from src.scraper.linkedin import LinkedInScraper
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_message_templates():
    """Test message template functionality."""
    print("🔍 Testing message templates...")
    
    try:
        from src.bot.messages import MessageTemplates, JobType
        
        # Test welcome message
        welcome = MessageTemplates.welcome_message("TestUser")
        assert "TestUser" in welcome
        assert "LinkedIn" in welcome
        
        # Test job prompts
        job_prompt = MessageTemplates.job_type_prompt(JobType.JOB)
        intern_prompt = MessageTemplates.job_type_prompt(JobType.INTERNSHIP)
        
        assert "full-time job" in job_prompt.lower()
        assert "internship" in intern_prompt.lower()
        
        print("✅ Message templates working correctly")
        return True
    except Exception as e:
        print(f"❌ Message template error: {e}")
        return False


def test_configuration():
    """Test configuration management."""
    print("🔍 Testing configuration...")
    
    try:
        from src.utils.config import SearchConfig, WebDriverConfig, LoggingConfig
        
        # Test default configurations
        search_config = SearchConfig()
        assert search_config.default_location == "India"
        assert search_config.max_results == 10
        
        webdriver_config = WebDriverConfig()
        assert webdriver_config.page_load_timeout == 30
        
        logging_config = LoggingConfig()
        assert logging_config.level == "INFO"
        
        print("✅ Configuration management working correctly")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_url_building():
    """Test LinkedIn URL building."""
    print("🔍 Testing URL building...")
    
    try:
        from src.utils.config import SearchConfig, WebDriverConfig, LoggingConfig
        from src.scraper.linkedin import LinkedInScraper
        
        # Mock the configuration for testing
        class MockConfig:
            def __init__(self):
                self.search_config = SearchConfig()
                self.webdriver_config = WebDriverConfig()
                self.logging_config = LoggingConfig()
        
        scraper = LinkedInScraper(MockConfig())
        
        # Test URL building
        url = scraper._build_search_url(
            keyword="Java Developer",
            location="India",
            is_internship=False
        )
        
        assert "linkedin.com/jobs/search" in url
        assert "Java%20Developer" in url
        assert "India" in url
        
        # Test internship URL
        intern_url = scraper._build_search_url(
            keyword="Software Engineer",
            is_internship=True
        )
        
        assert "intern" in intern_url.lower()
        assert "f_JT=I" in intern_url
        
        print("✅ URL building working correctly")
        return True
    except Exception as e:
        print(f"❌ URL building error: {e}")
        return False


def test_message_formatting():
    """Test message formatting utilities."""
    print("🔍 Testing message formatting...")
    
    try:
        from src.bot.messages import MessageFormatter, LocationType
        
        # Test company name extraction
        test_url = "https://linkedin.com/jobs/view/123-at-google-inc-456"
        company = MessageFormatter.extract_company_name(test_url)
        assert isinstance(company, str)
        assert len(company) > 0
        
        # Test location type determination
        india_url = "https://linkedin.com/jobs/view/123?location=bangalore"
        location_type = MessageFormatter.determine_location_type(india_url)
        assert location_type == LocationType.INDIA
        
        remote_url = "https://linkedin.com/jobs/view/123?f_WT=2"
        location_type = MessageFormatter.determine_location_type(remote_url)
        assert location_type == LocationType.REMOTE
        
        print("✅ Message formatting working correctly")
        return True
    except Exception as e:
        print(f"❌ Message formatting error: {e}")
        return False


def run_all_tests():
    """Run all basic tests."""
    print("🧪 LinkedIn Job Bot - Basic Functionality Tests")
    print("=" * 55)
    
    tests = [
        test_imports,
        test_message_templates,
        test_configuration,
        test_url_building,
        test_message_formatting
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 55)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
