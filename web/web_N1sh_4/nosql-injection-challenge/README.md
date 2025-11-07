```bash
# Build the Docker image
docker build --no-cache -t web_n1sh_4:latest .

# Run the container
docker run -d --name web_n1sh_4_challenge -p 3001:3000 web_n1sh_4:latest

```