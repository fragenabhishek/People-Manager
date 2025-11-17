"""
Logging utility module
Provides structured logging for the application
"""
import logging
import sys
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = 'people_manager',
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for log output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'people_manager') -> logging.Logger:
    """Get existing logger or create new one"""
    return logging.getLogger(name)

