#!/bin/bash

echo "Building web_N1sh_5 Docker container..."
docker build -t web_n1sh_5:latest .

echo "Running web_N1sh_5 container..."
docker run -d \
  --name web_n1sh_5_challenge \
  -p 3000:3000 \
  web_n1sh_5:latest

echo "Container started successfully!"
echo "Application available at: http://localhost:3000"
echo "Use 'docker logs web_n1sh_5_challenge' to view logs"
echo "Use 'docker stop web_n1sh_5_challenge' to stop the container"