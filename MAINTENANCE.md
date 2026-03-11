# Maintenance & Cleanup Guide

This guide covers how to prevent double processing and maintain the YouTube archive system.

## How Double Processing is Prevented

The agent uses **multiple layers** to prevent processing videos twice:

### 1. Database Check (Primary Protection)
Every time the agent runs, it:
1. Fetches the watchlist from YouTube
2. **Checks the database** for each video ID
3. Only processes videos **not already in the database**

```python
# In agent.py - compare() method
if self.db.video_exists(video_id):
    continue  # Skip, already processed
```

### 2. Google Drive Check (Safety Layer)
**NEW:** Before downloading, the agent also checks Google Drive:
1. Lists all `.mp4` files from Google Drive
2. Extracts video IDs using the naming pattern: `TITLE_VIDEO_ID.mp4`
3. Skips videos that are already uploaded
4. **Auto-syncs**: If video is on Drive but not in database, it adds it to the database

```python
# In agent.py - compare() method
gdrive_video_ids = get_gdrive_video_ids(self.config)
if video_id in gdrive_video_ids:
    # Already on Drive, add to database to sync state
    self.db.add_video(...)
    continue
```

**Benefits:**
- ✅ Prevents re-downloading if database was reset
- ✅ Prevents re-uploading if file already exists on Drive
- ✅ Auto-syncs database with Drive state
- ✅ Safe even after manual uploads to Drive

### 3. Transactional Updates
The database is only updated **after successful upload** to Google Drive:
- ✅ Download → Compress → Upload → **Update DB** → Cleanup
- ❌ If upload fails, video stays OUT of database
- ✅ Next run will retry the failed video

### 4. Atomic File Operations
- Downloads go to `data/downloads/VIDEO_ID.mp4`
- Compressed files go to `data/compressed/TITLE_VIDEO_ID.mp4`
- Local files are **deleted immediately** after successful upload
- No leftover files = no confusion

## Regular Cleanup Procedures

### Quick Check (Daily/Weekly)
```bash
# Show current status
make db-stats

# View recent cron runs
tail -20 data/cron.log

# Check for orphaned files
make cleanup
```

### Verify Sync (Weekly/Monthly)
```bash
# Compare database with Google Drive
make verify-sync
```

This checks:
- Videos in database but missing from Google Drive ⚠️
- Videos on Google Drive but missing from database ℹ️

### Full Cleanup (As Needed)
```bash
# Interactive cleanup script
make cleanup
```

This will:
1. Find orphaned downloads (incomplete/failed downloads)
2. Find orphaned compressed files (failed uploads)
3. Show database statistics
4. Check for running containers
5. Show disk space

## Common Scenarios

### Scenario 1: Upload Failed Mid-Process

**What happens:**
- Video downloads successfully
- Compression succeeds
- Upload to Google Drive fails (network issue, quota, etc.)
- Compressed file remains in `data/compressed/`
- Database is **NOT updated** (video still marked as "not processed")

**How to fix:**
```bash
# 1. Check for orphaned files
make cleanup

# 2. Let the agent retry on next run
make docker-daily
# OR wait for cron (10pm)

# 3. Verify after retry
make verify-sync
```

### Scenario 2: Agent Ran Multiple Times

**What happens:**
- First run: processes videos, updates database
- Second run: fetches watchlist, checks database, **finds all videos already processed**, exits
- No double processing! ✅

**No action needed** - the database prevents duplicates.

### Scenario 3: Running Both Cron AND Continuous Mode

**Danger:** Both processes could interfere with each other.

**Prevention:**
```bash
# Check if container is running
docker ps | grep youtube-archive

# If continuous mode is running
make docker-down

# Then use cron only (recommended)
crontab -l
```

**Rule:** Choose ONE execution method:
- ✅ **Cron daily** (recommended for most users)
- ✅ **Continuous mode** (for 24/7 monitoring)
- ❌ **Both at once** (will cause conflicts)

### Scenario 4: Database Corruption

**Rare but possible** if system crashes during write.

**Symptoms:**
```bash
make db-stats
# Returns error or weird numbers
```

**Recovery:**
```bash
# 1. Backup current database
cp data/archive.db data/archive.db.backup

# 2. Try to repair
sqlite3 data/archive.db "PRAGMA integrity_check;"

# 3. If corrupt, rebuild from Google Drive
make verify-sync
# This will show what's on Drive

# 4. Export what you can
sqlite3 data/archive.db ".dump" > backup.sql

# 5. Create fresh database
rm data/archive.db
make docker-daily  # Creates new database
```

### Scenario 5: Manually Uploaded Videos to Google Drive

If you uploaded videos directly to Google Drive (not through the agent):

```bash
# Check the difference
make verify-sync
# Will show: "Videos on Google Drive but MISSING from database"

# This is OK! The database tracks agent-processed videos.
# Manually uploaded videos won't appear in database.
```

## Preventing Issues

### Best Practices

1. **Use ONE execution method**
   - Cron daily (recommended): `crontab -e`
   - OR continuous: `make docker-up`
   - NOT both

2. **Regular monitoring**
   ```bash
   # Weekly check
   make verify-sync
   make db-stats
   ```

3. **Keep Docker Desktop running**
   - Set to start on login
   - Otherwise cron jobs will fail

4. **Monitor disk space**
   ```bash
   df -h /Users/segorov/Projects/yt_sync
   ```

5. **Check logs regularly**
   ```bash
   tail -f data/cron.log
   ```

### Automatic Cleanup

The agent **already cleans up** after each video:
```python
# In agent.py - act() method
cleanup_files([
    download_path,
    compressed_path
])
```

Files are removed **immediately** after successful upload.

### Manual Cleanup

If you need to clean up manually:

```bash
# Remove all orphaned files (safe)
rm -f data/downloads/*
rm -f data/compressed/*

# Database is preserved
ls -lh data/archive.db
```

## Emergency Procedures

### Reset Everything (Nuclear Option)

⚠️ **WARNING:** This deletes all tracking. Videos on Google Drive are safe.

```bash
# 1. Stop agent
make docker-down

# 2. Backup database
cp data/archive.db data/archive.db.emergency-backup

# 3. Delete database
rm data/archive.db

# 4. Delete all local files
rm -f data/downloads/*
rm -f data/compressed/*

# 5. Run agent (creates fresh database)
make docker-daily

# 6. Verify Google Drive (still has all videos)
rclone ls gdrive:/youtube_archive/
```

### Restore from Backup

```bash
# Stop agent
make docker-down

# Restore database
cp data/archive.db.backup data/archive.db

# Verify
make db-stats
make verify-sync

# Resume
make docker-up
# OR let cron run
```

## Monitoring Commands Quick Reference

```bash
# Status
make db-stats                    # Database statistics
make verify-sync                 # Check DB vs Google Drive sync
make cleanup                     # Interactive cleanup

# Logs
tail -f data/cron.log           # Watch cron executions
docker logs youtube-archive     # Container logs (if running)

# Files
ls -lh data/downloads/          # Should be empty
ls -lh data/compressed/         # Should be empty
ls -lh data/archive.db          # Database file

# Google Drive
rclone ls gdrive:/youtube_archive/       # List all files
rclone size gdrive:/youtube_archive/     # Total size

# Containers
docker ps | grep youtube        # Running containers
make docker-stats               # Resource usage
```

## Troubleshooting

### "Videos processed but not in Google Drive"
```bash
make verify-sync
# Shows: "Videos in database but MISSING from Google Drive"

# Solution: Re-upload failed videos
# Mark them as failed in DB
sqlite3 data/archive.db "UPDATE videos SET status='failed' WHERE video_id='VIDEO_ID';"

# Next run will retry
make docker-daily
```

### "Orphaned files accumulating"
```bash
make cleanup
# Answer 'y' to remove orphaned files

# Check why uploads are failing
tail -50 data/cron.log
```

### "Database says 0 videos but Drive has many"
```bash
# Database was deleted/reset but Drive is fine
# This is OK - database will rebuild as new videos come in
# Old videos on Drive are safe and can stay there
make verify-sync  # See the difference
```

## Summary

**The system is designed to be safe:**
- ✅ Database prevents double processing
- ✅ Files deleted after successful upload
- ✅ Failed uploads can be retried
- ✅ Google Drive is the source of truth (videos are safe there)
- ✅ Database can be rebuilt if needed

**Regular maintenance:**
1. Weekly: `make verify-sync`
2. Monthly: `make cleanup`
3. Always: Check `data/cron.log` for errors

**Golden rule:**
The database tracks what the agent has processed. Google Drive has the actual videos. If they don't match, it's usually because:
- Upload failed (retry will fix)
- Manual upload (that's fine)
- Database was reset (rebuild over time)
