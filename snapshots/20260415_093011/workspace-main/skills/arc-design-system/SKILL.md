# ARC Design System — Living Standard

## Purpose
Ensure every hub page and service UI is consistent, mobile-first, and meets quality standards across all devices (iPhone, MacBook, desktop).

## When to Use
- Before building any new hub page or UI component
- When modifying existing pages
- During design review / validation

## Tools

### Design Validator (hub/00-design-validator/)
Browser-based tool for validating any hub page:
1. Select a page from the dropdown or enter a URL
2. See side-by-side iPhone (390×844) and Desktop (1024×700) previews
3. Run auto-checks for: back link, viewport, dark theme, scroll, auto-refresh
4. Manual checklist for: touch targets, readability, status colors, loading states
5. Score out of 12 quality checks

### Quality Checklist (must pass ALL before shipping)
- [ ] Has ← Hub back link in header
- [ ] Has mobile viewport meta tag (`width=device-width, initial-scale=1.0`)
- [ ] Uses dark background (var(--bg) or #0a0a0f)
- [ ] No horizontal scrollbar on any device
- [ ] Has auto-refresh (setInterval, 10-60s)
- [ ] Handles API failures gracefully (shows message, not blank)
- [ ] Touch targets ≥ 44px height on mobile
- [ ] Uses standard status colors (green/red/yellow)
- [ ] Text readable at phone distance
- [ ] Nothing clips or overlaps on mobile
- [ ] Shows loading state before data arrives
- [ ] Matches ARC design system (cards, borders, fonts)

## Design Tokens

```css
/* Colors */
--bg: #0a0a0f;
--card: #12121a;
--border: #1e1e2e;
--text: #e0e0e0;
--dim: #888;
--accent: #6c8aff;
--green: #4ade80;
--red: #f87171;
--yellow: #facc15;
--orange: #fb923c;
--purple: #a78bfa;

/* Typography */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
/* Sizes: 11px labels, 13px body, 14px default, 16-18px headings */

/* Spacing: 8px grid */
/* Radius: 8-10px cards, 20px pills/badges, 4-6px small elements */
```

## Component Patterns

### Page Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[Name] — ARC Platform</title>
<style>
:root{--bg:#0a0a0f;--card:#12121a;--border:#1e1e2e;--text:#e0e0e0;--dim:#888;--accent:#6c8aff;--green:#4ade80;--red:#f87171;--yellow:#facc15;--orange:#fb923c;--purple:#a78bfa}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.header{background:var(--card);border-bottom:1px solid var(--border);padding:12px 16px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:100}
.header a{color:var(--dim);text-decoration:none;font-size:20px}
.header h1{font-size:17px;font-weight:600;flex:1}
</style>
</head>
<body>
<div class="header">
  <a href="../">←</a>
  <h1>[Page Name]</h1>
</div>
<!-- Content -->
<script>
const HOST = window.location.hostname;
// Auto-refresh
setInterval(refresh, 10000);
</script>
</body>
</html>
```

### Status Dot
```html
<div style="width:10px;height:10px;border-radius:50%;background:var(--green)"></div>
```

### Card
```html
<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px">
  Content
</div>
```

### Badge
```html
<span style="font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(74,222,128,.15);color:var(--green)">active</span>
```

## Service API Rules
- All API calls use `AbortController` with 3-4s timeout
- Prefer routing through ARC Watchdog (8098) for localhost-bound services
- Show loading state immediately, update when data arrives
- If API fails, show last known state + "stale" indicator, never blank screen

## Mobile-Specific Rules
- No fixed positioning except sticky header
- Scrollable tabs with `-webkit-overflow-scrolling: touch`
- No hover-only interactions (everything must work with tap)
- Test with Safari iOS (most restrictive browser)
- `visibilitychange` handler for background/foreground (iOS kills connections)

## Validation Workflow
1. Build the page
2. Open Design Validator: `http://[TAILSCALE_IP]:8090/00-design-validator/`
3. Load your page in the validator
4. Run auto-checks
5. Complete manual checklist
6. Score must be ≥ 90% (11/12) before shipping
7. If issues found, fix and re-validate

## Updating This Standard
When you discover a new edge case or pattern:
1. Add it to this SKILL.md
2. Update the auto-checks in `hub/00-design-validator/index.html` if automatable
3. Post to comms #projects so all agents learn
4. Update `docs/ARC_PLATFORM_STANDARD.md` if it's a fundamental rule
