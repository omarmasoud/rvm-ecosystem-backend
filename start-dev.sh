#!/bin/bash

echo "Building RVM Backend Docker image..."
docker build -f Dockerfile -t rvm-backend .

echo "Starting RVM Backend container..."
docker run -p 8000:8000 --name rvm-backend-app rvm-backend

echo "Container stopped. To remove it, run: docker rm rvm-backend-app" 