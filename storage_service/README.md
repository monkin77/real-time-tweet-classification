# Python Data Storage Service

## 1. Project Overview

This service is the final link in our real-time disaster tweet identification pipeline. Its sole responsibility is to consume enriched, classified tweet messages from the `classified_tweets` topic, validate the data, and write it as a document to a MongoDB collection. This creates a persistent, queryable archive of all identified disaster-related events.

The service is designed to be a lightweight, resilient, and scalable background worker.

---

## 2. System Architecture & Data Flow

The service operates as a dedicated consumer in the data pipeline:

**`classified_tweets` Topic → Data Storage Service → MongoDB Database**

1.  **Consume:** The service subscribes to the `classified_tweets` topic (on either Redis or Kafka).
2.  **Deserialize & Validate:** For each incoming JSON message, it deserializes the data and validates its structure using Pydantic models. This ensures data integrity and prevents malformed documents from entering the database.
3.  **Store:** It connects to a MongoDB instance and inserts the validated data as a new document into a specified collection (e.g., `disaster_tweets`).

---

## 3. Tech Stack

* **Language:** Python 3.9+
* **Asynchronous Framework:** The service will be built using Python's native `asyncio` to handle I/O-bound tasks (consuming messages, database writes) efficiently.
* **Message Queue Clients:**
    * `redis-py` (async version) for Redis Pub/Sub.
    * `aiokafka` for a native asynchronous Kafka consumer.
* **Database Driver:** `PyMongo` for MongoDB, with `Motor` for asynchronous operations.
* **Data Validation:** `pydantic` for robust data modeling and validation.
* **Configuration:** `python-dotenv` for managing environment variables.

---

## 4. Project Structure

This structure provides a clean separation of concerns for each component of the service.

```
/storage-service
|
├── app/
│   ├── init.py
│   ├── main.py             # Main application entry point and lifespan events
│   ├── consumer.py         # Logic for consuming from Redis or Kafka
│   ├── database.py         # MongoDB connection and insertion logic
│   ├── models.py           # Pydantic models for data validation
│   └── config.py           # Configuration loading
|
├── .env.example            # Example environment variables
├── .gitignore
└── requirements.txt        # Python dependencies
```

---

## 5. Configuration (`.env.example`)

The service is configured entirely through environment variables. For local development, create a `.env` file from this template.

```ini
# Consumer Configuration (where to read from)
# Can be "redis" or "kafka"
CONSUMER_TYPE="redis"

# Redis Configuration
REDIS_ADDR="redis://localhost:6379"
REDIS_CHANNEL="classified_tweets"

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
KAFKA_CONSUMER_GROUP_ID="storage-group-1"
KAFKA_TOPIC="classified_tweets"

# MongoDB Configuration
MONGO_URI="mongodb://localhost:27017/"
MONGO_DATABASE="disaster_tweets_db"
MONGO_COLLECTION="tweets"
```