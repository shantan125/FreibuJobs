"""
Configuration Management Module

Professional configuration handling with validation, type checking, 
and environment variable management for the LinkedIn Job & Internship Bot.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Configuration for bot parameters."""
    telegram_token: str = ""
    
    def __post_init__(self):
        """Initialize telegram token from environment."""
        if not self.telegram_token:
            self.telegram_token = os.getenv("TELEGRAM_TOKEN", "")
            if not self.telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")


@dataclass
class SearchConfig:
    """Configuration for job search parameters."""
    max_results: int = 10
    search_keywords: str = "software intern"
    time_filter: str = "r86400"  # last 24 hours (default)
    time_filter_fallback_2days: str = "r172800"  # last 2 days fallback
    time_filter_fallback_7days: str = "r604800"  # last 7 days fallback
    scroll_count: int = 3
    wait_timeout: int = 15
    default_location: str = "India"
    include_remote: bool = True
    include_global: bool = True


@dataclass
class WebDriverConfig:
    """Configuration for WebDriver parameters."""
    headless: bool = True
    window_size: str = "1920,1080"
    page_load_timeout: int = 30
    implicit_wait: int = 10
    timeout: int = 30
    retry_attempts: int = 3
    chrome_driver_path: Optional[str] = None
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class LoggingConfig:
    """Configuration for logging parameters."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


class ConfigurationManager:
    """
    Professional configuration manager for the LinkedIn Bot.
    
    Handles environment variables, validation, and provides typed configuration objects.
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Path to the environment file
        """
        self.env_file = env_file
        self.project_root = Path(__file__).parent.parent.parent
        self.env_path = self.project_root / env_file
        
        # Load environment variables
        load_dotenv(self.env_path)
        
        # Initialize configurations
        self.telegram_token = self._get_telegram_token()
        self.bot_config = self._create_bot_config()
        self.search_config = self._create_search_config()
        self.webdriver_config = self._create_webdriver_config()
        self.logging_config = self._create_logging_config()
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        self._validate_configuration()
    
    def _get_telegram_token(self) -> Optional[str]:
        """Get and validate Telegram bot token."""
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_TOKEN not found in environment variables")
        
        # Basic token format validation
        if ':' not in token:
            raise ValueError("Invalid Telegram token format")
        
        return token
    
    def _create_bot_config(self) -> BotConfig:
        """Create bot configuration from environment variables."""
        return BotConfig(telegram_token=self.telegram_token)
    
    def _create_search_config(self) -> SearchConfig:
        """Create search configuration from environment variables."""
        return SearchConfig(
            max_results=int(os.getenv('MAX_RESULTS', '10')),
            search_keywords=os.getenv('SEARCH_KEYWORDS', 'software intern'),
            time_filter=os.getenv('TIME_FILTER', 'r86400'),
            scroll_count=int(os.getenv('SCROLL_COUNT', '3')),
            wait_timeout=int(os.getenv('WAIT_TIMEOUT', '15')),
            default_location=os.getenv('DEFAULT_LOCATION', 'India'),
            include_remote=os.getenv('INCLUDE_REMOTE', 'true').lower() == 'true',
            include_global=os.getenv('INCLUDE_GLOBAL', 'true').lower() == 'true'
        )
    
    def _create_webdriver_config(self) -> WebDriverConfig:
        """Create WebDriver configuration from environment variables."""
        return WebDriverConfig(
            headless=os.getenv('HEADLESS', 'true').lower() == 'true',
            window_size=os.getenv('WINDOW_SIZE', '1920,1080'),
            page_load_timeout=int(os.getenv('PAGE_LOAD_TIMEOUT', '30')),
            implicit_wait=int(os.getenv('IMPLICIT_WAIT', '10')),
            timeout=int(os.getenv('DRIVER_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('RETRY_ATTEMPTS', '3')),
            chrome_driver_path=os.getenv('CHROME_DRIVER_PATH'),
            user_agent=os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        )
    
    def _create_logging_config(self) -> LoggingConfig:
        """Create logging configuration from environment variables."""
        return LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO').upper(),
            format=os.getenv('LOG_FORMAT', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file=os.getenv('LOG_FILE', None)
        )
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.logging_config.level, logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=self.logging_config.format,
            force=True
        )
        
        # Add file handler if specified
        if self.logging_config.file:
            log_file_path = self.project_root / self.logging_config.file
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setFormatter(logging.Formatter(self.logging_config.format))
            logging.getLogger().addHandler(file_handler)
    
    def _validate_configuration(self) -> None:
        """Validate all configuration parameters."""
        errors = []
        
        # Validate search config
        if self.search_config.max_results <= 0:
            errors.append("MAX_RESULTS must be greater than 0")
        
        if self.search_config.max_results > 50:
            errors.append("MAX_RESULTS should not exceed 50 for performance reasons")
        
        if self.search_config.wait_timeout <= 0:
            errors.append("WAIT_TIMEOUT must be greater than 0")
        
        # Validate webdriver config
        if self.webdriver_config.timeout <= 0:
            errors.append("DRIVER_TIMEOUT must be greater than 0")
        
        if self.webdriver_config.retry_attempts <= 0:
            errors.append("RETRY_ATTEMPTS must be greater than 0")
        
        # Validate window size format
        try:
            width, height = self.webdriver_config.window_size.split(',')
            int(width)
            int(height)
        except (ValueError, AttributeError):
            errors.append("WINDOW_SIZE must be in format 'width,height' (e.g., '1920,1080')")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        self.logger.info("Configuration validation successful")
    
    def get_env_info(self) -> Dict[str, Any]:
        """Get environment information for debugging."""
        return {
            'env_file': str(self.env_path),
            'env_exists': self.env_path.exists(),
            'project_root': str(self.project_root),
            'telegram_token_configured': bool(self.telegram_token),
            'search_location': self.search_config.default_location,
            'max_results': self.search_config.max_results,
            'log_level': self.logging_config.level
        }
    
    def __repr__(self) -> str:
        """String representation of configuration (hiding sensitive data)."""
        return (
            f"ConfigurationManager("
            f"telegram_token={'*' * 10 if self.telegram_token else 'None'}, "
            f"location={self.search_config.default_location}, "
            f"max_results={self.search_config.max_results})"
        )


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config() -> ConfigurationManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigurationManager: The global configuration instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def setup_logging() -> None:
    """Setup logging for the application."""
    # Logging is setup automatically in ConfigurationManager
    pass


if __name__ == "__main__":
    """Test configuration management."""
    import logging
    
    # Setup basic logging for testing
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🔧 Testing Professional Configuration Management")
    logger.info("=" * 60)
    
    try:
        # Test configuration loading
        config = get_config()
        logger.info(f"✅ Configuration loaded: {config}")
        
        # Test environment info
        env_info = config.get_env_info()
        logger.info("📊 Environment Info:")
        for key, value in env_info.items():
            logger.info(f"   {key}: {value}")
        
        # Test configuration objects
        logger.info(f"\n🔍 Search Config: max_results={config.search_config.max_results}, location={config.search_config.default_location}")
        logger.info(f"🌐 WebDriver Config: headless={config.webdriver_config.headless}, timeout={config.webdriver_config.timeout}")
        logger.info(f"📝 Logging Config: level={config.logging_config.level}")
        
        logger.info("\n✅ Professional configuration management test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}", exc_info=True)
        raise
