"""
Page routes for serving HTML templates.
Will be fully implemented in Phase 4.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page - placeholder for Phase 4.
    """
    return """
    <html>
        <head><title>English Dictation App</title></head>
        <body>
            <h1>English Dictation App</h1>
            <p>API is running. Pages will be implemented in Phase 4.</p>
            <p>Try <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """