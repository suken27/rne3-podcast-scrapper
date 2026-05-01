# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set timezone environment variable (can be overridden at runtime)
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests \
    beautifulsoup4 \
    mutagen

# Copy the script and entrypoint
COPY script.py .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
