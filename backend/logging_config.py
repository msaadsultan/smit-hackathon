import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Set up a logger with both file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        logs_dir / f"{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers for different components
api_logger = setup_logger("api")
db_logger = setup_logger("database")
auth_logger = setup_logger("auth")
ai_logger = setup_logger("ai")