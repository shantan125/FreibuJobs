# LinkedIn Bot Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: GitHub Actions (Recommended)

1. **Fork the repository** to your GitHub account

2. **Set up GitHub Secrets**:
   Go to your repository → Settings → Secrets and variables → Actions

   Add these secrets:

   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   DOCKER_USERNAME=your_dockerhub_username (optional)
   DOCKER_PASSWORD=your_dockerhub_token (optional)
   ```

3. **Push to main branch** - the pipeline will automatically:
   - Run tests and security scans
   - Build Docker image
   - Deploy if all checks pass

### Option 2: Docker Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/linkedin-bot.git
cd linkedin-bot

# Copy environment template
cp .env.template .env

# Edit .env with your configuration
nano .env

# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f linkedin-bot
```

### Option 3: Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/linkedin-bot.git
cd linkedin-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Edit .env with your configuration
# Set TELEGRAM_BOT_TOKEN at minimum

# Run the bot
python main.py
```

## 🔧 Configuration

### Required Configuration

- `TELEGRAM_BOT_TOKEN`: Get from @BotFather on Telegram

### Optional Configuration

- `MAX_RESULTS_PER_SEARCH`: Number of jobs to return (default: 10)
- `DEFAULT_LOCATION`: Default search location (default: India)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🏥 Health Checks

The bot includes built-in health checks:

- **HTTP endpoint**: `http://localhost:8080/health` (if metrics enabled)
- **Docker health check**: Automatically configured
- **Telegram connectivity**: Verified on startup

## 📊 Monitoring

### GitHub Actions Monitoring

- Automated testing on every push
- Security scanning with Bandit and Safety
- Code quality checks with Black, isort, flake8
- Dependency updates via Dependabot

### Docker Monitoring

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs linkedin-bot

# Monitor resource usage
docker stats linkedin-bot
```

### Production Monitoring

If you enable metrics (`ENABLE_METRICS=true`):

- Prometheus metrics at `:8080/metrics`
- Custom metrics for bot performance
- Error rate and response time tracking

## 🔄 CI/CD Pipeline

The pipeline includes:

1. **On Push/PR**:

   - Code quality checks (Black, isort, flake8, mypy)
   - Security scanning (Bandit, Safety)
   - Unit and integration tests
   - Multi-platform testing (Ubuntu, Windows, macOS)

2. **On Main Branch**:

   - Docker image build and push
   - Artifact creation
   - Automatic deployment (if configured)

3. **On Release Tag**:
   - GitHub release creation
   - Asset uploads (wheel, source)
   - Docker image tagging

## 🚨 Troubleshooting

### Common Issues

1. **Chrome WebDriver Issues**:

   ```bash
   # Check Chrome installation
   google-chrome --version

   # Install Chrome (Ubuntu)
   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
   apt-get update && apt-get install -y google-chrome-stable
   ```

2. **Permission Issues (Docker)**:

   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ./logs ./data
   ```

3. **Memory Issues**:
   ```bash
   # Increase Docker memory limit
   docker-compose up -d --memory=1g
   ```

### Debug Mode

Enable debug logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
DEBUG=true

# Or via environment variable
LOG_LEVEL=DEBUG python main.py
```

### Container Debugging

```bash
# Enter running container
docker exec -it linkedin-bot bash

# Check logs
docker logs linkedin-bot

# Restart container
docker-compose restart linkedin-bot
```

## 🔐 Security Best Practices

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for sensitive data
3. **Regularly update dependencies** (Dependabot helps)
4. **Monitor security alerts** in GitHub
5. **Use non-root user** in Docker (configured)
6. **Enable security scanning** in CI/CD

## 📈 Scaling

### Horizontal Scaling

- Deploy multiple instances with different bot tokens
- Use load balancer for web endpoints
- Separate processing workers

### Vertical Scaling

- Increase Docker memory/CPU limits
- Optimize Chrome options for performance
- Use Redis for caching (configured in docker-compose)

## 🎯 Production Deployment

For production deployment:

1. **Use production environment**:

   ```bash
   APP_ENV=production
   DEBUG=false
   LOG_LEVEL=WARNING
   ```

2. **Enable monitoring**:

   ```bash
   ENABLE_METRICS=true
   HEALTH_CHECK_ENABLED=true
   ```

3. **Set up alerts** for:

   - Container health status
   - Error rates
   - Memory/CPU usage
   - Telegram API connectivity

4. **Configure backups** for:
   - Configuration files
   - Log files
   - Any persistent data

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **GitHub Discussions**: Community support and questions
- **Documentation**: Check README.md for detailed usage
- **Logs**: Always include relevant logs when reporting issues

---

✅ **Ready to deploy!** Choose your preferred deployment option above.
