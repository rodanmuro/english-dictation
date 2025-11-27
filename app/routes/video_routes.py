"""
API routes for video processing.
"""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.utils.video_utils import extract_video_id
from app.services.youtube_service import download_audio, audio_exists
from app.services.deepgram_service import generate_srt, srt_exists, get_srt_path
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
    """Response model for video status - matches MVP plan."""
    status: str  # "downloading", "transcribing", "completed", "error"
    title: Optional[str] = None
    segments: Optional[List[Dict]] = None


class ProcessVideoResponse(BaseModel):
    """Response model for process video endpoint."""
    video_id: str
    status: str


# Background processing task storage
processing_tasks = {}


async def process_video_task(video_id: str, youtube_url: str):
    """
    Background task to process video.

    Steps (as per MVP plan):
    1. Set status: "downloading"
    2. Download audio (youtube_service)
    3. Set status: "transcribing"
    4. Generate SRT (deepgram_service)
    5. Parse SRT to JSON (srt_parser)
    6. Set status: "completed" with segments
    7. On error: set status: "error"
    """
    try:
        # Step 1: Set status "downloading"
        processing_tasks[video_id] = {
            "status": "downloading",
            "title": None,
            "segments": None
        }

        # Step 2: Download audio
        audio_result = await download_audio(video_id)

        # Step 3: Set status "transcribing"
        processing_tasks[video_id] = {
            "status": "transcribing",
            "title": audio_result['title'],
            "segments": None
        }

        # Step 4: Generate SRT
        srt_path = await generate_srt(video_id, audio_result['audio_path'])

        # Step 5: Parse SRT to JSON
        segments = parse_srt_to_json(srt_path)

        # Save to cache
        video_data = {
            "video_id": video_id,
            "title": audio_result['title'],
            "audio_path": audio_result['audio_path'],
            "srt_path": srt_path,
            "segment_count": len(segments)
        }
        add_video_to_cache(video_data)

        # Step 6: Set status "completed" with segments
        processing_tasks[video_id] = {
            "status": "completed",
            "title": audio_result['title'],
            "segments": segments
        }

    except Exception as e:
        # Step 7: On error
        processing_tasks[video_id] = {
            "status": "error",
            "title": None,
            "segments": None
        }
        print(f"[ERROR] Processing failed for {video_id}: {e}")


@router.post("/process-video")
async def process_video(request: ProcessVideoRequest):
    """
    Process a YouTube video for dictation.

    As per MVP plan:
    - Input: {youtube_url: "..."}
    - Extract video_id from URL
    - Check cache: if completed, return immediately
    - If not cached: start background task to process
    - Return: {video_id, status: "processing"}

    Args:
        request: ProcessVideoRequest with youtube_url

    Returns:
        {video_id, status}

    Raises:
        HTTPException: If URL is invalid
    """
    try:
        # Extract video ID from URL
        video_id = extract_video_id(request.youtube_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check cache: if completed, return immediately
    if video_in_cache(video_id):
        # Verify files still exist
        if audio_exists(video_id) and srt_exists(video_id):
            return {
                "video_id": video_id,
                "status": "completed"
            }

    # Check if already processing
    if video_id in processing_tasks:
        current_status = processing_tasks[video_id]["status"]
        return {
            "video_id": video_id,
            "status": current_status
        }

    # Start background processing
    processing_tasks[video_id] = {
        "status": "processing",
        "title": None,
        "segments": None
    }

    # Create background task
    asyncio.create_task(process_video_task(video_id, request.youtube_url))

    return {
        "video_id": video_id,
        "status": "processing"
    }


@router.get("/video/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    """
    Get processing status of a video.

    As per MVP plan (Endpoint 2):
    - Return: {status, segments, title} from cache
    - Used by frontend polling

    Status values:
    - "downloading": Downloading audio from YouTube
    - "transcribing": Transcribing with Deepgram
    - "completed": Ready with segments
    - "error": Processing failed

    Args:
        video_id: YouTube video ID

    Returns:
        VideoStatusResponse: {status, title, segments}

    Raises:
        HTTPException: If video not found
    """
    # Check processing tasks first
    if video_id in processing_tasks:
        task_status = processing_tasks[video_id]
        return VideoStatusResponse(
            status=task_status["status"],
            title=task_status.get("title"),
            segments=task_status.get("segments")
        )

    # Check cache
    if video_in_cache(video_id):
        cached_video = get_video_from_cache(video_id)

        # Verify files exist
        if audio_exists(video_id) and srt_exists(video_id):
            # Parse segments from SRT
            srt_path = get_srt_path(video_id)
            segments = parse_srt_to_json(srt_path)

            return VideoStatusResponse(
                status="completed",
                title=cached_video.get("title"),
                segments=segments
            )
        else:
            return VideoStatusResponse(
                status="error",
                title=None,
                segments=None
            )

    # Video not found
    raise HTTPException(
        status_code=404,
        detail=f"Video {video_id} not found. Please process it first using /api/process-video"
    )