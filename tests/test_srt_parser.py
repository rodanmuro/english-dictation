"""
Test script for SRT parser service.
"""
import json
from app.services.srt_parser import parse_srt_to_json, timestamp_to_seconds, count_segments


def test_parse_srt():
    """Test parsing SRT file to JSON array."""

    print("=" * 60)
    print("Testing SRT Parser Service")
    print("=" * 60)
    print()

    # Use the existing SRT file
    srt_path = "app/static/audios/jNQXAC9IVRw.srt"

    print(f"SRT file: {srt_path}")
    print()

    try:
        # Parse SRT
        segments = parse_srt_to_json(srt_path)

        print(f"[OK] SRT parsed successfully")
        print(f"[OK] Total segments: {len(segments)}")
        print()

        # Display first 5 segments
        print("First 5 segments:")
        print("-" * 60)
        for segment in segments[:5]:
            print(f"ID: {segment['id']}")
            print(f"  Start: {segment['start']:.3f}s")
            print(f"  End: {segment['end']:.3f}s")
            print(f"  Text: \"{segment['text']}\"")
            print()

        # Display as JSON
        print("JSON format (first 3 segments):")
        print("-" * 60)
        print(json.dumps(segments[:3], indent=2))
        print()

        # Verify structure
        print("Verification:")
        print("-" * 60)
        all_have_id = all('id' in s for s in segments)
        all_have_start = all('start' in s for s in segments)
        all_have_end = all('end' in s for s in segments)
        all_have_text = all('text' in s for s in segments)

        print(f"[CHECK] All segments have 'id': {'✓' if all_have_id else '✗'}")
        print(f"[CHECK] All segments have 'start': {'✓' if all_have_start else '✗'}")
        print(f"[CHECK] All segments have 'end': {'✓' if all_have_end else '✗'}")
        print(f"[CHECK] All segments have 'text': {'✓' if all_have_text else '✗'}")
        print()

        # Check data types
        first_segment = segments[0]
        print(f"[CHECK] ID is int: {'✓' if isinstance(first_segment['id'], int) else '✗'}")
        print(f"[CHECK] Start is float: {'✓' if isinstance(first_segment['start'], float) else '✗'}")
        print(f"[CHECK] End is float: {'✓' if isinstance(first_segment['end'], float) else '✗'}")
        print(f"[CHECK] Text is str: {'✓' if isinstance(first_segment['text'], str) else '✗'}")
        print()

        return True

    except Exception as e:
        print(f"[ERROR] Failed to parse SRT: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_timestamp_converter():
    """Test timestamp conversion function."""

    print("=" * 60)
    print("Testing Timestamp Conversion")
    print("=" * 60)
    print()

    test_cases = [
        ("00:00:00,080", 0.08),
        ("00:00:01,360", 1.36),
        ("00:00:05,120", 5.12),
        ("00:01:00,000", 60.0),
        ("01:00:00,000", 3600.0),
    ]

    passed = 0
    failed = 0

    for timestamp, expected in test_cases:
        try:
            result = timestamp_to_seconds(timestamp)
            if abs(result - expected) < 0.001:  # Allow small floating point difference
                print(f"[OK] {timestamp} = {result}s (expected {expected}s)")
                passed += 1
            else:
                print(f"[FAIL] {timestamp} = {result}s (expected {expected}s)")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {timestamp}: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print()

    return failed == 0


def test_count_segments():
    """Test segment counting function."""

    print("=" * 60)
    print("Testing Count Segments")
    print("=" * 60)
    print()

    srt_path = "app/static/audios/jNQXAC9IVRw.srt"

    try:
        count = count_segments(srt_path)
        print(f"[OK] Segment count: {count}")
        print()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to count segments: {e}")
        return False


def main():
    """Run all tests."""

    print("\n" + "=" * 60)
    print("SRT PARSER TEST SUITE")
    print("=" * 60)
    print()

    results = []

    # Test 1: Parse SRT
    results.append(test_parse_srt())

    # Test 2: Timestamp conversion
    results.append(test_timestamp_converter())

    # Test 3: Count segments
    results.append(test_count_segments())

    # Summary
    print("=" * 60)
    if all(results):
        print("[SUCCESS] ✓ ALL TESTS PASSED")
    else:
        print(f"[FAILURE] {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    print()

    return all(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)