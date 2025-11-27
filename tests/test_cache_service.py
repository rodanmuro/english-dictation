"""
Test script for cache service.
"""
import json
import os
from app.services.cache_service import (
    read_cache,
    write_cache,
    add_video_to_cache,
    get_video_from_cache,
    video_in_cache,
    clear_cache,
    remove_video_from_cache,
    CACHE_FILE
)


def test_write_and_read():
    """Test writing and reading cache."""

    print("=" * 60)
    print("Test 1: Write and Read Cache")
    print("=" * 60)
    print()

    # Clean up first
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("[CLEANUP] Removed existing cache.json")
        print()

    # Test data
    test_data = [
        {
            "video_id": "test123",
            "title": "Test Video 1",
            "audio_path": "app/static/audios/test123.mp3",
            "srt_path": "app/static/audios/test123.srt",
            "segment_count": 10,
            "timestamp": "2025-11-27T10:00:00"
        },
        {
            "video_id": "test456",
            "title": "Test Video 2",
            "audio_path": "app/static/audios/test456.mp3",
            "srt_path": "app/static/audios/test456.srt",
            "segment_count": 15,
            "timestamp": "2025-11-27T11:00:00"
        }
    ]

    # Write cache
    print("Writing test data to cache...")
    success = write_cache(test_data)
    print(f"[{'OK' if success else 'FAIL'}] Write cache: {success}")
    print()

    # Verify file exists
    exists = os.path.exists(CACHE_FILE)
    print(f"[{'OK' if exists else 'FAIL'}] Cache file exists: {exists}")
    print()

    # Read cache
    print("Reading cache...")
    cache_data = read_cache()
    print(f"[OK] Read {len(cache_data)} entries")
    print()

    # Verify data
    data_matches = cache_data == test_data
    print(f"[{'OK' if data_matches else 'FAIL'}] Data matches: {data_matches}")
    print()

    # Display cache
    print("Cache contents:")
    print("-" * 60)
    print(json.dumps(cache_data, indent=2))
    print("-" * 60)
    print()

    return success and exists and data_matches


def test_add_video():
    """Test adding video to cache."""

    print("=" * 60)
    print("Test 2: Add Video to Cache")
    print("=" * 60)
    print()

    # Clear cache first
    clear_cache()
    print("[CLEANUP] Cleared cache")
    print()

    # Add first video
    video1 = {
        "video_id": "jNQXAC9IVRw",
        "title": "Me at the zoo",
        "audio_path": "app/static/audios/jNQXAC9IVRw.mp3",
        "srt_path": "app/static/audios/jNQXAC9IVRw.srt",
        "segment_count": 8
    }

    print("Adding video 1...")
    success1 = add_video_to_cache(video1)
    print(f"[{'OK' if success1 else 'FAIL'}] Added video 1: {success1}")
    print()

    # Add second video
    video2 = {
        "video_id": "dQw4w9WgXcQ",
        "title": "Never Gonna Give You Up",
        "audio_path": "app/static/audios/dQw4w9WgXcQ.mp3",
        "srt_path": "app/static/audios/dQw4w9WgXcQ.srt",
        "segment_count": 100
    }

    print("Adding video 2...")
    success2 = add_video_to_cache(video2)
    print(f"[{'OK' if success2 else 'FAIL'}] Added video 2: {success2}")
    print()

    # Read cache
    cache = read_cache()
    count_correct = len(cache) == 2
    print(f"[{'OK' if count_correct else 'FAIL'}] Cache has 2 entries: {count_correct}")
    print()

    # Display cache
    print("Cache contents:")
    print("-" * 60)
    for entry in cache:
        print(f"ID: {entry['video_id']}")
        print(f"  Title: {entry['title']}")
        print(f"  Segments: {entry.get('segment_count', 'N/A')}")
        print(f"  Timestamp: {entry.get('timestamp', 'N/A')}")
        print()
    print("-" * 60)
    print()

    return success1 and success2 and count_correct


def test_get_video():
    """Test getting video from cache."""

    print("=" * 60)
    print("Test 3: Get Video from Cache")
    print("=" * 60)
    print()

    # Get existing video
    video_id = "jNQXAC9IVRw"
    print(f"Getting video: {video_id}")
    video = get_video_from_cache(video_id)

    if video:
        print("[OK] Video found")
        print(f"  Title: {video['title']}")
        print(f"  Segments: {video.get('segment_count', 'N/A')}")
        print()
        found = True
    else:
        print("[FAIL] Video not found")
        print()
        found = False

    # Get non-existing video
    print("Getting non-existing video: xyz123")
    video_none = get_video_from_cache("xyz123")
    not_found = video_none is None
    print(f"[{'OK' if not_found else 'FAIL'}] Returns None: {not_found}")
    print()

    return found and not_found


def test_video_exists():
    """Test checking if video exists."""

    print("=" * 60)
    print("Test 4: Check Video Exists")
    print("=" * 60)
    print()

    # Check existing
    exists1 = video_in_cache("jNQXAC9IVRw")
    print(f"[{'OK' if exists1 else 'FAIL'}] jNQXAC9IVRw exists: {exists1}")

    # Check non-existing
    exists2 = video_in_cache("xyz123")
    not_exists = not exists2
    print(f"[{'OK' if not_exists else 'FAIL'}] xyz123 not exists: {not_exists}")
    print()

    return exists1 and not_exists


def test_update_video():
    """Test updating video in cache."""

    print("=" * 60)
    print("Test 5: Update Video in Cache")
    print("=" * 60)
    print()

    # Update existing video
    video_id = "jNQXAC9IVRw"
    updated_video = {
        "video_id": video_id,
        "title": "Me at the zoo [UPDATED]",
        "audio_path": "app/static/audios/jNQXAC9IVRw.mp3",
        "srt_path": "app/static/audios/jNQXAC9IVRw.srt",
        "segment_count": 12  # Changed from 8 to 12
    }

    print(f"Updating video: {video_id}")
    success = add_video_to_cache(updated_video)
    print(f"[{'OK' if success else 'FAIL'}] Update success: {success}")
    print()

    # Get updated video
    video = get_video_from_cache(video_id)

    # Check if updated
    title_updated = video['title'] == "Me at the zoo [UPDATED]"
    count_updated = video['segment_count'] == 12

    print(f"[{'OK' if title_updated else 'FAIL'}] Title updated: {title_updated}")
    print(f"[{'OK' if count_updated else 'FAIL'}] Segment count updated: {count_updated}")
    print()

    # Check cache size didn't increase
    cache = read_cache()
    size_correct = len(cache) == 2  # Should still be 2, not 3
    print(f"[{'OK' if size_correct else 'FAIL'}] Cache size unchanged: {size_correct} (still 2 entries)")
    print()

    return success and title_updated and count_updated and size_correct


def test_remove_video():
    """Test removing video from cache."""

    print("=" * 60)
    print("Test 6: Remove Video from Cache")
    print("=" * 60)
    print()

    # Remove video
    video_id = "dQw4w9WgXcQ"
    print(f"Removing video: {video_id}")
    success = remove_video_from_cache(video_id)
    print(f"[{'OK' if success else 'FAIL'}] Remove success: {success}")
    print()

    # Check if removed
    exists = video_in_cache(video_id)
    removed = not exists
    print(f"[{'OK' if removed else 'FAIL'}] Video removed: {removed}")
    print()

    # Check cache size
    cache = read_cache()
    size_correct = len(cache) == 1
    print(f"[{'OK' if size_correct else 'FAIL'}] Cache size: {len(cache)} (expected 1)")
    print()

    return success and removed and size_correct


def test_clear_cache():
    """Test clearing cache."""

    print("=" * 60)
    print("Test 7: Clear Cache")
    print("=" * 60)
    print()

    # Clear cache
    print("Clearing cache...")
    success = clear_cache()
    print(f"[{'OK' if success else 'FAIL'}] Clear success: {success}")
    print()

    # Check if empty
    cache = read_cache()
    is_empty = len(cache) == 0
    print(f"[{'OK' if is_empty else 'FAIL'}] Cache is empty: {is_empty}")
    print()

    return success and is_empty


def main():
    """Run all tests."""

    print("\n" + "=" * 60)
    print("CACHE SERVICE TEST SUITE")
    print("=" * 60)
    print()

    results = []

    # Test 1: Write and read
    results.append(test_write_and_read())

    # Test 2: Add video
    results.append(test_add_video())

    # Test 3: Get video
    results.append(test_get_video())

    # Test 4: Video exists
    results.append(test_video_exists())

    # Test 5: Update video
    results.append(test_update_video())

    # Test 6: Remove video
    results.append(test_remove_video())

    # Test 7: Clear cache
    results.append(test_clear_cache())

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if all(results):
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
    else:
        print(f"[FAILURE] {passed}/{total} tests passed")
    print("=" * 60)
    print()

    return all(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)