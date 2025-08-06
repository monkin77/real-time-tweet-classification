#!/bin/bash

# Build the images and start the containers in the background
# To simply run without building, use `docker compose up -d`
docker compose up --build -d

# To see the logs from all services
# This will follow the logs, so you can see real-time output
docker compose logs -f

# To stop and remove the containers
# docker compose down
