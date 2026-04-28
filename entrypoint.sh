#!/bin/bash

# Set up cron job if CRON_EXPRESSION is set
if [ -n "$CRON_EXPRESSION" ]; then
    echo "Setting up cron job with expression: $CRON_EXPRESSION"
    echo "$CRON_EXPRESSION root python3 /app/script.py --config /app/config.txt >> /proc/1/fd/1 2>&1" > /etc/cron.d/rtve-job
    chmod 0644 /etc/cron.d/rtve-job
    echo "Starting cron daemon in foreground..."
    cron -f
else
    echo "No CRON_EXPRESSION set, running script once..."
    exec python3 /app/script.py "$@"
fi