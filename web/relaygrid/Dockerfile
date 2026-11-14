FROM python:3.13-slim

# Install system dependencies including uuid-runtime for uuidgen and fonts for captcha
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    uuid-runtime \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    ttf-bitstream-vera \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure pip installed binaries are in PATH
ENV PATH="/usr/local/bin:${PATH}"

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p static/profile_pics

# Copy entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command to run gunicorn with single worker
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
