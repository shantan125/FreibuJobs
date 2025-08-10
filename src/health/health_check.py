"""
Health Check and Metrics Module for Azure Integration

Provides health check endpoints and monitoring capabilities
for Azure Container Apps deployment.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any
from aiohttp import web, ClientSession
from datetime import datetime
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class HealthCheckServer:
    """Health check and metrics server for Azure deployment."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = web.Application()
        self.start_time = time.time()
        self.setup_routes()
    
    def setup_routes(self):
        """Set up health check and metrics routes."""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/ready', self.readiness_check)
        self.app.router.add_get('/metrics', self.metrics)
        self.app.router.add_get('/status', self.status)
        self.app.router.add_get('/', self.root)
    
    async def health_check(self, request) -> web.Response:
        """Liveness probe endpoint for Azure Container Apps."""
        try:
            # Basic health checks
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": int(time.time() - self.start_time),
                "checks": {
                    "telegram_imports": await self._check_telegram_imports(),
                    "selenium_imports": await self._check_selenium_imports(),
                    "configuration": await self._check_configuration(),
                    "memory_usage": await self._check_memory_usage()
                }
            }
            
            # Determine overall health
            all_healthy = all(check["status"] == "pass" for check in health_status["checks"].values())
            
            if all_healthy:
                health_status["status"] = "healthy"
                return web.json_response(health_status, status=200)
            else:
                health_status["status"] = "unhealthy"
                return web.json_response(health_status, status=503)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=503)
    
    async def readiness_check(self, request) -> web.Response:
        """Readiness probe endpoint for Azure Container Apps."""
        try:
            # Check if the bot is ready to serve requests
            readiness_status = {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {
                    "environment_variables": await self._check_environment_variables(),
                    "telegram_connectivity": await self._check_telegram_connectivity(),
                    "chrome_availability": await self._check_chrome_availability()
                }
            }
            
            all_ready = all(check["status"] == "pass" for check in readiness_status["checks"].values())
            
            if all_ready:
                return web.json_response(readiness_status, status=200)
            else:
                readiness_status["status"] = "not_ready"
                return web.json_response(readiness_status, status=503)
                
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return web.json_response({
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=503)
    
    async def metrics(self, request) -> web.Response:
        """Prometheus-style metrics endpoint."""
        try:
            import psutil
            
            metrics_data = {
                "linkedin_bot_uptime_seconds": int(time.time() - self.start_time),
                "linkedin_bot_memory_usage_bytes": psutil.Process().memory_info().rss,
                "linkedin_bot_cpu_percent": psutil.Process().cpu_percent(),
                "linkedin_bot_threads_count": psutil.Process().num_threads(),
                "linkedin_bot_status": 1  # 1 = healthy, 0 = unhealthy
            }
            
            # Convert to Prometheus format
            prometheus_output = ""
            for metric_name, value in metrics_data.items():
                prometheus_output += f"# HELP {metric_name} LinkedIn Bot metric\n"
                prometheus_output += f"# TYPE {metric_name} gauge\n"
                prometheus_output += f"{metric_name} {value}\n"
            
            return web.Response(text=prometheus_output, content_type="text/plain")
            
        except ImportError:
            # Fallback if psutil is not available
            basic_metrics = {
                "linkedin_bot_uptime_seconds": int(time.time() - self.start_time),
                "linkedin_bot_status": 1
            }
            
            prometheus_output = ""
            for metric_name, value in basic_metrics.items():
                prometheus_output += f"{metric_name} {value}\n"
            
            return web.Response(text=prometheus_output, content_type="text/plain")
    
    async def status(self, request) -> web.Response:
        """Detailed status endpoint."""
        try:
            from src.utils.config import ConfigurationManager
            
            status_info = {
                "service": "LinkedIn Job & Internship Bot",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": int(time.time() - self.start_time),
                "environment": os.getenv("AZURE_ENVIRONMENT", "development"),
                "azure_region": os.getenv("AZURE_LOCATION", "unknown"),
                "configuration": {
                    "telegram_bot_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
                    "azure_environment": os.getenv("AZURE_ENVIRONMENT", "not_set"),
                    "log_level": os.getenv("LOG_LEVEL", "INFO"),
                    "metrics_enabled": os.getenv("ENABLE_METRICS", "false").lower() == "true"
                }
            }
            
            return web.json_response(status_info, status=200)
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return web.json_response({
                "service": "LinkedIn Job & Internship Bot",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=500)
    
    async def root(self, request) -> web.Response:
        """Root endpoint with basic information."""
        return web.json_response({
            "service": "LinkedIn Job & Internship Bot",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "readiness": "/ready", 
                "metrics": "/metrics",
                "status": "/status"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _check_telegram_imports(self) -> Dict[str, Any]:
        """Check if Telegram libraries can be imported."""
        try:
            import telegram
            return {"status": "pass", "message": "Telegram library available"}
        except ImportError as e:
            return {"status": "fail", "message": f"Telegram import failed: {e}"}
    
    async def _check_selenium_imports(self) -> Dict[str, Any]:
        """Check if Selenium libraries can be imported."""
        try:
            import selenium
            from selenium import webdriver
            return {"status": "pass", "message": "Selenium library available"}
        except ImportError as e:
            return {"status": "fail", "message": f"Selenium import failed: {e}"}
    
    async def _check_configuration(self) -> Dict[str, Any]:
        """Check if basic configuration is available."""
        try:
            required_vars = ["TELEGRAM_BOT_TOKEN"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                return {"status": "fail", "message": f"Missing environment variables: {missing_vars}"}
            else:
                return {"status": "pass", "message": "Configuration complete"}
        except Exception as e:
            return {"status": "fail", "message": f"Configuration check failed: {e}"}
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory_percent = psutil.Process().memory_percent()
            
            if memory_percent > 90:
                return {"status": "warn", "message": f"High memory usage: {memory_percent:.1f}%"}
            else:
                return {"status": "pass", "message": f"Memory usage: {memory_percent:.1f}%"}
        except ImportError:
            return {"status": "pass", "message": "Memory monitoring not available"}
        except Exception as e:
            return {"status": "warn", "message": f"Memory check failed: {e}"}
    
    async def _check_environment_variables(self) -> Dict[str, Any]:
        """Check required environment variables."""
        required_vars = ["TELEGRAM_BOT_TOKEN"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return {"status": "fail", "message": f"Missing required variables: {missing_vars}"}
        else:
            return {"status": "pass", "message": "All required environment variables present"}
    
    async def _check_telegram_connectivity(self) -> Dict[str, Any]:
        """Check if we can connect to Telegram API."""
        try:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                return {"status": "fail", "message": "No Telegram bot token configured"}
            
            # Basic connectivity check
            async with ClientSession() as session:
                url = f"https://api.telegram.org/bot{token}/getMe"
                async with session.get(url) as response:
                    if response.status == 200:
                        return {"status": "pass", "message": "Telegram API accessible"}
                    else:
                        return {"status": "fail", "message": f"Telegram API returned {response.status}"}
        except Exception as e:
            return {"status": "fail", "message": f"Telegram connectivity check failed: {e}"}
    
    async def _check_chrome_availability(self) -> Dict[str, Any]:
        """Check if Chrome is available for Selenium."""
        try:
            import shutil
            
            # Check for Chrome executable
            chrome_paths = [
                "google-chrome-stable",
                "google-chrome", 
                "chromium-browser",
                "chrome"
            ]
            
            if os.name == 'nt':  # Windows
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                chrome_available = any(os.path.exists(path) for path in chrome_paths)
            else:
                chrome_available = any(shutil.which(path) for path in chrome_paths)
            
            if chrome_available:
                return {"status": "pass", "message": "Chrome browser available"}
            else:
                return {"status": "warn", "message": "Chrome browser not found"}
                
        except Exception as e:
            return {"status": "warn", "message": f"Chrome check failed: {e}"}
    
    async def start_server(self):
        """Start the health check server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"Health check server started on port {self.port}")
        logger.info(f"Health check endpoint: http://0.0.0.0:{self.port}/health")
        logger.info(f"Readiness endpoint: http://0.0.0.0:{self.port}/ready")
        logger.info(f"Metrics endpoint: http://0.0.0.0:{self.port}/metrics")
        
        return runner


def health_check() -> bool:
    """
    Simple synchronous health check for Docker healthcheck.
    Returns True if healthy, False otherwise.
    """
    try:
        # Basic import checks
        import telegram
        import selenium
        
        # Check if Telegram token is configured
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            return False
        
        # Check if Chrome is available
        import shutil
        chrome_available = shutil.which("google-chrome-stable") or shutil.which("google-chrome")
        if not chrome_available:
            logger.warning("Chrome not found, but continuing...")
        
        return True
        
    except ImportError as e:
        logger.error(f"Import error in health check: {e}")
        return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


async def main():
    """Run standalone health check server."""
    server = HealthCheckServer()
    runner = await server.start_server()
    
    try:
        await asyncio.Event().wait()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down health check server...")
        await runner.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
