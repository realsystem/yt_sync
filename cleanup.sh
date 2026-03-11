#!/bin/bash
# Cleanup script for YouTube Archive Agent
# Removes orphaned files and ensures database integrity

set -e

PROJECT_DIR="/Users/segorov/Projects/yt_sync"
cd "$PROJECT_DIR"

echo "=== YouTube Archive Cleanup ==="
echo ""

# Function to count files
count_files() {
    find "$1" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Check for orphaned downloads
DOWNLOADS_COUNT=$(count_files "data/downloads")
if [ "$DOWNLOADS_COUNT" -gt 0 ]; then
    echo "⚠️  Found $DOWNLOADS_COUNT orphaned file(s) in downloads/"
    echo "These are incomplete downloads that should be removed."
    echo ""
    find data/downloads -type f -ls
    echo ""
    read -p "Remove these files? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f data/downloads/*
        echo "✓ Removed orphaned downloads"
    fi
else
    echo "✓ No orphaned downloads"
fi
echo ""

# Check for orphaned compressed files
COMPRESSED_COUNT=$(count_files "data/compressed")
if [ "$COMPRESSED_COUNT" -gt 0 ]; then
    echo "⚠️  Found $COMPRESSED_COUNT orphaned file(s) in compressed/"
    echo "These are compressed videos that weren't uploaded to Google Drive."
    echo ""
    find data/compressed -type f -ls
    echo ""
    read -p "Remove these files? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f data/compressed/*
        echo "✓ Removed orphaned compressed files"
    fi
else
    echo "✓ No orphaned compressed files"
fi
echo ""

# Database statistics
echo "=== Database Statistics ==="
if [ -f "data/archive.db" ]; then
    sqlite3 data/archive.db "SELECT
        COUNT(*) as total_videos,
        COUNT(CASE WHEN status = 'archived' THEN 1 END) as archived,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
        ROUND(SUM(file_size)/1024.0/1024.0, 2) as total_mb
    FROM videos" | awk -F'|' '{print "Total videos: "$1"\nArchived: "$2"\nFailed: "$3"\nTotal size: "$4" MB"}'
else
    echo "No database found"
fi
echo ""

# Check for running containers
echo "=== Running Containers ==="
RUNNING=$(docker ps --filter "name=youtube-archive" --format "{{.Names}}" 2>/dev/null || echo "")
if [ -n "$RUNNING" ]; then
    echo "⚠️  Container is currently running: $RUNNING"
    echo "Stop it with: make docker-down"
else
    echo "✓ No containers running"
fi
echo ""

# Check disk space
echo "=== Disk Space ==="
df -h "$PROJECT_DIR" | tail -1 | awk '{print "Available: "$4" ("$5" used)"}'
echo ""

echo "=== Cleanup Complete ==="
