"""
Professional LinkedIn Job & Internship Bot

A comprehensive Telegram bot for searching LinkedIn jobs and internships
with India-focused results and interactive user experience.

Features:
- Interactive job/internship selection
- India-prioritized search with global fallback
- Professional code architecture
- Comprehensive error handling and logging
- Advanced performance monitoring
- No LinkedIn login required

Usage:
    python main.py
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.config import ConfigurationManager
from src.utils.logging import setup_logging, get_bot_logger, log_function, time_function
from src.bot.main import LinkedInJobBot


@log_function
def setup_project_logging() -> None:
    """Set up comprehensive project logging with performance monitoring."""
    # Get logging configuration from environment or use defaults
    import os
    
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/linkedin_bot.log')
    structured_logging = os.getenv('STRUCTURED_LOGGING', 'false').lower() == 'true'
    
    # Setup enhanced logging
    bot_logger = setup_logging(
        log_level=log_level,
        log_file=log_file, 
        structured_logging=structured_logging
    )
    
    # Log system information for debugging
    bot_logger.log_system_info()
    
    logger = bot_logger.get_logger(__name__)
    logger.info("Project logging initialized with enhanced features")
    logger.info(f"Log level: {log_level}, Structured: {structured_logging}, File: {log_file}")


@time_function
@log_function
async def main() -> None:
    """Main application entry point with comprehensive logging and monitoring."""
    bot_logger = get_bot_logger()
    logger = bot_logger.get_logger(__name__)
    
    try:
        logger.info("🚀 Starting LinkedIn Job & Internship Bot")
        bot_logger.performance.start_timer("bot_startup")
        
        # Initialize configuration manager
        logger.info("Initializing configuration manager...")
        config_manager = ConfigurationManager()
        
        logger.info("✅ Configuration loaded successfully", extra={
            'default_location': config_manager.search_config.default_location,
            'max_results': config_manager.search_config.max_results,
            'headless_mode': config_manager.webdriver_config.headless,
            'log_level': config_manager.logging_config.level
        })
        
        # Create and start the bot
        logger.info("Creating LinkedIn Job Bot instance...")
        bot = LinkedInJobBot(config_manager)
        
        bot_logger.performance.end_timer("bot_startup")
        logger.info("🎯 Bot initialization completed, starting main loop...")
        
        # Start the bot with performance monitoring
        bot_logger.performance.start_timer("bot_runtime")
        await bot.start_bot()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
        bot_logger.performance.end_timer("bot_runtime")
    except Exception as e:
        logger.error("💥 Fatal error occurred during bot execution", extra={
            'error_type': type(e).__name__,
            'error_message': str(e)
        }, exc_info=True)
        
        bot_logger.log_error_with_context(e, {
            'context': 'main_execution',
            'phase': 'startup_or_runtime'
        })
        raise
    finally:
        logger.info("🔄 Bot shutdown process completed")


@log_function
def run_bot() -> None:
    """
    Synchronous entry point for running the bot.
    
    Sets up logging and runs the async main function with proper
    error handling and performance monitoring.
    """
    try:
        # Setup enhanced logging first
        setup_project_logging()
        
        # Run the async bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger = get_bot_logger().get_logger(__name__)
        logger.info("Bot execution interrupted by user")
        
    except Exception as e:
        # Fallback logging if enhanced logging fails
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Critical failure in bot execution: {e}", exc_info=True)
        
        try:
            bot_logger = get_bot_logger()
            bot_logger.log_error_with_context(e, {
                'context': 'run_bot',
                'phase': 'main_entry_point'
            })
        except:
            pass  # Logging system failure, can't log the error
        
        raise


if __name__ == "__main__":
    run_bot()
