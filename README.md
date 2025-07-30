## Development Plan: Real-Time Disaster Tweet Identification System
This document outlines the development plan for a real-time system that ingests tweets, classifies them using a pre-trained Transformer model, and provides alerts for potential disasters.

# Real-Time Disaster Tweet Identification System

## 1. Project Overview

This project is a real-time data pipeline designed to identify tweets reporting on real-world disasters. It leverages a Transformer-based NLP model to classify tweets as either "disaster" or "not disaster." The system is architected to be scalable, resilient, and provide real-time insights.

The primary goal is to move a machine learning model from a research environment (like a Kaggle notebook) into a live, production-like system that processes data as it's generated.

---

## 2. System Architecture

The system is composed of four main components that work together in a pipeline:

![System Architecture Diagram](https://placehold.co/800x400/1e293b/ffffff?text=Data+Ingestion+%E2%86%92+Message+Queue+%E2%86%92+Model+Inference+%E2%86%92+Storage+%26+Alerting)

1.  **Data Ingestion (`ingestion_service`):** A Python service that connects to the X (Twitter) API's real-time filtered stream. It listens for tweets containing disaster-related keywords and publishes them to a message queue.

2.  **Message Queue (`message_broker`):** A message broker (like Apache Kafka or RabbitMQ) that acts as a buffer. It receives raw tweets from the ingestion service and holds them until they can be processed. This makes the system resilient to spikes in traffic or temporary downtime in the processing service.

3.  **Model Inference (`inference_service`):** A worker service that consumes tweets from the message queue. It preprocesses the tweet text and sends it to a model serving API. The model, wrapped in a REST API, returns a prediction, which is then attached to the tweet data.

4.  **Data Storage & Visualization (`datastore_and_dashboard`):** The final destination for the classified data.
    * **Database:** A database (e.g., MongoDB) stores the tweet, its classification, and other metadata.
    * **Dashboard:** A visualization tool (e.g., Grafana) connects to the database to display real-time analytics, such as a map of disaster events, trend graphs, and recent alerts.

---

## 3. Tech Stack

* **Programming Language:** Python 3.9+
* **Data Ingestion:** Tweepy, X API v2
* **Message Queue:** Apache Kafka / RabbitMQ (alternatively, Redis Pub/Sub for simplicity)
* **Model Serving:** FastAPI, BentoML
* **Database:** MongoDB / PostgreSQL
* **Dashboard:** Grafana / Kibana
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
├── inference_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py             # Consumes from queue, calls model API
│   └── model_api/
│       ├── main.py         # FastAPI endpoint for the model
│       └── model/          # Saved Transformer model files
|
└── dashboard/
├── grafana/
│   └── provisioning/
│       ├── dashboards.yml
│       └── datasources.yml
└── prometheus/
└── prometheus.yml
```

---

## Project Development Plan & Timeline

This plan breaks the project into four modules. Each module can be developed and tested independently. The estimated timeline is a guideline for a single developer with some familiarity with the technologies.

### **Module 1: Data Ingestion Service**
* **Goal:** Reliably stream tweets and publish them to a message queue.
* **Services to Use:**
    * **X API:** Apply for and set up developer access.
    * **Python Library:** `tweepy` for interacting with the API.
    * **Message Queue:** **Apache Kafka**. It's the industry standard for high-throughput data streams. For a simpler start, you could use **RabbitMQ**.
* **Tasks:**
    1.  **[Day 1-2]** Set up X Developer Account and get API keys.
    2.  **[Day 3]** Write a Python script (`ingestion_service/main.py`) to connect to the X API's filtered stream endpoint.
    3.  **[Day 4]** Define a filter with relevant keywords (e.g., `earthquake`, `fire`, `flood`, `hurricane`, `tsunami`).
    4.  **[Day 5-6]** Set up a Kafka broker using Docker. Create a topic named `raw_tweets`.
    5.  **[Day 7]** Modify the ingestion script to publish each incoming tweet as a JSON message to the `raw_tweets` Kafka topic.
    6.  **[Day 8]** Containerize the ingestion service with a `Dockerfile`.
* **Estimated Time:** ~8 Days

---

### **Module 2: Model Inference Service**
* **Goal:** Consume tweets from the queue, preprocess them, and classify them using the Transformer model.
* **Services to Use:**
    * **Model Serving:** **FastAPI**. It's extremely fast, easy to learn, and great for ML model APIs.
    * **ML Libraries:** `transformers`, `torch`/`tensorflow`.
* **Tasks:**
    1.  **[Day 9-10]** Create a FastAPI application (`inference_service/model_api/main.py`).
    2.  **[Day 11]** Load your trained Transformer model and tokenizer into the FastAPI app. Create a `/predict` endpoint that accepts text and returns a JSON prediction (`{"label": "disaster", "confidence": 0.95}`).
    3.  **[Day 12]** Containerize the FastAPI model server with its own `Dockerfile`.
    4.  **[Day 13-14]** Write the consumer script (`inference_service/main.py`) that reads messages from the `raw_tweets` Kafka topic.
    5.  **[Day 15]** For each message, extract the tweet text, perform the necessary preprocessing, and call the FastAPI `/predict` endpoint.
    6.  **[Day 16]** Publish the enriched data (original tweet + prediction) to a new Kafka topic named `classified_tweets`.
    7.  **[Day 17]** Containerize the consumer service.
* **Estimated Time:** ~9 Days

---

### **Module 3: Data Storage & Alerting**
* **Goal:** Persist the classified tweets for analysis and dashboarding.
* **Services to Use:**
    * **Database:** **MongoDB**. Its flexible, document-based nature is perfect for storing tweet data, which can have a variable structure.
* **Tasks:**
    1.  **[Day 18-19]** Set up a MongoDB instance using Docker.
    2.  **[Day 20-21]** Create a new consumer service (or extend the inference consumer) that subscribes to the `classified_tweets` Kafka topic.
    3.  **[Day 22-23]** For each message, parse the JSON and insert it as a new document into a MongoDB collection named `tweets`.
    4.  **[Day 24]** Containerize this storage service.
* **Estimated Time:** ~7 Days

---

### **Module 4: Visualization & Integration**
* **Goal:** Create a dashboard to monitor the system and visualize the results.
* **Services to Use:**
    * **Dashboarding:** **Grafana**. It's powerful, has a great user interface, and includes a native MongoDB plugin.
* **Tasks:**
    1.  **[Day 25]** Set up Grafana using Docker.
    2.  **[Day 26]** Configure the MongoDB data source in Grafana.
    3.  **[Day 27-28]** Create a new dashboard with panels:
        * A counter for total tweets processed.
        * A pie chart showing the distribution of "disaster" vs. "not disaster" tweets.
        * A table showing the most recent tweets classified as disasters.
        * (Advanced) A world map panel that plots tweets based on their geo-coordinates.
    4.  **[Day 29-30]** Create a `docker-compose.yml` file to orchestrate all the services (Kafka, ingestion, inference, storage, MongoDB, Grafana) so they can be launched with a single command.
* **Estimated Time:** ~6 Days

---
### **Total Estimated Project Time: ~30 Days**