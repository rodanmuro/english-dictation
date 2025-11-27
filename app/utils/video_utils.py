"""
Utility functions for YouTube video URL processing.
"""
import re
from urllib.parse import urlparse, parse_qs


def extract_video_id(youtube_url: str) -> str:
    """
    Extract video ID from YouTube URL.

    Supports multiple YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&feature=share
    - https://youtu.be/VIDEO_ID
    - https://youtu.be/VIDEO_ID?t=123

    Args:
        youtube_url: YouTube video URL

    Returns:
        str: Video ID (e.g., "7obx1BmOp3M")

    Raises:
        ValueError: If URL is invalid or video ID cannot be extracted

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=7obx1BmOp3M")
        '7obx1BmOp3M'
        >>> extract_video_id("https://youtu.be/7obx1BmOp3M")
        '7obx1BmOp3M'
    """
    # Clean the URL
    youtube_url = youtube_url.strip()

    # Pattern 1: youtube.com/watch?v=VIDEO_ID
    if "youtube.com/watch" in youtube_url:
        parsed = urlparse(youtube_url)
        video_id_list = parse_qs(parsed.query).get('v')
        if video_id_list:
            return video_id_list[0]

    # Pattern 2: youtu.be/VIDEO_ID
    if "youtu.be/" in youtube_url:
        # Extract video ID after youtu.be/
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', youtube_url)
        if match:
            return match.group(1)

    # Pattern 3: youtube.com/embed/VIDEO_ID
    if "youtube.com/embed/" in youtube_url:
        match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', youtube_url)
        if match:
            return match.group(1)

    # Pattern 4: youtube.com/v/VIDEO_ID
    if "youtube.com/v/" in youtube_url:
        match = re.search(r'youtube\.com/v/([a-zA-Z0-9_-]+)', youtube_url)
        if match:
            return match.group(1)

    # If no pattern matches, raise error
    raise ValueError(
        f"Invalid YouTube URL: {youtube_url}. "
        "Supported formats: youtube.com/watch?v=..., youtu.be/..."
    )


def validate_youtube_url(youtube_url: str) -> bool:
    """
    Validate if a URL is a valid YouTube URL.

    Args:
        youtube_url: URL to validate

    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    try:
        extract_video_id(youtube_url)
        return True
    except ValueError:
        return False
