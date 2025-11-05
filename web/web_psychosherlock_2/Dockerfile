# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Install uuidgen
RUN apk add --no-cache util-linux

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Build the application (includes obfuscation)
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start the application with entrypoint
CMD ["./entrypoint.sh"]
