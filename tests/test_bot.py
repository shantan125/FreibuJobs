"""
Test Suite for LinkedIn Job & Internship Bot

Professional test cases for all major components.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import ConfigurationManager, BotConfig, SearchConfig
from src.bot.messages import MessageTemplates, JobType, MessageFormatter, LocationType
from src.scraper.linkedin import LinkedInScraper


class TestConfigurationManager(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        self.config_manager = ConfigurationManager()
    
    def test_bot_config_creation(self):
        """Test bot configuration creation."""
        # Mock environment variable
        with patch.dict('os.environ', {'TELEGRAM_TOKEN': 'test_token'}):
            config = BotConfig()
            self.assertEqual(config.telegram_token, 'test_token')
    
    def test_search_config_defaults(self):
        """Test search configuration defaults."""
        config = SearchConfig()
        self.assertEqual(config.default_location, 'India')
        self.assertEqual(config.max_results, 10)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # This would test environment variable validation
        # Implementation depends on actual validation logic
        pass


class TestMessageTemplates(unittest.TestCase):
    """Test message template functionality."""
    
    def test_welcome_message(self):
        """Test welcome message generation."""
        message = MessageTemplates.welcome_message("TestUser")
        self.assertIn("TestUser", message)
        self.assertIn("LinkedIn Job & Internship Finder", message)
    
    def test_job_type_prompt(self):
        """Test job type prompt messages."""
        job_prompt = MessageTemplates.job_type_prompt(JobType.JOB)
        internship_prompt = MessageTemplates.job_type_prompt(JobType.INTERNSHIP)
        
        self.assertIn("full-time job", job_prompt)
        self.assertIn("internship", internship_prompt)
        self.assertIn("Java Developer", job_prompt)
        self.assertIn("Software Engineering Intern", internship_prompt)
    
    def test_search_progress_message(self):
        """Test search progress message."""
        message = MessageTemplates.search_progress_message(
            role="Java Developer",
            job_type=JobType.JOB,
            location="India",
            max_results=10
        )
        
        self.assertIn("Java Developer", message)
        self.assertIn("Job", message)
        self.assertIn("India", message)
        self.assertIn("10", message)


class TestMessageFormatter(unittest.TestCase):
    """Test message formatting utilities."""
    
    def test_extract_company_name(self):
        """Test company name extraction from URLs."""
        url = "https://www.linkedin.com/jobs/view/1234567890?refId=123&-at-google-inc-456"
        company = MessageFormatter.extract_company_name(url)
        self.assertIsInstance(company, str)
        self.assertNotEqual(company, "")
    
    def test_determine_location_type(self):
        """Test location type determination."""
        # Test India location
        india_url = "https://linkedin.com/jobs/view/123?location=bangalore"
        self.assertEqual(
            MessageFormatter.determine_location_type(india_url),
            LocationType.INDIA
        )
        
        # Test remote location
        remote_url = "https://linkedin.com/jobs/view/123?f_WT=2"
        self.assertEqual(
            MessageFormatter.determine_location_type(remote_url),
            LocationType.REMOTE
        )
        
        # Test global location
        global_url = "https://linkedin.com/jobs/view/123?location=newyork"
        self.assertEqual(
            MessageFormatter.determine_location_type(global_url),
            LocationType.GLOBAL
        )

    def test_extract_job_details_contract(self):
        """extractJobDetails should return a dict with company/title/location keys."""
        import asyncio
        url = "https://www.linkedin.com/jobs/view/123456"
        details = asyncio.get_event_loop().run_until_complete(
            MessageFormatter.extractJobDetails(url)
        )
        self.assertIn("company", details)
        self.assertIn("title", details)
        self.assertIn("location", details)
        self.assertIsInstance(details["company"], str)


class TestLinkedInScraperMethods(unittest.TestCase):
    """Test LinkedIn scraper methods (without actual web requests)."""
    
    def setUp(self):
        self.config_manager = ConfigurationManager()
        self.scraper = LinkedInScraper(self.config_manager)
    
    def test_build_search_url(self):
        """Test URL building for LinkedIn search."""
        url = self.scraper._build_search_url(
            keyword="Java Developer",
            location="India",
            is_internship=False
        )
        
        self.assertIn("Java%20Developer", url)
        self.assertIn("India", url)
        self.assertIn("linkedin.com/jobs/search", url)
    
    def test_build_internship_search_url(self):
        """Test URL building for internship search."""
        url = self.scraper._build_search_url(
            keyword="Software Engineer",
            location="Mumbai",
            is_internship=True
        )
        
        self.assertIn("Software%20Engineer%20intern", url)
        self.assertIn("Mumbai", url)
        self.assertIn("f_JT=I", url)  # Internship filter


class TestBotIntegration(unittest.IsolatedAsyncioTestCase):
    """Test bot integration components."""
    
    async def test_conversation_flow_simulation(self):
        """Simulate conversation flow without actual Telegram."""
        # This would test conversation handlers with mock Update objects
        # Implementation depends on actual handler structure
        pass
    
    async def test_search_functionality_mock(self):
        """Test search functionality with mocked scraper."""
        config_manager = ConfigurationManager()
        
        # Mock the scraper to return test data
        with patch('src.scraper.linkedin.LinkedInScraper') as mock_scraper:
            mock_instance = mock_scraper.return_value
            mock_instance.search_for_jobs_and_internships.return_value = [
                "https://linkedin.com/jobs/view/1",
                "https://linkedin.com/jobs/view/2"
            ]
            
            # Test would call the bot's search method here
            # and verify proper handling of results
            pass


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""
    
    def test_invalid_configuration(self):
        """Test handling of invalid configuration."""
        # Test missing required environment variables
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(Exception):
                config = BotConfig()
    
    def test_scraper_error_handling(self):
        """Test scraper error handling."""
        config_manager = ConfigurationManager()
        scraper = LinkedInScraper(config_manager)
        
        # Test with invalid parameters
        result = scraper.search_for_jobs_and_internships("", max_results=0)
        self.assertEqual(result, [])


def run_tests():
    """Run all tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running LinkedIn Job Bot Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
