"""
Main Bot Module

Professional Telegram bot for LinkedIn Job & Internship search.
Integrates all components for a comprehensive job search experience.
"""

import asyncio
import logging
import os
from typing import Optional, List

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ..utils.config import ConfigurationManager
from ..utils.logging import get_bot_logger, log_function, time_function
from ..scraper.linkedin import LinkedInScraper
from .handlers import ConversationHandlers
from .messages import MessageTemplates, MessageFormatter, JobOpportunity, JobType
from ..health.health_check import HealthCheckServer


class LinkedInJobBot:
    """Main LinkedIn Job & Internship Bot class."""
    
    @log_function
    def __init__(self, config_manager: ConfigurationManager):
        """Initialize the bot with configuration and enhanced logging."""
        self.config = config_manager
        self.bot_logger = get_bot_logger()
        self.logger = self.bot_logger.get_logger('bot.main')
        
        # Initialize components with logging
        self.logger.info("Initializing bot components...")
        self.scraper = LinkedInScraper(config_manager)
        self.conversation_handlers = ConversationHandlers(config_manager)
        
        # Initialize application
        self.application: Optional[Application] = None
        
        # Initialize health check server for Azure
        self.health_server: Optional[HealthCheckServer] = None
        self.health_runner = None
        
        self.logger.info("✅ LinkedIn Job Bot initialized successfully")
    
    @log_function
    def setup_application(self) -> Application:
        """Set up the Telegram application with enhanced logging."""
        try:
            self.logger.info("Setting up Telegram application...")
            
            # Create application
            self.application = Application.builder().token(
                self.config.bot_config.telegram_token
            ).build()
            
            # Add conversation handler
            conversation_handler = self.conversation_handlers.create_conversation_handler()
            self.application.add_handler(conversation_handler)
            
            # Add standalone command handlers
            self.application.add_handler(
                CommandHandler("help", self.conversation_handlers.help_command)
            )
            
            # Add search handler (for handling the actual search after role input)
            self.application.add_handler(
                CommandHandler("search", self.handle_search_command)
            )
            
            self.logger.info("✅ Telegram application configured successfully")
            return self.application
            
        except Exception as e:
            self.logger.error("❌ Failed to setup Telegram application", extra={
                'error_type': type(e).__name__,
                'error_message': str(e)
            }, exc_info=True)
            raise
    
    @log_function 
    async def handle_search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle search command with enhanced logging."""
        user_id = update.effective_user.id if update.effective_user else 0
        
        try:
            self.logger.debug(f"Processing search command for user {user_id}")
            # This is primarily used internally by the conversation flow
            await self.search_jobs_and_internships(update, context)
            
        except Exception as e:
            self.logger.error(f"❌ Error in search command for user {user_id}", extra={
                'user_id': user_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }, exc_info=True)
            await update.message.reply_text(MessageTemplates.error_message())
    
    @time_function
    @log_function
    async def search_jobs_and_internships(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Search for jobs and internships with comprehensive logging and performance monitoring."""
        user_id = update.effective_user.id if update.effective_user else 0
        
        try:
            # Get conversation data
            job_type, role = self.conversation_handlers.get_conversation_data(user_id)
            
            if not job_type or not role:
                self.logger.warning(f"Invalid state for user {user_id}: missing job_type or role")
                await update.message.reply_text(MessageTemplates.invalid_state_message())
                return
            
            # Log search request
            self.bot_logger.log_search_request(
                user_id=user_id,
                keyword=role,
                job_type=job_type.value
            )
            
            self.logger.info(f"🔍 Starting search for user {user_id}", extra={
                'user_id': user_id,
                'role': role,
                'job_type': job_type.value
            })
            
            # Start performance monitoring
            self.bot_logger.performance.start_timer(f"search_{user_id}")
            
            # Perform the search
            job_urls = await self._perform_search(role, job_type, user_id)
            
            search_duration = self.bot_logger.performance.end_timer(f"search_{user_id}")
            
            if job_urls:
                # Convert URLs to job opportunities
                opportunities = [
                    MessageFormatter.create_job_opportunity(url) 
                    for url in job_urls
                ]
                
                # Log successful search results
                self.bot_logger.log_search_results(
                    user_id=user_id,
                    keyword=role,
                    result_count=len(job_urls),
                    tier="multi_tier",
                    duration=search_duration
                )
                
                # Send success message with results
                success_msg = MessageTemplates.success_message(
                    role=role,
                    job_type=job_type,
                    location=self.config.search_config.default_location,
                    opportunities=opportunities
                )
                
                await update.message.reply_text(success_msg, parse_mode='Markdown')
                
                self.logger.info(f"✅ Search completed successfully for user {user_id}", extra={
                    'user_id': user_id,
                    'result_count': len(job_urls),
                    'duration': search_duration
                })
                
            else:
                # Log no results
                self.bot_logger.log_search_results(
                    user_id=user_id,
                    keyword=role,
                    result_count=0,
                    tier="multi_tier",
                    duration=search_duration
                )
                
                # Send no results message
                no_results_msg = MessageTemplates.no_results_message(
                    role=role,
                    location=self.config.search_config.default_location
                )
                
                await update.message.reply_text(no_results_msg, parse_mode='Markdown')
                
                self.logger.info(f"ℹ️ No results found for user {user_id}", extra={
                    'user_id': user_id,
                    'role': role,
                    'duration': search_duration
                })
            
            # Clear conversation data after search
            self.conversation_handlers.clear_conversation_data(user_id)
            
        except Exception as e:
            self.logger.error(f"❌ Error in search for user {user_id}", extra={
                'user_id': user_id,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }, exc_info=True)
            
            await update.message.reply_text(MessageTemplates.error_message())
            
            # Clear conversation data on error
            if update.effective_user:
                self.conversation_handlers.clear_conversation_data(update.effective_user.id)
    
    @time_function
    @log_function
    async def _perform_search(self, role: str, job_type: JobType, user_id: int) -> List[str]:
        """Perform the actual LinkedIn search with enhanced monitoring."""
        try:
            # Determine if searching for internships
            is_internship = job_type == JobType.INTERNSHIP
            
            self.logger.debug(f"Performing search for user {user_id}", extra={
                'user_id': user_id,
                'role': role,
                'is_internship': is_internship,
                'max_results': self.config.search_config.max_results
            })
            
            # Use the scraper to search
            job_urls = await asyncio.to_thread(
                self.scraper.search_for_jobs_and_internships,
                keyword=role,
                is_internship=is_internship,
                max_results=self.config.search_config.max_results
            )
            
            self.logger.info(f"🎯 Search completed for user {user_id}", extra={
                'user_id': user_id,
                'role': role,
                'urls_found': len(job_urls)
            })
            
            return job_urls
            
        except Exception as e:
            self.logger.error(f"❌ Search operation failed for user {user_id}", extra={
                'user_id': user_id,
                'role': role,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }, exc_info=True)
            return []
    
    async def start_bot(self) -> None:
        """Start the bot."""
        try:
            if not self.application:
                self.setup_application()
            
            # Start health check server for Azure Container Apps
            await self._start_health_server()
            
            self.logger.info("Starting LinkedIn Job Bot...")
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            self.logger.info("✅ LinkedIn Job Bot is running!")
            self.logger.info("Press Ctrl+C to stop the bot")
            
            # Keep the bot running using a simple loop
            import signal
            import asyncio
            
            # Create an event to wait for shutdown
            shutdown_event = asyncio.Event()
            
            def signal_handler(signum, frame):
                self.logger.info("Received shutdown signal")
                shutdown_event.set()
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Wait for shutdown signal
            await shutdown_event.wait()
            
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            raise
        finally:
            await self.stop_bot()
    
    async def stop_bot(self) -> None:
        """Stop the bot gracefully."""
        try:
            # Stop health server first
            await self._stop_health_server()
            
            if self.application:
                self.logger.info("Stopping LinkedIn Job Bot...")
                if self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                self.logger.info("✅ Bot stopped gracefully")
                
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    async def _start_health_server(self) -> None:
        """Start health check server for Azure Container Apps."""
        try:
            # Only start health server in production/Azure environments
            if os.getenv("AZURE_ENVIRONMENT") or os.getenv("ENABLE_HEALTH_CHECK", "false").lower() == "true":
                health_port = int(os.getenv("HEALTH_CHECK_PORT", "8080"))
                self.health_server = HealthCheckServer(port=health_port)
                self.health_runner = await self.health_server.start_server()
                self.logger.info(f"Health check server started on port {health_port}")
            else:
                self.logger.info("Health check server disabled (not in Azure environment)")
        except Exception as e:
            self.logger.warning(f"Failed to start health check server: {e}")
    
    async def _stop_health_server(self) -> None:
        """Stop health check server."""
        try:
            if self.health_runner:
                await self.health_runner.cleanup()
                self.logger.info("Health check server stopped")
        except Exception as e:
            self.logger.warning(f"Error stopping health check server: {e}")
    
    def run_bot(self) -> None:
        """Run the bot (synchronous entry point)."""
        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            self.logger.info("Bot execution interrupted")
        except Exception as e:
            self.logger.error(f"Fatal error running bot: {e}")
            raise


async def main() -> None:
    """Main async entry point."""
    try:
        # Initialize configuration
        config_manager = ConfigurationManager()
        config_manager.setup_logging()
        
        # Create and start bot
        bot = LinkedInJobBot(config_manager)
        await bot.start_bot()
        
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
