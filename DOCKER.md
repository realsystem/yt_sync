# Docker Setup for YouTube Archive Agent

Run the YouTube Archive Agent in a Docker container on your MacBook.

## Prerequisites

- Docker Desktop for Mac installed
- Google Drive configured with rclone
- Your configuration file ready

## Quick Start

### 1. Configure rclone (One-time Setup)

If you haven't already configured rclone:

```bash
rclone config
```

This creates `~/.config/rclone/rclone.conf` which Docker will use.

### 2. Create Your Configuration

```bash
cp config.example.py my_config.py
nano my_config.py  # Set your WATCHLIST_URL
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the agent
docker-compose up -d

# View logs
docker-compose logs -f
```

That's it! The agent is now running in the background.

---

## Detailed Usage

### Build the Image

```bash
# Using docker-compose (recommended)
docker-compose build

# Or using docker directly
docker build -t youtube-archive .
```

### Run the Container

**Using docker-compose (easiest):**

```bash
# Start in detached mode
docker-compose up -d

# Start in foreground (see logs)
docker-compose up

# Stop the container
docker-compose down

# Restart
docker-compose restart
```

**Using docker directly:**

```bash
docker run -d \
  --name youtube-archive \
  --restart unless-stopped \
  -v $(pwd)/my_config.py:/app/config/my_config.py:ro \
  -v ~/.config/rclone:/root/.config/rclone:ro \
  -v $(pwd)/data:/app/data \
  youtube-archive
```

### View Logs

```bash
# docker-compose
docker-compose logs -f

# docker
docker logs -f youtube-archive

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status

```bash
# docker-compose
docker-compose ps

# docker
docker ps | grep youtube-archive
```

### Execute Commands Inside Container

```bash
# docker-compose
docker-compose exec youtube-archive bash

# docker
docker exec -it youtube-archive bash

# Run agent once (test mode)
docker-compose exec youtube-archive python agent.py --config /app/config/my_config.py --once

# Check dependencies
docker-compose exec youtube-archive python agent.py --check-deps
```

### View Database

```bash
# Access SQLite database
docker-compose exec youtube-archive sqlite3 /app/data/archive.db

# SQL queries
sqlite> SELECT COUNT(*) FROM videos;
sqlite> SELECT title, downloaded_at FROM videos ORDER BY downloaded_at DESC LIMIT 10;
sqlite> .exit
```

---

## Configuration

### Environment Variables

Override configuration via environment variables in `docker-compose.yml`:

```yaml
environment:
  - YT_WATCHLIST_URL=https://www.youtube.com/playlist?list=YOUR_LIST
  - YT_CHECK_INTERVAL=3600
  - YT_MAX_RESOLUTION=720
  - YT_CRF=28
  - YT_LOG_LEVEL=INFO
  - TZ=America/Los_Angeles
```

### Volume Mounts

**Required:**
- `./my_config.py:/app/config/my_config.py` - Your configuration
- `~/.config/rclone:/root/.config/rclone` - rclone config with Google Drive credentials
- `./data:/app/data` - Persistent database storage

**Optional:**
- `./cookies.txt:/app/cookies.txt` - For private YouTube playlists
- `./downloads:/app/downloads` - View downloaded files (for debugging)
- `./compressed:/app/compressed` - View compressed files (for debugging)

### Data Persistence

All data is stored in the `./data` directory:
- `archive.db` - SQLite database tracking processed videos

The agent automatically deletes downloaded and compressed files after uploading to Google Drive (configurable).

---

## Maintenance

### Update the Container

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### View Resource Usage

```bash
docker stats youtube-archive
```

### Clean Up

```bash
# Stop and remove container
docker-compose down

# Remove image
docker rmi youtube-archive

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a
```

---

## Troubleshooting

### Check if rclone is configured

```bash
docker-compose exec youtube-archive rclone listremotes
```

Should show: `gdrive:`

### Test Google Drive connection

```bash
docker-compose exec youtube-archive rclone lsd gdrive:/youtube_archive
```

### Check available disk space

```bash
docker-compose exec youtube-archive df -h
```

### View full logs

```bash
docker-compose logs --tail=1000 > agent.log
```

### Container keeps restarting

```bash
# Check logs for errors
docker-compose logs

# Common issues:
# 1. my_config.py not found or invalid
# 2. rclone not configured
# 3. Invalid WATCHLIST_URL
# 4. Google Drive API not enabled
```

### Permission issues

```bash
# Fix data directory permissions
chmod 755 data
```

---

## Advanced Usage

### Run Once (Test Mode)

```bash
# Override CMD to run once
docker-compose run --rm youtube-archive \
  python agent.py --config /app/config/my_config.py --once
```

### Custom Configuration File

```bash
# Use a different config file
docker-compose run --rm \
  -v $(pwd)/custom_config.py:/app/config/my_config.py:ro \
  youtube-archive
```

### Debug Mode

```bash
# Run with verbose logging
docker-compose run --rm \
  -e YT_LOG_LEVEL=DEBUG \
  youtube-archive
```

### Multiple Instances

Run multiple agents for different playlists:

```bash
# Copy docker-compose.yml to docker-compose.playlist1.yml
# Modify container_name and config file
docker-compose -f docker-compose.playlist1.yml up -d
docker-compose -f docker-compose.playlist2.yml up -d
```

---

## Resource Limits

Control CPU and memory usage in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Max 2 CPU cores
      memory: 2G       # Max 2GB RAM
    reservations:
      cpus: '0.5'      # Min 0.5 CPU cores
      memory: 512M     # Min 512MB RAM
```

---

## Scheduled Running

### Option 1: Cron (macOS)

```bash
# Add to crontab
crontab -e

# Run once per day at 2 AM
0 2 * * * cd /Users/segorov/Projects/yt_sync && docker-compose run --rm youtube-archive python agent.py --config /app/config/my_config.py --once
```

### Option 2: Continuous Running

The default setup runs continuously, checking every hour. Just leave the container running:

```bash
docker-compose up -d
```

---

## Production Deployment

### Auto-start on Boot

Docker Desktop → Preferences → General → "Start Docker Desktop when you log in"

The container will auto-start with `restart: unless-stopped` in docker-compose.yml.

### Monitoring

```bash
# Add health check endpoint
docker inspect youtube-archive | grep -A 10 Health

# Monitor with Portainer (optional)
docker run -d -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce
```

### Logging to File

Logs are already configured to rotate (max 10MB, 3 files).

View location:
```bash
docker inspect youtube-archive | grep LogPath
```

---

## Comparison: Docker vs Native

| Feature | Docker | Native |
|---------|--------|--------|
| Setup | `docker-compose up` | Install yt-dlp, ffmpeg, rclone |
| Dependencies | Automatic | Manual |
| Isolation | ✅ Isolated | Shared system |
| Updates | `docker-compose build` | Update each tool |
| Portability | ✅ Works anywhere | macOS specific |
| Resource usage | +100-200MB | Lower |
| Debugging | Slightly harder | Easier |

**Recommendation:** Use Docker for easier setup and portability. Use native for slightly better performance.

---

## Security

- ✅ Configuration mounted read-only (`:ro`)
- ✅ rclone config mounted read-only
- ✅ No credentials in image
- ✅ Minimal base image (python:3.11-slim)
- ✅ Non-privileged container

---

## Next Steps

1. Start the agent: `docker-compose up -d`
2. Check logs: `docker-compose logs -f`
3. Monitor Google Drive: `rclone ls gdrive:/youtube_archive/`
4. Set up Android app to sync from Google Drive

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify config: `cat my_config.py`
3. Test rclone: `docker-compose exec youtube-archive rclone lsd gdrive:`
4. Check dependencies: `docker-compose exec youtube-archive python agent.py --check-deps`

---

**Your YouTube archive agent is now running in Docker!** 🐳
