"""
Integration test for YouTube download + Deepgram transcription.
Tests the complete flow from YouTube URL to SRT file generation.
"""
import asyncio
import os
from app.services.youtube_service import download_audio, audio_exists
from app.services.deepgram_service import generate_srt, srt_exists


async def test_full_integration():
    """
    Test the complete integration:
    1. Download audio from YouTube
    2. Generate SRT using Deepgram
    3. Verify both files exist
    """

    print("=" * 60)
    print("INTEGRATION TEST: YouTube + Deepgram")
    print("=" * 60)
    print()

    # Use a different short video for integration test
    # This is another very short video to minimize API costs
    test_video_id = "jNQXAC9IVRw"  # "Me at the zoo" - 18 seconds

    print(f"Test Video ID: {test_video_id}")
    print(f"URL: https://www.youtube.com/watch?v={test_video_id}")
    print()

    # Clean up any existing files for fresh test
    audio_path = f"app/static/audios/{test_video_id}.mp3"
    srt_path = f"app/static/audios/{test_video_id}.srt"

    print("[CLEANUP] Removing existing files for fresh test...")
    for path in [audio_path, srt_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"  [OK] Deleted: {path}")
            except Exception as e:
                print(f"  [WARN] Could not delete {path}: {e}")

    # Also remove info file
    info_file = f"app/static/audios/{test_video_id}.info.json"
    if os.path.exists(info_file):
        try:
            os.remove(info_file)
            print(f"  [OK] Deleted: {info_file}")
        except Exception as e:
            print(f"  [WARN] Could not delete {info_file}: {e}")

    print()

    # ==========================================
    # STEP 1: Download Audio from YouTube
    # ==========================================
    print("=" * 60)
    print("STEP 1: Download Audio from YouTube")
    print("=" * 60)
    print()

    try:
        audio_result = await download_audio(test_video_id)

        print()
        print("[SUCCESS] Audio download completed!")
        print(f"  Video ID: {audio_result['video_id']}")
        print(f"  Title: {audio_result['title']}")
        print(f"  Path: {audio_result['audio_path']}")

        # Verify file
        if os.path.exists(audio_result['audio_path']):
            file_size = os.path.getsize(audio_result['audio_path']) / 1024
            print(f"  Size: {file_size:.2f} KB")
            print()
        else:
            print("[ERROR] Audio file not found!")
            return False

    except Exception as e:
        print(f"[ERROR] Audio download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ==========================================
    # STEP 2: Generate SRT with Deepgram
    # ==========================================
    print("=" * 60)
    print("STEP 2: Generate SRT with Deepgram")
    print("=" * 60)
    print()

    try:
        srt_result = await generate_srt(test_video_id, audio_result['audio_path'])

        print()
        print("[SUCCESS] SRT generation completed!")
        print(f"  SRT Path: {srt_result}")

        # Verify file
        if os.path.exists(srt_result):
            file_size = os.path.getsize(srt_result) / 1024
            print(f"  Size: {file_size:.2f} KB")

            # Count segments
            with open(srt_result, 'r', encoding='utf-8') as f:
                content = f.read()
                segments = content.strip().split('\n\n')
                print(f"  Segments: {len(segments)}")

            # Show first few lines
            print()
            print("  First 15 lines:")
            print("  " + "-" * 56)
            with open(srt_result, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:15], 1):
                    print(f"  {i:2}: {line.rstrip()}")
            print("  " + "-" * 56)
            print()
        else:
            print("[ERROR] SRT file not found!")
            return False

    except Exception as e:
        print(f"[ERROR] SRT generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # ==========================================
    # STEP 3: Verify Integration
    # ==========================================
    print("=" * 60)
    print("STEP 3: Verify Integration")
    print("=" * 60)
    print()

    checks = []

    # Check 1: Both files exist
    audio_ok = audio_exists(test_video_id)
    srt_ok = srt_exists(test_video_id)

    print(f"[CHECK] Audio file exists: {'✓ YES' if audio_ok else '✗ NO'}")
    print(f"[CHECK] SRT file exists: {'✓ YES' if srt_ok else '✗ NO'}")
    checks.append(audio_ok and srt_ok)
    print()

    # Check 2: Files are not empty
    audio_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
    srt_size = os.path.getsize(srt_path) if os.path.exists(srt_path) else 0

    print(f"[CHECK] Audio file not empty: {'✓ YES' if audio_size > 0 else '✗ NO'} ({audio_size} bytes)")
    print(f"[CHECK] SRT file not empty: {'✓ YES' if srt_size > 0 else '✗ NO'} ({srt_size} bytes)")
    checks.append(audio_size > 0 and srt_size > 0)
    print()

    # Check 3: SRT has valid structure
    if os.path.exists(srt_path):
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_timestamps = '-->' in content
            has_text = len(content.strip()) > 50

            print(f"[CHECK] SRT has timestamps: {'✓ YES' if has_timestamps else '✗ NO'}")
            print(f"[CHECK] SRT has text content: {'✓ YES' if has_text else '✗ NO'}")
            checks.append(has_timestamps and has_text)
    else:
        checks.append(False)

    print()

    # Overall result
    all_passed = all(checks)

    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ✓ ALL INTEGRATION CHECKS PASSED")
        print()
        print("Complete workflow verified:")
        print("  YouTube URL → Audio Download → Deepgram Transcription → SRT File")
        print()
        print("The services are working together correctly!")
    else:
        print("[FAILURE] ✗ SOME INTEGRATION CHECKS FAILED")
        print(f"  Passed: {sum(checks)}/{len(checks)}")
    print("=" * 60)
    print()

    return all_passed


async def main():
    """Run integration test."""

    print("\n" + "=" * 60)
    print("YOUTUBE + DEEPGRAM INTEGRATION TEST")
    print("=" * 60)
    print()

    print("[INFO] This test will:")
    print("  1. Download a short video from YouTube (~18 seconds)")
    print("  2. Transcribe it using Deepgram API")
    print("  3. Verify the complete workflow")
    print()
    print("[WARN] This will use Deepgram API credits (minimal for short video)")
    print()

    input("Press ENTER to continue...")
    print()

    success = await test_full_integration()

    print()
    if success:
        print("=" * 60)
        print("✓ INTEGRATION TEST PASSED")
        print("=" * 60)
    else:
        print("=" * 60)
        print("✗ INTEGRATION TEST FAILED")
        print("=" * 60)
    print()

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)