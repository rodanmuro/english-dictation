# MVP Implementation Plan - English Dictation App

## Architecture Decisions

- ✅ **Storage:** SRT files saved to filesystem (`app/static/audios/*.srt`)
- ✅ **Cache:** Simple JSON file (`cache.json`) mapping `video_id → {status, segments, title}`
- ✅ **Progress Updates:** Simple polling (frontend checks status every 2 seconds)
- ✅ **Data Structure:** Array of objects `[{id, start, end, text}, ...]`
- ✅ **Segment Delivery:** Send all segments at once when processing completes

---

## Project Structure

```
english-dictation/
├── app/
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Settings (API keys, paths)
│   ├── services/                    # Business logic
│   │   ├── youtube_service.py       # Download audio (yt-dlp)
│   │   ├── deepgram_service.py      # Generate SRT (Deepgram API)
│   │   ├── srt_parser.py            # Parse SRT → JSON array
│   │   └── cache_service.py         # Read/write cache.json
│   ├── routes/
│   │   ├── video_routes.py          # API endpoints
│   │   └── page_routes.py           # HTML pages
│   ├── templates/                   # Jinja2 templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── processing.html
│   │   └── dictation.html
│   ├── static/
│   │   ├── css/styles.css
│   │   ├── js/
│   │   │   ├── processing.js        # Polling logic
│   │   │   └── dictation.js         # Validation logic
│   │   └── audios/                  # *.mp3, *.srt, cache.json
│   └── utils/
│       └── video_utils.py           # Extract video_id from URL
├── requirements.txt
├── .env
└── README.md
```

---

## Phase 1: Project Setup

1. Create directory structure
2. Create `requirements.txt` with dependencies:
   - fastapi, uvicorn, jinja2, python-multipart
   - yt-dlp, deepgram-sdk, deepgram-captions
   - python-dotenv, aiofiles
3. Create `.env` file with `DEEPGRAM_API_KEY`
4. Create `.gitignore` (ignore `.env`, `*.mp3`, `cache.json`)

---

## Phase 2: Backend Services

### 2.1 Config (`config.py`)
- Load environment variables (Deepgram API key, audio directory path)

### 2.2 Video Utils (`utils/video_utils.py`)
- Function: `extract_video_id(youtube_url)` → returns video ID
- Handle both formats: `youtube.com/watch?v=...` and `youtu.be/...`

### 2.3 YouTube Service (`services/youtube_service.py`)
- Function: `download_audio(video_id)` → downloads MP3, returns `{video_id, title, audio_path}`
- Use yt-dlp library
- Check if already downloaded (skip if exists)

### 2.4 Deepgram Service (`services/deepgram_service.py`)
- Function: `generate_srt(video_id, audio_path)` → generates SRT file, returns `srt_path`
- Use Deepgram SDK v5 with nova-3 model
- Use ResponseWrapper pattern (from tests/README.md)
- Check if already generated (skip if exists)

### 2.5 SRT Parser (`services/srt_parser.py`)
- Function: `parse_srt_to_json(srt_path)` → returns array of segments
- Parse SRT format (segment number, timestamps, text)
- Convert timestamps from `HH:MM:SS,mmm` to float seconds
- Return: `[{id: 0, start: 0.0, end: 1.04, text: "china"}, ...]`

### 2.6 Cache Service (`services/cache_service.py`)
- Function: `get_video_status(video_id)` → returns cached data or None
- Function: `save_video_status(video_id, status, segments, title)` → saves to cache.json
- Cache structure: `{video_id: {status, segments, title}}`

---

## Phase 3: API Routes

### 3.1 Video Routes (`routes/video_routes.py`)

#### Endpoint 1: `POST /api/process-video`
- Input: `{youtube_url: "..."}`
- Extract video_id from URL
- Check cache: if completed, return immediately
- If not cached: start background task to process
- Return: `{video_id, status: "processing"}`

#### Background Task:
1. Set status: "downloading"
2. Download audio (youtube_service)
3. Set status: "transcribing"
4. Generate SRT (deepgram_service)
5. Parse SRT to JSON (srt_parser)
6. Set status: "completed" with segments
7. On error: set status: "error"

#### Endpoint 2: `GET /api/video/{video_id}/status`
- Return: `{status, segments, title}` from cache
- Used by frontend polling

### 3.2 Page Routes (`routes/page_routes.py`)

#### Route 1: `GET /` → home.html
- Show YouTube URL input form

#### Route 2: `GET /processing/{video_id}` → processing.html
- Show "Processing..." message
- Frontend will poll `/api/video/{video_id}/status`

#### Route 3: `GET /dictation/{video_id}` → dictation.html
- Get segments from cache
- Inject segments into template via Jinja2
- Render dictation practice interface

### 3.3 Main App (`main.py`)
- Create FastAPI app
- Mount static files (`/static` → `app/static/`)
- Include routers (video_routes, page_routes)

---

## Phase 4: Frontend Templates (Jinja2)

### 4.1 Base Template (`base.html`)
- Common HTML structure
- Load CSS (`/static/css/styles.css`)
- Blocks: `{% block title %}`, `{% block content %}`, `{% block scripts %}`

### 4.2 Home Page (`home.html`)
- Form with YouTube URL input
- Submit button
- JavaScript: POST to `/api/process-video`, redirect to `/processing/{video_id}`

### 4.3 Processing Page (`processing.html`)
- Show status message ("Downloading...", "Transcribing...", "Complete!")
- Loading spinner/animation
- JavaScript: Poll `/api/video/{video_id}/status` every 2 seconds
- When status = "completed", redirect to `/dictation/{video_id}`

### 4.4 Dictation Page (`dictation.html`)
- YouTube video player (IFrame API)
- Input field for typing
- Progress bar, stats (errors, segment number)
- Buttons: Replay, Previous
- Jinja2 injects: `{{ video_id }}` and `{{ segments | tojson }}`

---

## Phase 5: Frontend JavaScript

### 5.1 Processing Logic (`static/js/processing.js`)
- Poll `/api/video/{video_id}/status` every 2 seconds
- Update UI based on status (downloading → transcribing → completed)
- Redirect to dictation page when complete

### 5.2 Dictation Logic (`static/js/dictation.js`)
- **Reuse logic from `tests/dictation.html` (lines 432-610)**
- YouTube IFrame API integration
- Character-by-character validation:
  - Compare typed text with expected text
  - If correct: update progress bar
  - If incorrect: remove last character, increment error count
  - If segment complete: move to next segment
- Replay button: replay current segment
- Previous button: go back to previous segment

---

## Phase 6: Styling (`static/css/styles.css`)
- **Reuse styles from `tests/dictation.html` (lines 7-209)**
- Add styles for home page (form, input, button)
- Add styles for processing page (loader animation)
- Consistent theme (purple gradient, modern UI)

---

## Phase 7: Testing

### End-to-End Flow:
1. Start server: `uvicorn app.main:app --reload`
2. Visit `http://localhost:8000`
3. Enter YouTube URL (e.g., `https://www.youtube.com/watch?v=7obx1BmOp3M`)
4. Click "Start Practice"
5. Wait on processing page (polling shows progress)
6. Auto-redirect to dictation page
7. Practice dictation (type segments, validate in real-time)
8. Test: Replay button, Previous button, error counting

### Test Cases:
- ✅ Valid YouTube URL
- ✅ Invalid YouTube URL (show error)
- ✅ Already processed video (instant redirect)
- ✅ Long video (test polling during processing)
- ✅ Network error handling
- ✅ Dictation validation accuracy

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `youtube_service.py` | Download MP3 from YouTube |
| `deepgram_service.py` | Generate SRT using Deepgram API |
| `srt_parser.py` | Convert SRT → JSON array |
| `cache_service.py` | Read/write cache.json |
| `video_routes.py` | API endpoints (process, status) |
| `page_routes.py` | HTML routes (home, processing, dictation) |
| `processing.html` | Polling page |
| `dictation.html` | Practice interface (reuse tests/dictation.html logic) |
| `processing.js` | Polling logic |
| `dictation.js` | Validation logic (from tests/dictation.html) |

---

## Estimated Timeline

- **Phase 1:** 30 min (setup)
- **Phase 2:** 2-3 hours (backend services)
- **Phase 3:** 1-2 hours (API routes)
- **Phase 4:** 1-2 hours (templates)
- **Phase 5:** 1-2 hours (JavaScript - mostly copying from tests/dictation.html)
- **Phase 6:** 30 min (CSS - mostly copying from tests/dictation.html)
- **Phase 7:** 1 hour (testing)

**Total: 6-10 hours**

---

## Technology Stack

### Backend:
- FastAPI (web framework)
- Jinja2 (templating - included with FastAPI)
- yt-dlp (YouTube download)
- deepgram-sdk (transcription)
- python-dotenv (environment variables)

### Frontend:
- Jinja2 Templates (server-rendered HTML)
- Vanilla JavaScript (interactive features)
- CSS3 (styling)
- YouTube IFrame API (video player)

### Storage:
- Filesystem (SRT files)
- JSON file (cache)

---

## Next Steps

1. Create project structure (Phase 1)
2. Implement backend services (Phase 2)
3. Build API routes (Phase 3)
4. Create frontend templates (Phase 4)
5. Add JavaScript logic (Phase 5)
6. Style the application (Phase 6)
7. Test end-to-end (Phase 7)
