# YouTube Archive Agent

An autonomous agent that maintains an archive of YouTube videos from a watchlist and stores them compressed in Google Drive, optimized for smartphone viewing and minimal storage size.

## Features

- **Autonomous Operation**: Runs continuously or on scheduled intervals
- **Smart Compression**: Optimizes videos for smartphone viewing (720p, H264, AAC)
- **Cloud Storage**: Automatically uploads to Google Drive via rclone
- **Memory/Database**: Tracks processed videos to avoid duplicates
- **Error Handling**: Robust retry logic for downloads, compression, and uploads
- **Agent-Style Workflow**: Observe → Compare → Plan → Act → Update → Repeat

## Architecture

The agent follows a classic agent workflow:

1. **Observe**: Read the YouTube watchlist (playlist or watch-later list)
2. **Compare**: Check local database for already processed videos
3. **Plan**: Determine which videos need processing
4. **Act**: Download, compress, upload, and store metadata
5. **Update**: Record processed videos in database
6. **Repeat**: Run on scheduled interval

## Project Structure

```
yt_sync/
├── agent.py           # Main agent loop and orchestration
├── tools.py           # Wrappers for external tools (yt-dlp, ffmpeg, rclone)
├── database.py        # SQLite database operations
├── config.py          # Configuration management with validation
├── requirements.txt   # Python dependencies
├── config.example.py  # Example configuration file
├── archive.db         # SQLite database (created on first run)
├── downloads/         # Temporary storage for raw downloads
├── compressed/        # Temporary storage for compressed videos
└── youtube_archive.log # Log file
```

## Requirements

### System Requirements

- macOS (tested on MacBook)
- Python 3.11+
- Homebrew package manager

### External Tools

- **yt-dlp**: YouTube video downloader
- **ffmpeg**: Video compression
- **rclone**: Google Drive upload

## Installation

**Choose your preferred method:**
- **🐳 Docker (Recommended)** - Easiest setup, isolated environment
- **💻 Native** - Better performance, more control

---

## 🐳 Docker Installation (Recommended)

### Quick Start

```bash
# 1. Clone the repository
git clone git@github.com:realsystem/yt_sync.git
cd yt_sync

# 2. Configure rclone for Google Drive
rclone config

# 3. Create your configuration
cp config.example.py my_config.py
nano my_config.py  # Set WATCHLIST_URL

# 4. Build and run
make docker-build
make docker-up

# 5. View logs
make docker-logs
```

That's it! The agent is now running in Docker.

**See [DOCKER.md](DOCKER.md) for complete Docker documentation.**

### Docker Commands

```bash
make docker-build      # Build image
make docker-up         # Start agent
make docker-down       # Stop agent
make docker-logs       # View logs
make docker-shell      # Access container
make docker-test       # Run once (test)
make help              # Show all commands
```

---

## 💻 Native Installation

### 1. Install System Dependencies

```bash
# Install external tools via Homebrew
brew install yt-dlp ffmpeg rclone
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Configure Google Drive with rclone

First time setup for Google Drive:

```bash
# Configure rclone
rclone config

# Follow the interactive prompts:
# 1. Choose 'n' for new remote
# 2. Name it 'gdrive'
# 3. Choose 'Google Drive' from the list
# 4. Follow OAuth2 authentication flow
# 5. Test the connection: rclone lsd gdrive:
```

Create the archive folder in Google Drive:

```bash
rclone mkdir gdrive:/youtube_archive
```

### 4. Configure the Agent

Copy the example configuration:

```bash
cp config.example.py my_config.py
```

Edit `my_config.py` and set your YouTube watchlist URL:

```python
# Required: Set your YouTube playlist or watch-later URL
WATCHLIST_URL = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Optional: Customize other settings
CHECK_INTERVAL = 3600  # Check every hour
MAX_RESOLUTION = "720"  # Maximum resolution
CRF = 28  # Compression quality (18-28, higher = smaller file)
```

### 5. Verify Installation

Check that all dependencies are installed:

```bash
python agent.py --check-deps
```

## Usage

### Run Continuously (Recommended)

The agent will run indefinitely, checking for new videos at the configured interval:

```bash
python agent.py --config my_config.py
```

### Run Once

Process the watchlist once and exit:

```bash
python agent.py --config my_config.py --once
```

### Using Environment Variables

Instead of a config file, you can use environment variables:

```bash
export YT_WATCHLIST_URL="https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
export YT_RCLONE_REMOTE="gdrive:/youtube_archive/"
export YT_CHECK_INTERVAL=3600

python agent.py
```

### Run as a Background Service

#### Using launchd (macOS)

Create a plist file at `~/Library/LaunchAgents/com.youtube.archive.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.archive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/Projects/yt_sync/agent.py</string>
        <string>--config</string>
        <string>/Users/YOUR_USERNAME/Projects/yt_sync/my_config.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Projects/yt_sync/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Projects/yt_sync/stderr.log</string>
</dict>
</plist>
```

Load and start the service:

```bash
launchctl load ~/Library/LaunchAgents/com.youtube.archive.plist
launchctl start com.youtube.archive
```

Stop the service:

```bash
launchctl stop com.youtube.archive
launchctl unload ~/Library/LaunchAgents/com.youtube.archive.plist
```

## Configuration Options

### Core Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `WATCHLIST_URL` | (required) | YouTube playlist or watch-later URL |
| `DOWNLOAD_DIR` | `downloads/` | Directory for raw video downloads |
| `COMPRESS_DIR` | `compressed/` | Directory for compressed videos |
| `DATABASE_PATH` | `archive.db` | SQLite database file path |
| `RCLONE_REMOTE` | `gdrive:/youtube_archive/` | rclone remote path |
| `CHECK_INTERVAL` | `3600` | Interval between checks (seconds) |

### Compression Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_RESOLUTION` | `720` | Maximum video resolution |
| `VIDEO_CODEC` | `libx264` | Video codec (H264) |
| `AUDIO_CODEC` | `aac` | Audio codec |
| `VIDEO_PRESET` | `slow` | FFmpeg preset (faster/slower) |
| `CRF` | `28` | Quality (18-28, higher = smaller) |
| `AUDIO_BITRATE` | `128k` | Audio bitrate |

### Other Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_RETRIES` | `3` | Retry attempts for failed operations |
| `RETRY_DELAY` | `10` | Delay between retries (seconds) |
| `DELETE_AFTER_UPLOAD` | `True` | Delete local files after upload |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `youtube_archive.log` | Log file path |

## How to Get Your YouTube Watchlist URL

### Option 1: Playlist URL

1. Go to YouTube
2. Navigate to any playlist (or create a new one)
3. Copy the URL (format: `https://www.youtube.com/playlist?list=PLAYLIST_ID`)

### Option 2: Watch Later List

Your Watch Later playlist URL:
```
https://www.youtube.com/playlist?list=WL
```

### Option 3: Liked Videos

Your Liked Videos playlist URL (may require authentication):
```
https://www.youtube.com/playlist?list=LL
```

## Database Schema

The agent uses SQLite to track processed videos:

```sql
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    channel TEXT,
    url TEXT NOT NULL,
    duration INTEGER,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    status TEXT DEFAULT 'completed'
);
```

## Video Compression Details

Videos are optimized for smartphone viewing with these settings:

- **Resolution**: Maximum 720p (maintains aspect ratio)
- **Video Codec**: H264 (libx264) - universal compatibility
- **Audio Codec**: AAC - efficient and compatible
- **Container**: MP4 with faststart flag for streaming
- **Quality**: CRF 28 (good quality, small file size)
- **Audio**: 128kbps AAC (clear audio, small size)

Example compression command:
```bash
ffmpeg -i input.mkv \
  -vf scale=-2:720 \
  -c:v libx264 \
  -preset slow \
  -crf 28 \
  -c:a aac \
  -b:a 128k \
  -movflags +faststart \
  output.mp4
```

## Logging

The agent uses structured logging with the following levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General operational messages
- **WARNING**: Non-critical issues
- **ERROR**: Errors that prevent video processing

Logs are written to both console and log file (configurable).

Example log output:
```
2024-03-10 10:15:23 - YouTubeArchiveAgent - INFO - === OBSERVE: Fetching watchlist ===
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - Observed 15 videos in watchlist
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - === COMPARE: Checking database ===
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - Found 3 new videos to process
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - === ACT: Processing video ===
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - Video: Cool Tutorial
2024-03-10 10:15:25 - YouTubeArchiveAgent - INFO - → Downloading...
2024-03-10 10:16:45 - YouTubeArchiveAgent - INFO - → Compressing...
2024-03-10 10:18:12 - YouTubeArchiveAgent - INFO - → Uploading to Google Drive...
2024-03-10 10:19:05 - YouTubeArchiveAgent - INFO - ✓ Successfully processed: Cool Tutorial
```

## Troubleshooting

### "WATCHLIST_URL is not configured"

Set your watchlist URL in the config file or environment variable:
```bash
export YT_WATCHLIST_URL="https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

### "Missing required tools"

Install the external dependencies:
```bash
brew install yt-dlp ffmpeg rclone
```

### "Upload failed"

Verify rclone is configured correctly:
```bash
rclone lsd gdrive:/youtube_archive/
```

### Database Issues

Reset the database (WARNING: loses all tracking data):
```bash
rm archive.db
python agent.py --once  # Reinitialize
```

### Low Disk Space

Enable automatic cleanup:
```python
DELETE_AFTER_UPLOAD = True  # In config
```

Or manually clean:
```bash
rm -rf downloads/* compressed/*
```

## Performance Tips

1. **Adjust Compression Quality**: Lower CRF (18-23) = better quality, larger files
2. **Faster Encoding**: Use `VIDEO_PRESET = "fast"` (larger files)
3. **Higher Resolution**: Set `MAX_RESOLUTION = "1080"` for better quality
4. **Parallel Processing**: Run multiple instances with different playlists

## Storage Estimates

Approximate compressed file sizes (720p, CRF 28):

- 10 minute video: ~50-100 MB
- 30 minute video: ~150-300 MB
- 60 minute video: ~300-600 MB

## Security Notes

- **Credentials**: rclone stores credentials in `~/.config/rclone/rclone.conf`
- **API Keys**: No API keys required (uses OAuth2 for Google Drive)
- **Private Videos**: Agent cannot access private videos (requires cookies/authentication)

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions welcome! Areas for improvement:

- Support for multiple cloud storage providers
- Web UI for monitoring
- Parallel video processing
- Custom compression profiles
- Email notifications
- Webhook integrations

## Support

For issues or questions, please check:

1. Log file: `youtube_archive.log`
2. Run with `--check-deps` to verify installation
3. Test individual components (yt-dlp, ffmpeg, rclone) separately
