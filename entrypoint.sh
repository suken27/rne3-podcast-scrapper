#!/bin/bash

# Set up cron job if CRON_EXPRESSION is set
if [ -n "$CRON_EXPRESSION" ]; then
    echo "Setting up cron job with expression: $CRON_EXPRESSION"
    echo "$CRON_EXPRESSION python /app/script.py --config /app/config.txt" > /etc/cron.d/rtve-job
    chmod 0644 /etc/cron.d/rtve-job
    crontab /etc/cron.d/rtve-job
    echo "Starting cron daemon..."
    cron -f
else
    echo "No CRON_EXPRESSION set, running script once..."
    exec python /app/script.py "$@"
fi