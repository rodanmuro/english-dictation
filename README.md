# English Dictation App

A web-based learning tool designed to help users improve their English listening comprehension and typing skills through interactive dictation practice using YouTube videos.

## Features

- 🎥 Turn any YouTube video into an interactive dictation exercise
- 🤖 AI-powered transcription using Deepgram's Whisper model
- ✍️ Real-time character-by-character typing validation
- 📊 Track errors and progress through each video
- 🔊 Replay segments and navigate between them
- 💾 Smart caching - processed videos are saved for instant reuse

## How It Works

1. **Submit a YouTube URL** - Paste any YouTube video link
2. **Automatic Processing** - The app downloads audio and generates accurate subtitles
3. **Interactive Practice** - Listen to segments and type what you hear
4. **Instant Feedback** - Real-time validation and error tracking

## Technology Stack

- **Backend:** FastAPI, Python 3.7+
- **Frontend:** Jinja2 Templates, Vanilla JavaScript
- **Transcription:** Deepgram API (Whisper nova-3 model)
- **Video:** YouTube IFrame API
- **Storage:** Filesystem (SRT files) + JSON cache

## Installation

### Prerequisites

- Python 3.7 or higher
- FFmpeg (required for audio extraction)
- Deepgram API key ([Get one here](https://console.deepgram.com/))

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd english-dictation
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your Deepgram API key:
```
DEEPGRAM_API_KEY=your_actual_api_key_here
```

## Running the Application

1. **Activate virtual environment:**
```bash
source .venv/bin/activate
```

2. **Start the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Open your browser:**
```
http://localhost:8000
```

## Usage

1. Visit the home page
2. Paste a YouTube URL (e.g., `https://www.youtube.com/watch?v=7obx1BmOp3M`)
3. Click "Start Practice"
4. Wait while the app processes the video (downloads audio + generates subtitles)
5. Start typing what you hear - the app validates in real-time!

## Project Structure

```
english-dictation/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── services/              # Business logic
│   │   ├── youtube_service.py    # YouTube audio download
│   │   ├── deepgram_service.py   # AI transcription
│   │   ├── srt_parser.py         # SRT file parsing
│   │   └── cache_service.py      # Caching system
│   ├── routes/                # API endpoints
│   │   ├── video_routes.py       # Video processing API
│   │   └── page_routes.py        # HTML page routes
│   ├── templates/             # Jinja2 HTML templates
│   ├── static/                # CSS, JavaScript, audio files
│   └── utils/                 # Utility functions
├── planning/                  # Project documentation
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## API Endpoints

- `POST /api/process-video` - Submit YouTube URL for processing
- `GET /api/video/{video_id}/status` - Check processing status
- `GET /` - Home page
- `GET /processing/{video_id}` - Processing status page
- `GET /dictation/{video_id}` - Dictation practice page

## Development

See [planning/MVP_IMPLEMENTATION_PLAN.md](planning/MVP_IMPLEMENTATION_PLAN.md) for detailed implementation plan and architecture decisions.

## License

MIT License

## Credits

- **yt-dlp** - YouTube download library
- **Deepgram** - AI transcription service
- **FastAPI** - Web framework
- **YouTube IFrame API** - Video embedding