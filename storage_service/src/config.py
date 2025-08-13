import os
from typing import Optional
from dotenv import load_dotenv

class ConfigError(Exception):
    '''Custom exception for configuration errors.'''
    pass

class Config:
    # Define all variables with defaults set to None or as appropriate
    def __init__(self):
        load_dotenv(override=True)

        # Required fields (always required)
        self.CONSUMER_TYPE = self._require("CONSUMER_TYPE", choices={"redis", "kafka"})
        self.CONSUMER_TOPIC = self._require("CONSUMER_TOPIC")
        self.CONSUMER_BASE_URL = self._require("CONSUMER_BASE_URL")
        self.CONSUMER_PORT = int(self._require("CONSUMER_PORT"))

        self.MONGO_URI = self._require("MONGO_URI")
        self.MONGO_DATABASE = self._require("MONGO_DATABASE")
        self.MONGO_COLLECTION = self._require("MONGO_COLLECTION")

        # Logging configuration
        self.LOG_LEVEL = self._require("LOG_LEVEL",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
    def _require(self, key, choices=None):
        val = os.getenv(key)
        if not val:
            raise ConfigError(f"Missing required config variable: {key}")
        if choices and val not in choices:
            raise ConfigError(f"{key} must be one of {choices}, got '{val}'")
        return val

    def _cast_bool(self, val) -> bool:
        return str(val).strip().lower() in {"1", "true", "yes"}
    



# Usage:
# from config import Config, ConfigError
# config = Config()
