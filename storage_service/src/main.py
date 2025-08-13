# /storage_service/src/main.py - Entry Point for the Storage Service
from config import Config
from pymongo import MongoClient
from logger import logger, set_log_level
from subscriber.create_subscriber import create_subscriber
import asyncio

# Load the Configuration from the Environment Variables
cfg = Config()
logger.info(f"Configuration loaded: {cfg.__dict__}")

# -----------------------------------------------------
# -------------- Logger Initialization ----------------
# -----------------------------------------------------
# Set the logger level based on the configuration. Defaults to INFO if not set.
set_log_level(cfg.LOG_LEVEL)


# Connect to MongoDB
db_client = MongoClient(cfg.MONGO_URI)
db = db_client[cfg.MONGO_DATABASE]  # Access the specified database
collection = db[cfg.MONGO_COLLECTION]  # Access the specified collection

# Print a message to confirm connection
logger.info(f"Connected to MongoDB at {cfg.MONGO_URI}, using database '{cfg.MONGO_DATABASE}' and collection '{cfg.MONGO_COLLECTION}'.")


# -----------------------------------------------------
# -------------- Initialize Subscriber ----------------
# -----------------------------------------------------
subscriber = create_subscriber(
    subscriber_type=cfg.CONSUMER_TYPE,
    base_url=cfg.CONSUMER_BASE_URL,
    port=cfg.CONSUMER_PORT,
    topic=cfg.CONSUMER_TOPIC
)

# -----------------------------------------------------
# -------------- Define Msg Processing ----------------
# -----------------------------------------------------
async def process_message(message_data: bytes):
    """
    The main processing pipeline for a single message.
    """
    logger.debug(f"Processing message: {message_data[:250]}...")  # Print first 200 chars for brevity

    try:
        logger.debug("TODO")
    except Exception as e:
        logger.error(f"Failed to process message. Error: {e}. Message: {message_data[:200]}...")

# -----------------------------------------------------
# -------------- Define Background Tasks --------------
# -----------------------------------------------------
async def run_consumer():
    '''
    Run the message consumer. 
    This function will continuously listen for message on the specified
    topic and process them.
    '''
    try:
        async for message in subscriber.consume():
            # Process each message as it arrives from the subscriber
            await process_message(message)
    except Exception as e:
        logger.error(f"Error in consumer loop: {e}")
    finally:
        # Ensure the subscriber is closed properly
        await subscriber.close()
        logger.info("Subscriber closed successfully.")


# -----------------------------------------------------
# -------------- Start Background Tasks ---------------
# -----------------------------------------------------
# Run the consumer in an asyncio event loop
if __name__ == "__main__":
    try:
        logger.info("Starting the Storage Service consumer...")
        asyncio.run(run_consumer())
    except KeyboardInterrupt:
        logger.info("Storage Service consumer stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Close the MongoDB connection gracefully
        db_client.close()
        logger.info("MongoDB connection closed. Exiting Storage Service.")

        # Close the subscriber if it was initialized
        if subscriber:
            asyncio.run(subscriber.close())
            logger.info("Subscriber closed successfully.")