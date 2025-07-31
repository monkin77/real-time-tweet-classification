#!/bin/bash

# Build the images and start the containers in the background
docker compose up --build -d

# To see the logs from all services
docker compose logs -f

# To stop and remove the containers
# docker compose down
