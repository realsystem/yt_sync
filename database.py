"""
Database module for YouTube Archive Agent.

Manages SQLite database for tracking archived videos.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class Database:
    """Manages the SQLite database for video archive tracking."""

    def __init__(self, db_path: str = "archive.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema if not exists."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    channel TEXT,
                    url TEXT NOT NULL,
                    duration INTEGER,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    status TEXT DEFAULT 'completed'
                )
            """)

            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_video_id
                ON videos(video_id)
            """)

            logger.info("Database initialized successfully")

    def video_exists(self, video_id: str) -> bool:
        """
        Check if a video has already been archived.

        Args:
            video_id: YouTube video ID

        Returns:
            True if video exists in database, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM videos WHERE video_id = ? LIMIT 1",
                (video_id,)
            )
            return cursor.fetchone() is not None

    def add_video(
        self,
        video_id: str,
        title: str,
        url: str,
        channel: Optional[str] = None,
        duration: Optional[int] = None,
        file_size: Optional[int] = None,
        status: str = 'completed'
    ) -> bool:
        """
        Add a new video to the archive database.

        Args:
            video_id: YouTube video ID
            title: Video title
            url: Video URL
            channel: Channel name (optional)
            duration: Video duration in seconds (optional)
            file_size: Compressed file size in bytes (optional)
            status: Video status (completed, archived, failed) (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO videos
                    (video_id, title, channel, url, duration, file_size, downloaded_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    video_id,
                    title,
                    channel,
                    url,
                    duration,
                    file_size,
                    datetime.now().isoformat(),
                    status
                ))
                logger.info(f"Added video to database: {video_id} - {title}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Video already exists in database: {video_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to add video to database: {e}")
            return False

    def get_all_videos(self) -> List[Dict]:
        """
        Get all archived videos.

        Returns:
            List of video records as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT video_id, title, channel, url, duration,
                       downloaded_at, file_size, status
                FROM videos
                ORDER BY downloaded_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_video_count(self) -> int:
        """
        Get total number of archived videos.

        Returns:
            Count of videos in database
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM videos")
            return cursor.fetchone()[0]

    def get_total_size(self) -> int:
        """
        Get total size of all archived videos.

        Returns:
            Total size in bytes
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(file_size) FROM videos WHERE file_size IS NOT NULL")
            result = cursor.fetchone()[0]
            return result if result else 0

    def delete_video(self, video_id: str) -> bool:
        """
        Delete a video record from the database.

        Args:
            video_id: YouTube video ID

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM videos WHERE video_id = ?", (video_id,))
                logger.info(f"Deleted video from database: {video_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete video: {e}")
            return False
