# Makefile for LinkedIn Bot Development

.PHONY: help install test lint format clean build docker run dev

# Default target
help:
	@echo "LinkedIn Bot Development Commands"
	@echo "================================"
	@echo ""
	@echo "🔧 Development:"
	@echo "  install     - Install dependencies and dev tools"
	@echo "  dev         - Run bot in development mode"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  clean       - Clean build artifacts and cache"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker      - Build Docker image"
	@echo "  docker-run  - Run bot in Docker container"
	@echo "  docker-dev  - Run Docker in development mode"
	@echo ""
	@echo "📦 Build:"
	@echo "  build       - Build distribution packages"
	@echo "  release     - Create a new release"
	@echo ""
	@echo "🔍 Quality:"
	@echo "  security    - Run security checks"
	@echo "  coverage    - Run tests with coverage report"
	@echo "  pre-commit  - Install pre-commit hooks"

# Development setup
install:
	@echo "🔧 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .[dev]
	@echo "✅ Dependencies installed"

# Install pre-commit hooks
pre-commit:
	@echo "🔧 Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Development mode
dev:
	@echo "🚀 Starting bot in development mode..."
	python main.py

# Testing
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --tb=short

coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
	@echo "📊 Coverage report generated in htmlcov/"

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy src/ --ignore-missing-imports

format:
	@echo "🎨 Formatting code..."
	black src/ tests/ *.py --line-length=127
	isort src/ tests/ *.py --profile=black --line-length=127
	@echo "✅ Code formatted"

format-check:
	@echo "🔍 Checking code format..."
	black --check --diff src/ tests/ *.py --line-length=127
	isort --check-only --diff src/ tests/ *.py --profile=black --line-length=127

# Security
security:
	@echo "🔐 Running security checks..."
	safety check
	bandit -r src/
	@echo "✅ Security checks completed"

# Docker commands
docker:
	@echo "🐳 Building Docker image..."
	docker build -f deploy/Dockerfile -t linkedin-bot:latest .
	@echo "✅ Docker image built"

docker-run:
	@echo "🐳 Running bot in Docker..."
	cd deploy && docker-compose up -d
	cd deploy && docker-compose logs -f linkedin-bot

docker-dev:
	@echo "🐳 Running Docker in development mode..."
	cd deploy && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

docker-stop:
	@echo "🛑 Stopping Docker containers..."
	cd deploy && docker-compose down

docker-logs:
	@echo "📋 Showing Docker logs..."
	cd deploy && docker-compose logs -f linkedin-bot

# Build and packaging
build:
	@echo "📦 Building distribution packages..."
	python -m build
	@echo "✅ Packages built in dist/"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean completed"

# Release management
release-check:
	@echo "🔍 Checking release readiness..."
	$(MAKE) test
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) build
	@echo "✅ Release checks passed"

release:
	@echo "🚀 Creating release..."
	@read -p "Enter version (e.g., 1.0.0): " version; \
	git tag -a "v$$version" -m "Release v$$version"; \
	git push origin "v$$version"
	@echo "✅ Release tag created and pushed"

# Environment setup
env-setup:
	@echo "🔧 Setting up environment..."
	cp config/.env.example .env
	@echo "📝 Please edit .env file with your configuration"
	@echo "💡 Minimum required: TELEGRAM_BOT_TOKEN"

# Health check
health:
	@echo "🏥 Running health checks..."
	python -c "from main import health_check; exit(0 if health_check() else 1)"
	@echo "✅ Health check passed"

# Quick start for new developers
setup: install env-setup pre-commit
	@echo ""
	@echo "🎉 Setup completed!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your Telegram bot token"
	@echo "2. Run 'make dev' to start the bot"
	@echo "3. Run 'make test' to verify everything works"
	@echo ""

# CI/CD helpers
ci-test:
	@echo "🤖 Running CI tests..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test
	$(MAKE) build

# Documentation
docs:
	@echo "📚 Opening documentation..."
	@echo "README.md - Project overview and usage"
	@echo "DEPLOYMENT.md - Deployment guide"
	@echo "docs/ - Additional documentation"

# Development utilities
logs:
	@echo "📋 Showing recent logs..."
	tail -f logs/linkedin_bot.log

debug:
	@echo "🐛 Starting bot in debug mode..."
	LOG_LEVEL=DEBUG python main.py

# Database utilities (for future use)
db-init:
	@echo "🗄️ Initializing database..."
	# Add database initialization commands here

db-migrate:
	@echo "🗄️ Running database migrations..."
	# Add migration commands here

# Monitoring
monitor:
	@echo "📊 Starting monitoring dashboard..."
	cd deploy && docker-compose --profile monitoring up -d

# Performance testing
perf-test:
	@echo "⚡ Running performance tests..."
	# Add performance testing commands here
