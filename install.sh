#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Building RVM Ecosystem Backend Docker image..."
docker build -f Dockerfile.prod -t rvm-backend .

echo "Docker image built. Now running the container."
echo "Ensure you set environment variables like DATABASE_URL and SECRET_KEY."

# Example of how to run, replace with actual production values
# This command runs in detached mode (-d) and removes the container when it exits (--rm)
# It also sets example environment variables.

docker run -d --rm -p 8000:8000 \
  -e DATABASE_URL="your_postgresql_connection_string_here" \
  -e DEBUG="False" \
  -e SECRET_KEY="your_django_secret_key_here" \
  --name rvm-backend-app \
  rvm-backend

echo "RVM Ecosystem Backend container is starting. Access it at http://localhost:8000/"
echo "Check container logs with: docker logs rvm-backend-app"
echo "To stop the container: docker stop rvm-backend-app" 