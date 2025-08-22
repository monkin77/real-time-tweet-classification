# Go Data Ingestion Service
This service is responsible for connecting to the X (Twitter) API v2, consuming the real-time filtered tweet stream, and publishing the data to a message queue for downstream processing. It is written in Go for high performance and reliability.

## 1. Tech Stack
**Language**: Go (version 1.18+)

**X API Communication**: We will use Go's native net/http client to connect to the X API v2 streaming endpoint. While some third-party libraries exist, the direct approach gives us full control and avoids external dependencies for a critical task.

**Pub/Sub (Message Queue)**:
- For Development: Redis Pub/Sub using the go-redis/redis library. It's lightweight and perfect for rapid development.
- For Production: Apache Kafka using the official Confluent Go client, confluent-kafka-go. It's built for high-throughput, persistent, and scalable messaging.

**Configuration Management**: godotenv for loading environment variables from a .env file during development.

## 2. Project Skeleton & Structure
This structure organizes the code logically, making it easy to manage and test. You can create these folders and files in VS Code to get started.

```
/ingestion_service
|
├── cmd/
│   └── main.go             # Main application entry point
|
├── internal/
│   ├── config/
│   │   └── config.go       # Load and manage environment variables
│   ├── publisher/
│   │   ├── publisher.go    # Defines the Publisher interface
│   │   ├── redis_pub.go    # Redis implementation of the Publisher
│   │   └── kafka_pub.go    # Kafka implementation of the Publisher
│   └── twitter/
│       └── stream.go       # Logic for connecting and streaming from X API
|
├── .env.example            # Example environment variables
├── .gitignore
├── go.mod                  # Go module dependencies
├── go.sum
└── README.md               # This file
```

## 3. Configuration
The service is configured using environment variables. For local development, create a .env file by copying the `.env.example` file:

```
# X (Twitter) API Credentials
# Get these from your Twitter Developer Portal
TWITTER_BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"

# Publisher Configuration
# PUBLISHER_TYPE can be "redis" or "kafka"
PUBLISHER_TYPE="redis"

# Redis Configuration (if PUBLISHER_TYPE is "redis")
REDIS_ADDR="localhost:6379"
REDIS_PASSWORD=""
REDIS_CHANNEL="raw_tweets"

# Kafka Configuration (if PUBLISHER_TYPE is "kafka")
KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
KAFKA_TOPIC="raw_tweets"

# Development Mode
# SET to "true" to use the mock streamer (reads from a local file)
DEV_MOCK_STREAM="true"
```

## 4. How to Run
The application is run from the root directory.

Before running the client, ensure you have the Redis/Kafka server running for development purposes. You can use the provided `build_redis_server.sh` or `build_kafka_server.sh` scripts to start a Redis or Kafka server in a Docker container.

### Data Ingestion Client
```bash
./client.sh
```

### Mock X API Server
```bash
./mock_server.sh
```