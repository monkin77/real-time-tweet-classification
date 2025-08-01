import asyncio
import json
import os
import random
import httpx
# import redis.asyncio as redis
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, HTTPException, on_event
from pydantic import BaseModel, Field
from typing import List

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
    label: str
    confidence: float

class ClassifiedTweet(BaseModel):
    """Represents the final, enriched data to be published."""
    id: str
    text: str
    label: str
    confidence: float


# --- FastAPI Application Setup ---
app = FastAPI(
    title="Inference Service",
    description="Consumes tweets, classifies them, and publishes the results.",
)

# Global clients that will be initialized on startup
# http_client: httpx.AsyncClient = None
# kafka_producer: AIOKafkaProducer = None
# redis_client: redis.Redis = None


# --- Lifespan Events (Startup and Shutdown) ---

@app.on_event("startup")
async def startup_event():
    """Initializes all necessary clients and starts the background consumer task."""
    global http_client, kafka_producer, redis_client
    
    print("--- Starting Inference Service ---")
    
    # Initialize a persistent HTTP client for making requests to the model API
    http_client = httpx.AsyncClient()
    
    # Initialize the appropriate publisher client based on config
    if PUBLISHER_TYPE == "kafka":
        print(f"Initializing Kafka producer for topic: {KAFKA_PUB_TOPIC}")
        kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        await kafka_producer.start()
    elif PUBLISHER_TYPE == "redis":
        print(f"Initializing Redis client for publishing to channel: {REDIS_PUB_CHANNEL}")
        redis_client = redis.from_url(REDIS_ADDR, decode_responses=True)
    
    # Start the message consumer as a background task
    print(f"Starting {CONSUMER_TYPE} consumer as a background task...")
    asyncio.create_task(run_consumer())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleans up resources on application shutdown."""
    print("--- Shutting Down Inference Service ---")
    if http_client:
        await http_client.aclose()
    if kafka_producer:
        await kafka_producer.stop()
    if redis_client:
        await redis_client.close()
    print("--- Shutdown Complete ---")


# --- Core Logic ---

async def classify_tweet(text: str) -> ClassificationResult:
    """Sends tweet text to the external ML model API for classification."""
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
    """Publishes the classified tweet to the appropriate message queue."""
    message = json.dumps(payload).encode("utf-8")
    if PUBLISHER_TYPE == "kafka" and kafka_producer:
        await kafka_producer.send_and_wait(KAFKA_PUB_TOPIC, message)
    elif PUBLISHER_TYPE == "redis" and redis_client:
        await redis_client.publish(REDIS_PUB_CHANNEL, message)


async def process_message(message_data: bytes):
    """The main processing pipeline for a single message."""
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


# --- Background Consumer Task ---

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
    consumer = AIOKafkaConsumer(
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
        await consumer.stop()


async def consume_from_redis():
    """Continuously consumes messages from a Redis Pub/Sub channel."""
    # Note: We create a new client here because the one for publishing
    # cannot be used for blocking pub/sub operations simultaneously.
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


# --- API Endpoint (for health checks) ---

@app.get("/")
def read_root():
    """A simple health check endpoint."""
    return {"status": "Inference Service is running"}

# To run this application:
# 1. Save it as `main.py`.
# 2. Install dependencies: pip install fastapi uvicorn httpx "redis[hiredis]" aiokafka
# 3. Set your environment variables (e.g., in a .env file and use a loader).
# 4. Run with uvicorn: uvicorn main:app --reload