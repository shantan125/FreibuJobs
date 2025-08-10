"""
LinkedIn Scraper Module

Professional LinkedIn scraping functionality for job and internship search.
Implements multi-tier search strategy with India-first approach and true real-time streaming.
"""

import time
import asyncio
import logging
from typing import List, Optional, Set, Callable
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from ..utils.config import ConfigurationManager
from ..utils.logging import get_bot_logger, log_function, time_function


class LinkedInScraper:
    """
    Professional LinkedIn scraper with real-time streaming capabilities.
    
    Features:
    - Multi-tier search strategy (India-first approach)
    - Real-time job streaming with immediate callbacks
    - Robust error handling and retry mechanisms
    - Rate limiting and anti-detection measures
    """
    
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the LinkedIn scraper with configuration."""
        self.config = config_manager
        self.logger = get_bot_logger(__name__)
        self.driver = None
        self.is_logged_in = False
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with optimal configuration for LinkedIn scraping."""
        try:
            chrome_options = Options()
            
            # Performance and stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # Anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent to appear more legitimate
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Headless mode for production
            if self.config.scraper_config.headless:
                chrome_options.add_argument("--headless")
            
            # Window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Create service
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Additional anti-detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            raise WebDriverException(f"Driver setup failed: {e}")

    def _get_driver(self) -> webdriver.Chrome:
        """Get or create a WebDriver instance."""
        if not self.driver:
            self.driver = self._setup_driver()
        return self.driver

    def _close_driver(self) -> None:
        """Safely close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")

    async def _extract_job_urls_streaming(self, driver: webdriver.Chrome, 
                                        job_callback: Optional[Callable] = None,
                                        all_found_urls: Optional[Set[str]] = None,
                                        max_results: int = 10) -> List[str]:
        """
        Extract job URLs with real-time streaming - sends each job immediately when found.
        
        Args:
            driver: WebDriver instance
            job_callback: Async callback function to call for each job found
            all_found_urls: Set to track already found URLs (avoid duplicates)
            max_results: Maximum number of jobs to find
            
        Returns:
            List of job URLs found
        """
        job_urls = []
        found_count = 0
        
        if all_found_urls is None:
            all_found_urls = set()
            
        try:
            # Wait for job listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list"))
            )
            
            # Find all job links on the current page
            job_elements = driver.find_elements(By.CSS_SELECTOR, "a[data-control-name='job_card_click']")
            
            self.logger.info(f"Found {len(job_elements)} job elements on page")
            
            for job_element in job_elements:
                if found_count >= max_results:
                    break
                    
                try:
                    job_url = job_element.get_attribute("href")
                    if job_url and job_url not in all_found_urls:
                        # Clean the URL
                        if "?" in job_url:
                            job_url = job_url.split("?")[0]
                        
                        # Add to tracking sets
                        all_found_urls.add(job_url)
                        job_urls.append(job_url)
                        found_count += 1
                        
                        self.logger.info(f"Found job {found_count}: {job_url}")
                        
                        # REAL-TIME STREAMING: Send job immediately via callback
                        if job_callback:
                            try:
                                await job_callback(job_url)
                                # Small delay to avoid overwhelming the user interface
                                await asyncio.sleep(0.3)
                            except Exception as callback_error:
                                self.logger.error(f"Error in streaming callback: {callback_error}")
                        
                except Exception as e:
                    self.logger.error(f"Error extracting job URL: {e}")
                    continue
            
            # Try to load more jobs by scrolling if we need more results
            if found_count < max_results:
                try:
                    # Scroll to load more jobs
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2)  # Wait for potential lazy loading
                    
                    # Look for "Show more jobs" button
                    try:
                        show_more_button = driver.find_element(
                            By.CSS_SELECTOR, 
                            "button[aria-label*='Show more jobs'], .infinite-scroller__show-more-button"
                        )
                        if show_more_button.is_enabled():
                            driver.execute_script("arguments[0].click();", show_more_button)
                            await asyncio.sleep(3)  # Wait for new jobs to load
                            
                            # Recursively extract more jobs
                            additional_urls = await self._extract_job_urls_streaming(
                                driver, job_callback, all_found_urls, max_results - found_count
                            )
                            job_urls.extend(additional_urls)
                            
                    except Exception:
                        self.logger.info("No 'Show more jobs' button found or not clickable")
                        
                except Exception as scroll_error:
                    self.logger.error(f"Error during scrolling: {scroll_error}")
            
        except TimeoutException:
            self.logger.error("Timeout waiting for job listings to load")
        except Exception as e:
            self.logger.error(f"Error extracting job URLs: {e}")
            
        return job_urls

    def _build_search_url(self, keyword: str, location: str = "", 
                         is_internship: bool = False, time_filter: str = "r86400") -> str:
        """Build LinkedIn job search URL with specified parameters."""
        base_url = "https://www.linkedin.com/jobs/search"
        
        params = []
        
        # Add keyword
        if keyword:
            params.append(f"keywords={keyword.replace(' ', '%20')}")
        
        # Add location
        if location:
            params.append(f"location={location.replace(' ', '%20').replace(',', '%2C')}")
        
        # Add time filter (default: last 24 hours)
        params.append(f"f_TPR={time_filter}")
        
        # Add experience level for internships
        if is_internship:
            params.append("f_E=1")  # Internship level
        
        # Sort by most recent
        params.append("sortBy=DD")
        
        # Combine all parameters
        if params:
            full_url = f"{base_url}?{'&'.join(params)}"
        else:
            full_url = base_url
            
        self.logger.info(f"Built search URL: {full_url}")
        return full_url

    async def _search_jobs_by_criteria_streaming(self, keyword: str, location: str = "", 
                                               is_internship: bool = False, 
                                               max_results: int = 10,
                                               time_filter: str = "r86400",
                                               job_callback: Optional[Callable] = None,
                                               all_found_urls: Optional[Set[str]] = None) -> List[str]:
        """
        Search for jobs by specific criteria with real-time streaming.
        
        This method performs the actual web scraping and streams results in real-time.
        """
        job_urls = []
        
        if all_found_urls is None:
            all_found_urls = set()
        
        driver = None
        try:
            driver = self._get_driver()
            
            # Build and navigate to search URL
            search_url = self._build_search_url(keyword, location, is_internship, time_filter)
            driver.get(search_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Extract job URLs with streaming
            job_urls = await self._extract_job_urls_streaming(
                driver, job_callback, all_found_urls, max_results
            )
            
            self.logger.info(f"Found {len(job_urls)} jobs for '{keyword}' in '{location}'")
            
        except Exception as e:
            self.logger.error(f"Error in job search: {e}")
        
        return job_urls

    async def search_jobs_streaming(self, keyword: str, max_results: int = 10, 
                                  time_filter: str = "r86400", 
                                  job_callback: Optional[Callable] = None) -> List[str]:
        """
        Search for jobs with real-time streaming - sends each job immediately when found.
        
        Args:
            keyword: Job search keyword (e.g., "Java Developer")
            max_results: Maximum number of jobs to find
            time_filter: Time filter for job posting date
            job_callback: Async callback function called for each job found
            
        Returns:
            List of all job URLs found
        """
        return await self._streaming_search(
            keyword=keyword,
            is_internship=False,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )

    async def search_internships_streaming(self, keyword: str, max_results: int = 10, 
                                         time_filter: str = "r86400", 
                                         job_callback: Optional[Callable] = None) -> List[str]:
        """
        Search for internships with real-time streaming - sends each job immediately when found.
        
        Args:
            keyword: Internship search keyword (e.g., "Software Engineering")
            max_results: Maximum number of internships to find
            time_filter: Time filter for posting date
            job_callback: Async callback function called for each internship found
            
        Returns:
            List of all internship URLs found
        """
        return await self._streaming_search(
            keyword=keyword,
            is_internship=True,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )

    async def _streaming_search(self, keyword: str, is_internship: bool, max_results: int,
                              time_filter: str, job_callback: Optional[Callable] = None) -> List[str]:
        """
        Core streaming search implementation with multi-tier strategy.
        
        Strategy:
        1. India-specific locations (primary tier)
        2. Remote jobs suitable for India (secondary tier)
        3. Global opportunities (fallback tier)
        
        Each job is sent immediately via callback as it's discovered.
        """
        all_job_urls: List[str] = []
        all_found_urls: Set[str] = set()
        found_count = 0
        
        try:
            job_type = "internship" if is_internship else "job"
            self.logger.info(f"Starting real-time streaming search for '{keyword}' ({job_type})")
            
            # Tier 1: India-specific locations with immediate streaming
            india_locations = [
                "India",
                "Bangalore, India", 
                "Mumbai, India",
                "Delhi, India",
                "Hyderabad, India",
                "Pune, India",
                "Chennai, India",
                "Kolkata, India"
            ]
            
            for location in india_locations:
                if found_count >= max_results:
                    break
                
                self.logger.info(f"Streaming search in {location}...")
                
                # Calculate remaining results needed
                remaining_results = max_results - found_count
                
                # Perform streaming search for this location
                location_urls = await self._search_jobs_by_criteria_streaming(
                    keyword=keyword,
                    location=location,
                    is_internship=is_internship,
                    max_results=remaining_results,
                    time_filter=time_filter,
                    job_callback=job_callback,
                    all_found_urls=all_found_urls
                )
                
                # Track new unique jobs
                for job_url in location_urls:
                    if job_url not in all_found_urls:
                        all_job_urls.append(job_url)
                        all_found_urls.add(job_url)
                        found_count += 1
                
                # Rate limiting between locations to avoid being blocked
                if found_count < max_results:
                    await asyncio.sleep(2)
            
            # Tier 2: Remote positions if we need more results
            if found_count < max_results:
                self.logger.info("Searching for remote positions...")
                
                remote_locations = ["Remote", "Work from Home"]
                
                for remote_location in remote_locations:
                    if found_count >= max_results:
                        break
                    
                    remaining_results = max_results - found_count
                    
                    remote_urls = await self._search_jobs_by_criteria_streaming(
                        keyword=keyword,
                        location=remote_location,
                        is_internship=is_internship,
                        max_results=remaining_results,
                        time_filter=time_filter,
                        job_callback=job_callback,
                        all_found_urls=all_found_urls
                    )
                    
                    # Track new unique jobs
                    for job_url in remote_urls:
                        if job_url not in all_found_urls:
                            all_job_urls.append(job_url)
                            all_found_urls.add(job_url)
                            found_count += 1
                    
                    await asyncio.sleep(2)
            
            # Tier 3: Global search without location filter (fallback)
            if found_count < max_results:
                self.logger.info("Performing global search as fallback...")
                
                remaining_results = max_results - found_count
                
                global_urls = await self._search_jobs_by_criteria_streaming(
                    keyword=keyword,
                    location="",  # No location filter
                    is_internship=is_internship,
                    max_results=remaining_results,
                    time_filter=time_filter,
                    job_callback=job_callback,
                    all_found_urls=all_found_urls
                )
                
                # Track new unique jobs
                for job_url in global_urls:
                    if job_url not in all_found_urls:
                        all_job_urls.append(job_url)
                        all_found_urls.add(job_url)
                        found_count += 1
            
            self.logger.info(f"Streaming search completed: {found_count} {job_type}s found for '{keyword}'")
            
        except Exception as e:
            self.logger.error(f"Error in streaming search: {e}")
        finally:
            # Clean up resources
            self._close_driver()
        
        return all_job_urls

    # Non-streaming methods (legacy support)
    def search_jobs(self, keyword: str, max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """Non-streaming job search (legacy method)."""
        return self.search_for_jobs_and_internships(keyword, False, max_results, time_filter)

    def search_internships(self, keyword: str, max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """Non-streaming internship search (legacy method)."""
        return self.search_for_jobs_and_internships(keyword, True, max_results, time_filter)

    def search_for_jobs_and_internships(self, keyword: str, is_internship: bool = False,
                                      max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """
        Legacy non-streaming search method for backward compatibility.
        """
        try:
            # Run the async streaming method synchronously (without callback)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self._streaming_search(
                    keyword=keyword,
                    is_internship=is_internship,
                    max_results=max_results,
                    time_filter=time_filter,
                    job_callback=None  # No streaming callback
                )
            )
            
            loop.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Error in legacy search: {e}")
            return []

    def __del__(self):
        """Cleanup on object destruction."""
        self._close_driver()
