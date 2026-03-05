# YouTube Understanding

Analyze YouTube videos with combined audio transcription and visual frame analysis.

## Quick Start

```bash
# Analyze a video
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "https://youtube.com/watch?v=..."

# With high quality settings
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py "https://youtube.com/watch?v=..." --whisper-model large-v3-turbo --frame-interval 15

# List all analyzed jobs
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --list

# Get summary of a specific job
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --summary yt-1234567890

# Export full analysis
python3 ~/.openclaw/workspace-main/tools/youtube-understand/cli.py --export yt-1234567890
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

- **POST /api/analyze** — Start video analysis
  - Body: `{url, whisper_model?, frame_interval?, vision_model?, summary_model?, max_frames?}`
  - Returns: `{job_id, status: "queued"}`

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
- Real-time progress tracking
- Job history management
- Interactive transcript with search
- Frame analysis gallery with lightbox
- Export and download capabilities
- Mobile-responsive design

## How It Works

1. **Download** — Uses yt-dlp to download audio (high quality) and video (low quality for frames)
2. **Transcribe** — Transcribes audio with Whisper (local, medium model default)
3. **Extract Frames** — Extracts frames every 30s via ffmpeg (configurable interval)
4. **Analyze Frames** — Analyzes each frame with qwen3.5:4b vision model via Ollama
5. **Merge Understanding** — Combines transcript + visual analysis into comprehensive document
6. **Generate Summary** — Creates concise summary with qwen3.5:0.8b
7. **Save Everything** — Stores all results to `~/.openclaw/computer-use-data/youtube/`

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

## Tips & Best Practices

- **Use `--whisper-model large-v3-turbo`** for best transcription accuracy
- **Use `--frame-interval 15`** for visual-heavy content (demos, slides, coding)
- **Use `--frame-interval 60`** for talking-head videos to save GPU time
- **Long videos (>1hr)** may take 10-30 minutes to fully process
- **All processing is 100% local** — no API keys needed
- **GPU memory limited** — frames processed sequentially, not in parallel

## Data Storage

All analysis data is stored in: `~/.openclaw/computer-use-data/youtube/`

Each job gets its own directory: `~/.openclaw/computer-use-data/youtube/yt-{timestamp}/`

Files created per job:
- `audio.wav` — Downloaded audio
- `video.mp4` — Low-quality video for frame extraction
- `frames/` — Extracted frame images
- `job.json` — Complete job metadata and results
- `transcript.txt` — Simple timestamped transcript
- `transcript.json` — Full Whisper output with segments
- `frames.json` — Frame analysis results
- `understanding.md` — Merged transcript + visual analysis
- `summary.md` — Generated summary
- `export.md` — Complete export document

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
# Start analysis via API
curl -X POST http://localhost:8099/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtu.be/dQw4w9WgXcQ", "whisper_model": "medium"}'

# Check job status
curl http://localhost:8099/api/jobs/yt-1234567890

# Download export
curl http://localhost:8099/api/jobs/yt-1234567890/export > video_analysis.md
```