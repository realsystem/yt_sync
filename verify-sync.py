#!/usr/bin/env python3
"""
Verify sync between database and Google Drive
Checks for:
- Videos in database but missing from Google Drive
- Videos on Google Drive but missing from database
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "archive.db"
GDRIVE_REMOTE = "gdrive:/youtube_archive/"

def get_db_videos():
    """Get list of video IDs from database with status 'archived'"""
    if not DB_PATH.exists():
        print("❌ Database not found:", DB_PATH)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, title FROM videos WHERE status = 'archived'")
    videos = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return videos

def get_gdrive_videos():
    """Get list of video IDs from Google Drive"""
    try:
        result = subprocess.run(
            ["rclone", "lsf", GDRIVE_REMOTE],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        # Extract video IDs from filenames (format: title_ID.mp4)
        video_ids = {}
        for f in files:
            if f.endswith('.mp4'):
                # Extract ID (last part before .mp4)
                parts = f.rsplit('_', 1)
                if len(parts) == 2:
                    video_id = parts[1].replace('.mp4', '')
                    video_ids[video_id] = f
        return video_ids
    except subprocess.CalledProcessError as e:
        print(f"❌ Error accessing Google Drive: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ rclone not found. Make sure it's installed.")
        sys.exit(1)

def main():
    print("=== Verifying Sync Between Database and Google Drive ===\n")

    print("📊 Fetching database records...")
    db_videos = get_db_videos()
    print(f"   Found {len(db_videos)} archived videos in database")

    print("\n☁️  Fetching Google Drive files...")
    gdrive_videos = get_gdrive_videos()
    print(f"   Found {len(gdrive_videos)} videos on Google Drive")

    print("\n" + "="*60)

    # Check for videos in DB but missing from Drive
    missing_from_drive = set(db_videos.keys()) - set(gdrive_videos.keys())
    if missing_from_drive:
        print("\n⚠️  Videos in database but MISSING from Google Drive:")
        for vid_id in missing_from_drive:
            print(f"   - {vid_id}: {db_videos[vid_id]}")
        print(f"\n   Total: {len(missing_from_drive)} videos")
        print("\n   Fix: Re-upload or mark as failed in database:")
        print("   sqlite3 data/archive.db \"UPDATE videos SET status='failed' WHERE video_id='VIDEO_ID';\"")
    else:
        print("\n✅ All database videos are on Google Drive")

    # Check for videos on Drive but missing from DB
    missing_from_db = set(gdrive_videos.keys()) - set(db_videos.keys())
    if missing_from_db:
        print("\n⚠️  Videos on Google Drive but MISSING from database:")
        for vid_id in missing_from_db:
            print(f"   - {vid_id}: {gdrive_videos[vid_id]}")
        print(f"\n   Total: {len(missing_from_db)} videos")
        print("\n   Fix: This is OK if videos were manually uploaded.")
        print("   Or remove from Google Drive if they shouldn't be there:")
        print("   rclone delete gdrive:/youtube_archive/FILENAME.mp4")
    else:
        print("\n✅ All Google Drive videos are in database")

    print("\n" + "="*60)

    if not missing_from_drive and not missing_from_db:
        print("\n🎉 Perfect sync! Database and Google Drive match.")
        return 0
    else:
        print("\n⚠️  Sync issues detected. Review above and take action if needed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
