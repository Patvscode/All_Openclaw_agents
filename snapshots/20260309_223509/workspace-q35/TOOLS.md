# JESS Tools

## Key Commands
- `memquery "question"` — search memory (port 8102)
- `smart-file-edit check <file>` — check file size before reading
- `comms post general "msg"` / `comms dm main "msg"` — agent comms
- `board list` — task board
- `wc -c <file>` — always check size before reading
- `node --check file.js` — verify JS syntax

## Voice (Sesame CSM-1B)
- `voice say "text" --voice jess --send` — generate as Jess
- `voice hear file.ogg` — transcribe audio

## File Safety
- Under 15KB → safe to read
- 15-30KB → read-only, use `edit` for changes
- Over 30KB → DO NOT READ. Write to new file or use `smart-file-edit`

## System
- DGX Spark, 128GB RAM, GB10 GPU
- Model: Qwen3.5-122B-A10B on port 18080
- Ollama: port 11434 (0.8b, 2b, 4b)
- Hub: http://100.109.173.109:8090
- Test page: hub/99-jess-test/
