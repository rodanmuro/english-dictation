"""
Full integration test for complete workflow:
YouTube Download -> Deepgram Transcription -> SRT Parsing -> Cache Storage

This test verifies all backend services working together.
"""
import asyncio
import os
import json
from app.services.youtube_service import download_audio, audio_exists
from app.services.deepgram_service import generate_srt, srt_exists
from app.services.srt_parser import parse_srt_to_json, count_segments
from app.services.cache_service import (
    add_video_to_cache,
    get_video_from_cache,
    video_in_cache,
    clear_cache
)


async def test_complete_workflow():
    """
    Test the complete integration workflow:
    1. Download audio from YouTube
    2. Generate SRT using Deepgram
    3. Parse SRT to JSON array
    4. Store metadata in cache
    5. Verify all data is consistent
    """

    print("=" * 70)
    print("FULL INTEGRATION TEST: Complete Backend Workflow")
    print("=" * 70)
    print()

    # Use short video for testing
    test_video_id = "jNQXAC9IVRw"  # "Me at the zoo" - 18 seconds
    test_url = f"https://www.youtube.com/watch?v={test_video_id}"

    print(f"Test Video ID: {test_video_id}")
    print(f"URL: {test_url}")
    print()

    # ================================================================
    # CLEANUP: Remove existing files and cache for fresh test
    # ================================================================
    print("=" * 70)
    print("CLEANUP: Preparing Fresh Test Environment")
    print("=" * 70)
    print()

    audio_path = f"app/static/audios/{test_video_id}.mp3"
    srt_path = f"app/static/audios/{test_video_id}.srt"
    info_file = f"app/static/audios/{test_video_id}.info.json"

    files_to_remove = [audio_path, srt_path, info_file]

    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[OK] Deleted: {file_path}")
            except Exception as e:
                print(f"[WARN] Could not delete {file_path}: {e}")

    # Clear cache
    clear_cache()
    print(f"[OK] Cleared cache")
    print()

    # ================================================================
    # STEP 1: Download Audio from YouTube
    # ================================================================
    print("=" * 70)
    print("STEP 1: Download Audio from YouTube")
    print("=" * 70)
    print()

    try:
        audio_result = await download_audio(test_video_id)

        print("[SUCCESS] Audio download completed")
        print(f"  Video ID: {audio_result['video_id']}")
        print(f"  Title: {audio_result['title']}")
        print(f"  Path: {audio_result['audio_path']}")

        if os.path.exists(audio_result['audio_path']):
            audio_size = os.path.getsize(audio_result['audio_path']) / 1024
            print(f"  Size: {audio_size:.2f} KB")
            print()
        else:
            print("[ERROR] Audio file not found!")
            return False

        video_title = audio_result['title']

    except Exception as e:
        print(f"[ERROR] Audio download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ================================================================
    # STEP 2: Generate SRT with Deepgram
    # ================================================================
    print("=" * 70)
    print("STEP 2: Generate SRT with Deepgram")
    print("=" * 70)
    print()

    try:
        srt_result = await generate_srt(test_video_id, audio_result['audio_path'])

        print("[SUCCESS] SRT generation completed")
        print(f"  SRT Path: {srt_result}")

        if os.path.exists(srt_result):
            srt_size = os.path.getsize(srt_result) / 1024
            print(f"  Size: {srt_size:.2f} KB")
            print()
        else:
            print("[ERROR] SRT file not found!")
            return False

    except Exception as e:
        print(f"[ERROR] SRT generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ================================================================
    # STEP 3: Parse SRT to JSON Array
    # ================================================================
    print("=" * 70)
    print("STEP 3: Parse SRT to JSON Array")
    print("=" * 70)
    print()

    try:
        # Parse SRT
        segments = parse_srt_to_json(srt_result)

        print(f"[SUCCESS] SRT parsed successfully")
        print(f"  Total segments: {len(segments)}")
        print()

        # Verify count matches
        segment_count_check = count_segments(srt_result)
        count_matches = len(segments) == segment_count_check

        print(f"[CHECK] Segment count verification: {count_matches}")
        print(f"  parse_srt_to_json: {len(segments)}")
        print(f"  count_segments: {segment_count_check}")
        print()

        if not count_matches:
            print("[ERROR] Segment count mismatch!")
            return False

        # Display first 3 segments
        print("First 3 segments:")
        print("-" * 70)
        for segment in segments[:3]:
            print(f"ID: {segment['id']}")
            print(f"  Start: {segment['start']:.3f}s")
            print(f"  End: {segment['end']:.3f}s")
            print(f"  Text: \"{segment['text']}\"")
            print()
        print("-" * 70)
        print()

    except Exception as e:
        print(f"[ERROR] SRT parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ================================================================
    # STEP 4: Store Metadata in Cache
    # ================================================================
    print("=" * 70)
    print("STEP 4: Store Metadata in Cache")
    print("=" * 70)
    print()

    try:
        # Prepare video metadata
        video_data = {
            "video_id": test_video_id,
            "title": video_title,
            "audio_path": audio_result['audio_path'],
            "srt_path": srt_result,
            "segment_count": len(segments)
        }

        # Add to cache
        cache_success = add_video_to_cache(video_data)

        if cache_success:
            print("[SUCCESS] Video metadata added to cache")
            print(f"  Video ID: {video_data['video_id']}")
            print(f"  Title: {video_data['title']}")
            print(f"  Segments: {video_data['segment_count']}")
            print()
        else:
            print("[ERROR] Failed to add video to cache")
            return False

    except Exception as e:
        print(f"[ERROR] Cache storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ================================================================
    # STEP 5: Verify Complete Integration
    # ================================================================
    print("=" * 70)
    print("STEP 5: Verify Complete Integration")
    print("=" * 70)
    print()

    checks = []

    # Check 1: All files exist
    print("[CHECK 1] File Existence")
    audio_ok = audio_exists(test_video_id)
    srt_ok = srt_exists(test_video_id)
    print(f"  Audio file: {'YES' if audio_ok else 'NO'}")
    print(f"  SRT file: {'YES' if srt_ok else 'NO'}")
    checks.append(audio_ok and srt_ok)
    print()

    # Check 2: Cache contains video
    print("[CHECK 2] Cache Storage")
    in_cache = video_in_cache(test_video_id)
    print(f"  Video in cache: {'YES' if in_cache else 'NO'}")
    checks.append(in_cache)
    print()

    # Check 3: Cache data is correct
    print("[CHECK 3] Cache Data Integrity")
    cached_video = get_video_from_cache(test_video_id)

    if cached_video:
        title_matches = cached_video['title'] == video_title
        count_matches = cached_video['segment_count'] == len(segments)
        has_timestamp = 'timestamp' in cached_video

        print(f"  Title matches: {'YES' if title_matches else 'NO'}")
        print(f"  Segment count matches: {'YES' if count_matches else 'NO'}")
        print(f"  Has timestamp: {'YES' if has_timestamp else 'NO'}")

        checks.append(title_matches and count_matches and has_timestamp)
    else:
        print("  ERROR: Video not found in cache")
        checks.append(False)
    print()

    # Check 4: SRT segments are valid
    print("[CHECK 4] SRT Segment Validation")
    all_have_required_fields = all(
        'id' in s and 'start' in s and 'end' in s and 'text' in s
        for s in segments
    )
    all_have_correct_types = all(
        isinstance(s['id'], int) and
        isinstance(s['start'], float) and
        isinstance(s['end'], float) and
        isinstance(s['text'], str)
        for s in segments
    )

    print(f"  All segments have required fields: {'YES' if all_have_required_fields else 'NO'}")
    print(f"  All segments have correct types: {'YES' if all_have_correct_types else 'NO'}")

    checks.append(all_have_required_fields and all_have_correct_types)
    print()

    # Check 5: Workflow consistency
    print("[CHECK 5] Data Consistency Across Services")

    # Segment count from different sources should match
    segments_from_parser = len(segments)
    segments_from_counter = count_segments(srt_result)
    segments_from_cache = cached_video['segment_count'] if cached_video else 0

    consistency_check = (
        segments_from_parser == segments_from_counter == segments_from_cache
    )

    print(f"  SRT Parser: {segments_from_parser} segments")
    print(f"  SRT Counter: {segments_from_counter} segments")
    print(f"  Cache: {segments_from_cache} segments")
    print(f"  All match: {'YES' if consistency_check else 'NO'}")

    checks.append(consistency_check)
    print()

    # ================================================================
    # FINAL RESULT
    # ================================================================
    all_passed = all(checks)

    print("=" * 70)
    if all_passed:
        print("[SUCCESS] ALL INTEGRATION CHECKS PASSED")
        print()
        print("Complete workflow verified:")
        print("  1. YouTube URL -> Audio Download")
        print("  2. Audio File -> Deepgram Transcription -> SRT File")
        print("  3. SRT File -> JSON Array Parsing")
        print("  4. Video Metadata -> Cache Storage")
        print("  5. Data Consistency Across All Services")
        print()
        print("All backend services are working together correctly!")
        print()

        # Display final cache entry
        print("Final Cache Entry:")
        print("-" * 70)
        print(json.dumps(cached_video, indent=2))
        print("-" * 70)
    else:
        print("[FAILURE] SOME INTEGRATION CHECKS FAILED")
        print(f"  Passed: {sum(checks)}/{len(checks)}")

    print("=" * 70)
    print()

    return all_passed


async def main():
    """Run full integration test."""

    print("\n" + "=" * 70)
    print("FULL BACKEND INTEGRATION TEST")
    print("=" * 70)
    print()

    print("[INFO] This test will verify the complete backend workflow:")
    print("  1. Download audio from YouTube")
    print("  2. Transcribe using Deepgram API")
    print("  3. Parse SRT to JSON format")
    print("  4. Store metadata in cache")
    print("  5. Verify data consistency")
    print()
    print("[WARN] This will use Deepgram API credits (minimal for short video)")
    print()

    input("Press ENTER to continue...")
    print()

    success = await test_complete_workflow()

    print()
    if success:
        print("=" * 70)
        print("FULL INTEGRATION TEST PASSED")
        print("=" * 70)
    else:
        print("=" * 70)
        print("FULL INTEGRATION TEST FAILED")
        print("=" * 70)
    print()

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)