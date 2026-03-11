"""
Tools module for YouTube Archive Agent.

Wraps external tools: yt-dlp, ffmpeg, and rclone.
"""

import subprocess
import json
import logging
import time
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Base exception for tool-related errors."""
    pass


def sanitize_filename(title: str, video_id: str, max_length: int = 50) -> str:
    """
    Create a clean, filesystem-safe filename from video title.

    Args:
        title: Original video title
        video_id: YouTube video ID
        max_length: Maximum length for the title portion

    Returns:
        Sanitized filename (without extension)

    Examples:
        "My Cool Video! (2024)" -> "My_Cool_Video_2024_abc123"
        "测试视频 Test" -> "Test_abc123"
    """
    # Remove or replace special characters
    # Keep only alphanumeric, spaces, hyphens, underscores
    clean_title = re.sub(r'[^\w\s-]', '', title)

    # Replace multiple spaces with single space
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()

    # Replace spaces with underscores
    clean_title = clean_title.replace(' ', '_')

    # Remove multiple underscores
    clean_title = re.sub(r'_+', '_', clean_title)

    # Shorten if too long
    if len(clean_title) > max_length:
        clean_title = clean_title[:max_length].rstrip('_')

    # If title is empty or too short after sanitization, use a default
    if len(clean_title) < 3:
        clean_title = "video"

    # Append video ID to ensure uniqueness
    filename = f"{clean_title}_{video_id}"

    return filename


def find_tool(tool_name: str) -> str:
    """
    Find tool in PATH or common homebrew locations.

    Args:
        tool_name: Name of the tool to find

    Returns:
        Full path to the tool or just the tool name if found in PATH
    """
    # Try to find in PATH first
    try:
        result = subprocess.run(
            ['which', tool_name],
            capture_output=True,
            text=True,
            check=True
        )
        path = result.stdout.strip()
        if path:
            return path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check common homebrew locations on macOS
    common_paths = [
        f'/opt/homebrew/bin/{tool_name}',  # Apple Silicon
        f'/usr/local/bin/{tool_name}',      # Intel Mac
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    # Return tool name as fallback (will fail if not found)
    return tool_name


def run_command(
    cmd: List[str],
    max_retries: int = 3,
    retry_delay: int = 10,
    capture_output: bool = True
) -> Tuple[int, str, str]:
    """
    Run a shell command with retry logic.

    Args:
        cmd: Command and arguments as list
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        ToolError: If command fails after all retries
    """
    for attempt in range(max_retries):
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return result.returncode, result.stdout, result.stderr

            logger.warning(
                f"Command failed (attempt {attempt + 1}/{max_retries}): "
                f"{result.stderr}"
            )

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise ToolError(f"Command failed: {e}")

    raise ToolError(f"Command failed after {max_retries} attempts")


def get_watchlist_videos(watchlist_url: str, config: Config) -> List[Dict]:
    """
    Get video metadata from a YouTube watchlist/playlist.

    Args:
        watchlist_url: URL of the YouTube playlist or watch-later list
        config: Configuration object

    Returns:
        List of video metadata dictionaries

    Raises:
        ToolError: If yt-dlp fails to fetch playlist
    """
    if not watchlist_url:
        logger.error("No watchlist URL provided")
        return []

    logger.info(f"Fetching watchlist from: {watchlist_url}")

    yt_dlp = find_tool('yt-dlp')
    cmd = [
        yt_dlp,
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        watchlist_url
    ]

    # Add cookies file if it exists (for private playlists)
    cookies_file = Path('cookies.txt')
    if cookies_file.exists():
        cmd.extend(['--cookies', str(cookies_file)])

    try:
        returncode, stdout, stderr = run_command(cmd, max_retries=config.MAX_RETRIES)

        videos = []
        for line in stdout.strip().split('\n'):
            if not line:
                continue

            try:
                video_data = json.loads(line)
                videos.append({
                    'video_id': video_data.get('id', ''),
                    'title': video_data.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={video_data.get('id', '')}",
                    'duration': video_data.get('duration', 0),
                    'channel': video_data.get('uploader', video_data.get('channel', 'Unknown'))
                })
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse video data: {e}")
                continue

        logger.info(f"Found {len(videos)} videos in watchlist")
        return videos

    except ToolError as e:
        logger.error(f"Failed to fetch watchlist: {e}")
        return []


def download_video(url: str, output_dir: Path, config: Config) -> Optional[Path]:
    """
    Download a video using yt-dlp.

    Args:
        url: YouTube video URL
        output_dir: Directory to save downloaded video
        config: Configuration object

    Returns:
        Path to downloaded file, or None if failed

    Raises:
        ToolError: If download fails after retries
    """
    logger.info(f"Downloading video: {url}")

    output_template = str(output_dir / "%(id)s.%(ext)s")

    yt_dlp = find_tool('yt-dlp')
    cmd = [
        yt_dlp,
        "-f", "bestvideo+bestaudio/best",
        "-o", output_template,
        "--no-warnings",
        "--no-playlist",
        "--no-check-certificate",  # Skip SSL verification (for corporate proxies)
        url
    ]

    # Add cookies file if it exists (for private videos)
    cookies_file = Path('cookies.txt')
    if cookies_file.exists():
        cmd.extend(['--cookies', str(cookies_file)])

    try:
        returncode, stdout, stderr = run_command(
            cmd,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )

        # Find the downloaded file
        video_id = url.split('v=')[-1].split('&')[0]
        for file in output_dir.glob(f"{video_id}.*"):
            if file.is_file():
                logger.info(f"Downloaded: {file}")
                return file

        logger.error("Downloaded file not found")
        return None

    except ToolError as e:
        logger.error(f"Download failed: {e}")
        raise


def compress_video(
    input_path: Path,
    output_path: Path,
    config: Config
) -> Optional[Path]:
    """
    Compress video using ffmpeg for smartphone viewing.

    Args:
        input_path: Path to input video file
        output_path: Path to output compressed file
        config: Configuration object

    Returns:
        Path to compressed file, or None if failed

    Raises:
        ToolError: If compression fails
    """
    logger.info(f"Compressing video: {input_path}")

    # Ensure output path has .mp4 extension
    if output_path.suffix != '.mp4':
        output_path = output_path.with_suffix('.mp4')

    ffmpeg = find_tool('ffmpeg')
    cmd = [
        ffmpeg,
        "-i", str(input_path),
        "-vf", f"scale=-2:{config.MAX_RESOLUTION}",
        "-c:v", config.VIDEO_CODEC,
        "-preset", config.VIDEO_PRESET,
        "-crf", str(config.CRF),
        "-c:a", config.AUDIO_CODEC,
        "-b:a", config.AUDIO_BITRATE,
        "-movflags", "+faststart",
        "-y",  # Overwrite output file
        str(output_path)
    ]

    try:
        returncode, stdout, stderr = run_command(
            cmd,
            max_retries=1,  # Don't retry compression
            capture_output=True
        )

        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"Compressed: {output_path} ({file_size / 1024 / 1024:.2f} MB)")
            return output_path
        else:
            logger.error("Compressed file not found")
            return None

    except ToolError as e:
        logger.error(f"Compression failed: {e}")
        raise


def upload_to_drive(file_path: Path, config: Config) -> bool:
    """
    Upload file to Google Drive using rclone.

    Args:
        file_path: Path to file to upload
        config: Configuration object

    Returns:
        True if upload successful, False otherwise

    Raises:
        ToolError: If upload fails after retries
    """
    logger.info(f"Uploading to Google Drive: {file_path}")

    rclone = find_tool('rclone')
    cmd = [
        rclone,
        "copy",
        str(file_path),
        config.RCLONE_REMOTE,
        "--progress"
    ]

    try:
        returncode, stdout, stderr = run_command(
            cmd,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY
        )

        logger.info(f"Upload completed: {file_path.name}")
        return True

    except ToolError as e:
        logger.error(f"Upload failed: {e}")
        raise


def remove_local_files(*file_paths: Path) -> None:
    """
    Remove local files after successful upload.

    Args:
        *file_paths: Variable number of file paths to remove
    """
    for file_path in file_paths:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Removed local file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")


def get_gdrive_video_ids(config: Config) -> set:
    """
    Get list of video IDs already uploaded to Google Drive.

    Extracts video IDs from filenames using pattern: TITLE_VIDEO_ID.mp4

    Args:
        config: Configuration object

    Returns:
        Set of video IDs (strings) found on Google Drive

    Examples:
        - "My_Video_Title_abc123.mp4" -> "abc123"
        - "Test_xyz789.mp4" -> "xyz789"
    """
    logger.info("Checking Google Drive for existing videos...")

    rclone = find_tool('rclone')
    cmd = [
        rclone,
        "lsf",
        config.RCLONE_REMOTE,
        "--files-only"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )

        if result.returncode != 0:
            logger.warning(f"Could not list Google Drive files: {result.stderr}")
            return set()

        video_ids = set()
        files = result.stdout.strip().split('\n')

        for filename in files:
            if not filename or not filename.endswith('.mp4'):
                continue

            # Extract video ID from filename pattern: TITLE_VIDEO_ID.mp4
            # YouTube video IDs are ALWAYS exactly 11 characters
            # Take the last 11 characters before .mp4
            try:
                # Remove .mp4 extension
                name_without_ext = filename[:-4]

                # Get the last 11 characters (video ID is always 11 chars)
                if len(name_without_ext) >= 11:
                    potential_id = name_without_ext[-11:]

                    # YouTube video IDs are 11 characters, alphanumeric with - and _
                    if re.match(r'^[A-Za-z0-9_-]{11}$', potential_id):
                        video_ids.add(potential_id)
                        logger.debug(f"Found on Drive: {potential_id} ({filename})")
                    else:
                        logger.debug(f"Skipping non-standard filename: {filename}")
            except Exception as e:
                logger.debug(f"Could not parse filename: {filename} - {e}")
                continue

        logger.info(f"Found {len(video_ids)} videos already on Google Drive")
        return video_ids

    except subprocess.TimeoutExpired:
        logger.warning("Timeout checking Google Drive, skipping Drive check")
        return set()
    except Exception as e:
        logger.warning(f"Error checking Google Drive: {e}")
        return set()


def check_dependencies() -> bool:
    """
    Check if all required external tools are installed.

    Returns:
        True if all dependencies are available, False otherwise
    """
    required_tools = ['yt-dlp', 'ffmpeg', 'rclone']
    missing_tools = []

    for tool in required_tools:
        tool_path = find_tool(tool)
        try:
            result = subprocess.run(
                [tool_path, '--version'],
                capture_output=True,
                check=False  # Don't raise on non-zero exit
            )
            # ffmpeg returns 0, but some tools might return 1 for --version
            # Check if we got any output (stdout or stderr)
            if result.stdout or result.stderr:
                logger.info(f"✓ {tool} is installed at {tool_path}")
            else:
                logger.error(f"✗ {tool} is NOT installed")
                missing_tools.append(tool)
        except FileNotFoundError:
            logger.error(f"✗ {tool} is NOT installed")
            missing_tools.append(tool)

    if missing_tools:
        logger.error(f"Missing required tools: {', '.join(missing_tools)}")
        logger.error("Please install them using: brew install " + " ".join(missing_tools))
        return False

    logger.info("All required tools are installed")
    return True
