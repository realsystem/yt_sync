#!/usr/bin/env python3
"""
YouTube Archive Agent

An autonomous agent that maintains an archive of YouTube videos from a watchlist
and stores them compressed in Google Drive.

Agent workflow:
1. Observe: Read the YouTube watchlist
2. Compare: Check local database for already processed videos
3. Plan: Determine which videos need processing
4. Act: Download, compress, upload, and store metadata
5. Update: Record processed videos in database
6. Repeat: Run on scheduled interval
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Dict
import argparse

from config import Config, load_config
from database import Database
from tools import (
    get_watchlist_videos,
    download_video,
    compress_video,
    upload_to_drive,
    remove_local_files,
    check_dependencies,
    sanitize_filename,
    ToolError
)


def setup_logging(config: Config) -> None:
    """
    Configure structured logging.

    Args:
        config: Configuration object with logging settings
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, config.LOG_LEVEL.upper())

    handlers = [logging.StreamHandler(sys.stdout)]

    if config.LOG_FILE:
        handlers.append(logging.FileHandler(config.LOG_FILE))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )


class YouTubeArchiveAgent:
    """
    Autonomous agent for archiving YouTube videos to Google Drive.
    """

    def __init__(self, config: Config):
        """
        Initialize the agent.

        Args:
            config: Configuration object
        """
        self.config = config
        self.db = Database(str(config.DATABASE_PATH))
        self.logger = logging.getLogger(self.__class__.__name__)

    def observe(self) -> List[Dict]:
        """
        Step 1: Observe - Read the YouTube watchlist.

        Returns:
            List of video metadata from the watchlist
        """
        self.logger.info("=== OBSERVE: Fetching watchlist ===")
        videos = get_watchlist_videos(self.config.WATCHLIST_URL, self.config)
        self.logger.info(f"Observed {len(videos)} videos in watchlist")
        return videos

    def compare(self, videos: List[Dict]) -> List[Dict]:
        """
        Step 2: Compare - Filter out already processed videos.

        Args:
            videos: List of video metadata from watchlist

        Returns:
            List of new videos that need processing
        """
        self.logger.info("=== COMPARE: Checking database ===")
        new_videos = []
        skipped_count = 0

        for video in videos:
            video_id = video.get('video_id')
            title = video.get('title', '')

            if not video_id:
                continue

            # Skip private, deleted, or unavailable videos
            if title in ['[Private video]', '[Deleted video]', '[Unavailable video]']:
                self.logger.warning(f"Skipping unavailable video: {video_id} - {title}")
                skipped_count += 1
                continue

            if not self.db.video_exists(video_id):
                new_videos.append(video)
                self.logger.debug(f"New video found: {video_id} - {title}")
            else:
                self.logger.debug(f"Already archived: {video_id}")

        if skipped_count > 0:
            self.logger.warning(f"Skipped {skipped_count} unavailable videos")
        self.logger.info(f"Found {len(new_videos)} new videos to process")
        return new_videos

    def plan(self, new_videos: List[Dict]) -> List[Dict]:
        """
        Step 3: Plan - Determine processing order and strategy.

        Args:
            new_videos: List of new videos to process

        Returns:
            Ordered list of videos to process
        """
        self.logger.info("=== PLAN: Preparing processing queue ===")

        # Sort by duration (shortest first) to get quick wins
        sorted_videos = sorted(
            new_videos,
            key=lambda v: v.get('duration', 0) or 0
        )

        self.logger.info(f"Processing queue: {len(sorted_videos)} videos")
        return sorted_videos

    def act(self, video: Dict) -> bool:
        """
        Step 4: Act - Download, compress, upload, and store metadata.

        Args:
            video: Video metadata dictionary

        Returns:
            True if successful, False otherwise
        """
        video_id = video.get('video_id')
        title = video.get('title', 'Unknown')
        url = video.get('url')

        self.logger.info(f"=== ACT: Processing video ===")
        self.logger.info(f"Video: {title}")
        self.logger.info(f"ID: {video_id}")

        downloaded_file = None
        compressed_file = None

        try:
            # Download
            self.logger.info("→ Downloading...")
            downloaded_file = download_video(
                url,
                self.config.DOWNLOAD_DIR,
                self.config
            )

            if not downloaded_file:
                self.logger.error("Download failed")
                return False

            # Compress
            self.logger.info("→ Compressing...")
            # Create clean filename from title
            clean_filename = sanitize_filename(title, video_id)
            compressed_file = self.config.COMPRESS_DIR / f"{clean_filename}.mp4"
            compressed_file = compress_video(
                downloaded_file,
                compressed_file,
                self.config
            )

            if not compressed_file:
                self.logger.error("Compression failed")
                return False

            # Upload
            self.logger.info("→ Uploading to Google Drive...")
            upload_success = upload_to_drive(compressed_file, self.config)

            if not upload_success:
                self.logger.error("Upload failed")
                return False

            # Get file size
            file_size = compressed_file.stat().st_size if compressed_file.exists() else None

            # Update database
            self.logger.info("→ Updating database...")
            self.db.add_video(
                video_id=video_id,
                title=title,
                url=url,
                channel=video.get('channel'),
                duration=video.get('duration'),
                file_size=file_size
            )

            # Cleanup
            if self.config.DELETE_AFTER_UPLOAD:
                self.logger.info("→ Cleaning up local files...")
                remove_local_files(downloaded_file, compressed_file)

            self.logger.info(f"✓ Successfully processed: {title}")
            return True

        except ToolError as e:
            self.logger.error(f"Processing failed: {e}")
            return False

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return False

        finally:
            # Ensure cleanup happens even on error (if configured)
            if self.config.DELETE_AFTER_UPLOAD:
                remove_local_files(downloaded_file, compressed_file)

    def update(self, video: Dict, success: bool) -> None:
        """
        Step 5: Update - Record processing results.

        Args:
            video: Video metadata
            success: Whether processing was successful
        """
        if success:
            self.logger.info("=== UPDATE: Video successfully archived ===")
        else:
            self.logger.warning("=== UPDATE: Video processing failed ===")

    def run_cycle(self) -> Dict[str, int]:
        """
        Run one complete agent cycle.

        Returns:
            Statistics dictionary with processed/failed counts
        """
        stats = {
            'observed': 0,
            'new': 0,
            'processed': 0,
            'failed': 0
        }

        try:
            # Step 1: Observe
            videos = self.observe()
            stats['observed'] = len(videos)

            if not videos:
                self.logger.info("No videos in watchlist")
                return stats

            # Step 2: Compare
            new_videos = self.compare(videos)
            stats['new'] = len(new_videos)

            if not new_videos:
                self.logger.info("All videos already archived")
                return stats

            # Step 3: Plan
            processing_queue = self.plan(new_videos)

            # Step 4 & 5: Act and Update
            for video in processing_queue:
                success = self.act(video)
                self.update(video, success)

                if success:
                    stats['processed'] += 1
                else:
                    stats['failed'] += 1

        except Exception as e:
            self.logger.error(f"Cycle error: {e}", exc_info=True)

        return stats

    def run_forever(self) -> None:
        """
        Run the agent continuously with scheduled intervals.
        """
        self.logger.info("=== YouTube Archive Agent Started ===")
        self.logger.info(f"Check interval: {self.config.CHECK_INTERVAL} seconds")
        self.logger.info(f"Watchlist: {self.config.WATCHLIST_URL}")
        self.logger.info(f"Archive location: {self.config.RCLONE_REMOTE}")

        # Show archive statistics
        video_count = self.db.get_video_count()
        total_size = self.db.get_total_size()
        self.logger.info(f"Current archive: {video_count} videos, {total_size / 1024 / 1024:.2f} MB")

        cycle_number = 0

        try:
            while True:
                cycle_number += 1
                self.logger.info(f"\n{'=' * 60}")
                self.logger.info(f"Starting cycle #{cycle_number}")
                self.logger.info(f"{'=' * 60}\n")

                stats = self.run_cycle()

                self.logger.info(f"\n{'=' * 60}")
                self.logger.info(f"Cycle #{cycle_number} complete")
                self.logger.info(f"Observed: {stats['observed']} | New: {stats['new']} | "
                               f"Processed: {stats['processed']} | Failed: {stats['failed']}")
                self.logger.info(f"{'=' * 60}\n")

                self.logger.info(f"Sleeping for {self.config.CHECK_INTERVAL} seconds...")
                time.sleep(self.config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            self.logger.info("\n=== Agent stopped by user ===")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise


def main():
    """Main entry point for the agent."""
    parser = argparse.ArgumentParser(
        description='YouTube Archive Agent - Autonomous video archiving to Google Drive'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (do not loop)'
    )
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if required dependencies are installed'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    setup_logging(config)

    logger = logging.getLogger(__name__)

    # Check dependencies if requested
    if args.check_deps:
        logger.info("Checking dependencies...")
        if check_dependencies():
            logger.info("✓ All dependencies are installed")
            sys.exit(0)
        else:
            logger.error("✗ Missing dependencies")
            sys.exit(1)

    # Check dependencies before starting
    if not check_dependencies():
        logger.error("Cannot start: missing required dependencies")
        sys.exit(1)

    # Validate watchlist URL
    if not config.WATCHLIST_URL:
        logger.error("WATCHLIST_URL is not configured")
        logger.error("Please set it in config.py or environment variable YT_WATCHLIST_URL")
        sys.exit(1)

    # Initialize and run agent
    agent = YouTubeArchiveAgent(config)

    if args.once:
        logger.info("Running single cycle...")
        stats = agent.run_cycle()
        logger.info(f"Cycle complete - Processed: {stats['processed']}, Failed: {stats['failed']}")
    else:
        agent.run_forever()


if __name__ == '__main__':
    main()
