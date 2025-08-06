# Dockerfile for the Classification Service

# Stage 1: Build the application with Poetry
FROM python:3.10-slim AS builder

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

# - Debugging - Print the contents of the .venv directory for debugging
# RUN echo "Contents of .venv:" && ls -la .venv

# Copy the rest of the application source code
COPY src/ ./src
# Copy the .env file if it exists
COPY .env ./

# Stage 2: Create the final, lean image
FROM python:3.10-slim

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
EXPOSE 8000


# Command to run the application
# --- Debugging ---
# CMD echo "files in WD: $(ls -a)\n" \
#    echo "files in src: $(ls src)\n" && \
#    echo "files in .venv: $(ls .venv/)"

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
# Alternatively, you can use uvicorn to run the application
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
