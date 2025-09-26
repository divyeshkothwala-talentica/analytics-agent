"""
Logging configuration and utilities for the analytics agent
"""

import os
import logging
import logging.handlers
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging():
    """
    Set up logging configuration for the application
    """
    # Get configuration from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'logs/analytics_agent.log')
    
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module
    
    Args:
        name (str): Name of the logger (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with the given name and level
    
    Args:
        name (str): Logger name
        level: Logging level
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class
    """
    
    @property
    def logger(self):
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper


def log_performance(operation_name):
    """
    Context manager for logging performance of operations
    
    Args:
        operation_name (str): Name of the operation being timed
    
    Usage:
        with log_performance("database_query"):
            # Your code here
            pass
    """
    class PerformanceLogger:
        def __init__(self, name):
            self.name = name
            self.logger = get_logger(__name__)
            self.start_time = None
        
        def __enter__(self):
            self.start_time = datetime.now()
            self.logger.debug(f"Starting {self.name}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            execution_time = (datetime.now() - self.start_time).total_seconds()
            if exc_type is None:
                self.logger.debug(f"{self.name} completed in {execution_time:.3f}s")
            else:
                self.logger.error(f"{self.name} failed after {execution_time:.3f}s: {exc_val}")
    
    return PerformanceLogger(operation_name)


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()