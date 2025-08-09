"""
Advanced Logging Utilities for LinkedIn Job & Internship Bot

Provides structured logging, performance monitoring, and comprehensive
error tracking for production environments.
"""

import logging
import logging.handlers
import time
import functools
import traceback
import sys
import os
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_data['extra'] = log_data.get('extra', {})
                log_data['extra'][key] = value
        
        return json.dumps(log_data, ensure_ascii=False)


class PerformanceMonitor:
    """Performance monitoring utility for tracking execution times."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self._start_times[operation] = time.time()
        self.logger.debug(f"Started timing operation: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and log the duration."""
        if operation not in self._start_times:
            self.logger.warning(f"No start time found for operation: {operation}")
            return 0.0
        
        duration = time.time() - self._start_times.pop(operation)
        self.logger.info(f"Operation '{operation}' completed in {duration:.3f}s", 
                        extra={'operation': operation, 'duration': duration})
        return duration
    
    def time_function(self, func: Callable) -> Callable:
        """Decorator to time function execution."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            self.start_timer(func_name)
            try:
                result = func(*args, **kwargs)
                self.end_timer(func_name)
                return result
            except Exception as e:
                self.end_timer(func_name)
                self.logger.error(f"Function '{func_name}' failed: {e}", 
                                extra={'function': func_name, 'error': str(e)})
                raise
        return wrapper


class BotLogger:
    """Centralized logging configuration for the LinkedIn Bot."""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 structured_logging: bool = False,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize bot logging.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            structured_logging: Enable JSON structured logging
            max_file_size: Maximum log file size before rotation
            backup_count: Number of backup files to keep
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        self.structured_logging = structured_logging
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        self._setup_logging()
        self.logger = logging.getLogger('linkedin_bot')
        self.performance = PerformanceMonitor(self.logger)
        
        # Log initialization
        self.logger.info("Bot logging initialized", extra={
            'log_level': log_level,
            'structured_logging': structured_logging,
            'log_file': log_file
        })
    
    def _setup_logging(self) -> None:
        """Configure logging handlers and formatters."""
        # Remove existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        if self.structured_logging:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # File handler (with rotation if specified)
        handlers = [console_handler]
        
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=self.log_level,
            handlers=handlers,
            force=True
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a specific module."""
        return logging.getLogger(f'linkedin_bot.{name}')
    
    def log_function_call(self, func: Callable) -> Callable:
        """Decorator to log function calls with parameters and results."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            logger = self.get_logger(func.__module__)
            
            # Log function entry
            logger.debug(f"Entering function: {func_name}", extra={
                'function': func_name,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function completed successfully: {func_name}", extra={
                    'function': func_name,
                    'success': True
                })
                return result
            except Exception as e:
                logger.error(f"Function failed: {func_name}", extra={
                    'function': func_name,
                    'error': str(e),
                    'error_type': type(e).__name__
                }, exc_info=True)
                raise
        return wrapper
    
    def log_user_action(self, user_id: int, action: str, **details) -> None:
        """Log user actions for analytics and debugging."""
        self.logger.info(f"User action: {action}", extra={
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            **details
        })
    
    def log_search_request(self, user_id: int, keyword: str, job_type: str, **details) -> None:
        """Log search requests for monitoring and analytics."""
        self.logger.info("Search request initiated", extra={
            'user_id': user_id,
            'keyword': keyword,
            'job_type': job_type,
            'timestamp': datetime.utcnow().isoformat(),
            **details
        })
    
    def log_search_results(self, user_id: int, keyword: str, result_count: int, 
                          tier: str, **details) -> None:
        """Log search results for analytics."""
        self.logger.info("Search results obtained", extra={
            'user_id': user_id,
            'keyword': keyword,
            'result_count': result_count,
            'search_tier': tier,
            'timestamp': datetime.utcnow().isoformat(),
            **details
        })
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log errors with additional context information."""
        self.logger.error(f"Error occurred: {error}", extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }, exc_info=True)
    
    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log performance metrics."""
        self.logger.info("Performance metrics", extra={
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_system_info(self) -> None:
        """Log system information for debugging."""
        import platform
        import psutil
        
        try:
            system_info = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
            }
            
            self.logger.info("System information", extra=system_info)
        except ImportError:
            self.logger.warning("psutil not available, skipping detailed system info")
        except Exception as e:
            self.logger.warning(f"Failed to gather system info: {e}")


# Global logger instance
_bot_logger: Optional[BotLogger] = None


def get_bot_logger() -> BotLogger:
    """Get the global bot logger instance."""
    global _bot_logger
    if _bot_logger is None:
        # Default configuration
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/linkedin_bot.log')
        structured_logging = os.getenv('STRUCTURED_LOGGING', 'false').lower() == 'true'
        
        _bot_logger = BotLogger(
            log_level=log_level,
            log_file=log_file,
            structured_logging=structured_logging
        )
    return _bot_logger


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None,
                 structured_logging: bool = False) -> BotLogger:
    """
    Setup global bot logging.
    
    Args:
        log_level: Logging level
        log_file: Path to log file
        structured_logging: Enable JSON structured logging
        
    Returns:
        BotLogger instance
    """
    global _bot_logger
    _bot_logger = BotLogger(
        log_level=log_level,
        log_file=log_file,
        structured_logging=structured_logging
    )
    return _bot_logger


# Convenience decorators
def log_function(func: Callable) -> Callable:
    """Decorator to log function calls."""
    return get_bot_logger().log_function_call(func)


def time_function(func: Callable) -> Callable:
    """Decorator to time function execution."""
    return get_bot_logger().performance.time_function(func)


if __name__ == "__main__":
    # Test logging setup
    logger = setup_logging("DEBUG", "test_logs.log", structured_logging=True)
    
    test_logger = logger.get_logger("test")
    test_logger.info("Test message")
    test_logger.warning("Test warning")
    test_logger.error("Test error")
    
    print("Logging test completed. Check test_logs.log for output.")
