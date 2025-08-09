"""
LinkedIn Scraper Module

Professional LinkedIn scraping functionality for job and internship search.
Implements multi-tier search strategy with India-first approach.
"""

import time
import logging
from typing import List, Optional, Set
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..utils.config import ConfigurationManager
from ..utils.logging import get_bot_logger, log_function, time_function


class LinkedInScraper:
    """Professional LinkedIn scraper with advanced search capabilities."""
    
    @log_function
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the scraper with enhanced logging and configuration."""
        self.config = config_manager
        self.bot_logger = get_bot_logger()
        self.logger = self.bot_logger.get_logger('scraper.linkedin')
        self.driver: Optional[webdriver.Chrome] = None
        
        self.logger.info("✅ LinkedIn Scraper initialized with enhanced logging")
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with optimal configuration."""
        try:
            chrome_options = Options()
            
            # Add Chrome options for stability and performance
            chrome_options.add_argument("--headless")  # Run in background without opening window
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-images")  # Load faster, less detection
            chrome_options.add_argument("--disable-javascript")  # Avoid JS-based detection
            chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set preferences to avoid popups and notifications
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                    "images": 2,  # Block images for faster loading
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Set user agent
            chrome_options.add_argument(
                f"--user-agent={self.config.webdriver_config.user_agent}"
            )
            
            # Window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Try to create service with ChromeDriver path if specified
            service = None
            if self.config.webdriver_config.chrome_driver_path:
                try:
                    service = Service(self.config.webdriver_config.chrome_driver_path)
                    self.logger.info(f"Using specified ChromeDriver: {self.config.webdriver_config.chrome_driver_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to use specified ChromeDriver path: {e}")
            
            # Create driver with better error handling
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if service:
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        driver = webdriver.Chrome(options=chrome_options)
                    
                    # Test if driver is working
                    driver.get("data:,")  # Simple test page
                    self.logger.info("✅ Chrome WebDriver initialized successfully")
                    break
                    
                except Exception as e:
                    self.logger.warning(f"WebDriver attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise Exception(f"Failed to initialize WebDriver after {max_retries} attempts: {e}")
                    import time
                    time.sleep(2)  # Wait before retry
            
            # Hide webdriver flag and set navigator properties
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # Set timeouts
            driver.implicitly_wait(self.config.webdriver_config.implicit_wait)
            driver.set_page_load_timeout(self.config.webdriver_config.page_load_timeout)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            raise
    
    def _get_driver(self) -> webdriver.Chrome:
        """Get or create WebDriver instance."""
        if not self.driver:
            self.driver = self._setup_driver()
        return self.driver
    
    def _close_driver(self) -> None:
        """Close WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
    
    def _extract_job_urls(self, driver: webdriver.Chrome) -> List[str]:
        """Extract job URLs from current page, with fallback to job info."""
        job_urls = []
        
        try:
            # Wait for job listings to load with updated selector
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list .job-search-card"))
            )
            
            # Try multiple selectors to find job links
            selectors_to_try = [
                ".job-search-card__link",  # Main job card links
                ".jobs-search-card__link",  # Alternative job card links
                "a[href*='/jobs/view/']",  # Direct URL pattern match
                ".job-search-card h3 a",  # Job title links within cards
                ".base-search-card__title a"  # Base card title links
            ]
            
            for selector in selectors_to_try:
                if job_urls:  # Stop if we found URLs
                    break
                    
                try:
                    job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.debug(f"Trying selector '{selector}': found {len(job_elements)} elements")
                    
                    for element in job_elements:
                        try:
                            href = element.get_attribute('href')
                            if href and '/jobs/view/' in href and href not in job_urls:
                                job_urls.append(href)
                        except Exception as e:
                            self.logger.debug(f"Error extracting URL from element: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Error with selector '{selector}': {e}")
                    continue
            
            # If no direct links found, extract job info from cards (fallback strategy)
            if not job_urls:
                self.logger.info("No direct job URLs found, extracting job info from cards")
                job_cards = driver.find_elements(By.CSS_SELECTOR, ".jobs-search__results-list .job-search-card")
                
                for i, card in enumerate(job_cards[:10]):  # Limit to first 10 cards
                    try:
                        # Extract job title
                        title_selectors = ["h3", ".job-search-card__title", ".base-search-card__title", "h4", "h2"]
                        title = "Unknown Position"
                        for title_sel in title_selectors:
                            try:
                                title_elem = card.find_element(By.CSS_SELECTOR, title_sel)
                                if title_elem and title_elem.text.strip():
                                    title = title_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        # Extract company name  
                        company_selectors = [
                            ".hidden-nested-link", 
                            ".job-search-card__subtitle",
                            ".base-search-card__subtitle",
                            "h4",
                            "[data-entity-urn*='company']"
                        ]
                        company = "Unknown Company"
                        for comp_sel in company_selectors:
                            try:
                                company_elem = card.find_element(By.CSS_SELECTOR, comp_sel)
                                if company_elem and company_elem.text.strip():
                                    company = company_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        # Extract location if available
                        location_selectors = [
                            ".job-search-card__location",
                            ".base-search-card__metadata",
                            "[data-test-id*='location']"
                        ]
                        location = ""
                        for loc_sel in location_selectors:
                            try:
                                location_elem = card.find_element(By.CSS_SELECTOR, loc_sel)
                                if location_elem and location_elem.text.strip():
                                    location = location_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        # Create a structured job info string instead of URL
                        job_info = f"TITLE: {title} | COMPANY: {company}"
                        if location:
                            job_info += f" | LOCATION: {location}"
                        
                        job_urls.append(job_info)
                        
                    except Exception as e:
                        self.logger.debug(f"Error extracting job info from card {i}: {e}")
                        continue
            
            self.logger.info(f"Extracted {len(job_urls)} job entries from current page")
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for job listings to load")
        except Exception as e:
            self.logger.error(f"Error extracting job URLs: {e}")
        
        return job_urls
    
    def _build_search_url(self, keyword: str, location: str = "", 
                         time_filter: str = "r86400", work_type: str = "", 
                         is_internship: bool = False) -> str:
        """Build LinkedIn job search URL with parameters."""
        base_url = "https://www.linkedin.com/jobs/search/"
        
        # Prepare search parameters
        params = []
        
        # Keyword processing
        if is_internship and "intern" not in keyword.lower():
            keyword = f"{keyword} intern"
        
        params.append(f"keywords={keyword.replace(' ', '%20')}")
        
        # Location
        if location:
            params.append(f"location={location.replace(' ', '%20')}")
        
        # Time filter (default: last 24 hours)
        params.append(f"f_TPR={time_filter}")
        
        # Work type filter
        if work_type:
            params.append(f"f_WT={work_type}")
        
        # Job type filter for internships
        if is_internship:
            params.append("f_JT=I")  # Internship filter
        
        # Sort by date
        params.append("sortBy=DD")
        
        # Build final URL
        url = f"{base_url}?{'&'.join(params)}"
        
        self.logger.debug(f"Built search URL: {url}")
        return url
    
    def _search_jobs_by_criteria(self, keyword: str, location: str = "", 
                               work_type: str = "", is_internship: bool = False,
                               max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """Search jobs by specific criteria."""
        job_urls = []
        driver = None
        
        try:
            driver = self._get_driver()
            
            # Build search URL
            search_url = self._build_search_url(
                keyword=keyword,
                location=location,
                work_type=work_type,
                is_internship=is_internship,
                time_filter=time_filter
            )
            
            # Navigate to search page
            driver.get(search_url)
            time.sleep(3)  # Allow page to load
            
            # Extract jobs from multiple pages if needed
            pages_checked = 0
            max_pages = 3  # Limit to first 3 pages
            
            while len(job_urls) < max_results and pages_checked < max_pages:
                # Extract URLs from current page
                page_urls = self._extract_job_urls(driver)
                
                # Add new URLs
                for url in page_urls:
                    if url not in job_urls:
                        job_urls.append(url)
                        if len(job_urls) >= max_results:
                            break
                
                pages_checked += 1
                
                # Try to go to next page if we need more results
                if len(job_urls) < max_results and pages_checked < max_pages:
                    try:
                        next_button = driver.find_element(
                            By.CSS_SELECTOR, 
                            "button[aria-label='View next page']"
                        )
                        if next_button.is_enabled():
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                        else:
                            break
                    except Exception:
                        break  # No more pages
            
            search_type = f"{location} {work_type}".strip()
            if is_internship:
                search_type += " internships"
            else:
                search_type += " jobs"
            
            self.logger.info(f"Found {len(job_urls)} {search_type} for '{keyword}'")
            
        except Exception as e:
            self.logger.error(f"Error searching jobs by criteria: {e}")
        
        return job_urls[:max_results]
    
    def search_for_jobs_and_internships(self, keyword: str, is_internship: bool = False,
                                      max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """
        Search for jobs and internships with multi-tier strategy.
        
        Strategy:
        1. India-focused search (specific cities)
        2. Remote jobs suitable for India
        3. Global opportunities as fallback
        """
        all_job_urls: Set[str] = set()
        
        try:
            self.logger.info(f"Starting comprehensive search for '{keyword}' "
                           f"({'internship' if is_internship else 'job'})")
            
            # Tier 1: India-specific locations
            india_locations = [
                "India",
                "Bangalore, India", 
                "Mumbai, India",
                "Delhi, India",
                "Hyderabad, India",
                "Pune, India"
            ]
            
            for location in india_locations:
                if len(all_job_urls) >= max_results:
                    break
                
                urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    location=location,
                    is_internship=is_internship,
                    max_results=max_results // 2,  # Get some from each source
                    time_filter=time_filter
                )
                
                all_job_urls.update(urls)
                time.sleep(2)  # Rate limiting
            
            # Tier 2: Remote positions (if we need more results)
            if len(all_job_urls) < max_results:
                remote_urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    work_type="2",  # Remote work type
                    is_internship=is_internship,
                    max_results=max_results // 3,
                    time_filter=time_filter
                )
                
                all_job_urls.update(remote_urls)
                time.sleep(2)
            
            # Tier 3: Global search as fallback (if still need more)
            if len(all_job_urls) < max_results:
                global_urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    is_internship=is_internship,
                    max_results=max_results // 4,
                    time_filter=time_filter
                )
                
                all_job_urls.update(global_urls)
            
            # Convert to list and limit results
            final_urls = list(all_job_urls)[:max_results]
            
            self.logger.info(f"Comprehensive search completed: {len(final_urls)} total URLs for '{keyword}'")
            
            return final_urls
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive search: {e}")
            return []
        
        finally:
            # Always close driver after search
            self._close_driver()
    
    def search_jobs(self, keyword: str, max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """Search for full-time jobs with progressive time filtering."""
        return self.search_for_jobs_and_internships(
            keyword=keyword,
            is_internship=False,
            max_results=max_results,
            time_filter=time_filter
        )
    
    def search_internships(self, keyword: str, max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """Search for internships with progressive time filtering."""
        return self.search_for_jobs_and_internships(
            keyword=keyword,
            is_internship=True,
            max_results=max_results,
            time_filter=time_filter
        )
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self._close_driver()
