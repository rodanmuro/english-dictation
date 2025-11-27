"""
Deepgram transcription service.
Generates SRT subtitle files using Deepgram's AI transcription API.
"""
import os
import asyncio
from typing import Optional
from deepgram import DeepgramClient
from deepgram_captions import DeepgramConverter, srt

from app.config import settings


class ResponseWrapper:
    """
    Wrapper class for Deepgram SDK v5 response compatibility.

    The deepgram-captions library expects a response object with a to_json() method,
    but Deepgram SDK v5 uses Pydantic v2 which has model_dump_json() instead.
    This wrapper bridges that compatibility gap.
    """
    def __init__(self, response):
        self._response = response

    def to_json(self):
        """Convert Pydantic v2 response to JSON string."""
        return self._response.model_dump_json()


async def generate_srt(video_id: str, audio_path: str) -> str:
    """
    Generate SRT subtitle file using Deepgram AI transcription.

    This function transcribes the audio file using Deepgram's nova-3 Whisper model
    and converts the transcription to SRT (SubRip Subtitle) format. If the SRT file
    already exists, it skips transcription and returns the existing file path.

    Args:
        video_id: YouTube video ID (used for SRT filename)
        audio_path: Path to the audio file (MP3)

    Returns:
        str: Path to the generated SRT file

    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If Deepgram API call fails

    Example:
        >>> srt_path = await generate_srt("7obx1BmOp3M", "app/static/audios/7obx1BmOp3M.mp3")
        >>> print(srt_path)
        "app/static/audios/7obx1BmOp3M.srt"
    """
    # Define SRT output path
    srt_path = os.path.join(settings.audio_dir, f"{video_id}.srt")

    # Check if SRT already exists
    if os.path.exists(srt_path):
        print(f"[OK] SRT already exists: {srt_path}")
        return srt_path

    # Verify audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[TRANSCRIBE] Starting transcription for: {audio_path}")

    # Read audio file
    with open(audio_path, "rb") as audio_file:
        audio_data = audio_file.read()

    print(f"[TRANSCRIBE] Audio file size: {len(audio_data) / (1024*1024):.2f} MB")

    # Transcribe in thread pool to avoid blocking
    def _transcribe():
        # Initialize Deepgram client
        client = DeepgramClient(api_key=settings.deepgram_api_key)

        # Call Deepgram API
        response = client.listen.v1.media.transcribe_file(
            request=audio_data,
            model="nova-3",
            utterances=True  # Generate natural speech segments
        )

        # Wrap response for compatibility
        wrapped_response = ResponseWrapper(response)

        # Convert to DeepgramConverter
        transcription = DeepgramConverter(wrapped_response)

        # Generate SRT captions
        srt_content = srt(transcription)

        return srt_content

    # Run blocking operation in thread pool
    loop = asyncio.get_event_loop()
    srt_content = await loop.run_in_executor(None, _transcribe)

    # Save SRT file
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"[OK] SRT file generated: {srt_path}")
    print(f"[OK] SRT file size: {len(srt_content) / 1024:.2f} KB")

    return srt_path


def get_srt_path(video_id: str) -> str:
    """
    Get the file path for a video's SRT subtitle file.

    Args:
        video_id: YouTube video ID

    Returns:
        str: Path to the SRT file
    """
    return os.path.join(settings.audio_dir, f"{video_id}.srt")


def srt_exists(video_id: str) -> bool:
    """
    Check if SRT file already exists for a video.

    Args:
        video_id: YouTube video ID

    Returns:
        bool: True if SRT file exists, False otherwise
    """
    return os.path.exists(get_srt_path(video_id))