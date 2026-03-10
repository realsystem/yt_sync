#!/usr/bin/env python3
"""
Automated rclone setup script for YouTube Archive Agent.

This script helps configure rclone with your Google OAuth credentials.
"""

import json
import subprocess
import sys
from pathlib import Path


def load_client_secret(file_path):
    """Load Google OAuth client secret from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        if 'installed' in data:
            client_id = data['installed']['client_id']
            client_secret = data['installed']['client_secret']
            return client_id, client_secret
        else:
            print("❌ Error: Invalid client secret format")
            return None, None
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        return None, None
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in file: {file_path}")
        return None, None


def check_rclone_installed():
    """Check if rclone is installed."""
    try:
        subprocess.run(['rclone', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def authorize_rclone(client_id, client_secret):
    """Authorize rclone with Google OAuth."""
    print("\n🔐 Authorizing rclone with Google...")
    print("Your browser will open for authorization.")
    print("Please sign in and grant access.\n")

    try:
        result = subprocess.run(
            ['rclone', 'authorize', 'drive', client_id, client_secret],
            capture_output=True,
            text=True,
            check=True
        )

        # Extract token from output
        output = result.stdout
        if 'Paste the following into your remote machine' in output:
            # Extract the token
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'Paste the following' in line and i + 1 < len(lines):
                    token = lines[i + 1].strip()
                    return token

        print("✅ Authorization successful!")
        print("\nToken received. You can now configure rclone.")
        return output

    except subprocess.CalledProcessError as e:
        print(f"❌ Authorization failed: {e.stderr}")
        return None


def print_manual_instructions(client_id, client_secret):
    """Print manual configuration instructions."""
    print("\n" + "="*70)
    print("MANUAL RCLONE CONFIGURATION")
    print("="*70)
    print("\nRun this command:")
    print("\n  rclone config\n")
    print("Then follow these steps:")
    print("\n1. Choose: n (New remote)")
    print("2. Name: gdrive")
    print("3. Storage: drive (or the number for Google Drive)")
    print(f"4. client_id: {client_id}")
    print(f"5. client_secret: {client_secret}")
    print("6. Scope: 1 (Full access)")
    print("7. Root folder: (leave blank, press Enter)")
    print("8. Service account: (leave blank, press Enter)")
    print("9. Advanced config: n")
    print("10. Auto config: y (browser will open)")
    print("11. Sign in with your Google account")
    print("12. Confirm: y")
    print("\n" + "="*70)


def test_rclone_connection():
    """Test rclone connection to Google Drive."""
    print("\n🧪 Testing rclone connection...")

    try:
        result = subprocess.run(
            ['rclone', 'lsd', 'gdrive:'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Connection successful!")
        print("\nYour Google Drive folders:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Connection failed!")
        print(f"Error: {e.stderr}")
        return False


def create_archive_folder():
    """Create the youtube_archive folder in Google Drive."""
    print("\n📁 Creating youtube_archive folder...")

    try:
        subprocess.run(
            ['rclone', 'mkdir', 'gdrive:/youtube_archive'],
            capture_output=True,
            check=True
        )
        print("✅ Folder created: gdrive:/youtube_archive")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to create folder")
        return False


def main():
    """Main setup function."""
    print("="*70)
    print("YouTube Archive Agent - rclone Setup")
    print("="*70)

    # Check if rclone is installed
    if not check_rclone_installed():
        print("\n❌ Error: rclone is not installed")
        print("\nInstall it with:")
        print("  brew install rclone")
        sys.exit(1)

    print("\n✅ rclone is installed")

    # Find client secret file
    client_secret_files = list(Path('.').glob('client_secret_*.json'))

    if not client_secret_files:
        print("\n❌ No client secret file found")
        print("\nPlease ensure your client_secret_*.json file is in this directory")
        sys.exit(1)

    client_secret_file = client_secret_files[0]
    print(f"\n📄 Found client secret file: {client_secret_file.name}")

    # Load credentials
    client_id, client_secret = load_client_secret(client_secret_file)

    if not client_id or not client_secret:
        print("\n❌ Failed to load credentials")
        sys.exit(1)

    print(f"\n✅ Loaded credentials")
    print(f"   Client ID: {client_id[:50]}...")

    # Check if rclone is already configured
    try:
        result = subprocess.run(
            ['rclone', 'listremotes'],
            capture_output=True,
            text=True,
            check=True
        )

        if 'gdrive:' in result.stdout:
            print("\n⚠️  rclone is already configured with 'gdrive' remote")
            response = input("\nDo you want to reconfigure? (y/n): ").strip().lower()
            if response != 'y':
                print("\nSkipping configuration. Testing existing setup...")
                if test_rclone_connection():
                    create_archive_folder()
                    print("\n✅ Setup complete!")
                return
    except subprocess.CalledProcessError:
        pass

    # Print instructions
    print("\n" + "="*70)
    print("IMPORTANT: Before proceeding, update your OAuth configuration!")
    print("="*70)
    print("\n1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Select project: jovial-archive-489815-s4")
    print("3. Click on your OAuth 2.0 Client ID")
    print("4. Add these Authorized redirect URIs:")
    print("   - http://localhost")
    print("   - http://127.0.0.1:53682/")
    print("   - http://localhost:53682/")
    print("5. Click SAVE")
    print("6. Wait ~5 minutes for changes to propagate")
    print("\n" + "="*70)

    response = input("\nHave you completed the steps above? (y/n): ").strip().lower()

    if response != 'y':
        print("\nPlease complete the OAuth configuration first, then run this script again.")
        print_manual_instructions(client_id, client_secret)
        sys.exit(0)

    # Provide manual instructions
    print_manual_instructions(client_id, client_secret)

    print("\n\n⏳ Waiting for you to complete rclone configuration...")
    input("\nPress Enter once you've completed the 'rclone config' steps above...")

    # Test connection
    if test_rclone_connection():
        create_archive_folder()
        print("\n" + "="*70)
        print("✅ Setup Complete!")
        print("="*70)
        print("\nNext steps:")
        print("1. Configure your watchlist:")
        print("   cp config.example.py my_config.py")
        print("   nano my_config.py  # Set WATCHLIST_URL")
        print("\n2. Test the agent:")
        print("   python agent.py --config my_config.py --once")
        print("\n3. Run continuously:")
        print("   python agent.py --config my_config.py")
        print("="*70)
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
