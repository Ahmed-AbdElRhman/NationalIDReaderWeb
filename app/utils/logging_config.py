import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger  # For structured JSON logging
from dotenv import load_dotenv
from concurrent_log_handler import ConcurrentRotatingFileHandler


load_dotenv()

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['timestamp'] = record.created
        if not log_record.get('app_name'):
            log_record['app_name'] = os.getenv('APP_NAME', 'flask_app')

def setup_logging(app):
    """Configure logging for the application"""
    # Get configuration from environment variables with defaults
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'logxs/IDReader.log')
    max_log_size = int(os.getenv('MAX_LOG_SIZE_MB', 10)) * 1024 * 1024  # Convert MB to bytes
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 10))
    enable_console = os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() in ['true', '1', 't']
    enable_file = os.getenv('LOG_ENABLE_FILE', 'true').lower() in ['true', '1', 't']

    # Create Log directory and log file if they do not exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Ensure the log file exists
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            pass
    # Ensure the log file is writable
    if not os.access(log_file, os.W_OK):
        raise PermissionError(f"Log file '{log_file}' is not writable.")
    
    # Set up the root logger
    logging.basicConfig(level=logging.DEBUG)  # Set default level to DEBUG for initial setup
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set the log level
    numeric_level = getattr(logging, log_level, logging.INFO)
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    json_formatter = CustomJsonFormatter(
        # '%(timestamp)s %(level)s %(name)s %(message)s %(app_name)s'
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and add handlers
    handlers = []
    
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
    
    if enable_file:
        file_handler = ConcurrentRotatingFileHandler(
            filename=log_file,
            maxBytes=max_log_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
    '%(asctime)-22s  %(levelname)-7s  %(message)s Filename::%(filename)s:%(lineno)d '
))
        handlers.append(file_handler)
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configure Flask's logger
    if app:
        app.logger.handlers.clear()
        for handler in handlers:
            app.logger.addHandler(handler)
        app.logger.setLevel(numeric_level)
        app.logger.propagate = False
    
    # Example log messages to verify setup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.debug("Debug messages will only show if LOG_LEVEL=DEBUG")