# YouTube Archive Agent - Docker Image
FROM python:3.11-slim

# Install system dependencies including rclone
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    ca-certificates \
    rclone \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp via pip (more reliable than curl)
RUN pip install --no-cache-dir yt-dlp

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py tools.py database.py config.py ./

# Create directories for downloads and compressed files
RUN mkdir -p /app/downloads /app/compressed /app/data

# Copy config example (user will override with their own)
COPY config.example.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=5m --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('/app/data/archive.db'); conn.close()" || exit 1

# Run the agent
CMD ["python", "agent.py", "--config", "/app/config/my_config.py"]
