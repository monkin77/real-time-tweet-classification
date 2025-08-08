import os
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    '''Custom exception for configuration errors.'''
    pass

class Config:
    # Define all variables with defaults set to None or as appropriate
    
    # Define the Types of Consumer and Publisher
    PUB_SUB_TYPE: Optional[str] = None  # 'kafka' or 'redis'
    CONSUMER_TOPIC: Optional[str] = None
    PUBLISHER_TOPIC: Optional[str] = None

    STREAM_BASE_URL: Optional[str] = None
    STREAM_PORT: Optional[int] = None
    STREAM_ADDR: Optional[str] = None  # This will be constructed as "STREAM_BASE_URL:STREAM_PORT"

    # Redis configuration
    REDIS_PASSWORD: Optional[str]

    # Kafka configuration
    KAFKA_CONSUMER_GROUP_ID: Optional[str]

    # AI Model API configuration
    SV_BASE_URL: str
    SV_PORT: int
    MODEL_API_ENDPOINT: str

    # Logging configuration
    LOG_LEVEL: str

    def __init__(self):
        load_dotenv(override=True)

        # Required fields (always required)
        self.PUB_SUB_TYPE = self._require("PUB_SUB_TYPE", choices={"kafka", "redis"})
        self.SV_BASE_URL = self._require("SV_BASE_URL")
        self.SV_PORT = int(self._require("SV_PORT"))
        # Validate the AI Model API Endpoint
        if not self.SV_BASE_URL or not self.SV_PORT:
            raise ConfigError("SV_BASE_URL and SV_PORT must be set and valid")
        self.MODEL_API_ENDPOINT = f"{self.SV_BASE_URL}:{self.SV_PORT}/predict"
        
        """ self.RUN_MOCK_MODEL_API = self._cast_bool(
            # Default to 'false' if not set
            os.getenv("RUN_MOCK_MODEL_API", "false")
        ) """

        # Check the Stream Base URL and Port
        self.STREAM_BASE_URL = self._require("STREAM_BASE_URL")
        self.STREAM_PORT = int(self._require("STREAM_PORT"))
        # Validate the Stream Address
        if not self.STREAM_BASE_URL or not self.STREAM_PORT:
            raise ConfigError("STREAM_BASE_URL and STREAM_PORT must be set and valid")
        self.STREAM_ADDR = f"{self.STREAM_BASE_URL}:{self.STREAM_PORT}"


        # Conditionally required fields (based on type)
        if self.PUB_SUB_TYPE == "kafka":
            self.KAFKA_CONSUMER_GROUP_ID = self._require("KAFKA_CONSUMER_GROUP_ID")
        else:
            self.KAFKA_CONSUMER_GROUP_ID = None

        # Validate the Channel Topics
        self.CONSUMER_TOPIC = self._require("CONSUMER_TOPIC")
        self.PUBLISHER_TOPIC = self._require("PUBLISHER_TOPIC")

        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

        # Logging configuration
        self.LOG_LEVEL = self._require("LOG_LEVEL", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
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
