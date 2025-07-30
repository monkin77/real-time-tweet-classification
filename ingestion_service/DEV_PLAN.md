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

## 4. How to Set Up and Run
**Step 1: Initialize Go Module**

In your terminal, inside the ingestion-service directory, initialize the Go module.

```bash
go mod init github.com/your-username/ingestion-service
```

**Step 2: Install Dependencies**
Get the necessary Go libraries.

```
# Redis client
go get github.com/go-redis/redis/v8

# Kafka client (requires librdkafka)
# See https://github.com/confluentinc/confluent-kafka-go for installation details
go get github.com/confluentinc/confluent-kafka-go/v2/kafka

# For loading .env files
go get github.com/joho/godotenv
```

**Step 3: Running the Service**
The application is run from the cmd directory.

```bash
go run ./cmd/main.go
```

The service will:

1. Load configuration from the .env file.
2. Check the DEV_MOCK_STREAM flag.
3. Initialize the specified publisher (Redis or Kafka).
4. Start streaming tweets (either from the live API or a local file) and publish them.

## 5. Development vs. Production (Mocking the Stream)
To avoid hitting X API rate limits during development, the service includes a mock streamer.

### How it works:

- When `DEV_MOCK_STREAM` is set to `"true"` in your .env file, the service will not connect to the X API.

- Instead, it will read from a local file (e.g., `tweets.csv` from the Kaggle competition) and publish each line to the message queue on a timer, simulating a live stream.

- This allows you to develop and test the entire downstream pipeline (inference, storage, dashboard) without making a single live API call.

### To use the mock streamer:

1. Place your tweets.csv file in the project's root directory.
2. Set DEV_MOCK_STREAM="true" in your .env file.
3. Implement the file-reading logic within your twitter/stream.go file, guarded by a check for the config flag.

---

This README provides a complete starting point. You can now begin to fill in the Go code for each file, starting with the configuration, then the publisher, and finally the streaming logic.