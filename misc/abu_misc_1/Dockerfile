# Platform Nine and Three-Quarters - Discord Hunt Challenge

FROM node:18-alpine

WORKDIR /app

# Install system dependencies (uuidgen)
RUN apk add --no-cache util-linux

# Install dependencies directly
RUN npm install express@4.18.2 --save --omit=dev

# Copy application files
COPY server.js ./
COPY public/ ./public/

# Expose port
EXPOSE 3000

# Set entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
