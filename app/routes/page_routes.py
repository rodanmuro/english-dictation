"""
Page routes for serving HTML templates.
As per MVP Plan Section 3.2.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.cache_service import get_video_from_cache, video_in_cache
from app.services.deepgram_service import srt_exists, get_srt_path
from app.services.srt_parser import parse_srt_to_json


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Route 1: GET / → home.html

    As per MVP plan:
    - Show YouTube URL input form

    Will be fully implemented in Phase 4.
    """
    # For now, return a placeholder
    # In Phase 4, this will render home.html template
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/processing/{video_id}", response_class=HTMLResponse)
async def processing(request: Request, video_id: str):
    """
    Route 2: GET /processing/{video_id} → processing.html

    As per MVP plan:
    - Show "Processing..." message
    - Frontend will poll /api/video/{video_id}/status

    Will be fully implemented in Phase 4.
    """
    # For now, return a placeholder
    # In Phase 4, this will render processing.html template
    return templates.TemplateResponse(
        "processing.html",
        {"request": request, "video_id": video_id}
    )


@router.get("/dictation/{video_id}", response_class=HTMLResponse)
async def dictation(request: Request, video_id: str):
    """
    Route 3: GET /dictation/{video_id} → dictation.html

    As per MVP plan:
    - Get segments from cache
    - Inject segments into template via Jinja2
    - Render dictation practice interface

    Will be fully implemented in Phase 4.
    """
    # Check if video exists in cache
    if not video_in_cache(video_id):
        raise HTTPException(
            status_code=404,
            detail=f"Video {video_id} not found. Please process it first."
        )

    # Get video metadata from cache
    cached_video = get_video_from_cache(video_id)

    # Verify SRT file exists
    if not srt_exists(video_id):
        raise HTTPException(
            status_code=404,
            detail=f"SRT file for video {video_id} not found."
        )

    # Parse segments from SRT
    srt_path = get_srt_path(video_id)
    segments = parse_srt_to_json(srt_path)

    # Render dictation template with segments injected
    # In Phase 4, this will render dictation.html template
    return templates.TemplateResponse(
        "dictation.html",
        {
            "request": request,
            "video_id": video_id,
            "title": cached_video.get("title", "Unknown"),
            "segments": segments
        }
    )