# YouTube Archive Sync - Android App

A minimalistic, secure Android app for automatically syncing videos from Google Drive to your phone.

## Features

- ✅ Automatic background sync from Google Drive
- ✅ WiFi-only sync option (saves mobile data)
- ✅ Configurable sync interval (15min, 1hr, 6hr, daily)
- ✅ Notifications on sync completion
- ✅ Simple, minimalistic UI
- ✅ Battery optimized (WorkManager)
- ✅ No ads, no tracking, free forever

## Build Requirements

- macOS (your MacBook)
- Android Studio or command-line build tools
- JDK 17+
- Android SDK (API 34)

## Quick Start

### 1. Setup (One-time)

```bash
# Install Android SDK and tools
make setup

# This will:
# - Download Android command-line tools
# - Install required SDK packages
# - Setup environment
```

### 2. Build the App

```bash
# Build debug APK
make build

# Build release APK (signed)
make release
```

### 3. Install on Phone

```bash
# Install on connected device via USB
make install

# Or install wirelessly (if phone IP is 192.168.1.100)
make install-wifi PHONE_IP=192.168.1.100
```

### 4. Development

```bash
# Run on connected device
make run

# View logs
make logs

# Run tests
make test

# Clean build
make clean
```

## Project Structure

```
android_sync_app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/ytarchive/sync/
│   │   │   │   ├── MainActivity.kt          # Main UI
│   │   │   │   ├── SyncWorker.kt            # Background sync
│   │   │   │   ├── DriveService.kt          # Google Drive API
│   │   │   │   ├── NotificationHelper.kt    # Notifications
│   │   │   │   └── SettingsManager.kt       # User preferences
│   │   │   ├── res/                         # Resources (UI, strings)
│   │   │   └── AndroidManifest.xml          # App configuration
│   │   └── test/                            # Unit tests
│   └── build.gradle.kts                     # App build config
├── build.gradle.kts                         # Project build config
├── settings.gradle.kts                      # Gradle settings
├── gradle.properties                        # Build properties
├── Makefile                                 # Build automation
└── README.md                                # This file
```

## Configuration

Edit these files before building:

### 1. Google Drive API Credentials

Create `app/src/main/res/raw/credentials.json`:
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
  }
}
```

### 2. App Signing (for Release)

Create `keystore.properties`:
```properties
storeFile=/path/to/keystore.jks
storePassword=your_store_password
keyAlias=your_key_alias
keyPassword=your_key_password
```

Generate keystore:
```bash
make generate-keystore
```

## Usage

### First Run Setup

1. Install the app on your phone
2. Open the app
3. Tap "Connect Google Drive"
4. Sign in with your Google account
5. Grant permissions
6. Configure sync settings:
   - Sync interval (default: 1 hour)
   - WiFi only (recommended: ON)
   - Storage location (default: /Videos/YouTube/)

### Background Sync

The app will automatically:
- Check Google Drive every hour (or your configured interval)
- Download new videos to your phone
- Show notification when complete
- Respect WiFi-only setting

### Manual Sync

Tap "Sync Now" button to force immediate sync.

## Building for Release

```bash
# 1. Generate signing key (first time only)
make generate-keystore

# 2. Build signed release APK
make release

# Output: app/build/outputs/apk/release/app-release.apk
```

## Publishing to Play Store

1. Build release APK: `make release`
2. Go to Google Play Console
3. Create new app
4. Upload APK
5. Fill in store listing
6. Submit for review

## Security

- ✅ Uses OAuth2 for Google Drive (no password stored)
- ✅ Credentials stored in Android Keystore
- ✅ HTTPS only communication
- ✅ No analytics or tracking
- ✅ Minimal permissions (Internet, Storage, Network state)
- ✅ Open source (audit the code!)

## Permissions Required

- `INTERNET` - Download from Google Drive
- `ACCESS_NETWORK_STATE` - Check WiFi status
- `WRITE_EXTERNAL_STORAGE` - Save videos to phone
- `POST_NOTIFICATIONS` - Show sync notifications (Android 13+)

## Troubleshooting

### Build fails

```bash
# Clean and rebuild
make clean
make build
```

### Can't connect to device

```bash
# Check device is connected
adb devices

# Enable USB debugging on phone:
# Settings -> Developer Options -> USB Debugging
```

### App crashes on startup

```bash
# View crash logs
make logs
```

### Sync not working

1. Check WiFi is enabled (if WiFi-only is ON)
2. Check Google Drive credentials are valid
3. Re-authenticate: Tap "Disconnect" then "Connect Google Drive"

## Development Tips

### Enable Developer Mode

```bash
# Build with debug logging
make build-debug

# View all logs
make logs-verbose
```

### Testing on Emulator

```bash
# Create emulator (first time)
make create-emulator

# Start emulator
make start-emulator

# Install app
make install
```

## License

Free and open source. Use, modify, distribute freely.

## Contributing

This is a minimal, focused app. Contributions welcome for:
- Bug fixes
- Security improvements
- Battery optimization
- Translation to other languages

No feature bloat - keep it simple!
