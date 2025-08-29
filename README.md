# Real-Time Disaster Tweet Identification System

## 1. Project Overview

This project is a real-time data pipeline designed to identify tweets reporting on real-world disasters. It leverages a **Transformer-based NLP model** to classify tweets as either "disaster" or "not disaster." The system is architected to be scalable, resilient, and provide real-time insights.

The primary goal is to move a machine learning model from a research environment (like a Kaggle notebook) into a live, production-like system that processes data as it's generated.

---

## 2. System Architecture

The system is composed of four main components that work together in a pipeline:

1.  **Data Ingestion (`ingestion_service`):** A Python service that connects to the *X (Twitter) API's real-time filtered strea*m. It listens for tweets containing disaster-related keywords and publishes them to a message queue.

2.  **Message Queue (`message_broker`):** A message broker (like *Apache Kafka* or *Redis Pub/Sub*) that acts as a buffer. It is responsible for transporting messages between microsservices, related to *raw tweets* *classified tweets*.

3.  **Model Inference (`classification_service`):** A worker service that consumes tweets from the *raw_tweets* message queue. It preprocesses the tweet text and sends it to a model serving API. The model, wrapped in a REST API, returns a prediction, which is then attached to the tweet data and published to another message queue *classified_tweets*. The model was trained using a Transformer architecture (like BERT or DistilBERT) and fine-tuned on a labeled dataset of disaster-related tweets from a Kaggle competition. The following [GitHub repository](https://github.com/monkin77/llm-learn/tree/master/nlp_disaster_tweets) includes the code used for training and fine-tuning the model.

4.  **Data Storage & Visualization (`storage_service` and `visualization_service`):** The final destination for the classified data.
    * **Database:** A database (**MongoDB**) stores the tweet, its classification, and other metadata.
    * **Dashboard:** A visualization tool (**Grafana**) connects to the database to display real-time analytics, such as trend graphs, nº disaster tweets over time, and alerts for high activity.

5. **Mock X API Server (`mock_x_api`):** For development and testing purposes, a mock server simulates the X API's behavior, allowing the ingestion service to be tested without needing live access to the X API. This allows extensive testing without hitting rate limits.

---

## 3. Tech Stack

* **Programming Languages:** Python 3.9+, Golang, MongoDB Query Language.
* **Data Ingestion:** Tweepy, X API v2, Golang.
* **Message Queue:** Apache Kafka / Redis Pub/Sub for simplicity
* **Model Serving:** FastAPI and Keras/TensorFlow
* **Database:** MongoDB
* **Dashboard:** Grafana
* **Containerization:** Docker, Docker Compose

---

## 4. Project Structure
```
/real-time-disaster-tweets
|
├── docker-compose.yml
|
├── ingestion_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py             # Connects to X API and publishes to queue
|
├── classification_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py             # Consumes from queue, calls model API
│   └── model_api/
│       ├── main.py         # FastAPI endpoint for the model
│       └── model/          # Saved Transformer model files
|
└── kafka/
    ├── build_kafka_server.sh
├── storage_service/
│   ├── Dockerfile
│   ├── src
│   │   └── main.py         # Entrypoint for storage service
|
|
└── visualization_service/
    ├── README.md          # Documentation for Grafana setup
```

---

## Project Development Plan & Timeline
Refer to the [DEV_PLAN.md](DEV_PLAN.md) for a detailed development plan, timeline, and milestones.