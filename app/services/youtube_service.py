"""
YouTube audio download service.
Downloads audio from YouTube videos and converts to MP3 format.
"""
import os
import asyncio
from typing import Dict
import yt_dlp

from app.config import settings


async def download_audio(video_id: str) -> Dict[str, str]:
    """
    Download audio from YouTube video and convert to MP3.

    This function downloads the best quality audio available from a YouTube video
    and converts it to MP3 format (192 kbps). If the file already exists, it skips
    the download and returns the existing file information.

    Args:
        video_id: YouTube video ID (e.g., "7obx1BmOp3M")

    Returns:
        Dict containing:
            - video_id (str): The YouTube video ID
            - title (str): Video title
            - audio_path (str): Path to the downloaded MP3 file

    Raises:
        Exception: If download fails or video is unavailable

    Example:
        >>> result = await download_audio("7obx1BmOp3M")
        >>> print(result)
        {
            "video_id": "7obx1BmOp3M",
            "title": "Video Title",
            "audio_path": "app/static/audios/7obx1BmOp3M.mp3"
        }
    """
    # Ensure audio directory exists
    os.makedirs(settings.audio_dir, exist_ok=True)

    # Define output path
    output_path = os.path.join(settings.audio_dir, f"{video_id}.mp3")

    # Check if already downloaded
    if os.path.exists(output_path):
        print(f"[OK] Audio already exists: {output_path}")

        # Try to get video title from existing info file
        info_file = os.path.join(settings.audio_dir, f"{video_id}.info.json")
        title = video_id  # Default to video_id if no info file

        if os.path.exists(info_file):
            import json
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    title = info.get('title', video_id)
            except Exception:
                pass  # If reading fails, use video_id as title

        return {
            "video_id": video_id,
            "title": title,
            "audio_path": output_path
        }

    # yt-dlp configuration
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(settings.audio_dir, f"{video_id}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,  # Show download progress
        'no_warnings': False,
        'extract_flat': False,
        'writeinfojson': True,  # Save video info for title retrieval
    }

    # Build YouTube URL
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"[DOWNLOAD] Starting download from: {youtube_url}")

    # Download in a thread pool to avoid blocking
    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            return info

    # Run blocking operation in thread pool
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _download)

    # Extract title
    title = info.get('title', video_id)

    print(f"[OK] Audio downloaded: {output_path}")
    print(f"[OK] Title: {title}")

    return {
        "video_id": video_id,
        "title": title,
        "audio_path": output_path
    }


def get_audio_path(video_id: str) -> str:
    """
    Get the file path for a video's audio file.

    Args:
        video_id: YouTube video ID

    Returns:
        str: Path to the MP3 file
    """
    return os.path.join(settings.audio_dir, f"{video_id}.mp3")


def audio_exists(video_id: str) -> bool:
    """
    Check if audio file already exists for a video.

    Args:
        video_id: YouTube video ID

    Returns:
        bool: True if audio file exists, False otherwise
    """
    return os.path.exists(get_audio_path(video_id))