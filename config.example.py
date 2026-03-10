"""
Example Configuration for YouTube Archive Agent

Copy this file to my_config.py and customize your settings.

Usage:
    cp config.example.py my_config.py
    # Edit my_config.py with your settings
    python agent.py --config my_config.py
"""

# ==============================================================================
# REQUIRED SETTINGS
# ==============================================================================

# YouTube watchlist URL
# This can be a playlist URL, Watch Later, or Liked Videos
# Examples:
#   - Playlist: "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
#   - Watch Later: "https://www.youtube.com/playlist?list=WL"
#   - Liked Videos: "https://www.youtube.com/playlist?list=LL"
WATCHLIST_URL = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"


# ==============================================================================
# DIRECTORY SETTINGS
# ==============================================================================

# Directory for raw video downloads (temporary storage)
DOWNLOAD_DIR = "downloads"

# Directory for compressed videos (temporary storage)
COMPRESS_DIR = "compressed"

# SQLite database file path
DATABASE_PATH = "archive.db"


# ==============================================================================
# GOOGLE DRIVE SETTINGS
# ==============================================================================

# rclone remote path for Google Drive
# Format: "remote_name:/path/to/folder/"
# Make sure you've configured rclone with: rclone config
RCLONE_REMOTE = "gdrive:/youtube_archive/"


# ==============================================================================
# AGENT LOOP SETTINGS
# ==============================================================================

# Interval between watchlist checks in seconds
# Examples:
#   - 1 hour: 3600
#   - 30 minutes: 1800
#   - 6 hours: 21600
#   - 12 hours: 43200
CHECK_INTERVAL = 3600  # 1 hour


# ==============================================================================
# VIDEO COMPRESSION SETTINGS
# ==============================================================================

# Maximum video resolution (height in pixels)
# Common values: "480", "720", "1080"
# Recommended for smartphones: "720"
MAX_RESOLUTION = "720"

# Video codec (H264 is widely compatible)
VIDEO_CODEC = "libx264"

# Audio codec (AAC is widely compatible)
AUDIO_CODEC = "aac"

# FFmpeg encoding preset
# Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# Trade-off: faster = larger file size, slower = smaller file size
# Recommended: "slow" for best compression
VIDEO_PRESET = "slow"

# Constant Rate Factor (CRF) - quality setting
# Range: 0-51 (lower = better quality, larger file)
# Recommended values:
#   - 18-22: High quality (larger files)
#   - 23-28: Good quality (balanced)
#   - 29-35: Lower quality (smaller files)
# Recommended for smartphones: 28
CRF = 28

# Audio bitrate
# Common values: "96k", "128k", "192k", "256k"
# Recommended for smartphones: "128k"
AUDIO_BITRATE = "128k"


# ==============================================================================
# RETRY SETTINGS
# ==============================================================================

# Maximum number of retry attempts for failed operations
MAX_RETRIES = 3

# Delay between retries in seconds
RETRY_DELAY = 10


# ==============================================================================
# LOGGING SETTINGS
# ==============================================================================

# Logging level
# Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
# Recommended: "INFO"
LOG_LEVEL = "INFO"

# Log file path (set to None for console only)
LOG_FILE = "youtube_archive.log"


# ==============================================================================
# CLEANUP SETTINGS
# ==============================================================================

# Delete local files after successful upload to save disk space
# Recommended: True (unless you want to keep local copies)
DELETE_AFTER_UPLOAD = True
