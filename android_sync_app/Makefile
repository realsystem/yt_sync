# YouTube Archive Sync - Android App Makefile
# Build automation for macOS

.PHONY: help setup build release install run test clean

# Variables
ANDROID_HOME ?= $(HOME)/Library/Android/sdk
SDK_TOOLS_URL = https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip
GRADLE = /opt/homebrew/bin/gradle
ADB = $(ANDROID_HOME)/platform-tools/adb
PHONE_IP ?= 192.168.1.100
export PATH := /opt/homebrew/opt/openjdk@17/bin:$(PATH)

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help:
	@echo "$(GREEN)YouTube Archive Sync - Build Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  make setup              - Install Android SDK and dependencies"
	@echo "  make generate-keystore  - Generate signing keystore"
	@echo ""
	@echo "$(YELLOW)Build:$(NC)"
	@echo "  make build              - Build debug APK"
	@echo "  make release            - Build signed release APK"
	@echo "  make clean              - Clean build artifacts"
	@echo ""
	@echo "$(YELLOW)Install & Run:$(NC)"
	@echo "  make install            - Install on USB-connected device"
	@echo "  make install-wifi       - Install wirelessly (set PHONE_IP=x.x.x.x)"
	@echo "  make run                - Build and run on device"
	@echo "  make uninstall          - Remove app from device"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  make test               - Run unit tests"
	@echo "  make lint               - Run code linting"
	@echo "  make logs               - View app logs"
	@echo ""
	@echo "$(YELLOW)Emulator:$(NC)"
	@echo "  make create-emulator    - Create Android emulator"
	@echo "  make start-emulator     - Start emulator"
	@echo "  make stop-emulator      - Stop emulator"

# Setup Android SDK and tools
setup:
	@echo "$(GREEN)Setting up Android development environment...$(NC)"
	@mkdir -p $(ANDROID_HOME)/cmdline-tools
	@if [ ! -d "$(ANDROID_HOME)/cmdline-tools/latest" ]; then \
		echo "Downloading Android SDK tools..."; \
		curl -o /tmp/android-tools.zip $(SDK_TOOLS_URL); \
		unzip -q /tmp/android-tools.zip -d $(ANDROID_HOME)/cmdline-tools; \
		mv $(ANDROID_HOME)/cmdline-tools/cmdline-tools $(ANDROID_HOME)/cmdline-tools/latest; \
		rm /tmp/android-tools.zip; \
	fi
	@echo "Installing SDK packages..."
	@$(ANDROID_HOME)/cmdline-tools/latest/bin/sdkmanager --install \
		"platform-tools" \
		"platforms;android-34" \
		"build-tools;34.0.0" \
		"extras;google;google_play_services"
	@$(ANDROID_HOME)/cmdline-tools/latest/bin/sdkmanager --licenses
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "Add to your ~/.zshrc or ~/.bash_profile:"
	@echo "export ANDROID_HOME=$(ANDROID_HOME)"
	@echo "export PATH=\$$PATH:\$$ANDROID_HOME/platform-tools:\$$ANDROID_HOME/cmdline-tools/latest/bin"

# Generate signing keystore
generate-keystore:
	@echo "$(GREEN)Generating release keystore...$(NC)"
	@keytool -genkey -v \
		-keystore release.keystore \
		-alias ytarchive \
		-keyalg RSA \
		-keysize 2048 \
		-validity 10000
	@echo "$(GREEN)✓ Keystore generated: release.keystore$(NC)"
	@echo "Create keystore.properties with:"
	@echo "storeFile=release.keystore"
	@echo "storePassword=YOUR_PASSWORD"
	@echo "keyAlias=ytarchive"
	@echo "keyPassword=YOUR_PASSWORD"

# Build debug APK
build:
	@echo "$(GREEN)Building debug APK...$(NC)"
	@$(GRADLE) assembleDebug
	@echo "$(GREEN)✓ Debug APK built: app/build/outputs/apk/debug/app-debug.apk$(NC)"

# Build release APK
release:
	@echo "$(GREEN)Building release APK...$(NC)"
	@if [ ! -f "keystore.properties" ]; then \
		echo "$(YELLOW)Warning: keystore.properties not found$(NC)"; \
		echo "Run 'make generate-keystore' first"; \
		exit 1; \
	fi
	@$(GRADLE) assembleRelease
	@echo "$(GREEN)✓ Release APK built: app/build/outputs/apk/release/app-release.apk$(NC)"

# Clean build artifacts
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	@$(GRADLE) clean
	@rm -rf app/build
	@echo "$(GREEN)✓ Clean complete$(NC)"

# Install on USB-connected device
install: build
	@echo "$(GREEN)Installing app on device...$(NC)"
	@$(ADB) install -r app/build/outputs/apk/debug/app-debug.apk
	@echo "$(GREEN)✓ App installed$(NC)"

# Install wirelessly
install-wifi: build
	@echo "$(GREEN)Connecting to device at $(PHONE_IP)...$(NC)"
	@$(ADB) connect $(PHONE_IP):5555
	@$(ADB) -s $(PHONE_IP):5555 install -r app/build/outputs/apk/debug/app-debug.apk
	@echo "$(GREEN)✓ App installed wirelessly$(NC)"

# Uninstall app
uninstall:
	@echo "$(GREEN)Uninstalling app...$(NC)"
	@$(ADB) uninstall com.ytarchive.sync || true
	@echo "$(GREEN)✓ App uninstalled$(NC)"

# Build and run on device
run: install
	@echo "$(GREEN)Starting app...$(NC)"
	@$(ADB) shell am start -n com.ytarchive.sync/.MainActivity
	@echo "$(GREEN)✓ App started$(NC)"

# Run unit tests
test:
	@echo "$(GREEN)Running unit tests...$(NC)"
	@$(GRADLE) test
	@echo "$(GREEN)✓ Tests complete$(NC)"

# Run lint checks
lint:
	@echo "$(GREEN)Running lint checks...$(NC)"
	@$(GRADLE) lint
	@echo "$(GREEN)✓ Lint complete$(NC)"
	@echo "Report: app/build/reports/lint-results.html"

# View app logs
logs:
	@echo "$(GREEN)Viewing app logs (Ctrl+C to stop)...$(NC)"
	@$(ADB) logcat -s YTArchiveSync:V AndroidRuntime:E

logs-verbose:
	@$(ADB) logcat

# Create Android emulator
create-emulator:
	@echo "$(GREEN)Creating Android emulator...$(NC)"
	@$(ANDROID_HOME)/cmdline-tools/latest/bin/sdkmanager "system-images;android-34;google_apis;arm64-v8a"
	@echo "no" | $(ANDROID_HOME)/cmdline-tools/latest/bin/avdmanager create avd \
		-n YTArchive_Emulator \
		-k "system-images;android-34;google_apis;arm64-v8a" \
		-d "pixel_6"
	@echo "$(GREEN)✓ Emulator created: YTArchive_Emulator$(NC)"

# Start emulator
start-emulator:
	@echo "$(GREEN)Starting emulator...$(NC)"
	@$(ANDROID_HOME)/emulator/emulator -avd YTArchive_Emulator &

# Stop emulator
stop-emulator:
	@echo "$(GREEN)Stopping emulator...$(NC)"
	@$(ADB) emu kill

# Check connected devices
devices:
	@echo "$(GREEN)Connected devices:$(NC)"
	@$(ADB) devices -l

# Bundle release (for Play Store)
bundle:
	@echo "$(GREEN)Building Android App Bundle (AAB)...$(NC)"
	@$(GRADLE) bundleRelease
	@echo "$(GREEN)✓ Bundle built: app/build/outputs/bundle/release/app-release.aab$(NC)"
	@echo "Upload this to Google Play Console"

# Development build with debugging
build-debug:
	@echo "$(GREEN)Building debug version with verbose logging...$(NC)"
	@$(GRADLE) assembleDebug -Pdebug.logging=true

# Quick reinstall (faster than full install)
reinstall:
	@echo "$(GREEN)Reinstalling app...$(NC)"
	@$(ADB) shell pm uninstall com.ytarchive.sync || true
	@$(ADB) install -r app/build/outputs/apk/debug/app-debug.apk
	@echo "$(GREEN)✓ App reinstalled$(NC)"

# Enable wireless debugging
enable-wireless:
	@echo "$(GREEN)Enabling wireless debugging...$(NC)"
	@echo "1. Connect device via USB"
	@echo "2. Make sure device is on same WiFi network"
	@$(ADB) tcpip 5555
	@echo "3. Disconnect USB cable"
	@echo "4. Find device IP: Settings -> About -> Status -> IP"
	@echo "5. Run: make install-wifi PHONE_IP=<device_ip>"

# Check app size
size:
	@echo "$(GREEN)APK sizes:$(NC)"
	@du -h app/build/outputs/apk/debug/app-debug.apk 2>/dev/null || echo "Debug APK not built"
	@du -h app/build/outputs/apk/release/app-release.apk 2>/dev/null || echo "Release APK not built"

# Generate dependency report
dependencies:
	@echo "$(GREEN)Generating dependency report...$(NC)"
	@$(GRADLE) app:dependencies > dependencies.txt
	@echo "$(GREEN)✓ Report saved: dependencies.txt$(NC)"
