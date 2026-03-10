# Complete Setup Guide - YouTube Archive Sync Android App

## Prerequisites

Before building the app, ensure you have:

1. **Java Development Kit (JDK) 17 or higher**
   ```bash
   # Check Java version
   java -version

   # Install JDK on macOS
   brew install openjdk@17
   ```

2. **Android SDK** (will be installed automatically by Makefile)

3. **Google Drive API Credentials** (from your existing OAuth setup)

---

## Step 1: Initial Setup

### 1.1 Clone/Navigate to Project

```bash
cd /Users/segorov/Projects/yt_sync/android_sync_app
```

### 1.2 Make gradlew Executable

```bash
chmod +x gradlew
```

### 1.3 Run Automatic Setup

```bash
make setup
```

This will:
- Download Android SDK command-line tools
- Install required SDK packages (API 34, build tools)
- Accept SDK licenses
- Set up environment

**Add to your shell profile** (~/.zshrc or ~/.bash_profile):

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin
```

Then reload:
```bash
source ~/.zshrc
```

---

## Step 2: Configure Google Drive API

### 2.1 Create credentials.json

Create file: `app/src/main/res/raw/credentials.json`

```bash
mkdir -p app/src/main/res/raw
```

Copy your Google OAuth credentials:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Security Note:** This file is excluded from git (.gitignore)

### 2.2 Update OAuth Redirect URI

In Google Cloud Console:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project: YOUR_PROJECT_NAME
3. Edit your OAuth client
4. Add redirect URI: `com.ytarchive.sync://oauth2callback`
5. Click SAVE

---

## Step 3: Generate Signing Key (for Release Builds)

```bash
make generate-keystore
```

You'll be prompted for:
- First and last name
- Organization
- City/Location
- State
- Country code
- Password (remember this!)

This creates `release.keystore`

### 3.1 Create keystore.properties

Create file in project root:

```bash
cat > keystore.properties << EOF
storeFile=release.keystore
storePassword=YOUR_KEYSTORE_PASSWORD
keyAlias=ytarchive
keyPassword=YOUR_KEY_PASSWORD
EOF
```

Replace `YOUR_KEYSTORE_PASSWORD` and `YOUR_KEY_PASSWORD` with the passwords you entered.

---

## Step 4: Build the App

### 4.1 Build Debug APK (for testing)

```bash
make build
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

### 4.2 Build Release APK (for production)

```bash
make release
```

Output: `app/build/outputs/apk/release/app-release.apk`

---

## Step 5: Install on Your Phone

### 5.1 Enable USB Debugging on Phone

1. Go to Settings → About Phone
2. Tap "Build Number" 7 times to enable Developer Mode
3. Go to Settings → Developer Options
4. Enable "USB Debugging"

### 5.2 Connect Phone via USB

```bash
# Check device is connected
adb devices
```

You should see your device listed.

### 5.3 Install App

```bash
make install
```

---

## Step 6: Test the App

### 6.1 Launch App

```bash
make run
```

Or launch manually from your phone's app drawer.

### 6.2 View Logs

```bash
make logs
```

This shows real-time logs from the app.

---

## Alternative: Install Wirelessly

### Enable Wireless Debugging

1. Connect phone via USB
2. Run:
   ```bash
   make enable-wireless
   ```

3. Disconnect USB

4. Find phone's IP address:
   - Settings → About → Status → IP Address
   - Let's say it's: `192.168.1.100`

5. Install wirelessly:
   ```bash
   make install-wifi PHONE_IP=192.168.1.100
   ```

---

## Common Build Commands

```bash
# Build debug APK
make build

# Build release APK
make release

# Install on connected device
make install

# Build and run
make run

# Run tests
make test

# Clean build
make clean

# View logs
make logs

# Check APK size
make size

# Generate dependency report
make dependencies
```

---

## Troubleshooting

### Build Fails with "SDK not found"

```bash
# Re-run setup
make setup

# Ensure ANDROID_HOME is set
echo $ANDROID_HOME
```

### "Device not found" when installing

```bash
# Check USB debugging is enabled
adb devices

# Try reconnecting USB cable

# Restart adb
adb kill-server
adb start-server
```

### Gradle Build Fails

```bash
# Clean and rebuild
make clean
make build

# Update Gradle wrapper
./gradlew wrapper --gradle-version=8.2
```

### App Crashes on Startup

```bash
# View crash logs
make logs

# Common causes:
# 1. Missing credentials.json
# 2. Incorrect OAuth configuration
# 3. Missing permissions
```

### Google Sign-In Fails

1. Check credentials.json exists in `app/src/main/res/raw/`
2. Verify OAuth redirect URI in Google Console
3. Ensure Google Drive API is enabled
4. Check app is using correct SHA-1 fingerprint (for production)

---

## Building for Google Play Store

### 1. Generate Signed Release APK

```bash
make release
```

### 2. Or Generate App Bundle (AAB) - Recommended

```bash
make bundle
```

Output: `app/build/outputs/bundle/release/app-release.aab`

### 3. Upload to Play Console

1. Go to: https://play.google.com/console
2. Create new app
3. Upload AAB file
4. Fill in store listing:
   - Title: "YT Archive Sync"
   - Short description: "Automatically sync YouTube videos from Google Drive to your phone"
   - Category: "Productivity" or "Tools"
   - Privacy Policy: (required - host a simple page)
5. Set content rating
6. Submit for review

---

## Security Checklist

Before releasing:

- [ ] Remove all test/debug code
- [ ] Credentials.json is in .gitignore
- [ ] ProGuard enabled for release build
- [ ] Release APK is signed
- [ ] No hardcoded passwords or API keys
- [ ] Permissions are minimal and justified
- [ ] Privacy policy is published

---

## Development Tips

### Fast Development Cycle

```bash
# Quick reinstall without full build
./gradlew installDebug

# Or use make command
make reinstall
```

### Debug with Android Studio

1. Open Android Studio
2. File → Open → Select `android_sync_app` folder
3. Wait for Gradle sync
4. Run → Run 'app'

### Testing on Emulator

```bash
# Create emulator
make create-emulator

# Start emulator
make start-emulator

# Install app
make install
```

---

## File Structure Reference

```
android_sync_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/ytarchive/sync/
│   │   │   ├── MainActivity.kt              ← Main UI
│   │   │   ├── SyncWorker.kt                ← Background sync
│   │   │   ├── DriveService.kt              ← Google Drive API
│   │   │   ├── SettingsManager.kt           ← Preferences
│   │   │   ├── NotificationHelper.kt        ← Notifications
│   │   │   └── AuthCallbackActivity.kt      ← OAuth callback
│   │   ├── res/
│   │   │   ├── values/
│   │   │   │   ├── strings.xml              ← App strings
│   │   │   │   ├── colors.xml               ← Color palette
│   │   │   │   └── themes.xml               ← App theme
│   │   │   ├── xml/
│   │   │   │   ├── file_paths.xml           ← File provider paths
│   │   │   │   ├── backup_rules.xml         ← Backup config
│   │   │   │   └── data_extraction_rules.xml
│   │   │   └── raw/
│   │   │       └── credentials.json         ← OAuth credentials
│   │   └── AndroidManifest.xml              ← App manifest
│   ├── build.gradle.kts                     ← App build config
│   └── proguard-rules.pro                   ← ProGuard rules
├── build.gradle.kts                         ← Project build config
├── settings.gradle.kts                      ← Gradle settings
├── gradle.properties                        ← Build properties
├── keystore.properties                      ← Signing config (create this)
├── release.keystore                         ← Signing key (generated)
├── Makefile                                 ← Build automation
└── README.md                                ← Documentation
```

---

## Next Steps

1. Build the app: `make build`
2. Install on your phone: `make install`
3. Open the app
4. Tap "Connect Google Drive"
5. Sign in with your Google account
6. Configure sync settings
7. Tap "Sync Now" to test

The app will then automatically sync in the background based on your configured interval!

---

## Support

For issues:
1. Check logs: `make logs`
2. Review this guide
3. Check Android documentation
4. File an issue in the repository

---

**You're ready to build!** Run `make build` to start.
