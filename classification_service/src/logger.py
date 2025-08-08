
import logging
import sys

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a handler to write logs to the console
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

# Create a default logger for the application
logger = get_logger(__name__)
