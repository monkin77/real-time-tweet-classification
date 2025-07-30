# Bash Script to build Redis Server fom Docker image
# This script pulls the Redis image and runs it in a Docker container.
# Ensure Docker is installed and running before executing this script.
docker run --name redis-dev -p 6379:6379 -d redis