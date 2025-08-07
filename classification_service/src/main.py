import asyncio
import json
import random
import httpx
# import redis.asyncio as redis
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, HTTPException
from typing import List
from pub_sub.publisher.publisher import Publisher
from pub_sub.publisher.create_publisher import create_publisher
from pub_sub.subscriber.subscriber import Subscriber
from pub_sub.subscriber.create_subscriber import create_subscriber
from config import Config
from models import RawTweetData, ClassifiedTweet, ClassificationResult, ClassifLabel, RawTweet, PredictTweet


# -----------------------------------------------------
# ---------------------- Configuration ----------------
# -----------------------------------------------------
config = Config()
print(f"Configuration loaded: {config.__dict__}")

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
        base_url=config.STREAM_BASE_URL,
        port=config.STREAM_PORT
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
# TODO: Define the URL for the server?
app = FastAPI(
    title="Inference Service",
    description="Consumes tweets, classifies them, and publishes the results.",
    on_startup=[startup_handler],
    on_shutdown=[shutdown_handler]
)


# -------------------------------------
# ---------- Core Logic ---------------
# -------------------------------------
async def classify_tweet(text: str) -> ClassificationResult:
    """
    Sends tweet text to the external ML model API for classification.

    :param text: The tweet text to be classified.

    :return: ClassificationResult containing the label and confidence score.
    """
    USE_MOCK = False

    try:
        if USE_MOCK:
            # MOCK Response
            return ClassificationResult(
                label=random.choice([ClassifLabel.DISASTER, ClassifLabel.NON_DISASTER]),
                confidence=random.uniform(0.5, 1.0)
            )
    
        # Call the model API to classify the tweet text
        response = await http_client.post(config.MODEL_API_ENDPOINT, json={"text": text}, timeout=10.0)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return ClassificationResult(**data)
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
    num_subscribers = await producer.publish(config.PUBLISHER_TOPIC, message)

    # Could try to resend the message if no subscribers are available
    if num_subscribers == 0:
        print(f"No subscribers for topic '{config.PUBLISHER_TOPIC}'. Message not received.")


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

# ---------------------------
# ------ API Endpoints ------
#----------------------------
@app.get("/")
async def root():
    """A simple health check endpoint."""
    return {"status": "Inference Service is running"}

@app.post("/predict", response_model=ClassifiedTweet)
async def predict(tweet: PredictTweet) -> ClassifiedTweet:
    '''
    Endpoint to classify a tweet as Disaster or Non-Disaster.
    :param tweet: The tweet text to classify.

    :return: The classified tweet with label and confidence.
    '''
    print(f"Received tweet for classification: {tweet.text[:100]}...")

    # 1. Classify the tweet text by calling the model API
    classification = await classify_tweet(tweet.text)
    print(f"Classification result: {classification}")

    # 2. Create the enriched payload
    classified_tweet = ClassifiedTweet(
        id=tweet.id,
        text=tweet.text,
        label=classification.label,
        confidence=classification.confidence,
    )

    # Send the classified tweet to the Client
    return classified_tweet