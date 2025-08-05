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
from pub_sub.publisher.kafka_pub import KafkaPub
from pub_sub.publisher.create_publisher import create_publisher

# --- Configuration ---
# Load configuration from environment variables
CONSUMER_TYPE = os.getenv("CONSUMER_TYPE", "redis")
PUBLISHER_TYPE = os.getenv("PUBLISHER_TYPE", "redis")
REDIS_ADDR = os.getenv("REDIS_ADDR", "redis://localhost:6379")
REDIS_SUB_CHANNEL = os.getenv("REDIS_SUB_CHANNEL", "raw_tweets")
REDIS_PUB_CHANNEL = os.getenv("REDIS_PUB_CHANNEL", "classified_tweets")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_CONSUMER_GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP_ID", "inference-group")
KAFKA_SUB_TOPIC = os.getenv("KAFKA_SUB_TOPIC", "raw_tweets")
KAFKA_PUB_TOPIC = os.getenv("KAFKA_PUB_TOPIC", "classified_tweets")
MODEL_API_ENDPOINT = os.getenv("MODEL_API_ENDPOINT", "http://localhost:8001/predict")


# --- Pydantic Models for Data Validation ---

class RawTweetData(BaseModel):
    """Represents the 'data' field of an incoming raw tweet message."""
    id: str
    text: str

class RawTweet(BaseModel):
    """Represents the full structure of an incoming raw tweet message."""
    data: RawTweetData

class ClassificationResult(BaseModel):
    """Represents the response from the ML model API."""
    label: str  # TODO: Define the possible labels with an Enum
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
async def startup_handler():
    '''
    Lifespan context manager to handle startup and shutdown events.
    Async keyword is used to allow asynchronous operations during startup.
    '''
    print("--- Starting Inference Service ---")

    global http_client, producer
    
    print("--- Starting Inference Service ---")
    
    # Initialize a persistent HTTP client for making requests to the model API
    http_client = httpx.AsyncClient()
    
    # Initialize the appropriate publisher client based on config
    producer = create_publisher(
        publisher_type=PUBLISHER_TYPE,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )
    
    # Start the message consumer as a background task
    print(f"Starting {CONSUMER_TYPE} consumer as a background task...")
    asyncio.create_task(run_consumer()) # This will run indefinitely in the background


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
        response = await http_client.post(MODEL_API_ENDPOINT, json={"text": text}, timeout=10.0)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return ClassificationResult(**data)
    except httpx.RequestError as e:
        print(f"Error calling model API: {e}")
        # In a real system, you might want to return a default/error state
        # or have a retry mechanism.
        return ClassificationResult(label="classification_error", confidence=0.0)


async def publish_message(payload: dict):
    """
    Publishes the classified tweet to the appropriate message queue.
    """
    # Convert the payload to a JSON byte string
    message = json.dumps(payload).encode("utf-8")

    # Send the message to the appropriate publisher based on configuration
    print(f"TODO: Publish message to {PUBLISHER_TYPE} channel/topic")
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
    try:
        # 1. Parse and validate the incoming message
        raw_tweet = RawTweet.parse_raw(message_data)
        
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
        await publish_message(classified_tweet.dict())
        
        print(f"Successfully processed and published tweet ID: {classified_tweet.id}")

    except Exception as e:
        print(f"Failed to process message. Error: {e}. Message: {message_data[:200]}...")

# ---------------------------------------------------
# ---------- Background Consumer Task ---------------
# ---------------------------------------------------
async def run_consumer():
    """Runs the appropriate consumer based on the environment configuration."""
    if CONSUMER_TYPE == "kafka":
        await consume_from_kafka()
    elif CONSUMER_TYPE == "redis":
        await consume_from_redis()
    else:
        print(f"Error: Invalid CONSUMER_TYPE '{CONSUMER_TYPE}'. Exiting.")


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

async def consume_from_redis():
    """Continuously consumes messages from a Redis Pub/Sub channel."""
    # Note: We create a new client here because the one for publishing
    # cannot be used for blocking pub/sub operations simultaneously.

    """ 
    sub_client = redis.from_url(REDIS_ADDR)
    pubsub = sub_client.pubsub()
    await pubsub.subscribe(REDIS_SUB_CHANNEL)
    print(f"Redis consumer subscribed to channel '{REDIS_SUB_CHANNEL}'. Waiting for messages...")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await process_message(message["data"])
    finally:
        await sub_client.close() 
    """
    pass


# --- API Endpoints ---

@app.get("/")
async def root():
    """A simple health check endpoint."""
    return {"status": "Inference Service is running"}


