# Dockerfile - Defines the Build Process of the Image for the Ingestion Service
# Essentially, sets up an image that can run the ingestion client and the mock API Containers.

# Stage 1: Builder
# Use the official Go image as a parent image.
# Using bookworm as the base Debian image to ensure it contains the necessary C libraries for the Confluent Kafka client.
FROM golang:1.24.3-bookworm AS builder

# Set the working directory inside the container.
WORKDIR /app

# Copy go.mod and go.sum to download dependencies first,
# leveraging Docker's layer caching for faster subsequent builds.
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the application's source code.
# Your source code is in a 'src' directory.
COPY src/ ./src/

# Build the ingestion client application.
# IMPORTANT: Cannot disable CGO for the Confluent Kafka client, so we need to ensure the build is compatible.
RUN GOOS=linux go build -o /ingestion_client ./src/main.go

# Build the mock API server application.
RUN CGO_ENABLED=0 GOOS=linux go build -o /mock_api_server ./src/mock_x_api/mock_api.go

# Stage 2: Final image
# Use a minimal base image for the final container to keep it small and secure.
# Using Debian Bookworm Slim to ensure it contains the necessary C libraries for the Confluent Kafka client.
FROM debian:bookworm-slim

# Set the working directory.
WORKDIR /app

# Copy the compiled binaries from the builder stage.
COPY --from=builder /ingestion_client .
COPY --from=builder /mock_api_server .

# Copy the environment variables file to the final image (Change name to .env if needed).
COPY .env.docker_mock .env

# The mock API needs the dataset. This assumes the dataset is in src/mock_x_api/dataset
COPY src/mock_x_api/dataset ./dataset

# Copy and set up the entrypoint script that will choose which binary to run.
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Expose the port the mock API server runs on.
EXPOSE 8080

# Set the entrypoint. This will run when the container starts.
ENTRYPOINT ["./entrypoint.sh"]
