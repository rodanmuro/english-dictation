"""
SRT subtitle file parser.
Converts SRT files to JSON array format for the dictation application.
"""
import re
from typing import List, Dict


def parse_srt_to_json(srt_path: str) -> List[Dict]:
    """
    Parse SRT subtitle file to JSON array format.

    Converts SRT format to a list of segment dictionaries suitable for
    the dictation application frontend.

    SRT Format:
        1
        00:00:00,080 --> 00:00:01,360
        alright

        2
        00:00:01,600 --> 00:00:03,760
        so here we are one of the elephants

    JSON Format:
        [
            {"id": 0, "start": 0.08, "end": 1.36, "text": "alright"},
            {"id": 1, "start": 1.6, "end": 3.76, "text": "so here we are one of the elephants"}
        ]

    Args:
        srt_path: Path to the SRT file

    Returns:
        List of segment dictionaries with keys: id, start, end, text

    Raises:
        FileNotFoundError: If SRT file doesn't exist
        ValueError: If SRT format is invalid

    Example:
        >>> segments = parse_srt_to_json("app/static/audios/video.srt")
        >>> print(segments[0])
        {"id": 0, "start": 0.08, "end": 1.36, "text": "alright"}
    """
    # Read SRT file
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newline (segment separator)
    segments_raw = content.strip().split('\n\n')
    segments = []

    for idx, segment_raw in enumerate(segments_raw):
        lines = segment_raw.strip().split('\n')

        # SRT format:
        # Line 0: segment number
        # Line 1: timestamps
        # Line 2+: text (can be multiple lines)

        if len(lines) < 3:
            # Skip malformed segments (must have at least number, timestamp, text)
            continue

        # Parse timestamp line (Line 1)
        timestamp_line = lines[1]
        text = ' '.join(lines[2:])  # Join all text lines

        # Parse timestamps: HH:MM:SS,mmm --> HH:MM:SS,mmm
        match = re.match(
            r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})',
            timestamp_line
        )

        if match:
            start_h, start_m, start_s, start_ms, end_h, end_m, end_s, end_ms = match.groups()

            # Convert to float seconds
            start_time = (
                int(start_h) * 3600 +
                int(start_m) * 60 +
                int(start_s) +
                int(start_ms) / 1000
            )

            end_time = (
                int(end_h) * 3600 +
                int(end_m) * 60 +
                int(end_s) +
                int(end_ms) / 1000
            )

            segments.append({
                "id": idx,
                "start": start_time,
                "end": end_time,
                "text": text
            })
        else:
            # Invalid timestamp format - skip this segment
            print(f"[WARN] Skipping segment {idx}: Invalid timestamp format")
            continue

    return segments


def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert SRT timestamp to seconds.

    Args:
        timestamp: SRT timestamp in format HH:MM:SS,mmm

    Returns:
        float: Time in seconds

    Example:
        >>> timestamp_to_seconds("00:00:05,120")
        5.12
    """
    match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', timestamp)

    if not match:
        raise ValueError(f"Invalid timestamp format: {timestamp}")

    hours, minutes, seconds, milliseconds = match.groups()

    total_seconds = (
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds) +
        int(milliseconds) / 1000
    )

    return total_seconds


def count_segments(srt_path: str) -> int:
    """
    Count the number of segments in an SRT file.

    Args:
        srt_path: Path to the SRT file

    Returns:
        int: Number of segments

    Example:
        >>> count = count_segments("video.srt")
        >>> print(count)
        162
    """
    segments = parse_srt_to_json(srt_path)
    return len(segments)