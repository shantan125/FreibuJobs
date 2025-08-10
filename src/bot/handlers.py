"""
Conversation Handlers Module

Professional conversation management for the LinkedIn Job & Internship Bot.
Handles user interactions, state management, and conversation flow.
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
    """Professional conversation handlers for the bot."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.conversation_data = ConversationData()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /start command."""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Clear any existing conversation data
            self.conversation_data.clear_user_data(user_id)
            
            # Create keyboard with job type options
            keyboard = [
                [
                    InlineKeyboardButton("Full-Time Job", callback_data="job"),
                    InlineKeyboardButton("Internship", callback_data="internship")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send welcome message
            welcome_msg = MessageTemplates.welcome_message(user.first_name or "there")
            
            await update.message.reply_text(
                welcome_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"User {user_id} started conversation")
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
            self.logger.info(f"Help command executed for user {update.effective_user.id}")
            
        except Exception as e:
            self.logger.error(f"Error in help_command: {e}")
            await update.message.reply_text(MessageTemplates.error_message())
    
    async def handle_job_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle job type selection callback."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            job_type_str = query.data
            
            # Validate and convert job type
            if job_type_str not in ["job", "internship"]:
                await query.edit_message_text(MessageTemplates.invalid_state_message())
                return ConversationHandler.END
            
            job_type = JobType.JOB if job_type_str == "job" else JobType.INTERNSHIP
            
            # Store job type in conversation data
            self.conversation_data.set_user_data(user_id, "job_type", job_type)
            
            # Send role input prompt
            prompt_msg = MessageTemplates.job_type_prompt(job_type)
            
            await query.edit_message_text(prompt_msg, parse_mode='Markdown')
            
            self.logger.info(f"User {user_id} selected job type: {job_type.value}")
            return ConversationState.ENTERING_ROLE.value
            
        except Exception as e:
            self.logger.error(f"Error in handle_job_type_selection: {e}")
            await query.edit_message_text(MessageTemplates.error_message())
            return ConversationHandler.END
    
    async def handle_role_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle role input from user."""
        try:
            user_id = update.effective_user.id
            role = update.message.text.strip()
            
            if not role:
                await update.message.reply_text(
                    "Please enter a valid role name.",
                    parse_mode='Markdown'
                )
                return ConversationState.ENTERING_ROLE.value
            
            # Get job type from conversation data
            job_type = self.conversation_data.get_user_value(user_id, "job_type")
            if not job_type:
                await update.message.reply_text(MessageTemplates.invalid_state_message())
                return ConversationHandler.END
            
            # Store role in conversation data
            self.conversation_data.set_user_data(user_id, "role", role)
            
            # Send search progress message
            progress_msg = MessageTemplates.search_progress_message(
                role=role,
                job_type=job_type,
                location=self.config.search_config.default_location,
                max_results=self.config.search_config.max_results
            )
            
            await update.message.reply_text(progress_msg, parse_mode='Markdown')
            
            self.logger.info(f"User {user_id} entered role: {role}")
            
            # Immediately trigger the search instead of waiting for another message
            await self.perform_search(update, context, user_id, job_type, role)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error in handle_role_input: {e}")
            await update.message.reply_text(MessageTemplates.error_message())
            return ConversationHandler.END
    
    async def send_progress_update(self, update: Update, message: str) -> None:
        """Send progress update to user."""
        try:
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error sending progress update: {e}")

    async def perform_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, job_type: JobType, role: str) -> None:
        """Perform the actual LinkedIn search with progressive updates."""
        import time  # Import time at the function level to avoid scope issues
        
        try:
            # Step 1: Initialize
            await self.send_progress_update(update, 
                f"**Starting search for {role}**\n\n"
                          )
            
            # Import here to avoid circular imports
            from ..scraper.linkedin import LinkedInScraper
            
            # Create scraper instance
            scraper = LinkedInScraper(self.config)
            
            # Step 2: Configure search parameters
            await self.send_progress_update(update,
                f"**Target Role**: {role}\n"
                f"**Search Type**: {job_type.value.title()}\n"
                f"**Primary Location**: {self.config.search_config.default_location}\n"
            )
            
            # Progressive time search strategy
            time_filters = [
                (self.config.search_config.time_filter, "last 24 hours"),
                (self.config.search_config.time_filter_fallback_2days, "last 2 days"),
                (self.config.search_config.time_filter_fallback_7days, "last 7 days")
            ]
            
            search_query = role
            max_results = self.config.search_config.max_results
            job_urls = []
            
            self.logger.info(f"Starting progressive LinkedIn search for user {user_id}: {role} ({job_type.value})")
            
            # Step 3: Begin search process
            for i, (time_filter, time_description) in enumerate(time_filters, 1):
                try:
                    await self.send_progress_update(update,
                        f"**Step 3/5**: Searching LinkedIn ({i}/3)\n\n"
                        f"**Keywords**: {role}\n"
                    )
                    
                    self.logger.info(f"Searching for {role} in {time_description}")
                    
                    # Choose the appropriate search method based on job type
                    if job_type == JobType.JOB:
                        job_urls = scraper.search_jobs(
                            keyword=search_query, 
                            max_results=max_results,
                            time_filter=time_filter
                        )
                    else:  # INTERNSHIP
                        job_urls = scraper.search_internships(
                            keyword=search_query, 
                            max_results=max_results,
                            time_filter=time_filter
                        )
                    
                    # If we found jobs, break out of the loop
                    if job_urls:
                        await self.send_progress_update(update,
                            f"**Found {len(job_urls)} opportunities!**\n\n"
                            f"**Time Range**: {time_description}\n"
                            f"**Processing results...**"
                        )
                        self.logger.info(f"Found {len(job_urls)} jobs for {role} in {time_description}")
                        break
                    else:
                        await self.send_progress_update(update,
                            f"**No results in {time_description}**\n\n"
                            f"**Expanding search to longer timeframe...**"
                        )
                        self.logger.info(f"No jobs found for {role} in {time_description}, trying longer timeframe")
                        
                except Exception as search_error:
                    self.logger.error(f"Error searching with {time_description}: {search_error}")
                    await self.send_progress_update(update,
                        f"**Search issue with {time_description}**\n\n"
                        f"**Trying alternative timeframe...**"
                    )
                    continue
            
            # Step 4: Process results
            if job_urls:
                await self.send_progress_update(update,
                    f"**Step 4/5**: Processing {len(job_urls)} opportunities\n\n"
                    f"**Categorizing by location...**\n"
                    f"� **Formatting results...**"
                )
                
                # Convert URLs to JobOpportunity objects
                from .messages import MessageFormatter
                
                opportunities = []
                for url in job_urls:
                    try:
                        opportunity = MessageFormatter.create_job_opportunity(url)
                        opportunities.append(opportunity)
                    except Exception as e:
                        self.logger.error(f"Error processing job URL {url}: {e}")
                        continue
                
                # Step 5: Final results
                await self.send_progress_update(update,
                    f"**Step 5/5**: Search complete!\n\n"
                    f"**Found**: {len(opportunities)} {role} opportunities\n"
                    f"📤 **Sending results...**"
                )
                
                # Find which time range was successful
                successful_timeframe = "recent postings"
                for time_filter, time_description in time_filters:
                    if job_urls:
                        successful_timeframe = time_description
                        break
                
                results_msg = MessageTemplates.success_message(
                    role=role,
                    job_type=job_type,
                    location=self.config.search_config.default_location,
                    opportunities=opportunities
                )
                
                # Add timeframe and search details
                enhanced_msg = (
                    results_msg + 
                    f"\n\n**Search Range**: {successful_timeframe}\n"
                    f"🕐 **Search Time**: {time.strftime('%H:%M:%S')}\n"
                    f"**Keywords Used**: {role}\n"
                    f"**Locations Searched**: India → Remote → Global"
                )
                
                await update.message.reply_text(enhanced_msg, parse_mode='Markdown')
                self.logger.info(f"Sent {len(job_urls)} job results to user {user_id} from {successful_timeframe}")
            else:
                # No results found even with 7-day search
                await self.send_progress_update(update,
                    f"**Step 5/5**: Search complete - No results\n\n"
                    f"**Searched all timeframes without success**"
                )
                
                no_results_msg = (
                    f"**No {role} positions found**\n\n"
                    f"**Comprehensive search completed:**\n"
                    f"✓ Last 24 hours\n"
                    f"✓ Last 2 days\n"
                    f"✓ Last 7 days\n\n"
                    f"**Locations searched:**\n"
                    f"✓ {self.config.search_config.default_location}\n"
                    f"✓ Remote positions\n"
                    f"✓ Global opportunities\n\n"
                    f"**Suggestions to improve results:**\n"
                    f"• Try different keywords:\n"
                    f"  - 'Software Developer' instead of 'Java Developer'\n"
                    f"  - 'Backend Developer' instead of 'Java Developer'\n"
                    f"  - 'Full Stack Developer' for broader results\n"
                    f"• Try broader terms like 'Software Engineer'\n"
                    f"• Check back in a few hours - new jobs are posted regularly\n\n"
                    f"**Try again with different keywords using /start**\n"
                    f"**Search completed at**: {time.strftime('%H:%M:%S')}"
                )
                await update.message.reply_text(no_results_msg, parse_mode='Markdown')
                self.logger.info(f"No jobs found for user {user_id} query: {search_query} (tried all timeframes)")
                
        except Exception as e:
            self.logger.error(f"Error performing search for user {user_id}: {e}")
            await update.message.reply_text(
                "**Search Error**\n\n"
                f"Sorry, there was an error performing your search for '{role}'\n\n"
                f"**What happened:**\n"
                f"• Technical issue during LinkedIn search\n"
                f"• This could be temporary\n\n"
                f"**What you can do:**\n"
                f"• Wait 1-2 minutes and try again with /start\n"
                f"• Try different keywords\n"
                f"• The service will be restored automatically\n\n"
                f"**Error time**: {time.strftime('%H:%M:%S')}",
                parse_mode='Markdown'
            )
        finally:
            # Clean up conversation data
            self.clear_conversation_data(user_id)
    
    async def handle_search_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the actual search request."""
        try:
            user_id = update.effective_user.id
            
            # Get conversation data
            job_type = self.conversation_data.get_user_value(user_id, "job_type")
            role = self.conversation_data.get_user_value(user_id, "role")
            
            if not job_type or not role:
                await update.message.reply_text(MessageTemplates.invalid_state_message())
                return ConversationHandler.END
            
            # Store context for the search function to use
            context.user_data.update({
                'job_type': job_type,
                'role': role,
                'user_id': user_id
            })
            
            self.logger.info(f"Initiating search for user {user_id}: {role} ({job_type.value})")
            
            # This will be handled by the search_jobs_and_internships function
            # which is called from the main bot file
            return ConversationState.SEARCHING.value
            
        except Exception as e:
            self.logger.error(f"Error in handle_search_request: {e}")
            await update.message.reply_text(MessageTemplates.error_message())
            return ConversationHandler.END
    
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
            
            self.logger.info(f"Fallback triggered for user {user_id}")
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"Error in handle_fallback: {e}")
            return ConversationHandler.END
    
    def get_conversation_data(self, user_id: int) -> Tuple[Optional[JobType], Optional[str]]:
        """Get conversation data for a user."""
        job_type = self.conversation_data.get_user_value(user_id, "job_type")
        role = self.conversation_data.get_user_value(user_id, "role")
        return job_type, role
    
    def clear_conversation_data(self, user_id: int) -> None:
        """Clear conversation data for a user."""
        self.conversation_data.clear_user_data(user_id)


class ConversationStateManager:
    """Manages conversation states and transitions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_conversation_handler(self, handlers: ConversationHandlers) -> ConversationHandler:
        """Create and configure conversation handler."""
        from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
        
        return ConversationHandler(
            entry_points=[CommandHandler("start", handlers.start_command)],
            states={
                ConversationState.SELECTING_JOB_TYPE.value: [
                    CallbackQueryHandler(
                        handlers.handle_job_type_selection,
                        pattern="^(job|internship)$"
                    )
                ],
                ConversationState.ENTERING_ROLE.value: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handlers.handle_role_input
                    )
                ],
                ConversationState.SEARCHING.value: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handlers.handle_search_request
                    )
                ]
            },
            fallbacks=[
                CommandHandler("start", handlers.start_command),
                MessageHandler(filters.ALL, handlers.handle_fallback)
            ],
            conversation_timeout=300,  # 5 minutes timeout
            per_user=True,
            per_chat=False,
            name="job_search_conversation"
        )
