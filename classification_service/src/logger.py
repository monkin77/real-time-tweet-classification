
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

log_level_to_int: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
def set_log_level(level: str) -> None:
    """
    Sets the logging level for the root logger.
    """
    log_level_param = log_level_to_int.get(level.upper(), logging.INFO)

    # Update the root logger's level
    global logger
    logger.setLevel(log_level_param)

    # Update console handler's level
    logger.handlers[0].setLevel(log_level_param)

    logger.info(f"--- Logging level set to {level.upper()} ({log_level_param})---\n")


# Create a default logger for the application
logger = get_logger(__name__)
