"""
Cache service for storing video metadata.
Manages cache.json file with video information.
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from app.config import settings


CACHE_FILE = os.path.join(settings.audio_dir, "cache.json")


def read_cache() -> List[Dict]:
    """
    Read the cache file and return list of video metadata.

    Returns:
        List of video metadata dictionaries
        Empty list if cache doesn't exist
    """
    if not os.path.exists(CACHE_FILE):
        return []

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Validate it's a list
        if not isinstance(cache_data, list):
            print(f"[WARN] Cache file is not a list, returning empty cache")
            return []

        return cache_data

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse cache.json: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to read cache: {e}")
        return []


def write_cache(cache_data: List[Dict]) -> bool:
    """
    Write video metadata to cache file.

    Args:
        cache_data: List of video metadata dictionaries

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure audio directory exists
        os.makedirs(settings.audio_dir, exist_ok=True)

        # Write to cache file with pretty formatting
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to write cache: {e}")
        return False


def add_video_to_cache(video_data: Dict) -> bool:
    """
    Add or update a video entry in the cache.

    Args:
        video_data: Dictionary with video metadata
                   Required keys: video_id, title
                   Optional keys: audio_path, srt_path, timestamp, segment_count

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate required fields
        if 'video_id' not in video_data:
            print("[ERROR] video_data must contain 'video_id'")
            return False
        if 'title' not in video_data:
            print("[ERROR] video_data must contain 'title'")
            return False

        # Read current cache
        cache = read_cache()

        # Check if video already exists
        video_id = video_data['video_id']
        existing_index = None

        for i, entry in enumerate(cache):
            if entry.get('video_id') == video_id:
                existing_index = i
                break

        # Add timestamp if not present
        if 'timestamp' not in video_data:
            video_data['timestamp'] = datetime.now().isoformat()

        # Update or append
        if existing_index is not None:
            # Update existing entry
            cache[existing_index] = video_data
            print(f"[CACHE] Updated video: {video_id}")
        else:
            # Add new entry
            cache.append(video_data)
            print(f"[CACHE] Added video: {video_id}")

        # Write back to cache
        return write_cache(cache)

    except Exception as e:
        print(f"[ERROR] Failed to add video to cache: {e}")
        return False


def get_video_from_cache(video_id: str) -> Optional[Dict]:
    """
    Get video metadata from cache by video ID.

    Args:
        video_id: YouTube video ID

    Returns:
        Video metadata dictionary if found, None otherwise
    """
    cache = read_cache()

    for entry in cache:
        if entry.get('video_id') == video_id:
            return entry

    return None


def video_in_cache(video_id: str) -> bool:
    """
    Check if a video exists in cache.

    Args:
        video_id: YouTube video ID

    Returns:
        True if video is in cache, False otherwise
    """
    return get_video_from_cache(video_id) is not None


def clear_cache() -> bool:
    """
    Clear all entries from cache.

    Returns:
        True if successful, False otherwise
    """
    return write_cache([])


def remove_video_from_cache(video_id: str) -> bool:
    """
    Remove a video from cache.

    Args:
        video_id: YouTube video ID to remove

    Returns:
        True if removed, False if not found or error
    """
    cache = read_cache()

    # Filter out the video
    new_cache = [entry for entry in cache if entry.get('video_id') != video_id]

    # Check if anything was removed
    if len(new_cache) == len(cache):
        print(f"[WARN] Video {video_id} not found in cache")
        return False

    print(f"[CACHE] Removed video: {video_id}")
    return write_cache(new_cache)