"""
Test script for video_utils.py
"""
from app.utils.video_utils import extract_video_id, validate_youtube_url


def test_extract_video_id():
    """Test video ID extraction from various YouTube URL formats."""

    print("=" * 60)
    print("Testing extract_video_id() function")
    print("=" * 60)

    # Test cases: (url, expected_video_id)
    test_cases = [
        # Standard youtube.com/watch format
        ("https://www.youtube.com/watch?v=7obx1BmOp3M", "7obx1BmOp3M"),
        ("https://youtube.com/watch?v=7obx1BmOp3M", "7obx1BmOp3M"),
        ("http://www.youtube.com/watch?v=7obx1BmOp3M", "7obx1BmOp3M"),

        # With additional parameters
        ("https://www.youtube.com/watch?v=7obx1BmOp3M&feature=share", "7obx1BmOp3M"),
        ("https://www.youtube.com/watch?v=7obx1BmOp3M&t=123", "7obx1BmOp3M"),

        # youtu.be short format
        ("https://youtu.be/7obx1BmOp3M", "7obx1BmOp3M"),
        ("https://youtu.be/7obx1BmOp3M?t=123", "7obx1BmOp3M"),

        # Embed format
        ("https://www.youtube.com/embed/7obx1BmOp3M", "7obx1BmOp3M"),

        # /v/ format
        ("https://www.youtube.com/v/7obx1BmOp3M", "7obx1BmOp3M"),
    ]

    passed = 0
    failed = 0

    for url, expected_id in test_cases:
        try:
            result = extract_video_id(url)
            if result == expected_id:
                print(f"✅ PASS: {url}")
                print(f"   → Extracted: {result}")
                passed += 1
            else:
                print(f"❌ FAIL: {url}")
                print(f"   → Expected: {expected_id}, Got: {result}")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: {url}")
            print(f"   → Exception: {e}")
            failed += 1
        print()

    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()


def test_invalid_urls():
    """Test that invalid URLs raise ValueError."""

    print("=" * 60)
    print("Testing invalid URLs (should raise ValueError)")
    print("=" * 60)

    invalid_urls = [
        "https://www.google.com",
        "https://vimeo.com/123456",
        "not a url at all",
        "https://youtube.com",  # No video ID
        "",  # Empty string
    ]

    passed = 0
    failed = 0

    for url in invalid_urls:
        try:
            result = extract_video_id(url)
            print(f"❌ FAIL: {url}")
            print(f"   → Should have raised ValueError, but got: {result}")
            failed += 1
        except ValueError as e:
            print(f"✅ PASS: {url}")
            print(f"   → Correctly raised ValueError: {e}")
            passed += 1
        except Exception as e:
            print(f"❌ ERROR: {url}")
            print(f"   → Unexpected exception: {e}")
            failed += 1
        print()

    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()


def test_validate_youtube_url():
    """Test URL validation function."""

    print("=" * 60)
    print("Testing validate_youtube_url() function")
    print("=" * 60)

    # Test cases: (url, expected_result)
    test_cases = [
        ("https://www.youtube.com/watch?v=7obx1BmOp3M", True),
        ("https://youtu.be/7obx1BmOp3M", True),
        ("https://www.google.com", False),
        ("not a url", False),
        ("", False),
    ]

    passed = 0
    failed = 0

    for url, expected in test_cases:
        result = validate_youtube_url(url)
        if result == expected:
            print(f"✅ PASS: {url}")
            print(f"   → Valid: {result}")
            passed += 1
        else:
            print(f"❌ FAIL: {url}")
            print(f"   → Expected: {expected}, Got: {result}")
            failed += 1
        print()

    print("-" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("VIDEO UTILS TEST SUITE")
    print("=" * 60)
    print("\n")

    # Run all tests
    test_extract_video_id()
    test_invalid_urls()
    test_validate_youtube_url()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)