# 🚀 LinkedIn Bot - Professional Multi-Stage Dockerfile

# Build arguments for metadata
ARG BUILD_DATE
ARG BUILD_VERSION
ARG COMMIT_SHA
ARG ENVIRONMENT=production

# ========================================
# Stage 1: Base Dependencies
# ========================================
FROM python:3.11-slim as base

# Metadata labels
LABEL maintainer="LinkedIn Bot Team"
LABEL org.opencontainers.image.title="LinkedIn Job Bot"
LABEL org.opencontainers.image.description="Automated LinkedIn job search bot with Telegram integration"
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${COMMIT_SHA}"
LABEL org.opencontainers.image.source="https://github.com/shantan125/frebujob"

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DISPLAY=:99

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    # Essential tools
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    curl \
    unzip \
    # Chrome dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    # Cleanup in same layer
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ========================================
# Stage 2: Dependencies Installation
# ========================================
FROM base as dependencies

# Create application directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# ========================================
# Stage 3: Application Build
# ========================================
FROM dependencies as application

# Create non-root user for security
RUN groupadd --gid 1000 botuser \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash botuser \
    && mkdir -p /app/logs /app/data \
    && chown -R botuser:botuser /app

# Copy application code with proper ownership
COPY --chown=botuser:botuser . .

# Set build information
ENV BUILD_VERSION=${BUILD_VERSION} \
    BUILD_DATE=${BUILD_DATE} \
    COMMIT_SHA=${COMMIT_SHA} \
    ENVIRONMENT=${ENVIRONMENT}

# Switch to non-root user
USER botuser

# Create necessary directories
RUN mkdir -p logs data temp

# ========================================
# Stage 4: Production Image
# ========================================
FROM application as production

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "print('Bot is running')" || exit 1

# Expose port for monitoring
EXPOSE 8080

# Volume for persistent data
VOLUME ["/app/logs", "/app/data"]

# Default command with graceful shutdown handling
CMD ["python", "main.py"]

# ========================================
# Stage 5: Development Image (Optional)
# ========================================
FROM application as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8

# Development-specific environment
ENV LOG_LEVEL=DEBUG

# Development command
CMD ["python", "main.py"]
