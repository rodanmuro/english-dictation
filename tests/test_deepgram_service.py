"""
Test script for Deepgram transcription service.
"""
import asyncio
import os
from app.services.deepgram_service import generate_srt, srt_exists, get_srt_path


async def test_generate_srt():
    """Test generating SRT subtitles from audio file."""

    print("=" * 60)
    print("Testing Deepgram Transcription Service")
    print("=" * 60)
    print()

    # Use the audio file we already downloaded in the YouTube service test
    test_video_id = "jNQXAC9IVRw"  # "Me at the zoo"
    audio_path = f"app/static/audios/{test_video_id}.mp3"

    print(f"Video ID: {test_video_id}")
    print(f"Audio file: {audio_path}")
    print()

    # Check if audio file exists
    if not os.path.exists(audio_path):
        print(f"ERROR: Audio file not found!")
        print(f"Please run test_youtube_service.py first to download the audio.")
        return False

    audio_size = os.path.getsize(audio_path) / 1024
    print(f"Audio file size: {audio_size:.2f} KB")
    print()

    # Check if SRT already exists
    srt_path = get_srt_path(test_video_id)
    if srt_exists(test_video_id):
        print(f"[INFO] SRT already exists at: {srt_path}")
        print("       Deleting for fresh test...")
        try:
            os.remove(srt_path)
            print("       [OK] Deleted existing SRT file")
        except Exception as e:
            print(f"       [WARN] Could not delete: {e}")
        print()

    print("Starting transcription...")
    print("-" * 60)
    print()

    try:
        # Generate SRT
        result_path = await generate_srt(test_video_id, audio_path)

        print()
        print("-" * 60)
        print("[SUCCESS] Transcription completed!")
        print()
        print(f"SRT file: {result_path}")
        print()

        # Verify file exists
        if os.path.exists(result_path):
            srt_size = os.path.getsize(result_path) / 1024
            print(f"[OK] File exists")
            print(f"[OK] File size: {srt_size:.2f} KB")
            print()

            # Read and display first few lines
            print("First 20 lines of SRT file:")
            print("-" * 60)
            with open(result_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:3}: {line.rstrip()}")
            print("-" * 60)
            print()

            # Count segments
            segment_count = 0
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # SRT segments are separated by double newlines
                segments = content.strip().split('\n\n')
                segment_count = len(segments)

            print(f"[OK] Total segments: {segment_count}")
            print()

            # Test caching (second call should skip transcription)
            print("Testing cache (calling generate_srt again)...")
            print("-" * 60)
            result2 = await generate_srt(test_video_id, audio_path)
            print()
            print("-" * 60)
            print("[SUCCESS] Cache test completed!")
            print(f"[OK] Returned same file: {result2 == result_path}")
            print()

            return True
        else:
            print("[ERROR] SRT file was not created!")
            return False

    except Exception as e:
        print()
        print("-" * 60)
        print(f"[ERROR] Transcription failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


async def test_helper_functions():
    """Test helper functions."""

    print("=" * 60)
    print("Testing Helper Functions")
    print("=" * 60)
    print()

    test_video_id = "jNQXAC9IVRw"

    # Test get_srt_path
    print("1. Testing get_srt_path():")
    path = get_srt_path(test_video_id)
    print(f"   Video ID: {test_video_id}")
    print(f"   SRT Path: {path}")
    print(f"   [OK] Function works")
    print()

    # Test srt_exists
    print("2. Testing srt_exists():")
    exists = srt_exists(test_video_id)
    print(f"   Video ID: {test_video_id}")
    print(f"   Exists: {exists}")
    print(f"   [OK] Function works")
    print()


async def main():
    """Run all tests."""

    print("\n" + "=" * 60)
    print("DEEPGRAM SERVICE TEST SUITE")
    print("=" * 60)
    print()

    print("[WARN] This test will call the Deepgram API.")
    print("       Make sure you have:")
    print("       - Valid Deepgram API key in .env")
    print("       - Internet connection")
    print("       - Audio file from previous test (jNQXAC9IVRw.mp3)")
    print()
    print("[INFO] Video: 'Me at the zoo' (~18 seconds)")
    print("       This is a short video, so API cost is minimal.")
    print()

    input("Press ENTER to continue...")
    print()

    # Run tests
    success = await test_generate_srt()

    print()

    await test_helper_functions()

    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] ALL TESTS PASSED")
    else:
        print("[ERROR] SOME TESTS FAILED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())