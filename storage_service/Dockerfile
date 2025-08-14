# Dockerfile - Defines the Build Process of the Image for the Storage Service
# This sets up an image that can run the storage service for classified tweets.

# Stage 1: Builder
# Use the official Python image as a parent image.
FROM python:3.11-slim AS builder

# Set poetry configurations to create the virtual environment in the project's root
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy only the files needed for dependency installation to leverage caching
COPY pyproject.toml poetry.lock README.md ./

# Install dependencies
# This will create a .venv folder in /app.
# RUN poetry install --no-root
RUN poetry install

# Copy the rest of the application source code
COPY src/ ./src
# Copy the .env file if it exists
COPY .env.docker .env


# Stage 2: Create the final, lean image
# Use the official Python image as the base for the final image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Activate the virtual environment by adding it to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code from the builder stage
COPY --from=builder /app/src ./src
# Copy the .env file from the builder stage
COPY --from=builder /app/.env ./

# Expose the port the service runs on
EXPOSE 8082

# -- Command to run the application ---
# Need to run the command from the src directory
WORKDIR /app/src

CMD ["python", "main.py"]