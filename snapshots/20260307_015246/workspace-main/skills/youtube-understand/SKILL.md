# Video Understanding

Analyze any video source with combined audio transcription and visual frame analysis.
Supports YouTube URLs, local file uploads, live camera streams, RTSP/HTTP streams, and screen recordings.

## Quick Start

```bash
# Analyze a YouTube video
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "https://youtube.com/watch?v=..."

# Analyze a local video file
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --file /path/to/video.mp4

# Live iPhone camera analysis
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --live node:iphone

# Live RTSP stream analysis  
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --live rtsp://192.168.1.100:554/stream

# Live screen capture
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --live screen

# With high quality settings
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --file video.mp4 --whisper-model large-v3-turbo --frame-interval 15

# List all analyzed jobs
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --list

# List available camera nodes
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --nodes

# Get summary of a specific job
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --summary vid-1234567890

# Export full analysis
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --export live-1234567890
```

## API Server (port 8099)

Start the API server:
```bash
python3 ~/.openclaw/workspace-main/tools/youtube-understand/server.py
```

Or use the systemd service:
```bash
systemctl --user start dgx-youtube-understand
systemctl --user enable dgx-youtube-understand
systemctl --user status dgx-youtube-understand
```

### API Endpoints

#### Video Analysis
- **POST /api/analyze** — Start YouTube video analysis
  - Body: `{url, whisper_model?, frame_interval?, vision_model?, summary_model?, max_frames?}`
  - Returns: `{job_id, status: "queued"}`

- **POST /api/upload** — Upload video file for analysis
  - Form data: `file` (video file) + config parameters
  - Returns: `{job_id, status: "queued", filename}`

#### Live Streams
- **POST /api/live/start** — Start live stream analysis
  - Body: `{source, config?}` where source is `node:<name>`, `rtsp://...`, `http://...`, or `screen`
  - Returns: `{job_id, status: "streaming"}`

- **POST /api/live/stop** — Stop a live stream
  - Body: `{job_id}`
  - Returns: `{job_id, status: "stopped"}`

- **GET /api/live/<job_id>** — Get live stream status and latest segments
- **GET /api/live/<job_id>/snapshot** — Get the most recent frame + analysis

#### Node Discovery
- **GET /api/nodes** — List available OpenClaw nodes with camera capability
- **POST /api/detect** — Auto-detect source type from input string

#### Job Management
- **GET /api/jobs** — List all jobs with status
- **GET /api/jobs/<id>** — Get complete job data
- **GET /api/jobs/<id>/summary** — Get just the summary
- **GET /api/jobs/<id>/transcript** — Get just the transcript
- **GET /api/jobs/<id>/frames** — Get frame analysis data
- **GET /api/jobs/<id>/export** — Download full markdown export
- **DELETE /api/jobs/<id>** — Delete a job and its files
- **GET /api/frame/<job_id>/<filename>** — Serve frame images
- **GET /health** — Health check

## Web Interface

Access the web interface at: **http://localhost:8090/29-youtube-understand/**

Features:
- **Multi-source support**: YouTube, file upload, live camera, streams, screen capture
- **Real-time live view**: Live frame preview with running analysis
- **Progress tracking**: Real-time progress for all analysis types
- **Job history management**: Browse and manage all completed analyses
- **Interactive transcript**: Search and navigate transcript with timestamps
- **Frame analysis gallery**: Visual frame analysis with lightbox viewer
- **Export capabilities**: Download complete markdown analysis reports
- **Node integration**: Automatic discovery and selection of paired iPhone cameras
- **Mobile-responsive design**: Works on all screen sizes

### Source Types
- **YouTube**: Enter any YouTube URL for comprehensive video analysis
- **Upload**: Drag & drop or select local video files (MP4, MKV, AVI, WebM, MOV)
- **Camera**: Live analysis from paired iPhone cameras via OpenClaw nodes
- **Stream**: Real-time analysis of RTSP/HTTP video streams
- **Screen**: Continuous capture and analysis of local screen content

## Sources

### YouTube Videos
- **Input**: YouTube URLs (`https://youtube.com/watch?v=...` or `https://youtu.be/...`)
- **Method**: Downloads audio + low-quality video using yt-dlp
- **CLI**: `python3 cli.py "https://youtube.com/watch?v=..."`

### Local Video Files  
- **Input**: Local file paths (MP4, MKV, AVI, WebM, MOV, M4V)
- **Method**: Direct file processing with ffmpeg for audio extraction
- **CLI**: `python3 cli.py --file /path/to/video.mp4`
- **Web**: Drag & drop or file picker with progress tracking

### iPhone Camera (Live)
- **Input**: `node:<node_name>` (requires paired iPhone via OpenClaw)
- **Method**: Real-time frame capture via `openclaw nodes camera snap`
- **Audio**: 10-second clips via `openclaw nodes camera clip` 
- **CLI**: `python3 cli.py --live node:iphone`
- **Web**: Node selector with automatic discovery

### RTSP/HTTP Streams (Live)
- **Input**: Stream URLs (`rtsp://...` or `http://...`)
- **Method**: Real-time frame capture via ffmpeg
- **Audio**: Continuous 10-second audio clips from stream
- **CLI**: `python3 cli.py --live rtsp://192.168.1.100:554/stream`
- **Web**: Stream URL input with start/stop controls

### Screen Capture (Live)
- **Input**: `screen` (captures X11 display :1)
- **Method**: Screenshots via ImageMagick `import` command
- **Audio**: Optional system audio capture (if configured)
- **CLI**: `python3 cli.py --live screen`
- **Web**: One-click screen capture start

## Live Analysis
Live sources are analyzed continuously:
- **Frame capture**: Every 10 seconds (configurable)
- **Vision analysis**: Each frame analyzed in real-time with qwen3.5:4b
- **Audio clips**: 10-second segments transcribed every 30 seconds
- **Running summary**: Generated every 5 frames for real-time understanding
- **Memory management**: Keeps last 100 segments, saves periodically to prevent bloat
- **Final export**: Complete analysis generated when stream is stopped

## How It Works

### Standard Analysis (YouTube & Local Files)
1. **Download/Load** — Downloads via yt-dlp or loads local file
2. **Transcribe** — Transcribes audio with Whisper (local, medium model default)
3. **Extract Frames** — Extracts frames every 30s via ffmpeg (configurable interval)
4. **Analyze Frames** — Analyzes each frame with qwen3.5:4b vision model via Ollama
5. **Merge Understanding** — Combines transcript + visual analysis into comprehensive document
6. **Generate Summary** — Creates concise summary with qwen3.5:0.8b
7. **Save Everything** — Stores all results to `~/.openclaw/computer-use-data/youtube/`

### Live Analysis (Camera, Streams, Screen)
1. **Continuous Capture** — Captures frames every 10s (configurable)
2. **Real-time Vision** — Analyzes each frame immediately with vision model
3. **Audio Segments** — Captures & transcribes 10s audio clips every 30s
4. **Running Summary** — Generates summary every 5 frames
5. **Memory Management** — Keeps last 100 segments in memory, saves to disk
6. **Final Processing** — On stop, generates complete summary and exports

## Configuration Options

### Whisper Models
- `tiny` — Fastest, lowest accuracy
- `base` — Fast, basic accuracy
- `medium` — **Default**, balanced speed/accuracy
- `large-v3-turbo` — Slowest, highest accuracy

### Frame Intervals
- `15` seconds — Dense analysis for visual-heavy content (demos, slides)
- `30` seconds — **Default**, balanced for most content
- `60` seconds — Sparse analysis for talking-head videos (saves GPU time)

### Vision/Summary Models
- Vision: `qwen3.5:4b` (only option currently)
- Summary: `qwen3.5:0.8b` (default) or `qwen3.5:2b` (higher quality)

### Live Stream Options
- `--capture-interval`: Seconds between frame captures (default: 10)
- `--audio-interval`: Seconds between audio clips (default: 30) 
- `--duration`: Total capture duration in seconds (default: unlimited)

Example: `python3 cli.py --live node:iphone --capture-interval 5 --duration 300`

## Tips & Best Practices

- **Use `--whisper-model large-v3-turbo`** for best transcription accuracy
- **Use `--frame-interval 15`** for visual-heavy content (demos, slides, coding)
- **Use `--frame-interval 60`** for talking-head videos to save GPU time
- **Long videos (>1hr)** may take 10-30 minutes to fully process
- **All processing is 100% local** — no API keys needed
- **GPU memory limited** — frames processed sequentially, not in parallel

## Data Storage

All analysis data is stored in: `~/.openclaw/computer-use-data/youtube/`

Each job gets its own directory:
- YouTube: `~/.openclaw/computer-use-data/youtube/yt-{timestamp}/`
- Local files: `~/.openclaw/computer-use-data/youtube/vid-{timestamp}/`
- Live streams: `~/.openclaw/computer-use-data/youtube/live-{timestamp}/`

Files created per job:

**Standard Analysis (YouTube/Local):**
- `audio.wav` — Downloaded/extracted audio
- `video.mp4` — Video file (downloaded or copied)
- `frames/` — Extracted frame images
- `job.json` — Complete job metadata and results
- `transcript.txt` — Simple timestamped transcript
- `transcript.json` — Full Whisper output with segments
- `frames.json` — Frame analysis results
- `understanding.md` — Merged transcript + visual analysis
- `summary.md` — Generated summary
- `export.md` — Complete export document

**Live Analysis:**
- `frames/` — Captured live frames (`live_0001.jpg`, etc.)
- `audio/` — Audio clips for transcription (if available)
- `job.json` — Live job metadata and captured segments
- `segments.json` — All captured segments with analysis
- `summary.md` — Final summary when stream is stopped

## SystemD Service

The API server can run as a systemd user service:

```bash
# Install service
mkdir -p ~/.config/systemd/user/
cp ~/.openclaw/workspace-main/tools/youtube-understand/youtube-understand.service ~/.config/systemd/user/dgx-youtube-understand.service

# Enable and start
systemctl --user daemon-reload
systemctl --user enable dgx-youtube-understand
systemctl --user start dgx-youtube-understand

# Check status
systemctl --user status dgx-youtube-understand

# View logs
journalctl --user -u dgx-youtube-understand -f
```

## Troubleshooting

### Service Won't Start
```bash
# Check if port is already in use
sudo netstat -tulpn | grep :8099

# Check service logs
journalctl --user -u dgx-youtube-understand -n 50

# Test manually
python3 ~/.openclaw/workspace-main/tools/youtube-understand/server.py
```

### Analysis Fails
- **yt-dlp errors**: Video may be private, region-blocked, or removed
- **Whisper errors**: Audio file corruption or missing model files
- **Vision model errors**: Ollama not running or model not loaded
- **Frame extraction fails**: Video-only download failed, trying audio-only content

### Performance Issues
- **Long processing time**: Normal for long videos or high-quality settings
- **GPU memory errors**: Frames processed sequentially to avoid this
- **Disk space**: Large videos can use significant storage

## Dependencies

All dependencies are already installed and working:
- `yt-dlp` at `/home/linuxbrew/.linuxbrew/bin/yt-dlp`
- `ffmpeg` at `/home/linuxbrew/.linuxbrew/bin/ffmpeg`
- `whisper` at `/home/linuxbrew/.linuxbrew/bin/whisper`
- Ollama at `localhost:11434` with required models
- Python 3 with Flask, requests, pathlib

## Examples

### Basic Usage
```bash
# Analyze with defaults
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "https://youtu.be/dQw4w9WgXcQ"
```

### High-Quality Analysis
```bash
# Best quality settings
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "https://youtu.be/dQw4w9WgXcQ" \
  --whisper-model large-v3-turbo \
  --frame-interval 15 \
  --summary-model qwen3.5:2b
```

### Batch Processing
```bash
# List and process multiple videos
for url in "https://youtu.be/video1" "https://youtu.be/video2"; do
  python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "$url" &
done
wait
```

### API Usage
```bash
# Start YouTube analysis via API
curl -X POST http://localhost:8099/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/dQw4w9WgXcQ", "whisper_model": "medium"}'

# Upload video file
curl -X POST http://localhost:8099/api/upload \
  -F "file=@video.mp4" \
  -F "whisper_model=medium" \
  -F "frame_interval=30"

# Start live iPhone camera
curl -X POST http://localhost:8099/api/live/start \
  -H "Content-Type: application/json" \
  -d '{"source": "node:iphone", "config": {"capture_interval": 10}}'

# Stop live stream
curl -X POST http://localhost:8099/api/live/stop \
  -H "Content-Type: application/json" \
  -d '{"job_id": "live-1234567890"}'

# Get live stream status
curl http://localhost:8099/api/live/live-1234567890

# Check available nodes
curl http://localhost:8099/api/nodes

# Check job status
curl http://localhost:8099/api/jobs/vid-1234567890

# Download export
curl http://localhost:8099/api/jobs/live-1234567890/export > analysis.md
```

### Node Examples
```bash
# List available camera nodes
python3 cli.py --nodes

# Live analysis from paired iPhone
python3 cli.py --live node:PatricksiPhone --duration 600

# Screen capture for 5 minutes
python3 cli.py --live screen --duration 300 --capture-interval 15

# RTSP security camera
python3 cli.py --live rtsp://admin:password@192.168.1.100:554/stream1
```