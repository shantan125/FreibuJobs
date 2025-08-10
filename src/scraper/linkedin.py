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
from webdriver_manager.chrome import ChromeDriverManager

from ..utils.config import ConfigurationManager
from ..utils.logging import get_bot_logger, log_function, time_function 
                                   time_filter: str = "r86400", job_callback=None) -> List[str]:
        """Search for jobs with real-time streaming - sends each job immediately when found."""
        return await self._streaming_search(
            keyword=keyword,
            is_internship=False,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )
    
    async def search_internships_streaming(self, keyword: str, max_results: int = 10, 
                                         time_filter: str = "r86400", job_callback=None) -> List[str]:
        """Search for internships with real-time streaming - sends each job immediately when found."""
        return await self._streaming_search(
            keyword=keyword,
            is_internship=True,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )
    
    async def _streaming_search(self, keyword: str, is_internship: bool, max_results: int,
                              time_filter: str, job_callback=None) -> List[str]:
        """
        Real-time streaming search that sends jobs immediately as they're found.
        """
        import asyncio
        
        all_job_urls: List[str] = []
        found_count = 0
        
        try:
            self.logger.info(f"Starting streaming search for '{keyword}' "
                           f"({'internship' if is_internship else 'job'})")
            
            # Tier 1: India-specific locations with immediate streaming
            india_locations = [
                "India",
                "Bangalore, India", 
                "Mumbai, India",
                "Delhi, India",
                "Hyderabad, India",
                "Pune, India"
            ]
            
            for location in india_locations:
                if found_count >= max_results:
                    break
                
                self.logger.info(f"Searching in {location}...")
                
                # Get jobs for this location
                location_urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    location=location,
                    is_internship=is_internship,
                    max_results=max_results,
                    time_filter=time_filter
                )
                
                # Stream each job immediately
                for job_url in location_urls:
                    if job_url not in all_job_urls and found_count < max_results:
                        all_job_urls.append(job_url)
                        found_count += 1
                        
                        # Send job immediately via callback
                        if job_callback:
                            try:
                                await job_callback(job_url)
                                # Small delay to avoid overwhelming the user
                                await asyncio.sleep(0.5)
                            except Exception as callback_error:
                                self.logger.error(f"Error in job callback: {callback_error}")
                
                # Rate limiting between locations
                await asyncio.sleep(1)
            
            # Tier 2: Remote positions (if we need more results)
            if found_count < max_results:
                self.logger.info("Searching remote positions...")
                
                remote_urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    work_type="2",  # Remote work type
                    is_internship=is_internship,
                    max_results=max_results,
                    time_filter=time_filter
                )
                
                # Stream remote jobs immediately
                for job_url in remote_urls:
                    if job_url not in all_job_urls and found_count < max_results:
                        all_job_urls.append(job_url)
                        found_count += 1
                        
                        if job_callback:
                            try:
                                await job_callback(job_url)
                                await asyncio.sleep(0.5)
                            except Exception as callback_error:
                                self.logger.error(f"Error in job callback: {callback_error}")
                
                await asyncio.sleep(1)
            
            # Tier 3: Global search as fallback (if still need more)
            if found_count < max_results:
                self.logger.info("Searching global opportunities...")
                
                global_urls = self._search_jobs_by_criteria(
                    keyword=keyword,
                    is_internship=is_internship,
                    max_results=max_results,
                    time_filter=time_filter
                )
                
                # Stream global jobs immediately
                for job_url in global_urls:
                    if job_url not in all_job_urls and found_count < max_results:
                        all_job_urls.append(job_url)
                        found_count += 1
                        
                        if job_callback:
                            try:
                                await job_callback(job_url)
                                await asyncio.sleep(0.5)
                            except Exception as callback_error:
                                self.logger.error(f"Error in job callback: {callback_error}")
            
            self.logger.info(f"Streaming search completed: {found_count} jobs found and sent for '{keyword}'")
            
            return all_job_urls
            
        except Exception as e:
            self.logger.error(f"Error in streaming search: {e}")
            return all_job_urls
        
        finally:
            # Always close driver after search
            self._close_driver()

    def search_for_jobs_and_internships(self, keyword: str, is_internship: bool = False, 
                                      max_results: int = 10, time_filter: str = "r86400") -> List[str]:og_function, time_function


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
        """Set up Chrome WebDriver with optimal configuration using webdriver-manager."""
        import os
        import platform
        
        try:
            chrome_options = Options()
            
            # Add Chrome options for stability and performance (Linux-optimized)
            chrome_options.add_argument("--headless")  # Run in background without opening window
            chrome_options.add_argument("--no-sandbox")  # Critical for Docker/Azure
            chrome_options.add_argument("--disable-dev-shm-usage")  # Critical for container environments
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
            chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            
            # Platform-specific options
            current_platform = platform.system().lower()
            if current_platform == "linux":
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--disable-background-networking")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument("--disable-sync")
                chrome_options.add_argument("--metrics-recording-only")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--single-process")  # For container environments
            
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set preferences to avoid popups and notifications
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 2  # Block images for faster loading
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Set user agent
            chrome_options.add_argument(
                f"--user-agent={self.config.webdriver_config.user_agent}"
            )
            
            # Window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Use webdriver-manager to automatically handle ChromeDriver installation and version matching
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Setting up ChromeDriver using webdriver-manager (attempt {attempt + 1}) on {current_platform}")
                    
                    # Use ChromeDriverManager to automatically download and manage ChromeDriver
                    driver_path = ChromeDriverManager().install()
                    self.logger.info(f"ChromeDriver downloaded to: {driver_path}")
                    
                    # Cross-platform path fixing
                    if "THIRD_PARTY_NOTICES" in driver_path:
                        # Extract the directory and find the actual chromedriver
                        driver_dir = os.path.dirname(driver_path)
                        
                        # Try different possible executable names based on platform
                        possible_names = []
                        if current_platform == "windows":
                            possible_names = ["chromedriver.exe", "chromedriver"]
                        else:  # Linux/Mac
                            possible_names = ["chromedriver", "google-chrome-stable", "chromium-browser"]
                        
                        for exe_name in possible_names:
                            actual_driver_path = os.path.join(driver_dir, exe_name)
                            if os.path.exists(actual_driver_path):
                                driver_path = actual_driver_path
                                self.logger.info(f"Fixed driver path to: {driver_path}")
                                break
                        else:
                            # Look for chromedriver in parent directory structure
                            parent_dir = os.path.dirname(driver_dir)
                            for exe_name in possible_names:
                                actual_driver_path = os.path.join(parent_dir, exe_name)
                                if os.path.exists(actual_driver_path):
                                    driver_path = actual_driver_path
                                    self.logger.info(f"Found driver in parent dir: {driver_path}")
                                    break
                    
                    # Make executable on Linux/Mac
                    if current_platform != "windows" and os.path.exists(driver_path):
                        os.chmod(driver_path, 0o755)
                        self.logger.info(f"Made driver executable: {driver_path}")
                    
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                    # Test if driver is working
                    driver.get("data:,")  # Simple test page
                    self.logger.info(f"✅ Chrome WebDriver initialized successfully on {current_platform}")
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
            self.logger.info(f"Starting job extraction from page: {driver.current_url}")
            
            # Wait for job listings to load with updated selector
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list .job-search-card, .base-search-card, .job-result-card"))
                )
                self.logger.info("Job cards found on page")
            except TimeoutException:
                self.logger.warning("Timeout waiting for job cards - trying alternative selectors")
                # Try with more generic selectors
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-entity-urn*='job'], .job-card, .result-card"))
                    )
                    self.logger.info("Alternative job elements found")
                except TimeoutException:
                    self.logger.error("No job elements found on page")
                    # Still continue to try extraction
            
            # Try multiple selectors to find job links (updated for current LinkedIn structure)
            selectors_to_try = [
                "a[href*='/jobs/view/']",  # Direct URL pattern match (most reliable)
                ".job-search-card a",  # Any link within job search cards
                ".base-search-card a[href*='/jobs/view/']",  # Base card job links
                ".job-result-card a[href*='/jobs/view/']",  # Result card job links
                "[data-entity-urn*='job'] a",  # Entity-based job links
                ".job-card a[href*='/jobs/view/']",  # Job card links
                ".result-card a[href*='/jobs/view/']",  # Generic result card links
                "h3 a[href*='/jobs/view/']",  # Job title links
                ".job-title a",  # Job title links
                ".job-search-card__link",  # Original selector as fallback
            ]
            
            for selector in selectors_to_try:
                try:
                    job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Trying selector '{selector}': found {len(job_elements)} elements")
                    
                    for element in job_elements:
                        try:
                            href = element.get_attribute('href')
                            if href and '/jobs/view/' in href:
                                # Clean up the URL (remove tracking parameters)
                                clean_url = href.split('?')[0] if '?' in href else href
                                if clean_url not in job_urls:
                                    job_urls.append(clean_url)
                                    self.logger.debug(f"Found job URL: {clean_url}")
                        except Exception as e:
                            self.logger.debug(f"Error extracting URL from element: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Error with selector '{selector}': {e}")
                    continue
                
                # Stop if we found a good number of URLs
                if len(job_urls) >= 10:  # Don't need to try all selectors if we found enough
                    break
            
            self.logger.info(f"Found {len(job_urls)} direct job URLs")
            
            # If no direct links found, extract job info from cards (fallback strategy)
            if not job_urls:
                self.logger.info("No direct job URLs found, extracting job info from cards")
                
                # Try multiple card selectors
                card_selectors = [
                    ".jobs-search__results-list .job-search-card",
                    ".base-search-card",
                    ".job-result-card",
                    ".job-card",
                    "[data-entity-urn*='job']"
                ]
                
                job_cards = []
                for card_selector in card_selectors:
                    try:
                        cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
                        if cards:
                            job_cards = cards
                            self.logger.info(f"Found {len(cards)} job cards using selector: {card_selector}")
                            break
                    except Exception as e:
                        self.logger.debug(f"Card selector '{card_selector}' failed: {e}")
                        continue
                
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
            self.logger.info(f"Starting search for: {keyword}, location: {location}, type: {'internship' if is_internship else 'job'}")
            driver = self._get_driver()
            self.logger.info("WebDriver initialized successfully")
            
            # Build search URL (no login required for job search)
            search_url = self._build_search_url(
                keyword=keyword,
                location=location,
                work_type=work_type,
                is_internship=is_internship,
                time_filter=time_filter
            )
            
            self.logger.info(f"Built search URL: {search_url}")
            
            # Navigate to search page
            self.logger.info("Navigating to LinkedIn search page...")
            driver.get(search_url)
            self.logger.info(f"Successfully navigated to: {driver.current_url}")
            time.sleep(5)  # Allow page to load
            
            # Log page title for debugging
            page_title = driver.title
            self.logger.info(f"Page title: {page_title}")
            
            # Check if we're on the right page or redirected
            if "jobs" not in driver.current_url.lower() and "jobs" not in page_title.lower():
                self.logger.warning(f"Possible redirect detected. Current URL: {driver.current_url}, Title: {page_title}")
            
            # Extract jobs from multiple pages if needed
            pages_checked = 0
            max_pages = 3  # Limit to first 3 pages
            
            while len(job_urls) < max_results and pages_checked < max_pages:
                self.logger.info(f"Extracting jobs from page {pages_checked + 1}")
                
                # Extract URLs from current page
                page_urls = self._extract_job_urls(driver)
                self.logger.info(f"Extracted {len(page_urls)} job entries from page {pages_checked + 1}")
                
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
                            self.logger.info(f"Going to page {pages_checked + 1}")
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                        else:
                            self.logger.info("Next button disabled, no more pages")
                            break
                    except Exception:
                        self.logger.info("No next page button found or failed to click")
                        break  # No more pages
            
            search_type = f"{location} {work_type}".strip()
            if is_internship:
                search_type += " internships"
            else:
                search_type += " jobs"
            
            self.logger.info(f"Search completed: Found {len(job_urls)} {search_type} for '{keyword}'")
            
        except Exception as e:
            self.logger.error(f"Error searching jobs by criteria: {e}", exc_info=True)
        
        return job_urls[:max_results]
    
    def _login_to_linkedin(self, driver: webdriver.Chrome) -> bool:
        """Login to LinkedIn for better access to job results."""
        try:
            self.logger.info("Attempting to login to LinkedIn...")
            
            # Navigate to LinkedIn login page
            driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Find email and password fields
            email_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Enter credentials
            email_field.clear()
            email_field.send_keys(self.config.linkedin_config.email)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(self.config.linkedin_config.password)
            time.sleep(1)
            
            # Click login button
            login_button.click()
            time.sleep(5)  # Wait for login to complete
            
            # Check if login was successful
            current_url = driver.current_url
            if "feed" in current_url or "linkedin.com" in current_url and "login" not in current_url:
                self.logger.info("✅ LinkedIn login successful")
                return True
            else:
                self.logger.warning(f"Login may have failed, current URL: {current_url}")
                return False
                
        except Exception as e:
            self.logger.error(f"LinkedIn login failed: {e}")
            return False
    
    async def search_for_jobs_and_internships_streaming(self, keyword: str, is_internship: bool = False,
                                      max_results: int = 10, time_filter: str = "r86400", 
                                      job_callback=None) -> List[str]:
        """
        Search for jobs and internships with real-time streaming.
        Calls job_callback immediately when each job is found.
        
        Strategy:
        1. India-focused search (specific cities)
        2. Remote jobs suitable for India
        3. Global opportunities as fallback
        """
        all_job_urls: Set[str] = set()
        
        try:
            self.logger.info(f"Starting streaming search for '{keyword}' "
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
                
                urls = await self._search_jobs_by_criteria_streaming(
                    keyword=keyword,
                    location=location,
                    is_internship=is_internship,
                    max_results=max_results // 2,  # Get some from each source
                    time_filter=time_filter,
                    job_callback=job_callback,
                    all_found_urls=all_job_urls
                )
                
                all_job_urls.update(urls)
                time.sleep(2)  # Rate limiting
            
            # Tier 2: Remote positions (if we need more results)
            if len(all_job_urls) < max_results:
                remote_urls = await self._search_jobs_by_criteria_streaming(
                    keyword=keyword,
                    work_type="2",  # Remote work type
                    is_internship=is_internship,
                    max_results=max_results // 3,
                    time_filter=time_filter,
                    job_callback=job_callback,
                    all_found_urls=all_job_urls
                )
                
                all_job_urls.update(remote_urls)
                time.sleep(2)
            
            # Tier 3: Global search as fallback (if still need more)
            if len(all_job_urls) < max_results:
                global_urls = await self._search_jobs_by_criteria_streaming(
                    keyword=keyword,
                    is_internship=is_internship,
                    max_results=max_results // 4,
                    time_filter=time_filter,
                    job_callback=job_callback,
                    all_found_urls=all_job_urls
                )
                
                all_job_urls.update(global_urls)
            
            # Convert to list and limit results
            final_urls = list(all_job_urls)[:max_results]
            
            self.logger.info(f"Streaming search completed: {len(final_urls)} total URLs for '{keyword}'")
            
            return final_urls
            
        except Exception as e:
            self.logger.error(f"Error in streaming search: {e}")
            return []
        
        finally:
            # Always close driver after search
            self._close_driver()

    async def search_jobs_streaming(self, keyword: str, max_results: int = 10, 
                                  time_filter: str = "r86400", job_callback=None) -> List[str]:
        """Search for full-time jobs with streaming updates."""
        return await self.search_for_jobs_and_internships_streaming(
            keyword=keyword,
            is_internship=False,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )
    
    async def search_internships_streaming(self, keyword: str, max_results: int = 10, 
                                         time_filter: str = "r86400", job_callback=None) -> List[str]:
        """Search for internships with streaming updates."""
        return await self.search_for_jobs_and_internships_streaming(
            keyword=keyword,
            is_internship=True,
            max_results=max_results,
            time_filter=time_filter,
            job_callback=job_callback
        )

    async def _search_jobs_by_criteria_streaming(self, keyword: str, location: str = "", 
                               work_type: str = "", is_internship: bool = False,
                               max_results: int = 10, time_filter: str = "r86400",
                               job_callback=None, all_found_urls=None) -> List[str]:
        """Search jobs by specific criteria with streaming updates."""
        job_urls = []
        driver = None
        
        try:
            self.logger.info(f"Starting streaming search for: {keyword}, location: {location}, type: {'internship' if is_internship else 'job'}")
            driver = self._get_driver()
            self.logger.info("WebDriver initialized successfully")
            
            # Build search URL (no login required for job search)
            search_url = self._build_search_url(
                keyword=keyword,
                location=location,
                work_type=work_type,
                is_internship=is_internship,
                time_filter=time_filter
            )
            
            self.logger.info(f"Built search URL: {search_url}")
            
            # Navigate to search page
            self.logger.info("Navigating to LinkedIn search page...")
            driver.get(search_url)
            self.logger.info(f"Successfully navigated to: {driver.current_url}")
            time.sleep(5)  # Allow page to load
            
            # Log page title for debugging
            page_title = driver.title
            self.logger.info(f"Page title: {page_title}")
            
            # Check if we're on the right page or redirected
            if "jobs" not in driver.current_url.lower() and "jobs" not in page_title.lower():
                self.logger.warning(f"Possible redirect detected. Current URL: {driver.current_url}, Title: {page_title}")
            
            # Extract jobs from multiple pages if needed with streaming
            pages_checked = 0
            max_pages = 3  # Limit to first 3 pages
            
            while len(job_urls) < max_results and pages_checked < max_pages:
                self.logger.info(f"Extracting jobs from page {pages_checked + 1}")
                
                # Extract URLs from current page with streaming callback
                page_urls = await self._extract_job_urls_streaming(driver, job_callback, all_found_urls)
                self.logger.info(f"Extracted {len(page_urls)} job entries from page {pages_checked + 1}")
                
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
                            self.logger.info(f"Going to page {pages_checked + 1}")
                            driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                        else:
                            self.logger.info("Next button disabled, no more pages")
                            break
                    except Exception:
                        self.logger.info("No next page button found or failed to click")
                        break  # No more pages
            
            search_type = f"{location} {work_type}".strip()
            if is_internship:
                search_type += " internships"
            else:
                search_type += " jobs"
            
            self.logger.info(f"Streaming search completed: Found {len(job_urls)} {search_type} for '{keyword}'")
            
            return job_urls
            
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn: {e}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    async def _extract_job_urls_streaming(self, driver, job_callback=None, all_found_urls=None) -> List[str]:
        """Extract job URLs from the current page with streaming callbacks."""
        job_urls = []
        
        try:
            # Wait for job listings to load
            job_containers = driver.find_elements(
                By.CSS_SELECTOR, 
                "div[data-entity-urn*='jobPosting']"
            )
            
            if not job_containers:
                # Fallback selector
                job_containers = driver.find_elements(
                    By.CSS_SELECTOR, 
                    ".job-search-card, .jobs-search__results-list li"
                )
            
            self.logger.info(f"Found {len(job_containers)} job containers")
            
            for container in job_containers:
                try:
                    # Try multiple methods to extract job URL
                    job_url = None
                    
                    # Method 1: Look for job title link
                    job_link = container.find_element(
                        By.CSS_SELECTOR, 
                        "h3 a, .job-card-list__title a, .job-search-card__title a"
                    )
                    if job_link:
                        job_url = job_link.get_attribute('href')
                    
                    if job_url and 'linkedin.com/jobs/view' in job_url:
                        # Clean URL
                        clean_url = job_url.split('?')[0]
                        
                        # Check if we already found this URL
                        if all_found_urls is None or clean_url not in all_found_urls:
                            job_urls.append(clean_url)
                            
                            # Add to global set if provided
                            if all_found_urls is not None:
                                all_found_urls.add(clean_url)
                            
                            # Call streaming callback immediately
                            if job_callback:
                                await job_callback(clean_url)
                        
                except Exception as e:
                    self.logger.debug(f"Error extracting URL from job container: {e}")
                    continue
            
            return job_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting job URLs: {e}")
            return []
    
    def search_for_jobs_and_internships(self, keyword: str, is_internship: bool = False,
                                      max_results: int = 10, time_filter: str = "r86400") -> List[str]:
        """
        Search for jobs and internships with multi-tier strategy (non-streaming version).
        
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
