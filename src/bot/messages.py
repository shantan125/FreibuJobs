"""
Message Templates Module

Professional message templates for the LinkedIn Job & Internship Bot.
Provides consistent, well-formatted messages with internationalization support.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class JobType(Enum):
    """Job type enumeration."""
    JOB = "job"
    INTERNSHIP = "internship"


class LocationType(Enum):
    """Location type enumeration."""
    INDIA = "🇮🇳"
    REMOTE = "🏠"
    GLOBAL = "🌍"


@dataclass
class JobOpportunity:
    """Data class for job opportunity information."""
    company: str
    url: str
    location_type: LocationType
    title: str = ""
    
    def __str__(self) -> str:
        return f"{self.location_type.value} [{self.company}]({self.url})"


class MessageTemplates:
    """Professional message templates for the bot."""
    
    # Emoji constants
    WAVE = "👋"
    SEARCH = "🔍"
    BRIEFCASE = "💼"
    GRADUATION = "🎓"
    LOCATION = "📍"
    GLOBE = "🌐"
    CLOCK = "⏱️"
    CHART = "📊"
    ROCKET = "🚀"
    LIGHTBULB = "💡"
    WARNING = "⚠️"
    SAD = "😔"
    PARTY = "🎉"
    REFRESH = "🔄"
    ROBOT = "🤖"
    STAR = "⭐"
    
    @staticmethod
    def welcome_message(user_name: str) -> str:
        """Generate welcome message for new users."""
        return (
            f"Hi {user_name}! {MessageTemplates.WAVE}\n\n"
            f"{MessageTemplates.SEARCH} **LinkedIn Job & Internship Finder**\n\n"
            "I can help you find opportunities on LinkedIn with focus on:\n"
            f"{MessageTemplates.LOCATION} **India** (Bangalore, Mumbai, Delhi, Hyderabad, Pune, etc.)\n"
            f"{MessageTemplates.GLOBE} **Remote** positions suitable for India\n"
            f"{MessageTemplates.GLOBE} **Global** opportunities as backup\n\n"
            "**What are you looking for?**"
        )
    
    @staticmethod
    def job_type_prompt(job_type: JobType) -> str:
        """Generate role input prompt based on job type."""
        if job_type == JobType.JOB:
            return (
                f"{MessageTemplates.BRIEFCASE} **Great! You're looking for a full-time job.**\n\n"
                f"{MessageTemplates.SEARCH} **What specific role are you interested in?**\n\n"
                "**Popular Examples:**\n"
                "• `Java Developer` ☕\n"
                "• `Python Developer` 🐍\n"
                "• `Frontend Developer` 🎨\n"
                "• `Backend Developer` ⚙️\n"
                "• `Full Stack Developer` 🌐\n"
                "• `DevOps Engineer` 🔧\n"
                "• `Data Scientist` 📊\n"
                "• `Machine Learning Engineer` 🤖\n"
                "• `Software Engineer` 💻\n"
                "• `React Developer` ⚛️\n"
                "• `Node.js Developer` 🟢\n"
                "• `Mobile App Developer` 📱\n\n"
                f"{MessageTemplates.LIGHTBULB} **Just type the role you want** (e.g., \"Java Developer\")\n"
                f"{MessageTemplates.ROCKET} **I'll search immediately and keep you updated!**"
            )
        else:  # INTERNSHIP
            return (
                f"{MessageTemplates.GRADUATION} **Perfect! You're looking for an internship.**\n\n"
                f"{MessageTemplates.SEARCH} **What type of internship are you interested in?**\n\n"
                "**Popular Examples:**\n"
                "• `Software Engineering Intern` 💻\n"
                "• `Java Developer Intern` ☕\n"
                "• `Python Developer Intern` 🐍\n"
                "• `Frontend Developer Intern` 🎨\n"
                "• `Backend Developer Intern` ⚙️\n"
                "• `Full Stack Developer Intern` 🌐\n"
                "• `Data Science Intern` 📊\n"
                "• `Machine Learning Intern` 🤖\n"
                "• `DevOps Intern` 🔧\n"
                "• `Mobile App Development Intern` 📱\n"
                "• `Web Development Intern` 🌐\n"
                "• `Software Developer Intern` 💻\n\n"
                f"{MessageTemplates.LIGHTBULB} **Just type the internship type you want** (e.g., \"Software Engineering Intern\")\n"
                f"{MessageTemplates.ROCKET} **I'll search immediately and keep you updated!**"
            )
    
    @staticmethod
    def search_progress_message(role: str, job_type: JobType, location: str, max_results: int) -> str:
        """Generate initial search progress message."""
        return (
            f"{MessageTemplates.SEARCH} **Starting search for {role}**\n\n"
            f"{MessageTemplates.CHART} **Search Type**: {job_type.value.title()}\n"
            f"{MessageTemplates.LOCATION} **Primary Location**: {location}\n"
            f"{MessageTemplates.GLOBE} **Also Searching**: Remote & Global opportunities\n"
            f"{MessageTemplates.CHART} **Max Results**: {max_results} positions\n\n"
            f"{MessageTemplates.ROCKET} **I'll keep you updated on the progress!**\n"
            f"{MessageTemplates.CLOCK} **Estimated time**: 30-45 seconds"
        )
    
    @staticmethod
    def success_message(role: str, job_type: JobType, location: str, 
                       opportunities: List[JobOpportunity]) -> str:
        """Generate success message with job opportunities."""
        message = (
            f"{MessageTemplates.PARTY} **{role} Opportunities Found!**\n\n"
            f"{MessageTemplates.CHART} **Search Type**: {job_type.value.title()}\n"
            f"{MessageTemplates.LOCATION} **Searched**: {location}, Remote & Global positions\n"
            f"{MessageTemplates.CHART} **Found**: {len(opportunities)} opportunities\n\n"
        )
        
        for i, opportunity in enumerate(opportunities, 1):
            message += f"**{i}.** {opportunity}\n"
        
        message += (
            f"\n{MessageTemplates.ROCKET} **Good luck with your applications!**\n"
            f"{MessageTemplates.LIGHTBULB} *Found {role} positions prioritized by location*\n"
            f"{MessageTemplates.REFRESH} *Use /start to search for different roles*"
        )
        
        return message
    
    @staticmethod
    def no_results_message(role: str, location: str) -> str:
        """Generate no results message."""
        return (
            f"{MessageTemplates.SAD} **No {role} positions found right now**\n\n"
            f"**Searched in:**\n"
            f"{MessageTemplates.LOCATION} {location}\n"
            f"{MessageTemplates.GLOBE} Remote positions\n"
            f"{MessageTemplates.GLOBE} Global opportunities\n\n"
            "**This could be because:**\n"
            f"• No new '{role}' postings in the last 24 hours\n"
            "• Try different keywords (e.g., 'Software Developer' vs 'Java Developer')\n"
            "• Weekend/holiday posting lull\n\n"
            f"{MessageTemplates.REFRESH} **Try again with different keywords using /start**\n"
            f"{MessageTemplates.LIGHTBULB} **Tip**: Try broader terms like 'Software Engineer' or 'Developer'"
        )
    
    @staticmethod
    def error_message() -> str:
        """Generate error message."""
        return (
            f"{MessageTemplates.WARNING} **Oops! Something went wrong**\n\n"
            "There was a technical issue while searching.\n\n"
            f"{MessageTemplates.REFRESH} **Please try again with /start**\n"
            "If the problem persists, the service might be temporarily unavailable."
        )
    
    @staticmethod
    def help_message(location: str, max_results: int) -> str:
        """Generate help message."""
        return (
            f"{MessageTemplates.ROBOT} **LinkedIn Job & Internship Bot Help**\n\n"
            "**Available Commands:**\n"
            f"• `/start` - Start interactive job/internship search\n"
            "• `/help` - Show this help message\n\n"
            "**How it works:**\n"
            f"1. {MessageTemplates.BRIEFCASE} **Choose**: Job or Internship\n"
            f"2. {MessageTemplates.LIGHTBULB} **Specify**: What role you want (e.g., 'Java Developer')\n"
            f"3. {MessageTemplates.SEARCH} **Search**: I search LinkedIn with smart prioritization\n"
            f"4. {MessageTemplates.CHART} **Results**: Get up to {max_results} fresh opportunities\n\n"
            "**Search Strategy:**\n"
            f"{MessageTemplates.LOCATION} **Primary**: {location} opportunities\n"
            f"{MessageTemplates.GLOBE} **Secondary**: Remote positions suitable for India\n"
            f"{MessageTemplates.GLOBE} **Backup**: Global opportunities\n\n"
            "**Supported Roles:**\n"
            f"{MessageTemplates.BRIEFCASE} **Jobs**: Java Developer, Python Developer, DevOps Engineer, etc.\n"
            f"{MessageTemplates.GRADUATION} **Internships**: Software Engineering Intern, Data Science Intern, etc.\n\n"
            "**Features:**\n"
            f"{MessageTemplates.STAR} Interactive role selection\n"
            f"{MessageTemplates.STAR} India-focused with global reach\n"
            f"{MessageTemplates.STAR} Fresh results from last 24 hours\n"
            f"{MessageTemplates.STAR} Smart job categorization ({LocationType.INDIA.value}/{LocationType.REMOTE.value}/{LocationType.GLOBAL.value})\n"
            f"{MessageTemplates.STAR} No LinkedIn login required\n\n"
            f"{MessageTemplates.LIGHTBULB} **Tip**: Use /start anytime to search for different roles!"
        )
    
    @staticmethod
    def invalid_state_message() -> str:
        """Generate invalid state message."""
        return (
            f"{MessageTemplates.WARNING} Please start with /start to begin your job search."
        )


class MessageFormatter:
    """Utility class for formatting messages."""
    
    @staticmethod
    def extract_company_name(job_info: str) -> str:
        """Extract company name from job info string or LinkedIn URL."""
        try:
            # Handle new job info format: "TITLE: ... | COMPANY: ... | LOCATION: ..."
            if "COMPANY:" in job_info:
                parts = job_info.split("|")
                for part in parts:
                    if "COMPANY:" in part:
                        company = part.split("COMPANY:")[1].strip()
                        return company if company else "Company"
            
            # Handle URL format (legacy)
            if '-at-' in job_info:
                company = job_info.split('-at-')[-1].split('-')[0].replace('%20', ' ').title()
                return company if company else "Company"
            return "Company"
        except Exception:
            return "Company"
    
    @staticmethod
    def extract_job_title(job_info: str) -> str:
        """Extract job title from job info string."""
        try:
            # Handle new job info format: "TITLE: ... | COMPANY: ... | LOCATION: ..."
            if "TITLE:" in job_info:
                parts = job_info.split("|")
                for part in parts:
                    if "TITLE:" in part:
                        title = part.split("TITLE:")[1].strip()
                        return title if title else "Position"
            return "Position"
        except Exception:
            return "Position"
    
    @staticmethod
    def extract_location_info(job_info: str) -> str:
        """Extract location info from job info string."""
        try:
            # Handle new job info format: "TITLE: ... | COMPANY: ... | LOCATION: ..."
            if "LOCATION:" in job_info:
                parts = job_info.split("|")
                for part in parts:
                    if "LOCATION:" in part:
                        location = part.split("LOCATION:")[1].strip()
                        return location if location else ""
            return ""
        except Exception:
            return ""
    
    @staticmethod
    def determine_location_type(job_info: str) -> LocationType:
        """Determine location type from job info string or URL."""
        info_lower = job_info.lower()
        
        # Check for India-specific terms
        india_terms = ['india', 'bangalore', 'mumbai', 'delhi', 'hyderabad', 'pune', 
                      'chennai', 'kolkata', 'ahmedabad', 'gurgaon', 'noida', 'bengaluru',
                      'karnataka', 'maharashtra', 'tamil nadu', 'andhra pradesh']
        if any(term in info_lower for term in india_terms):
            return LocationType.INDIA
        
        # Check for remote indicators
        if 'remote' in info_lower or 'f_WT=2' in job_info:
            return LocationType.REMOTE
        
        return LocationType.GLOBAL
    
    @staticmethod
    def create_job_opportunity(job_info: str, title: str = "") -> JobOpportunity:
        """Create a JobOpportunity object from job info string or URL."""
        company = MessageFormatter.extract_company_name(job_info)
        location_type = MessageFormatter.determine_location_type(job_info)
        extracted_title = MessageFormatter.extract_job_title(job_info)
        location_info = MessageFormatter.extract_location_info(job_info)
        
        # Create a display URL or use the job info
        if job_info.startswith("http"):
            display_url = job_info
        else:
            # Create a search-friendly URL for the job info
            search_title = extracted_title.replace(' ', '+')
            search_company = company.replace(' ', '+')
            display_url = f"https://www.linkedin.com/jobs/search/?keywords={search_title}+{search_company}"
        
        return JobOpportunity(
            company=f"{company}" + (f" ({location_info})" if location_info else ""),
            url=display_url,
            location_type=location_type,
            title=extracted_title or title
        )
