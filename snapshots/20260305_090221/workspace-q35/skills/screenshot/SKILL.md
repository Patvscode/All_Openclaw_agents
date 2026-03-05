# 📸 Screenshot Tool - Jess Skill

**Purpose:** Take screenshots of the current desktop and send them to Telegram automatically  
**Created:** 2026-03-03  
**Status:** ✅ Working

---

## 🚀 QUICK USAGE

### Basic Screenshot:
```bash
cd ~/.openclaw/workspace-q35/skills/screenshot
./screenshot.sh
```

### Screenshot with Caption:
```bash
./screenshot.sh --caption "My message here"
```

### Screenshot with Custom Output Path:
```bash
./screenshot.sh --output /path/to/save.png
```

---

## 📋 WHAT IT DOES

1. **Takes screenshot** using `gnome-screenshot` (or fallback tools)
2. **Saves to workspace** in `~/openclaw/workspace-q35/skills/screenshot/screenshots/`
3. **Sends to Telegram** via message tool with caption
4. **Returns file path** for reference

---

## 🔧 HOW IT WORKS

### Tool Chain:
1. **gnome-screenshot** (primary) - Takes screenshot with delay
2. **scrot** (fallback) - Alternative screenshot tool
3. **import** (fallback) - ImageMagick alternative
4. **message tool** - Sends to Telegram

### Default Settings:
- **Delay:** 2 seconds (gives time to switch windows)
- **Format:** PNG
- **Quality:** High
- **Save location:** `~/.openclaw/workspace-q35/skills/screenshot/screenshots/YYYY-MM-DD_HH-MM-SS.png`
- **Telegram:** Sends to current active channel

---

## 📁 FILES CREATED

```
~/.openclaw/workspace-q35/skills/screenshot/
├── SKILL.md              ✅ This file
├── screenshot.sh         ✅ Main script
├── screenshot.py         ✅ Python alternative (if needed)
└── screenshots/          ✅ Saved screenshots
    └── current_screen.png ✅ From Jess companion demo
```

---

## 💡 USE CASES

1. **Debugging:** Show what's happening on screen
2. **Progress updates:** Share work in progress
3. **Error reporting:** Capture error messages
4. **Documentation:** Create visual guides
5. **Testing:** Verify UI/UX changes
6. **Communication:** Show teammates what you see

---

## 🎯 EXAMPLE USAGE

### For Jess Companion Development:
```bash
# Take screenshot of companion page
./screenshot.sh --caption "Jess 3D Companion - Current Progress"

# Result: Screenshot sent to Telegram with caption
```

### For Error Debugging:
```bash
# Take screenshot of error
./screenshot.sh --caption "Error in console: WebGL not supported"

# Result: Screenshot with context sent immediately
```

---

## 🔧 CUSTOMIZATION

### Change Delay:
```bash
DELAY=5 ./screenshot.sh  # 5 second delay
```

### Change Output Format:
```bash
FORMAT=jpg ./screenshot.sh  # JPEG instead of PNG
```

### Send to Specific Channel:
```bash
CHANNEL_ID=-1001234567890 ./screenshot.sh --caption "Test"
```

---

## 🚨 TROUBLESHOOTING

### "gnome-screenshot not found":
- Install: `sudo apt install gnome-screenshot`
- Fallback: Script will try `scrot` or `import`

### "Telegram send failed":
- Check Telegram bot is configured
- Verify channel ID is correct
- Check file permissions

### "Screenshot too large":
- Script automatically compresses if >10MB
- Use FORMAT=jpg for smaller files

---

## 🎯 ADVANCED: POSITIONING THE SCREEN

### Capture Specific Window:
```bash
gnome-screenshot -w -f output.png  # Current window
```

### Capture Specific Region:
```bash
import -window root output.png  # Full screen
# Then crop with ImageMagick:
convert output.png -crop 800x600+100+100 +repage cropped.png
```

### Auto-Capture Browser:
```bash
# Wait for browser to load, then screenshot
sleep 3 && gnome-screenshot -f output.png
```

---

## 📊 INTEGRATION WITH OTHER TOOLS

### With Browser Automation:
```bash
# Open page, wait, screenshot
browser open http://localhost:8001
sleep 2
./screenshot.sh
```

### With Server Status:
```bash
# Check server, then screenshot
curl http://localhost:8001/api/status
./screenshot.sh --caption "Server status: $(curl -s http://localhost:8001/api/status)"
```

---

## 🔄 MAINTENANCE

### Update Script:
```bash
cd ~/.openclaw/workspace-q35/skills/screenshot
git pull  # If using git
```

### Test Installation:
```bash
./screenshot.sh --test  # Runs test screenshot
```

### Check Dependencies:
```bash
which gnome-screenshot scrot import  # Verify tools available
```

---

## 📝 NOTES

- **Default delay (2s)** gives time to switch to target window
- **PNG format** for best quality, **JPG** for smaller files
- **Sends to Telegram** automatically (no manual upload needed)
- **Saves locally** for reference and backup
- **Can be called** from any script or workflow

---

**Status:** ✅ Fully working and tested  
**Next:** Integrate with other tools for even better automation!