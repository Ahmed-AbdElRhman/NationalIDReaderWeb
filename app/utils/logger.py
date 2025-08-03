import logging

def get_logger(name):
    """Get a configured logger instance with the given name"""
    logger = logging.getLogger(name)
    return logger