"""
Main FastAPI application for English Dictation App.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.routes import video_routes, page_routes


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(video_routes.router, prefix="/api", tags=["video"])
app.include_router(page_routes.router, tags=["pages"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)