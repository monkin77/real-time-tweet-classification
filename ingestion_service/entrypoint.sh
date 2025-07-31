#!/bin/sh
# entrypoint.sh

# This script checks the SERVICE_TO_RUN environment variable
# and executes the appropriate binary.

set -e

if [ "$SERVICE_TO_RUN" = "mock_api" ]; then
  echo "Starting Mock API Server..."
  exec ./mock_api_server
else
  echo "Starting Ingestion Client..."
  exec ./ingestion_client
fi
