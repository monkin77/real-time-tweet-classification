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

    # Redis configuration
    REDIS_ADDR: Optional[str]
    REDIS_PASSWORD: Optional[str]

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS: Optional[str]
    KAFKA_CONSUMER_GROUP_ID: Optional[str]

    # AI Model API configuration
    MODEL_API_ENDPOINT: str
    RUN_MOCK_MODEL_API: bool

    def __init__(self):
        load_dotenv(override=True)

        # Required fields (always required)
        self.PUB_SUB_TYPE = self._require("PUB_SUB_TYPE", choices={"kafka", "redis"})
        self.MODEL_API_ENDPOINT = self._require("MODEL_API_ENDPOINT")
        self.RUN_MOCK_MODEL_API = self._cast_bool(
            # Default to 'false' if not set
            os.getenv("RUN_MOCK_MODEL_API", "false")
        )

        # Conditionally required fields (based on type)
        if self.PUB_SUB_TYPE == "kafka":
            self.KAFKA_BOOTSTRAP_SERVERS = self._require("KAFKA_BOOTSTRAP_SERVERS")
        else:
            self.KAFKA_BOOTSTRAP_SERVERS = None

        if self.PUB_SUB_TYPE == "kafka":
            self.KAFKA_CONSUMER_GROUP_ID = self._require("KAFKA_CONSUMER_GROUP_ID")
        else:
            self.KAFKA_CONSUMER_GROUP_ID = None

        if self.PUB_SUB_TYPE == "redis":
            self.REDIS_ADDR = self._require("REDIS_ADDR")
        else:
            self.REDIS_ADDR = None

        # Validate the Channel Topics
        self.CONSUMER_TOPIC = self._require("CONSUMER_TOPIC")
        self.PUBLISHER_TOPIC = self._require("PUBLISHER_TOPIC")

        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    def _require(self, key, choices=None):
        val = os.getenv(key)
        if not val:
            raise ConfigError(f"Missing required config variable: {key}")
        if choices and val not in choices:
            raise ConfigError(f"{key} must be one of {choices}, got '{val}'")
        return val

    def _cast_bool(self, val) -> bool:
        return str(val).strip().lower() in {"1", "true", "yes"}
    
    def get_stream_url(self) -> str:
        '''
        Returns the stream URL based on the PUB_SUB_TYPE.
        '''
        if self.PUB_SUB_TYPE == "kafka":
            return self.KAFKA_BOOTSTRAP_SERVERS
        elif self.PUB_SUB_TYPE == "redis":
            return self.REDIS_ADDR
        else:
            raise ValueError(f"Unsupported publisher type: {self.PUB_SUB_TYPE}")



# Usage:
# from config import Config, ConfigError
# config = Config()
