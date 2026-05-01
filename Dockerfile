FROM python:3-slim

# Set working directory
WORKDIR /app

# Set timezone environment variable (can be overridden at runtime)
ENV TZ=UTC

# Copy the script and entrypoint
COPY script.py .
COPY entrypoint.sh .

# Install system and Python dependencies in a single layer
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
       requests \
       beautifulsoup4 \
       mutagen \
    && chmod +x entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
