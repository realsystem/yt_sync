#!/bin/bash
# Daily YouTube Archive Agent Runner
# This script is designed to be run by cron

set -e

# Change to project directory
cd /Users/segorov/Projects/yt_sync

# Set PATH to include Docker
export PATH=/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:$PATH

# Log file
LOG_FILE="/Users/segorov/Projects/yt_sync/data/cron.log"

# Run the agent in "once" mode (process all videos and exit)
echo "=== YouTube Archive Agent - $(date) ===" >> "$LOG_FILE"
/usr/local/bin/docker compose run --rm youtube-archive \
    python agent.py --config /app/config/my_config.py --once \
    >> "$LOG_FILE" 2>&1

echo "=== Completed - $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
