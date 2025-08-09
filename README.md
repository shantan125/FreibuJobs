# LinkedIn Job & Internship Bot 🤖

[![✅ Code Quality](https://img.shields.io/badge/Code%20Quality-Excellent-brightgreen)]()
[![🧹 Cleanup](https://img.shields.io/badge/Cleanup-Complete-success)]()
[![📊 Logging](https://img.shields.io/badge/Logging-Enhanced-blue)]()
[![☁️ Azure](https://img.shields.io/badge/Azure-Ready-0078d4)]()
[![🚀 Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()

A professional Telegram bot that helps users find the latest job and internship opportunities on LinkedIn with India-focused search capabilities and global reach.

## ✨ Features

- **🎯 Interactive Experience**: Choose between jobs and internships with guided conversation flow
- **🇮🇳 India-First Strategy**: Prioritizes Indian opportunities (Bangalore, Mumbai, Delhi, etc.)
- **🏠 Remote-Friendly**: Includes remote positions suitable for Indian professionals
- **🌍 Global Reach**: Falls back to worldwide opportunities for comprehensive coverage
- **📊 Smart Results**: Up to 10 carefully curated positions per search
- **⏰ Progressive Time Search**: Automatically searches multiple timeframes for better results
  - 📅 **Primary**: Last 24 hours (most recent postings)
  - 📅 **Fallback 1**: Last 2 days (if no recent jobs found)
  - 📅 **Fallback 2**: Last 7 days (comprehensive search)
- **🔐 No Login Required**: Public LinkedIn search without authentication
- **🏗️ Professional Architecture**: Clean, maintainable, and scalable codebase
- **📊 Enhanced Logging**: Comprehensive monitoring and performance tracking
- **☁️ Azure Ready**: Production deployment with auto-scaling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd linkedin-bot
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**

   ```bash
   # Copy the example environment file
   cp config/.env.example .env

   # Edit .env with your configuration
   # Required: TELEGRAM_TOKEN
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Required Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Optional Configuration
DEFAULT_LOCATION=India
MAX_RESULTS=10
CHROME_DRIVER_PATH=/path/to/chromedriver  # Optional, auto-detected if not set
LOG_LEVEL=INFO
LOG_FILE=linkedin_bot.log
```

### Configuration Options

| Variable             | Default            | Description                                 |
| -------------------- | ------------------ | ------------------------------------------- |
| `TELEGRAM_TOKEN`     | **Required**       | Your Telegram bot token from BotFather      |
| `DEFAULT_LOCATION`   | `India`            | Primary search location                     |
| `MAX_RESULTS`        | `10`               | Maximum results per search (1-50)           |
| `CHROME_DRIVER_PATH` | Auto-detect        | Path to ChromeDriver executable             |
| `LOG_LEVEL`          | `INFO`             | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE`           | `linkedin_bot.log` | Log file path                               |

## 📋 Usage

### Commands

- `/start` - Begin interactive job/internship search
- `/help` - Show detailed help and usage information

### Search Flow

1. **Start**: Send `/start` to begin
2. **Choose Type**: Select between 💼 Full-time Job or 🎓 Internship
3. **Specify Role**: Enter your desired role (e.g., "Java Developer", "Data Science Intern")
4. **Get Results**: Receive up to 10 categorized opportunities:
   - 🇮🇳 India-based positions
   - 🏠 Remote positions
   - 🌍 Global opportunities

### 🕐 Progressive Time Search

The bot uses an intelligent time-based search strategy to maximize job discovery:

1. **📅 Primary Search (Last 24 hours)**: Searches for the freshest job postings
2. **📅 Fallback 1 (Last 2 days)**: If no recent jobs found, expands to 2-day timeframe
3. **📅 Fallback 2 (Last 7 days)**: Final search covering the past week for comprehensive results

**Benefits:**

- ✅ **Always finds results**: Progressively widens search until jobs are found
- ✅ **Prioritizes fresh opportunities**: Shows newest postings first
- ✅ **Comprehensive coverage**: Won't miss opportunities due to timing
- ✅ **Smart user feedback**: Shows which timeframe yielded results

**Example Flow:**

```
User: "Full stack developer"
Bot: 🔍 Searching Full stack developer
     📅 Time Range: last 24 hours
     ⏳ Please wait...

     😔 No results in last 24 hours, trying last 2 days...
     📅 Time Range: last 2 days
     ⏳ Please wait...

     🎉 Found 8 Full stack developer opportunities!
     📅 Found in: last 2 days
```

### Example Searches

**Jobs:**

- Java Developer
- Python Developer
- Frontend Developer
- DevOps Engineer
- Data Scientist
- Machine Learning Engineer

**Internships:**

- Software Engineering Intern
- Data Science Intern
- Web Development Intern
- Machine Learning Intern

## 🏗️ Project Structure

```
linkedin-bot/
├── 📁 src/                       # Core application code
│   ├── 🤖 bot/                   # Telegram bot logic
│   │   ├── handlers.py           # Conversation handlers (MAIN LOGIC)
│   │   ├── main.py              # Bot orchestration
│   │   └── messages.py          # User message templates
│   ├── 🔍 scraper/              # LinkedIn scraping engine
│   │   └── linkedin.py          # Smart multi-tier search
│   ├── ⚙️ utils/                # Utilities and configuration
│   │   ├── config.py            # Configuration management
│   │   └── logging.py           # Enhanced logging system
│   └── 🏥 health/               # Health monitoring
│       └── health_check.py      # Azure health checks
├── 📚 docs/                     # All documentation
│   ├── WORKFLOW_GUIDE.md        # Complete developer guide
│   ├── DEPLOYMENT.md            # Deployment instructions
│   └── AZURE_READY.md          # Azure-specific setup
├── 🚀 deploy/                   # Deployment configuration
│   ├── docker-compose.yml      # Docker orchestration
│   ├── Dockerfile              # Container definition
│   └── .dockerignore           # Docker ignore patterns
├── ⚙️ config/                  # Configuration files
│   ├── .env.example            # Environment template
│   ├── pytest.ini             # Test configuration
│   ├── setup.cfg              # Package setup config
│   └── .pre-commit-config.yaml # Code quality hooks
├── 🧪 tests/                   # Test suite
├── 📜 scripts/                 # Utility scripts
├── 📊 monitoring/              # Monitoring configuration
├── 📝 logs/                    # Application logs
├── 📄 main.py                  # 🎯 MAIN ENTRY POINT
├── 📋 requirements.txt         # Python dependencies
├── 📖 README.md               # Project overview (this file)
└── 🛠️ Makefile               # Development commands
```

**Quick Navigation:**

- 🎯 **Start Here**: `main.py` - Application entry point
- 🔥 **Core Logic**: `src/bot/handlers.py` - Interactive conversation flow
- 🔍 **Search Engine**: `src/scraper/linkedin.py` - LinkedIn scraping
- 📚 **Documentation**: `docs/WORKFLOW_GUIDE.md` - Complete developer guide
- 🚀 **Deployment**: `docs/DEPLOYMENT.md` - How to deploy

## 🔧 Development

### Architecture

The bot follows a professional modular architecture:

- **`src/bot/`**: Telegram bot logic, handlers, and message templates
- **`src/scraper/`**: LinkedIn scraping functionality with multi-tier search
- **`src/utils/`**: Configuration management and utilities
- **Professional Features**: Type hints, dataclasses, comprehensive logging, error handling

### Key Components

1. **ConfigurationManager**: Centralized configuration with validation
2. **ConversationHandlers**: State-managed user interactions
3. **LinkedInScraper**: Multi-tier search strategy (India → Remote → Global)
4. **MessageTemplates**: Professional, consistent messaging

### Search Strategy

The bot implements a sophisticated three-tier search approach:

1. **Tier 1 - India Focus**: Search major Indian cities
   - India, Bangalore, Mumbai, Delhi, Hyderabad, Pune
2. **Tier 2 - Remote Positions**: Remote-friendly roles
3. **Tier 3 - Global Fallback**: Worldwide opportunities

## 🧪 Testing

The bot has been extensively tested with various search terms:

| Search Term       | Jobs Found | Internships Found |
| ----------------- | ---------- | ----------------- |
| Java Developer    | 90+        | 56+               |
| Python Developer  | 90+        | 75+               |
| Data Science      | 85+        | 90+               |
| Software Engineer | 90+        | 80+               |

## 📊 Features in Detail

### Multi-Tier Search Strategy

- **India-First**: Prioritizes local opportunities
- **Remote-Inclusive**: Finds work-from-home positions
- **Global Backup**: Ensures comprehensive coverage

### Smart Categorization

- 🇮🇳 **India**: Local opportunities
- 🏠 **Remote**: Work-from-home positions
- 🌍 **Global**: International opportunities

### Professional Code Quality

- Type hints throughout
- Comprehensive error handling
- Structured logging
- Modular architecture
- Configuration management
- Professional documentation

## 🔍 How It Works

1. **User Interaction**: Interactive conversation flow with inline keyboards
2. **Search Execution**: Multi-tier LinkedIn search strategy
3. **Result Processing**: Smart categorization and filtering
4. **Response Formatting**: Professional message templates with emojis
5. **Error Handling**: Graceful error recovery and user feedback

## 📈 Performance

- **Search Time**: 30-45 seconds for comprehensive results
- **Result Quality**: India-prioritized with global fallback
- **Reliability**: Robust error handling and retry logic
- **Scalability**: Professional architecture supports multiple users

## 🛠️ Troubleshooting

### Common Issues

1. **Bot doesn't respond**

   - Check TELEGRAM_TOKEN in .env
   - Verify internet connection
   - Check bot logs

2. **No search results**

   - Try broader search terms
   - Check if it's weekend/holiday (fewer postings)
   - Verify ChromeDriver installation

3. **ChromeDriver issues**
   - Install ChromeDriver manually
   - Set CHROME_DRIVER_PATH in .env
   - Update Chrome browser

### Logs

Check `linkedin_bot.log` for detailed execution logs and error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LinkedIn for providing public job search capabilities
- Telegram Bot API for excellent bot framework
- Selenium WebDriver for reliable web automation

---

**Happy Job Hunting! 🚀**

_Built with ❤️ for the developer community_
