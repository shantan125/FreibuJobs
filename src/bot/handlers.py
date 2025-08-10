"""
Conversation Handlers Module

Professional conversation management for the LinkedIn Job & Internship Bot.
Handles user interactions, state management, and conversation flow with real-time streaming.
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum, auto

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from ..utils.config import ConfigurationManager
from .messages import MessageTemplates, JobType


class ConversationState(Enum):
    """Conversation state enumeration."""
    SELECTING_JOB_TYPE = auto()
    ENTERING_ROLE = auto()
    SEARCHING = auto()


class ConversationData:
    """Manages conversation data for users."""
    
    def __init__(self):
        self._user_data: Dict[int, Dict[str, Any]] = {}
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data, creating if not exists."""
        if user_id not in self._user_data:
            self._user_data[user_id] = {}
        return self._user_data[user_id]
    
    def set_user_data(self, user_id: int, key: str, value: Any) -> None:
        """Set user data."""
        user_data = self.get_user_data(user_id)
        user_data[key] = value
    
    def get_user_value(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get specific user value."""
        user_data = self.get_user_data(user_id)
        return user_data.get(key, default)
    
    def clear_user_data(self, user_id: int) -> None:
        """Clear user data."""
        if user_id in self._user_data:
            del self._user_data[user_id]


class ConversationHandlers:
    """Professional conversation handlers for the LinkedIn bot."""

    def __init__(self, config: ConfigurationManager):
        """Initialize conversation handlers."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.conversation_data = ConversationData()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /start command."""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Clear any existing conversation data
            self.conversation_data.clear_user_data(user_id)
            
            # Create job type selection keyboard
            keyboard = [
                [InlineKeyboardButton("Full-time Job", callback_data="job_full_time")],
                [InlineKeyboardButton("Internship", callback_data="job_internship")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_msg = MessageTemplates.welcome_message(user.first_name or "there")
            
            await update.message.reply_text(
                welcome_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Started conversation with user {user_id} ({user.username or 'no username'})")
            
            return ConversationState.SELECTING_JOB_TYPE.value
            
        except Exception as e:
            self.logger.error(f"Error in start_command: {e}")
            await update.message.reply_text(MessageTemplates.error_message())
            return ConversationHandler.END

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        try:
            help_msg = MessageTemplates.help_message(
                location=self.config.search_config.default_location,
                max_results=self.config.search_config.max_results
            )
            
            await update.message.reply_text(help_msg, parse_mode='Markdown')
            
            self.logger.info(f"Sent help message to user {update.effective_user.id}")
            
        except Exception as e:
            self.logger.error(f"Error in help_command: {e}")
            await update.message.reply_text(MessageTemplates.error_message())

    async def job_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle job type selection."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            
            # Parse job type
            if query.data == "job_full_time":
                job_type = JobType.JOB
            elif query.data == "job_internship":
                job_type = JobType.INTERNSHIP
            else:
                await query.edit_message_text("Invalid selection. Please use /start to try again.")
                return ConversationHandler.END
            
            # Store job type
            self.conversation_data.set_user_data(user_id, "job_type", job_type)
            
            # Send role prompt
            role_prompt = MessageTemplates.job_type_prompt(job_type)
            await query.edit_message_text(role_prompt, parse_mode='Markdown')
            
            self.logger.info(f"User {user_id} selected job type: {job_type.value}")
            
            return ConversationState.ENTERING_ROLE.value
            
        except Exception as e:
            self.logger.error(f"Error in job_type_selection: {e}")
            await update.callback_query.edit_message_text(MessageTemplates.error_message())
            return ConversationHandler.END

    async def role_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle role input and initiate search."""
        try:
            user_id = update.effective_user.id
            role = update.message.text.strip()
            
            # Validate role input
            if not role or len(role.strip()) < 3:
                await update.message.reply_text(
                    "**Please enter a valid role**\n\n"
                    "The role name should be at least 3 characters.\n\n"
                    "**Examples**: Java Developer, Python Developer, Software Engineer",
                    parse_mode='Markdown'
                )
                return ConversationState.ENTERING_ROLE.value
            
            # Store role
            self.conversation_data.set_user_data(user_id, "role", role)
            
            # Get job type
            job_type = self.conversation_data.get_user_value(user_id, "job_type")
            
            if not job_type:
                await update.message.reply_text(MessageTemplates.invalid_state_message())
                return ConversationHandler.END
            
            self.logger.info(f"User {user_id} entered role: {role} for {job_type.value}")
            
            # Start search immediately
            await self.perform_search(update, context, user_id, job_type, role)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error in role_input: {e}")
            await update.message.reply_text(MessageTemplates.error_message())
            return ConversationHandler.END

    async def perform_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, job_type: JobType, role: str) -> None:
        """Perform the actual LinkedIn search with real-time streaming updates."""
        try:
            self.logger.info(f"🔍 PERFORM_SEARCH CALLED - User: {user_id}, Type: {job_type.value}, Role: {role}")
            
            # Step 1: Initialize
            await self.send_progress_update(update, 
                f"**Starting search for {role}**\n\n"
                f"**I'll send you jobs immediately as I find them!**"
            )
            
            # Import here to avoid circular imports
            from ..scraper.linkedin import LinkedInScraper
            
            # Create scraper instance
            scraper = LinkedInScraper(self.config)
            
            # Step 2: Configure search parameters
            await self.send_progress_update(update,
                f"**Target Role**: {role}\n"
                f"**Search Type**: {job_type.value.title()}\n"
                f"**Strategy**: India → Remote → Global\n"
                f"**Searching LinkedIn now...**"
            )
            
            search_query = role
            max_results = self.config.search_config.max_results
            found_count = 0
            
            self.logger.info(f"Starting streaming LinkedIn search for user {user_id}: {role} ({job_type.value})")
            
            # Real-time job callback function
            async def job_found_callback(job_url: str):
                nonlocal found_count
                found_count += 1
                
                self.logger.info(f"🚀 STREAMING JOB CALLBACK #{found_count}: {job_url}")
                
                # Send job immediately using the enhanced message format
                job_message = MessageTemplates.format_single_job_message(
                    job_url=job_url,
                    role=role,
                    job_number=found_count
                )
                
                await update.message.reply_text(
                    job_message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                
                self.logger.info(f"✅ SENT STREAMING JOB {found_count} to user {user_id}")
            
            # Step 3: Begin TRUE real-time streaming search
            try:
                self.logger.info(f"🎯 STARTING STREAMING SEARCH - Type: {job_type.value}")
                
                # Choose the appropriate search method based on job type
                if job_type == JobType.JOB:
                    self.logger.info("📋 Using search_jobs_streaming method")
                    # Use TRUE streaming method - jobs sent immediately as found
                    job_urls = await scraper.search_jobs_streaming(
                        keyword=search_query, 
                        max_results=max_results,
                        time_filter=self.config.search_config.time_filter,
                        job_callback=job_found_callback  # Real-time streaming callback
                    )
                else:  # INTERNSHIP
                    self.logger.info("🎓 Using search_internships_streaming method")
                    # Use TRUE streaming method - internships sent immediately as found
                    job_urls = await scraper.search_internships_streaming(
                        keyword=search_query, 
                        max_results=max_results,
                        time_filter=self.config.search_config.time_filter,
                        job_callback=job_found_callback  # Real-time streaming callback
                    )
                
                # Note: Jobs are already sent via job_found_callback during the search
                # The job_urls list contains all found URLs for logging purposes
                
                # Step 4: Send completion message only (no job summary)
                total_found = len(job_urls)
                self.logger.info(f"📊 SEARCH COMPLETED - Total URLs returned: {total_found}, Jobs sent via callback: {found_count}")
                
                if total_found > 0:
                    await update.message.reply_text(
                        f"✅ **Search Complete!**\n\n"
                        f"📊 **Total Found**: {total_found} {role} opportunities\n"
                        f"🔍 **Search Strategy**: India → Remote → Global\n\n"
                        f"💼 **Good luck with your applications!**\n"
                        f"🔄 **Use /start to search for different roles**",
                        parse_mode='Markdown'
                    )
                    self.logger.info(f"Completed streaming search for user {user_id}: {total_found} jobs sent individually")
                else:
                    # No results found
                    no_results_msg = (
                        f"**No {role} positions found**\n\n"
                        f"**Comprehensive search completed:**\n"
                        f"✓ India locations (Bangalore, Mumbai, Delhi, etc.)\n"
                        f"✓ Remote positions suitable for India\n"
                        f"✓ Global opportunities\n\n"
                        f"**Suggestions to improve results:**\n"
                        f"• Try different keywords:\n"
                        f"  - 'Software Developer' instead of '{role}'\n"
                        f"  - 'Backend Developer' or 'Frontend Developer'\n"
                        f"  - 'Full Stack Developer' for broader results\n"
                        f"• Try broader terms like 'Software Engineer'\n"
                        f"• Check back in a few hours - new jobs are posted regularly\n\n"
                        f"**Try again with different keywords using /start**"
                    )
                    
                    await update.message.reply_text(no_results_msg, parse_mode='Markdown')
                    self.logger.info(f"No results found for user {user_id}: {role}")
                        
            except Exception as search_error:
                self.logger.error(f"Error in streaming search: {search_error}")
                await update.message.reply_text(
                    f"**Search Error**\n\n"
                    f"**There was an issue while searching for {role}**\n\n"
                    f"**Please try again with /start**\n"
                    f"If the problem persists, the service might be temporarily unavailable.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error in perform_search: {e}")
            await update.message.reply_text(
                f"**Oops! Something went wrong**\n\n"
                "There was a technical issue while searching.\n\n"
                f"**Please try again with /start**\n"
                "If the problem persists, the service might be temporarily unavailable.",
                parse_mode='Markdown'
            )
        finally:
            # Clear search state
            self.clear_conversation_data(user_id)
    
    async def send_progress_update(self, update: Update, message: str) -> None:
        """Send progress update to user."""
        try:
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error sending progress update: {e}")
    
    def clear_conversation_data(self, user_id: int) -> None:
        """Clear all conversation data for a user."""
        try:
            self.conversation_data.clear_user_data(user_id)
            self.logger.debug(f"Cleared conversation data for user {user_id}")
        except Exception as e:
            self.logger.error(f"Error clearing conversation data for user {user_id}: {e}")
    
    async def handle_timeout(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle conversation timeout."""
        try:
            await update.effective_message.reply_text(
                "**Conversation timed out**\n\n"
                "Please use /start to begin a new search.",
                parse_mode='Markdown'
            )
            
            user_id = update.effective_user.id
            self.conversation_data.clear_user_data(user_id)
            
            self.logger.info(f"Conversation timeout for user {user_id}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error in handle_timeout: {e}")
            return ConversationHandler.END
    
    async def handle_fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle fallback for unexpected messages."""
        try:
            await update.message.reply_text(
                "I didn't understand that. Please use /start to begin a new search.",
                parse_mode='Markdown'
            )
            
            user_id = update.effective_user.id
            self.conversation_data.clear_user_data(user_id)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error in handle_fallback: {e}")
            return ConversationHandler.END

    def create_conversation_handler(self) -> ConversationHandler:
        """Create and return the conversation handler."""
        from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
        
        return ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                ConversationState.SELECTING_JOB_TYPE.value: [
                    CallbackQueryHandler(self.job_type_selection, pattern="^job_(full_time|internship)$")
                ],
                ConversationState.ENTERING_ROLE.value: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.role_input)
                ],
                ConversationState.SEARCHING.value: [
                    # This state is handled programmatically, no user input expected
                ]
            },
            fallbacks=[
                CommandHandler("start", self.start_command),
                MessageHandler(filters.ALL, self.handle_fallback)
            ],
            conversation_timeout=300,  # 5 minutes timeout
            name="job_search_conversation"
        )
