# Quick Start Guide

Get your YouTube Archive Agent running in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
# Install external tools via Homebrew
brew install yt-dlp ffmpeg rclone

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Configure Google Drive (2 minutes)

```bash
# Configure rclone for Google Drive
rclone config

# Follow the prompts:
# - Choose 'n' for new remote
# - Name it 'gdrive'
# - Choose 'Google Drive' (usually option 15)
# - Leave client_id and client_secret blank (press Enter)
# - Choose 'Full access' scope (option 1)
# - Leave root_folder_id blank
# - Leave service_account_file blank
# - Choose 'n' for advanced config
# - Choose 'y' to auto config
# - Your browser will open - sign in to Google
# - Choose 'y' to confirm

# Create the archive folder
rclone mkdir gdrive:/youtube_archive

# Test the connection
rclone lsd gdrive:/
```

## Step 3: Configure Your Watchlist (1 minute)

```bash
# Copy the example config
cp config.example.py my_config.py

# Edit the config file
nano my_config.py
# or
code my_config.py
```

**Set your watchlist URL** - this is the only required change:

```python
WATCHLIST_URL = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

### Getting Your Playlist URL

**Option 1: Watch Later**
```
https://www.youtube.com/playlist?list=WL
```

**Option 2: Any Playlist**
1. Go to the playlist on YouTube
2. Copy the URL from the address bar
3. It should look like: `https://www.youtube.com/playlist?list=PLxxxxx`

## Step 4: Verify Installation

```bash
python agent.py --check-deps
```

You should see:
```
✓ yt-dlp is installed
✓ ffmpeg is installed
✓ rclone is installed
✓ All dependencies are installed
```

## Step 5: Run the Agent

### Test Run (process once and exit)

```bash
python agent.py --config my_config.py --once
```

### Continuous Run (recommended)

```bash
python agent.py --config my_config.py
```

Press `Ctrl+C` to stop.

## What Happens Next?

The agent will:

1. **Fetch** your watchlist
2. **Check** which videos are already archived
3. **Download** new videos
4. **Compress** them to ~720p MP4 (smartphone optimized)
5. **Upload** to Google Drive
6. **Delete** local files (saves disk space)
7. **Wait** 1 hour and repeat

## Monitoring

**Watch the logs:**
```bash
tail -f youtube_archive.log
```

**Check database:**
```bash
sqlite3 archive.db "SELECT COUNT(*) FROM videos;"
sqlite3 archive.db "SELECT title, file_size FROM videos ORDER BY downloaded_at DESC LIMIT 10;"
```

**Check Google Drive:**
```bash
rclone ls gdrive:/youtube_archive/
```

## Customization Tips

### Change compression quality (in my_config.py)

**Better quality, larger files:**
```python
CRF = 23  # Lower = better quality
MAX_RESOLUTION = "1080"
```

**Smaller files:**
```python
CRF = 32  # Higher = smaller size
VIDEO_PRESET = "fast"  # Faster encoding
```

### Change check interval

```python
CHECK_INTERVAL = 1800  # 30 minutes
CHECK_INTERVAL = 21600  # 6 hours
```

### Keep local files

```python
DELETE_AFTER_UPLOAD = False
```

## Running as a Background Service

### macOS (launchd)

Create `~/Library/LaunchAgents/com.youtube.archive.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.archive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
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

**Replace `YOUR_USERNAME` with your actual username!**

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.youtube.archive.plist
```

Check status:
```bash
launchctl list | grep youtube
```

Stop the service:
```bash
launchctl unload ~/Library/LaunchAgents/com.youtube.archive.plist
```

## Troubleshooting

### "No videos in watchlist"
- Check that your WATCHLIST_URL is correct
- Make sure the playlist is public or you're authenticated
- Try the URL in your browser first

### "Upload failed"
- Run `rclone lsd gdrive:/youtube_archive/` to test connection
- Reconfigure rclone if needed: `rclone config`

### "Download failed"
- The video might be private or deleted
- Check the log file for details
- The agent will skip it and continue with other videos

### High CPU/disk usage
- Compression is CPU-intensive (this is normal)
- Downloads are stored temporarily (will be deleted after upload)
- Lower `VIDEO_PRESET` to "fast" for less CPU usage

## Need Help?

1. Check the log file: `youtube_archive.log`
2. Read the full documentation: [README.md](README.md)
3. Run with DEBUG logging:
   ```python
   LOG_LEVEL = "DEBUG"
   ```

## Next Steps

- ✅ Archive is running automatically
- ✅ Videos are safely stored in Google Drive
- ✅ Optimized for smartphone viewing
- ✅ Minimal local storage usage

Enjoy your automated YouTube archive!
