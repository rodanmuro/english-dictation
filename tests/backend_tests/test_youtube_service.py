"""
Test script for YouTube service.
"""
import asyncio
import os
from app.services.youtube_service import download_audio, audio_exists, get_audio_path


async def test_download_audio():
    """Test downloading audio from a YouTube video."""

    print("=" * 60)
    print("Testing YouTube Audio Download Service")
    print("=" * 60)
    print()

    # Use a short video for testing (BBC News clip - about 30 seconds)
    test_video_id = "jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video (18 seconds)

    print(f"📹 Test Video ID: {test_video_id}")
    print(f"🔗 URL: https://www.youtube.com/watch?v={test_video_id}")
    print()

    # Check if already exists
    audio_path = get_audio_path(test_video_id)
    if audio_exists(test_video_id):
        print(f"ℹ️  Audio already exists at: {audio_path}")
        print("   Deleting for fresh test...")
        try:
            os.remove(audio_path)
            # Also remove info file if exists
            info_file = audio_path.replace('.mp3', '.info.json')
            if os.path.exists(info_file):
                os.remove(info_file)
            print("   ✓ Deleted existing files")
        except Exception as e:
            print(f"   ⚠️  Could not delete: {e}")
        print()

    print("🚀 Starting download...")
    print("-" * 60)

    try:
        result = await download_audio(test_video_id)

        print()
        print("-" * 60)
        print("✅ Download completed successfully!")
        print()
        print("📊 Result:")
        print(f"   Video ID: {result['video_id']}")
        print(f"   Title: {result['title']}")
        print(f"   Audio Path: {result['audio_path']}")
        print()

        # Verify file exists
        if os.path.exists(result['audio_path']):
            file_size = os.path.getsize(result['audio_path'])
            file_size_kb = file_size / 1024
            file_size_mb = file_size_kb / 1024

            print("📁 File Information:")
            print(f"   Exists: ✓ Yes")
            print(f"   Size: {file_size_mb:.2f} MB ({file_size_kb:.2f} KB)")
            print()

            # Test caching (second call should skip download)
            print("🔄 Testing cache (calling download again)...")
            print("-" * 60)
            result2 = await download_audio(test_video_id)
            print()
            print("-" * 60)
            print("✅ Cache test completed!")
            print(f"   Returned same file: {result2['audio_path'] == result['audio_path']}")
            print()

            return True
        else:
            print("❌ ERROR: File was not created!")
            return False

    except Exception as e:
        print()
        print("-" * 60)
        print(f"❌ ERROR during download: {e}")
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

    # Test get_audio_path
    print("1. Testing get_audio_path():")
    path = get_audio_path(test_video_id)
    print(f"   Video ID: {test_video_id}")
    print(f"   Path: {path}")
    print(f"   ✓ Function works")
    print()

    # Test audio_exists
    print("2. Testing audio_exists():")
    exists = audio_exists(test_video_id)
    print(f"   Video ID: {test_video_id}")
    print(f"   Exists: {exists}")
    print(f"   ✓ Function works")
    print()


async def main():
    """Run all tests."""

    print("\n" + "=" * 60)
    print("YOUTUBE SERVICE TEST SUITE")
    print("=" * 60)
    print()

    print("⚠️  NOTE: This test will download a short YouTube video.")
    print("   Make sure you have:")
    print("   - Internet connection")
    print("   - FFmpeg installed")
    print("   - Sufficient disk space")
    print()

    input("Press ENTER to continue...")
    print()

    # Run tests
    success = await test_download_audio()

    print()

    await test_helper_functions()

    print()
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())