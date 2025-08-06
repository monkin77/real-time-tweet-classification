# Model Inference Service
This service acts as the brain of the disaster tweet identification system. It consumes raw tweet messages from a message queue, classifies them by calling a machine learning model endpoint, and then publishes the enriched, classified data back to another queue for storage and analysis.

## Service Architecture & Data Flow
The service operates in a continuous loop with the following data flow:

`raw_tweets` Topic → **Inference Service** → `classified_tweets` Topic

1.  **Consume**: The service subscribes to the **raw_tweets topic** (on either Redis or Kafka).

2.  **Process**: For each incoming message, it deserializes the raw tweet JSON.

3.  **Classify**: It sends the tweet's text to a separate Model Serving API via an HTTP POST request.

4.  **Enrich**: It receives a classification (e.g., `{"label": "disaster", "confidence": 0.98}`) from the model API.

5.  **Publish**: It combines the original tweet data with the new classification data into a new JSON object.

6.  **Forward**: It publishes this enriched JSON object to the **classified_tweets topic**.

## Tech Stack
*   **Language**: Python
*   **Framework**: FastAPI
*   **Message Queue Clients**:
    *   `redis-py` (asyncio) for Redis
    *   `aiokafka` for Kafka
*   **Configuration**: Pydantic
*   **Dependency Management**: Poetry

## Project Structure
```
/classification_service
|
├── .venv/                  # Virtual environment
├── src/
│   ├── main.py             # Main application entry point & FastAPI server
│   ├── config.py           # Pydantic configuration settings
│   └── pub_sub/
│       ├── publisher/
│       │   ├── publisher.py
│       │   ├── create_publisher.py
│       │   ├── kafka_pub.py
│       │   └── redis_pub.py
│       └── subscriber/
│           ├── subscriber.py
│           ├── create_subscriber.py
│           ├── kafka_sub.py
│           └── redis_sub.py
|
├── .env.example            # Example environment variables
├── .gitignore
├── pyproject.toml          # Project metadata and dependencies
├── poetry.lock             # Exact versions of dependencies
└── README.md               # This file
```

## Configuration (`.env.example`)
The service uses environment variables for all its configuration. Create a `.env` file from the `.env.example` template.

```bash
# General Pub/Sub Configuration
# Defines which messaging system to use ("redis" or "kafka")
PUB_SUB_TYPE="redis"

# Common Stream/Queue Configuration
STREAM_BASE_URL="localhost" # For Redis, this is the host; for Kafka, the bootstrap server
STREAM_PORT=6379
STREAM_ADDR="localhost:9092" # Used for Kafka bootstrap servers

# Consumer (Subscriber) Configuration
CONSUMER_TOPIC="raw_tweets"
CONSUMER_GROUP_ID="inference-group" # Kafka-specific group ID

# Publisher Configuration
PUBLISHER_TOPIC="classified_tweets"

# Model API Endpoint
MODEL_API_ENDPOINT="http://localhost:8001/predict"
```

## How to Run

### 1. Set Up a Local Redis Instance
The easiest way to run Redis locally is with Docker.

```bash
docker run -d -p 6379:6379 --name redis-disaster-tweets redis/redis-stack:latest
```
This command will start a Redis container in the background and map its port 6379 to your local machine.

### 2. Install Dependencies
This project uses Poetry for dependency management.

```bash
# Install poetry if you haven't already
pip install poetry

# Install project dependencies
poetry install
```

### 3. Configure the Environment
Create a `.env` file by copying the `.env.example`.

```bash
cp .env.example .env
```
The default settings are configured to use Redis on `localhost:6379`, which matches the Docker command above.

### 4. Run the Service
You can run the FastAPI application using:

```bash
fastapi dev src/main.py
```
The service will now be running and connected to your local Redis instance. It will:
- Subscribe to the `raw_tweets` channel.
- Process messages as they arrive.
- Publish classified results to the `classified_tweets` channel.
