import asyncio
import json
import os
import random
import httpx
# import redis.asyncio as redis
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from pub_sub.publisher.publisher import Publisher
from pub_sub.publisher.create_publisher import create_publisher
from pub_sub.subscriber.subscriber import Subscriber
from pub_sub.subscriber.create_subscriber import create_subscriber
from config import Config
from enum import Enum

# --- Configuration ---
config = Config()

print(f"Configuration loaded: {config.__dict__}")

# Load configuration from environment variables
""" CONSUMER_TYPE = os.getenv("CONSUMER_TYPE", "redis")
PUBLISHER_TYPE = os.getenv("PUBLISHER_TYPE", "redis")
REDIS_ADDR = os.getenv("REDIS_ADDR", "redis://localhost:6379")
REDIS_SUB_CHANNEL = os.getenv("REDIS_SUB_CHANNEL", "raw_tweets")
REDIS_PUB_CHANNEL = os.getenv("REDIS_PUB_CHANNEL", "classified_tweets")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP_ID", "inference-group")
KAFKA_SUB_TOPIC = os.getenv("KAFKA_SUB_TOPIC", "raw_tweets")
KAFKA_PUB_TOPIC = os.getenv("KAFKA_PUB_TOPIC", "classified_tweets")
MODEL_API_ENDPOINT = os.getenv("MODEL_API_ENDPOINT", "http://localhost:8001/predict") """


# --- Pydantic Models for Data Validation ---

class RawTweetData(BaseModel):
    """Represents the 'data' field of an incoming raw tweet message."""
    id: str = Field(..., alias="id", description="Unique identifier for the tweet")
    text: str = Field(..., alias="text", description="Text content of the tweet")
    created_at: str = Field(..., alias="created_at", description="Timestamp when the tweet was created")
    author_id: str = Field(..., alias="author_id", description="ID of the user who authored the tweet")
    username: str = Field(..., alias="username", description="Username of the author")


class RawTweet(BaseModel):
    """Represents the full structure of an incoming raw tweet message."""
    data: RawTweetData


class ClassifLabel(str, Enum):
    """Enum for classification labels."""
    DISASTER = "disaster"
    NON_DISASTER = "non-disaster"
    CLASSIFICATION_ERROR = "classification_error"

class ClassificationResult(BaseModel):
    """Represents the response from the ML model API."""
    label: ClassifLabel = Field(..., description="Classification label", )  
    confidence: float


class ClassifiedTweet(BaseModel):
    """Represents the final, enriched data to be published."""
    id: str
    text: str
    label: str
    confidence: float


# -----------------------------------------------------
# --- Lifespan Server Events (Startup and Shutdown) ---
# -----------------------------------------------------
http_client: httpx.AsyncClient
producer: Publisher
subscriber: Subscriber


async def startup_handler():
    '''
    Lifespan context manager to handle startup and shutdown events.
    Async keyword is used to allow asynchronous operations during startup.
    '''
    print("--- Starting Inference Service ---")

    global http_client, producer, subscriber

    # Initialize a persistent HTTP client for making requests to the model API
    http_client = httpx.AsyncClient()

    # Initialize the appropriate publisher client based on config
    producer = create_publisher(
        publisher_type=config.PUB_SUB_TYPE,
        bootstrap_servers=config.STREAM_ADDR
    )

    # Initialize the appropriate subscriber client based on config
    subscriber = create_subscriber(
        subscriber_type=config.PUB_SUB_TYPE,
        base_url=config.STREAM_BASE_URL,
        port=config.STREAM_PORT,
        topic=config.CONSUMER_TOPIC
    )

    # Start the message consumer as a background task
    print(f"Starting {config.PUB_SUB_TYPE} consumer as a background task...")
    # This will run indefinitely in the background
    asyncio.create_task(run_consumer())


async def shutdown_handler():
    """Cleans up resources on application shutdown."""
    print("--- Shutting Down Inference Service... ---")

    if http_client:
        await http_client.aclose()
    if producer:
        await producer.close()

    print("--- Shutdown Complete ---")


# -------------------------------------
# --- FastAPI Server Initialization ---
# -------------------------------------
app = FastAPI(
    title="Inference Service",
    description="Consumes tweets, classifies them, and publishes the results.",
    on_startup=[startup_handler],
    on_shutdown=[shutdown_handler]
)

# Global clients that will be initialized on startup
http_client: httpx.AsyncClient = None
# kafka_producer: AIOKafkaProducer = None
# redis_client: redis.Redis = None


# -------------------------------------
# ---------- Core Logic ---------------
# -------------------------------------
async def classify_tweet(text: str) -> ClassificationResult:
    """
    Sends tweet text to the external ML model API for classification.
    """
    try:
        # MOCK Response
        return ClassificationResult(
            label=random.choice([ClassifLabel.DISASTER, ClassifLabel.NON_DISASTER]),
            confidence=random.uniform(0.5, 1.0)
        )

        """ response = await http_client.post(config.MODEL_API_ENDPOINT, json={"text": text}, timeout=10.0)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return ClassificationResult(**data) """
    except httpx.RequestError as e:
        print(f"Error calling model API: {e}")
        # In a real system, you might want to return a default/error state
        # or have a retry mechanism.
        return ClassificationResult(label=ClassifLabel.CLASSIFICATION_ERROR, confidence=0.0)


async def publish_message(payload: dict):
    """
    Publishes the classified tweet to the appropriate message queue.
    """
    # Convert the payload to a JSON byte string
    message = json.dumps(payload).encode("utf-8")

    # Send the message to the appropriate publisher based on configuration
    print(f"TODO: Publish message to {config.PUB_SUB_TYPE} channel/topic")

    await producer.publish(config.PUBLISHER_TOPIC, message)
    """
    if PUBLISHER_TYPE == "kafka" and kafka_producer:
        await kafka_producer.send_and_wait(KAFKA_PUB_TOPIC, message)
    elif PUBLISHER_TYPE == "redis" and redis_client:
        await redis_client.publish(REDIS_PUB_CHANNEL, message)
    """


async def process_message(message_data: bytes):
    """
    The main processing pipeline for a single message.
    """
    print(f"Processing message: {message_data[:200]}...")  # Print first 200 chars for brevity

    try:
        # 1. Parse and validate the incoming message - Deserialize the JSON data
        data_obj = json.loads(message_data.decode("utf-8"))
        raw_tweet = RawTweet.model_validate(
            data_obj,
            strict=True
        )

        # 2. Classify the tweet text by calling the model API
        classification = await classify_tweet(raw_tweet.data.text)

        # 3. Create the enriched payload
        classified_tweet = ClassifiedTweet(
            id=raw_tweet.data.id,
            text=raw_tweet.data.text,
            label=classification.label,
            confidence=classification.confidence,
        )

        # 4. Publish the classified tweet
        # Convert the classified tweet to a dictionary and publish it
        classif_tweet_dict = classified_tweet.model_dump()
        await publish_message(classif_tweet_dict)

        print(
            f"Successfully processed and published tweet ID: {classified_tweet.id}")

    except Exception as e:
        print(
            f"Failed to process message. Error: {e}. Message: {message_data[:200]}...")

# ---------------------------------------------------
# ---------- Background Consumer Task ---------------
# ---------------------------------------------------


async def run_consumer():
    """Runs the appropriate consumer based on the environment configuration."""
    try:
        async for message in subscriber.consume():
            # Process each messages as it arrives from the subscriber via the async Generator.
            await process_message(message)
    except Exception as e:
        print(f"Error in consumer loop: {e}")
    finally:
        await subscriber.close()


async def consume_from_kafka():
    """Continuously consumes messages from a Kafka topic."""
    """ consumer = AIOKafkaConsumer(
        KAFKA_SUB_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP_ID,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    print(f"Kafka consumer started for topic '{KAFKA_SUB_TOPIC}'. Waiting for messages...")
    try:
        async for msg in consumer:
            await process_message(msg.value)
    finally:
        await consumer.stop() """
    pass


# --- API Endpoints ---

@app.get("/")
async def root():
    """A simple health check endpoint."""
    return {"status": "Inference Service is running"}
