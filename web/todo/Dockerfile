FROM node:18-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    uuid-runtime \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install Node.js dependencies
RUN npm install --only=production

# Copy application files
COPY . .

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port
EXPOSE 3000

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default command to run the application
CMD ["node", "server.js"]