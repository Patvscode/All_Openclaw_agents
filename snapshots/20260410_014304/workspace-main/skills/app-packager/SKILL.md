# App Packager — Agent Skill

Package any hub dashboard (or web app) into a standalone desktop application using Electron. Creates distributable apps that work offline and can be shared.

## When to Use

- User wants a desktop version of a hub dashboard
- Need to share an app with someone who doesn't have access to the hub
- Want a permanent, distributable version of a web tool
- Building kiosk/dedicated-window apps from existing web UIs

## How It Works

1. Takes an existing HTML dashboard (single-file or multi-file)
2. Wraps it in a minimal Electron shell
3. Configures window, icon, title, and connection settings
4. Builds for the target platform (Linux ARM64 for Spark, or cross-compile)
5. Outputs a distributable package

## Quick Usage

```bash
# Package a single hub module
~/tools/app-packager/package.sh \
  --name "Computer Use" \
  --source ~/hub/26-computer-use-v2/ \
  --api-url http://localhost:8095 \
  --output ~/apps/

# Package with custom settings
~/tools/app-packager/package.sh \
  --name "Research Lab" \
  --source ~/hub/25-research-lab/ \
  --api-url http://localhost:8097 \
  --width 1200 --height 800 \
  --output ~/apps/
```

## What Gets Packaged

The packager creates:
```
apps/<app-name>/
├── package.json          # Electron config
├── main.js              # Electron main process
├── preload.js           # Security bridge
├── app/                 # Copy of the dashboard files
│   └── index.html       # (and any assets)
├── build.sh             # Build script for packaging
└── README.md            # How to run/distribute
```

## For Agents

When an agent needs to package an app:

```bash
# 1. Ensure electron and electron-builder are installed
npm list -g electron 2>/dev/null || npm install -g electron

# 2. Run the packager
cd ~/tools/app-packager
node create-app.js \
  --name "App Name" \
  --source /path/to/hub/module/ \
  --api http://localhost:PORT \
  --output ~/apps/

# 3. Test it
cd ~/apps/app-name && npx electron .

# 4. Build distributable
cd ~/apps/app-name && npx electron-builder --linux
```

## Connecting to APIs

Desktop apps need to know where the APIs live. The packager injects a config:

```javascript
// In the app, window.APP_CONFIG is available
window.APP_CONFIG = {
  apiUrl: "http://100.109.173.109:8095",  // Or localhost
  hubUrl: "http://100.109.173.109:8090",
  name: "Computer Use",
};
```

For sharing with friends: they need Tailscale access to the Spark, or the app needs to be configured with the correct API endpoint.

## Click-to-Run Desktop Launchers (Recommended)

The fastest path — uses Chromium's `--app` mode (looks native, no Electron needed):

```bash
# Build all launchers at once
~/tools/app-packager/build-launchers.sh

# Creates:
# ~/.local/share/applications/openclaw-*.desktop  (GNOME app menu entries)
# ~/.openclaw/apps/*.sh                            (launcher scripts)
# ~/.openclaw/apps/icons/*.svg                     (app icons)
```

Apps appear in the GNOME app menu. Click to launch — opens in a clean window, no browser chrome.

## Share with Friends

```bash
# Package any hub app as a zip
~/tools/app-packager/share-app.sh computer-use
# → ~/.openclaw/apps/shared/computer-use.zip
```

Recipient needs Tailscale access to the Spark (or change the API URL).

## Electron Apps (Heavier, Fully Standalone)

For true standalone distribution:
```bash
node ~/tools/app-packager/create-app.js --name "App" --source /path --api http://host:port --output ~/apps/
cd ~/apps/app && npm install && npm start
```

## Limitations

- Apps need the backend server running (they connect to APIs)
- Chromium launchers need chromium-browser installed
- Electron builds are ~150MB per app
- ARM64 Electron builds only on Spark; cross-compile for x86_64
- For friends: they need Tailscale or the API must be exposed
