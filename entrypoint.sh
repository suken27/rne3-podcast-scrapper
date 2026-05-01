#!/bin/bash

# Set up cron job if CRON_EXPRESSION is set
if [ -n "$CRON_EXPRESSION" ]; then
    echo "Setting up cron job with expression: $CRON_EXPRESSION"
    cat > /etc/cron.d/rtve-job <<EOF
SHELL=/bin/sh
PATH=/usr/local/bin:/usr/bin:/bin
$CRON_EXPRESSION root /usr/local/bin/python3 /app/script.py --dest /downloads --config /app/config.txt >> /proc/1/fd/1 2>&1
EOF
    chmod 0644 /etc/cron.d/rtve-job
    echo "Starting cron daemon in foreground..."
    cron -f
else
    echo "No CRON_EXPRESSION set, running script once..."
    exec /usr/local/bin/python3 /app/script.py --dest /downloads --config /app/config.txt "$@"
fi