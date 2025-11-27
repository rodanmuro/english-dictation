"""
API routes for video processing.
"""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.utils.video_utils import extract_video_id
from app.services.youtube_service import download_audio, audio_exists
from app.services.deepgram_service import generate_srt, srt_exists
from app.services.srt_parser import parse_srt_to_json
from app.services.cache_service import (
    add_video_to_cache,
    get_video_from_cache,
    video_in_cache
)


router = APIRouter()


# Request/Response models
class ProcessVideoRequest(BaseModel):
    """Request model for video processing."""
    youtube_url: str


class VideoStatusResponse(BaseModel):
    """Response model for video status."""
    video_id: str
    status: str  # "processing", "ready", "error"
    title: Optional[str] = None
    segment_count: Optional[int] = None
    message: Optional[str] = None


class ProcessVideoResponse(BaseModel):
    """Response model for process video endpoint."""
    video_id: str
    status: str
    message: str


# Background processing task storage
processing_tasks = {}


async def process_video_task(video_id: str, youtube_url: str):
    """
    Background task to process video.

    Steps:
    1. Download audio from YouTube
    2. Generate SRT using Deepgram
    3. Parse SRT to JSON
    4. Save metadata to cache
    """
    try:
        # Update status
        processing_tasks[video_id] = {
            "status": "processing",
            "message": "Downloading audio from YouTube..."
        }

        # Step 1: Download audio
        audio_result = await download_audio(video_id)

        processing_tasks[video_id]["message"] = "Transcribing audio with Deepgram..."

        # Step 2: Generate SRT
        srt_path = await generate_srt(video_id, audio_result['audio_path'])

        processing_tasks[video_id]["message"] = "Parsing subtitles..."

        # Step 3: Parse SRT to JSON
        segments = parse_srt_to_json(srt_path)

        processing_tasks[video_id]["message"] = "Saving to cache..."

        # Step 4: Save to cache
        video_data = {
            "video_id": video_id,
            "title": audio_result['title'],
            "audio_path": audio_result['audio_path'],
            "srt_path": srt_path,
            "segment_count": len(segments)
        }

        add_video_to_cache(video_data)

        # Mark as ready
        processing_tasks[video_id] = {
            "status": "ready",
            "title": audio_result['title'],
            "segment_count": len(segments),
            "message": "Video processed successfully"
        }

    except Exception as e:
        # Mark as error
        processing_tasks[video_id] = {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }


@router.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(request: ProcessVideoRequest):
    """
    Process a YouTube video for dictation.

    This endpoint:
    1. Validates the YouTube URL
    2. Extracts the video ID
    3. Checks if already processed (in cache)
    4. If not processed, starts background processing
    5. Returns video_id for status polling

    Args:
        request: ProcessVideoRequest with youtube_url

    Returns:
        ProcessVideoResponse with video_id and status

    Raises:
        HTTPException: If URL is invalid
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(request.youtube_url)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if video is already in cache
    if video_in_cache(video_id):
        cached_video = get_video_from_cache(video_id)

        # Verify files still exist
        if audio_exists(video_id) and srt_exists(video_id):
            return ProcessVideoResponse(
                video_id=video_id,
                status="ready",
                message="Video already processed and ready"
            )
        else:
            # Files missing, need to reprocess
            pass

    # Check if already processing
    if video_id in processing_tasks:
        current_status = processing_tasks[video_id]["status"]

        if current_status == "processing":
            return ProcessVideoResponse(
                video_id=video_id,
                status="processing",
                message="Video is already being processed"
            )
        elif current_status == "ready":
            return ProcessVideoResponse(
                video_id=video_id,
                status="ready",
                message="Video processing complete"
            )
        elif current_status == "error":
            # Clear error and allow retry
            del processing_tasks[video_id]

    # Start background processing
    processing_tasks[video_id] = {
        "status": "processing",
        "message": "Starting video processing..."
    }

    # Create background task
    asyncio.create_task(process_video_task(video_id, request.youtube_url))

    return ProcessVideoResponse(
        video_id=video_id,
        status="processing",
        message="Video processing started. Use /api/status/{video_id} to check progress."
    )


@router.get("/status/{video_id}", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    """
    Get processing status of a video.

    This endpoint returns the current status of a video:
    - "processing": Video is being processed
    - "ready": Video is ready for dictation
    - "error": Processing failed

    Args:
        video_id: YouTube video ID

    Returns:
        VideoStatusResponse with current status

    Raises:
        HTTPException: If video not found
    """
    # Check processing tasks first
    if video_id in processing_tasks:
        task_status = processing_tasks[video_id]

        return VideoStatusResponse(
            video_id=video_id,
            status=task_status["status"],
            title=task_status.get("title"),
            segment_count=task_status.get("segment_count"),
            message=task_status.get("message")
        )

    # Check cache
    if video_in_cache(video_id):
        cached_video = get_video_from_cache(video_id)

        # Verify files exist
        if audio_exists(video_id) and srt_exists(video_id):
            return VideoStatusResponse(
                video_id=video_id,
                status="ready",
                title=cached_video.get("title"),
                segment_count=cached_video.get("segment_count"),
                message="Video is ready for dictation"
            )
        else:
            return VideoStatusResponse(
                video_id=video_id,
                status="error",
                message="Video files are missing. Please reprocess."
            )

    # Video not found
    raise HTTPException(
        status_code=404,
        detail=f"Video {video_id} not found. Please process it first using /api/process-video"
    )