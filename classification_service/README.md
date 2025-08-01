# Go Model Inference Service
This service acts as the brain of the disaster tweet identification system. It consumes raw tweet messages from a message queue, classifies them by calling a machine learning model endpoint, and then publishes the enriched, classified data back to another queue for storage and analysis.

## Service Architecture & Data Flow
The service operates in a continuous loop with the following data flow:

`raw_tweets` Topic → **Inference Service** → `classified_tweets` Topic

1. **Consume**: The service subscribes to the **raw_tweets topic** (on either Redis or Kafka).

2. **Process**: For each incoming message, it deserializes the raw tweet JSON.

3. **Classify**: It sends the tweet's text to a separate Model Serving API via an HTTP POST request.

4. **Enrich**: It receives a classification (e.g., {"label": "disaster", "confidence": 0.98}) from the model API.

5. **Publish**: It combines the original tweet data with the new classification data into a new JSON object.

6. **Forward**: It publishes this enriched JSON object to the **classified_tweets topic**.

## Tech Stack
Language: **Python** (for the model API and inference service) 

**Message Queue Clients**:

- **Redis**: Redis Python client for Redis.

- **Kafka**: Confluent Kafka Python client for Kafka.

**Model Serving (to be built separately)**:

- **Python**: A REST API (e.g., built with `Python` and `FastAPI`) that serves your trained Transformer model.

- For initial development, this service includes a built-in Mock Model API.

**Configuration Management**: godotenv for .env file support.

## Project Skeleton & Structure
This structure separates concerns, making the service modular and testable.

```
/inference-service
|
├── cmd/
│   └── main.go             # Main application entry point & mock model API
|
├── internal/
│   ├── classifier/
│   │   └── classifier.go   # Logic to call the model API
│   ├── consumer/
│   │   ├── consumer.go     # Defines the Consumer interface
│   │   ├── redis_sub.go    # Redis implementation of the Consumer
│   │   └── kafka_sub.go    # Kafka implementation of the Consumer
│   ├── publisher/
│   │   ├── publisher.go    # Defines the Publisher interface
│   │   ├── redis_pub.go    # Redis implementation of the Publisher
│   │   └── kafka_pub.go    # Kafka implementation of the Publisher
│   └── config/
│       └── config.go       # Load and manage environment variables
|
├── .env.example            # Example environment variables
├── .gitignore
├── go.mod
├── go.sum
└── README.md               # This file
```

## Configuration (.env.example)
The service uses environment variables for all its configuration. Create a `.env` file from this template.

```bash
# Consumer Configuration (where to read from)
CONSUMER_TYPE="redis" # or "kafka"

# Publisher Configuration (where to write to)
PUBLISHER_TYPE="redis" # or "kafka"

# Redis Configuration
REDIS_ADDR="localhost:6379"
REDIS_PASSWORD=""
REDIS_SUB_CHANNEL="raw_tweets"
REDIS_PUB_CHANNEL="classified_tweets"

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
KAFKA_CONSUMER_GROUP_ID="inference-group-1"
KAFKA_SUB_TOPIC="raw_tweets"
KAFKA_PUB_TOPIC="classified_tweets"

# Model API Configuration
MODEL_API_ENDPOINT="http://localhost:8081/predict"

# Set to "true" to run the built-in mock model API on port 8081
RUN_MOCK_MODEL_API="true"
```

## Development Plan & How to Run
### Step 1: Set up Project
Initialize the Go module and install dependencies.

```bash
go mod init github.com/your-username/inference-service
go get github.com/go-redis/redis/v8
go get github.com/confluentinc/confluent-kafka-go/v2/kafka
go get github.com/joho/godotenv
```

### Step 2: Run the Mock Model API
For initial development, you don't need a real ML model. This service includes a mock API that you can enable.

1. Set RUN_MOCK_MODEL_API="true" in your .env file.
2. The main.go file will automatically start this mock server in the background. It listens on port 8081 and randomly classifies tweets.

### Step 3: Run the Inference Service
Launch the main application.

```bash
go run ./cmd/main.go
```

The service will connect to the message queue, start consuming **raw_tweets**, call the (mock) model API for classification, and publish the results to **classified_tweets**.

### Step 4: Integrate the Real Model (Future Step)
Once you have deployed your Python/FastAPI model server:

1. Set RUN_MOCK_MODEL_API="false" in your .env file.
2. Update MODEL_API_ENDPOINT to point to your real model's URL.
3. Restart the inference service. It will now make calls to your live model.