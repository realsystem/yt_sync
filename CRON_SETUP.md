# Cron Job Setup for Daily Runs

The agent is configured to run once per day at 10pm via macOS cron.

## Quick Setup

Open your crontab:
```bash
crontab -e
```

Add this line:
```
0 22 * * * /Users/segorov/Projects/yt_sync/run-daily.sh
```

Save and exit (`:wq` in vim, or `Ctrl+X` then `Y` in nano).

## Verify

Check your crontab:
```bash
crontab -l
```

## Logs

View the cron execution logs:
```bash
tail -f /Users/segorov/Projects/yt_sync/data/cron.log
```

Or use:
```bash
cat data/cron.log
```

## Manual Test

Test the daily run manually:
```bash
make docker-daily
```

## How It Works

1. **10:00 PM daily**: Cron triggers `run-daily.sh`
2. **Script runs**: Starts Docker container in `--once` mode
3. **Agent processes**: Downloads, compresses, uploads all new videos
4. **Container exits**: Automatically removed (`--rm` flag)
5. **Logs saved**: All output goes to `data/cron.log`

## Troubleshooting

### Cron job not running

1. Check if cron has Full Disk Access:
   - System Preferences → Security & Privacy → Privacy
   - Select "Full Disk Access"
   - Add `/usr/sbin/cron` (may need to click the lock to make changes)

2. Check the log file:
   ```bash
   tail data/cron.log
   ```

3. Run manually to see errors:
   ```bash
   ./run-daily.sh
   ```

### Docker not found

Make sure Docker Desktop is running and starts automatically:
- Docker Desktop → Preferences → General
- Check "Start Docker Desktop when you log in"

### Permission denied

Make sure the script is executable:
```bash
chmod +x run-daily.sh
```

## Alternative: Run Continuously

If you prefer the agent to run continuously (checking every hour):
```bash
# Remove the cron job
crontab -e
# Delete the line with run-daily.sh

# Start in continuous mode
make docker-up
```

## Schedule Changes

To change the schedule, edit your crontab:
```bash
crontab -e
```

Common schedules:
- `0 22 * * *` - Daily at 10:00 PM (current)
- `0 2 * * *` - Daily at 2:00 AM
- `0 9,21 * * *` - Twice daily: 9 AM and 9 PM
- `0 22 * * 1-5` - Weekdays only at 10 PM
- `*/30 * * * *` - Every 30 minutes

## Monitoring

View recent runs:
```bash
tail -20 data/cron.log
```

Check database:
```bash
make db-stats
```

Check Google Drive:
```bash
rclone ls gdrive:/youtube_archive/
```
