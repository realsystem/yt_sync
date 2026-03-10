# YouTube Archive Sync - Complete System Overview

## 🎯 System Architecture

This is a complete end-to-end solution for automatically archiving YouTube videos and syncing them to your Android phone.

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLETE SYSTEM FLOW                         │
└─────────────────────────────────────────────────────────────────┘

MacBook (Server)                    Google Drive                 Android Phone
─────────────────                   ────────────                 ─────────────

┌──────────────┐                   ┌──────────┐                 ┌─────────────┐
│ YouTube      │                   │          │                 │             │
│ Watchlist    │                   │  youtube_│                 │  Local      │
│              │                   │  archive/│                 │  Storage    │
└──────┬───────┘                   │          │                 │  /Videos/   │
       │                           └────┬─────┘                 │  YouTube/   │
       │                                │                       └──────▲──────┘
       │ 1. Observe                     │                              │
       ▼                                │                              │
┌──────────────┐                        │ 3. Upload                    │ 5. Auto-sync
│ Agent.py     │                        │    (compressed)              │    (background)
│              │                        │                              │
│ - Downloads  ├────────────────────────┘                              │
│ - Compresses │                                                       │
│ - Uploads    │                                                       │
│ - Repeats    │                                                       │
└──────────────┘                   ┌──────────┐                 ┌─────────────┐
                                   │  Drive   │◄────────────────┤ Android App │
       ▲                           │  API     │  4. List files  │             │
       │                           └──────────┘                 │ - Monitors  │
       │ 2. Schedule                                            │ - Downloads │
       │    (every hour)                                        │ - Notifies  │
┌──────────────┐                                                └─────────────┘
│  cron / loop │
└──────────────┘
```

---

## 📦 Components

### 1. **YouTube Archive Agent** (Python - MacBook)

Located in: `/Users/segorov/Projects/yt_sync/`

**Purpose:** Automatically archive YouTube videos to Google Drive

**Files:**
- `agent.py` - Main orchestration logic
- `tools.py` - External tool wrappers (yt-dlp, ffmpeg, rclone)
- `database.py` - SQLite tracking database
- `config.py` - Configuration management
- `my_config.py` - Your personal settings

**How it works:**
1. Fetches videos from YouTube watchlist
2. Downloads videos using yt-dlp
3. Compresses to 720p MP4 using ffmpeg
4. Uploads to Google Drive using rclone
5. Tracks in SQLite database
6. Repeats every hour

**Run it:**
```bash
python3 agent.py --config my_config.py
```

---

### 2. **Android Sync App** (Kotlin - Phone)

Located in: `/Users/segorov/Projects/yt_sync/android_sync_app/`

**Purpose:** Automatically download videos from Google Drive to your phone

**Key Components:**
- `MainActivity.kt` - User interface
- `SyncWorker.kt` - Background sync worker
- `DriveService.kt` - Google Drive API client
- `SettingsManager.kt` - User preferences
- `NotificationHelper.kt` - Sync notifications

**How it works:**
1. Connects to Google Drive (OAuth)
2. Checks `youtube_archive/` folder periodically
3. Downloads new videos to phone storage
4. Shows notifications
5. Respects WiFi-only setting

**Build it:**
```bash
cd android_sync_app
make build
make install
```

---

## 🚀 Complete Setup (End-to-End)

### Phase 1: Desktop Agent Setup

```bash
# 1. Install dependencies
brew install yt-dlp ffmpeg rclone

# 2. Configure rclone for Google Drive
rclone config

# 3. Configure Python agent
cp config.example.py my_config.py
# Edit: Set WATCHLIST_URL

# 4. Test agent
python3 agent.py --config my_config.py --once

# 5. Run continuously
python3 agent.py --config my_config.py
```

### Phase 2: Android App Setup

```bash
# 1. Navigate to Android project
cd android_sync_app

# 2. Setup build environment
make setup

# 3. Configure Google OAuth
mkdir -p app/src/main/res/raw
# Copy credentials.json

# 4. Build app
make build

# 5. Install on phone
make install
```

### Phase 3: Integration

1. **Desktop:** Agent runs continuously, uploading to `gdrive:/youtube_archive/`
2. **Phone:** App syncs from `gdrive:/youtube_archive/` to local storage
3. **Result:** Videos automatically appear on your phone!

---

## ⚙️ Configuration

### Desktop Agent Config (my_config.py)

```python
# Required
WATCHLIST_URL = "https://www.youtube.com/playlist?list=PLxxxxx"

# Optional
CHECK_INTERVAL = 3600  # 1 hour
MAX_RESOLUTION = "720"
CRF = 28  # Compression quality
DELETE_AFTER_UPLOAD = True
```

### Android App Settings

- **Sync Interval:** 15 min / 1 hour / 6 hours
- **WiFi Only:** ON (recommended)
- **Storage:** `/sdcard/Videos/YouTube/`

---

## 📊 Data Flow

```
YouTube Playlist
       ↓
  [Agent monitors every hour]
       ↓
  Download raw video (yt-dlp)
       ↓
  Compress to 720p MP4 (ffmpeg)
       ↓
  Upload to Google Drive (rclone)
       ↓
  Store metadata in SQLite
       ↓
  Delete local copy
       ↓
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       ↓
  Google Drive: youtube_archive/
       ↓
  [Android app monitors periodically]
       ↓
  Download to phone (WiFi only)
       ↓
  Show notification
       ↓
  Available in Videos app
```

---

## 🔒 Security Features

### Desktop Agent
- ✅ OAuth2 for Google Drive (via rclone)
- ✅ No credentials in code
- ✅ Parameterized SQL queries
- ✅ Input validation

### Android App
- ✅ OAuth2 for Google Drive
- ✅ Credentials in Android Keystore
- ✅ ProGuard code obfuscation
- ✅ Minimal permissions
- ✅ No analytics or tracking
- ✅ HTTPS only

---

## 📱 Android App Features

### User Interface
- **Material Design 3** (modern, clean)
- **Dark mode** (battery friendly)
- **Simple layout** (no clutter)

### Sync Engine
- **WorkManager** (battery optimized)
- **WiFi-only** option
- **Background sync** (works when app closed)
- **Smart scheduling** (respects Android battery restrictions)

### Notifications
- **Sync started:** "Checking for new videos..."
- **Progress:** "Downloaded 3 of 10 files"
- **Complete:** "Downloaded 5 new videos"
- **Error:** "Sync failed: [reason]"

---

## 🛠️ Build Commands Reference

### Desktop Agent

```bash
# Check dependencies
python agent.py --check-deps

# Run once (test)
python agent.py --config my_config.py --once

# Run continuously
python agent.py --config my_config.py

# View logs
tail -f youtube_archive.log
```

### Android App

```bash
# Build
make build          # Debug APK
make release        # Release APK (signed)
make bundle         # AAB for Play Store

# Install
make install        # USB
make install-wifi   # Wireless

# Test
make run           # Build + Install + Launch
make logs          # View app logs
make test          # Run unit tests

# Utilities
make clean         # Clean build
make size          # Check APK size
make devices       # List connected devices
```

---

## 📈 Storage Estimates

### Video Compression (720p, CRF 28)

| Original | Duration | Compressed | Savings |
|----------|----------|------------|---------|
| 500 MB   | 10 min   | ~80 MB     | 84%     |
| 1.5 GB   | 30 min   | ~250 MB    | 83%     |
| 3 GB     | 60 min   | ~500 MB    | 83%     |

### Phone Storage (100 videos)

- Average video: ~300 MB
- 100 videos: ~30 GB
- Recommend: 64 GB+ phone storage

---

## 🔄 Typical Workflow

### Daily Operation

1. **Morning:** Add videos to YouTube watchlist
2. **Automatic:** Agent downloads & uploads to Drive (every hour)
3. **Automatic:** Android app syncs to phone (when on WiFi)
4. **Evening:** Videos ready to watch on phone (offline)

### No manual intervention needed!

---

## 🐛 Troubleshooting

### Desktop Agent

**Problem:** "No videos in watchlist"
- Check WATCHLIST_URL is correct
- Verify playlist is accessible
- For private playlists: use cookies.txt

**Problem:** "Upload failed"
- Test rclone: `rclone lsd gdrive:/`
- Reconfigure: `rclone config`

### Android App

**Problem:** "Not connected to Google Drive"
- Check credentials.json exists
- Verify OAuth redirect URI in Google Console
- Re-authenticate in app

**Problem:** "Sync not working"
- Check WiFi is enabled (if WiFi-only is ON)
- Check battery saver is off
- View logs: `make logs`

---

## 📝 Maintenance

### Weekly
- Check agent logs: `tail youtube_archive.log`
- Verify phone storage space
- Review synced video count

### Monthly
- Update dependencies:
  ```bash
  brew upgrade yt-dlp ffmpeg rclone
  pip install --upgrade -r requirements.txt
  ```
- Clean old videos from Drive (if needed)
- Update Android app (if new version)

---

## 🎓 Technical Stack

### Desktop Agent
- **Language:** Python 3.11+
- **Tools:** yt-dlp, ffmpeg, rclone
- **Libraries:** pydantic, sqlite3, schedule

### Android App
- **Language:** Kotlin
- **UI:** Jetpack Compose (Material 3)
- **Architecture:** MVVM
- **Background:** WorkManager
- **Storage:** DataStore (preferences)
- **API:** Google Drive API v3
- **Min SDK:** 26 (Android 8.0+)
- **Target SDK:** 34 (Android 14)

---

## 📄 Project Files

### Desktop Agent
```
yt_sync/
├── agent.py                    # Main agent
├── tools.py                    # Tool wrappers
├── database.py                 # SQLite operations
├── config.py                   # Config management
├── my_config.py                # Your settings
├── requirements.txt            # Python dependencies
├── archive.db                  # SQLite database
└── youtube_archive.log         # Log file
```

### Android App
```
android_sync_app/
├── app/src/main/
│   ├── java/com/ytarchive/sync/  # Kotlin source
│   ├── res/                       # Resources
│   └── AndroidManifest.xml        # Manifest
├── Makefile                       # Build automation
├── SETUP_GUIDE.md                 # Detailed setup
└── README.md                      # Quick reference
```

---

## 🚀 Performance

### Desktop Agent
- **CPU:** Low (only during compression)
- **Memory:** ~200 MB
- **Disk:** Temporary (deletes after upload)
- **Network:** Uploads ~500 MB/hour (depends on videos)

### Android App
- **APK Size:** ~5 MB (release)
- **Memory:** ~30 MB (idle)
- **Battery:** Minimal (WorkManager optimized)
- **Network:** Downloads only on WiFi

---

## 🎯 Future Enhancements

Possible improvements:
- [ ] Video playback in app
- [ ] Delete synced videos after watching
- [ ] Multiple Google accounts
- [ ] Download priority/filtering
- [ ] Dark/Light theme toggle
- [ ] Statistics dashboard
- [ ] Video quality selection

---

## 📜 License

Free and open source. No restrictions.

---

## ✅ You're Ready!

**Desktop:**
```bash
python3 agent.py --config my_config.py
```

**Android:**
```bash
cd android_sync_app
make build
make install
```

Videos will automatically flow from YouTube → Drive → Phone!

Enjoy your automated video archive! 🎉
