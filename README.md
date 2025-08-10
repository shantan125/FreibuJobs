# LinkedIn Job & Internship Bot 🤖

[![Deploy to Azure](https://github.com/shantan125/FreibuJobs/actions/workflows/deploy.yml/badge.svg)](https://github.com/shantan125/FreibuJobs/actions/workflows/deploy.yml)
[![Azure Status](https://img.shields.io/badge/Azure-Live-success)]()
[![Real-time](https://img.shields.io/badge/Search-Real--time%20Streaming-brightgreen)]()

A professional Telegram bot that delivers LinkedIn job and internship opportunities in **real-time** with India-focused search and global reach.

## ✨ Key Features

### 🚀 **Real-Time Job Streaming**

- Jobs appear **instantly** as they're discovered (no waiting!)
- Live progress updates during search
- Immediate job notifications with company details

### 🎯 **Smart Search Strategy**

- **India-First**: Bangalore, Mumbai, Delhi, Hyderabad, Pune
- **Remote-Friendly**: Remote positions suitable for India
- **Global Reach**: Worldwide opportunities as backup
- **Progressive Time Filtering**: 24h → 2d → 7d automatically

### 💬 **Professional Experience**

- Clean, emoji-free interface
- Interactive job type selection (Jobs/Internships)
- Guided conversation flow
- No LinkedIn login required

## 🏗️ Architecture

```
linkedin-bot/
├── src/
│   ├── bot/           # Telegram bot handlers & messages
│   ├── scraper/       # LinkedIn scraping with streaming
│   ├── health/        # Health check endpoints
│   └── utils/         # Configuration & logging
├── .github/
│   └── workflows/     # Auto-deployment to Azure
├── .azure/            # Azure configuration
├── logs/              # Runtime logs
├── Dockerfile         # Container configuration
├── main.py           # Application entry point
└── requirements.txt   # Dependencies
```

## 🚀 Quick Start

### Local Development

1. **Clone & Install**

   ```bash
   git clone https://github.com/shantan125/FreibuJobs.git
   cd linkedin-bot
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your Telegram bot token
   ```

3. **Run Locally**
   ```bash
   python main.py
   ```

### Azure Deployment

**Automatic**: Push to `main` branch triggers auto-deployment via GitHub Actions.

**Manual**:

```bash
az containerapp up --name linkedin-bot-app --resource-group linkedin-bot-rg --source .
```

## 🔧 Configuration

Set environment variables in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
LOG_LEVEL=INFO
MAX_RESULTS_PER_SEARCH=10
DEFAULT_LOCATION=India
```

## 📊 Usage Example

```
User: /start
Bot: Choose job type (Job/Internship)
User: [Job]
Bot: Enter role (e.g., "Java Developer")
User: "Python Developer"

Bot: "Starting search for Python Developer..."
     "I'll send you jobs immediately as I find them!"

Bot: "Job 1 Found!
     Company: Accenture (Bangalore)
     Role: Python Developer
     Type: INDIA
     Apply: [View Position](link)
     Continuing search..."

Bot: "Job 2 Found!
     Company: Microsoft (Remote)
     Role: Senior Python Developer
     Type: REMOTE
     Apply: [View Position](link)
     Continuing search..."

... (jobs appear in real-time)

Bot: "Search Complete!
     Total Found: 8 Python Developer opportunities
     Good luck with your applications!"
```

## 🔧 Development

### Project Structure

- **Modular Design**: Clean separation of concerns
- **Real-time Streaming**: Jobs delivered as found, not in batches
- **Professional Logging**: Comprehensive monitoring
- **Health Checks**: Built-in status endpoints
- **Auto-scaling**: Azure Container Apps with 1-3 replicas

### Key Components

- `src/bot/handlers.py`: Real-time conversation management
- `src/scraper/linkedin.py`: Streaming job search with callbacks
- `src/bot/messages.py`: Professional message templates
- `src/utils/config.py`: Configuration management

## 🚀 Deployment

### Automatic Deployment

Every push to `main` automatically:

1. Builds new Docker image
2. Deploys to Azure Container Apps
3. Runs health checks
4. Updates live bot instantly

### Manual Commands

```bash
# View logs
az containerapp logs show --name linkedin-bot-app --resource-group linkedin-bot-rg --follow

# Scale app
az containerapp update --name linkedin-bot-app --resource-group linkedin-bot-rg --min-replicas 1

# Health check
curl https://your-app-url.azurecontainerapps.io
```

## 🏆 Performance

- **Speed**: Jobs appear 2-5 seconds after search starts (vs 30-45s batch processing)
- **Efficiency**: Real-time streaming eliminates waiting
- **Reliability**: Azure Container Apps with auto-scaling
- **Availability**: 24/7 uptime with health monitoring

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

**Built with ❤️ for the developer community**

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
