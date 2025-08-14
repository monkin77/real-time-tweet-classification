#!/bin/bash

# This script is used to run the disaster detection services locally.

# --- Ingestion Service Setup ---
cd ./ingestion_service
# Build and Run the Redis Server (background)
./build_redis_server.sh > redis_server.log 2>&1 &   # Sends output to redis_server.log (including errors)

# Run Mock API
./mock_server.sh > mock_server.log 2>&1 &

# Run Ingestion Service
./client.sh > client.log 2>&1 &

cd ..

# --- Inference Service Setup ---
cd ./classification_service
# Build and Run the Inference Service
./server.sh > server.log 2>&1 &   # Sends output to server.log (including errors)

cd ..

# --- Storage Service Setup ---
cd ./storage_service
# Build and Run the Storage Service
./run.sh > storage_service.log 2>&1 &   # Sends output to storage_service.log (including errors)

# Kill Processes on Exit. Does this work?
trap 'kill $(jobs -p)' EXIT