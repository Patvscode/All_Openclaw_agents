# UI Design System — Agent Skill

Standard design system for all agent dashboards and web UIs. Use this when building any new dashboard, tool interface, or web page for the hub.

## Design Tokens (CSS Custom Properties)

```css
:root {
  /* Backgrounds */
  --bg: #0a0a0f;           /* Page background */
  --surface: #12121a;       /* Card/panel backgrounds */
  --surface2: #1a1a28;      /* Elevated surfaces, inputs */
  --surface3: #222236;      /* Hover states, active items */

  /* Borders */
  --border: #2a2a40;        /* Default borders */

  /* Text */
  --text: #e0e0f0;          /* Primary text */
  --text2: #8888aa;         /* Secondary/muted text */

  /* Accent */
  --accent: #6c5ce7;        /* Primary action, links, focus */
  --accent2: #a29bfe;       /* Hover accent, highlights */

  /* Semantic Colors */
  --green: #00b894;         /* Success, online, complete */
  --red: #ff6b6b;           /* Error, danger, failed */
  --orange: #fdcb6e;        /* Warning, pending */
  --blue: #74b9ff;          /* Info, neutral status */
  --pink: #fd79a8;          /* Special/creative */
  --cyan: #00cec9;          /* Running, active */
}
```

## Typography

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text);
  background: var(--bg);
}
/* Scale: 11px labels → 13px body → 14px emphasis → 16-20px headings */
```

## Component Patterns

### Cards
```css
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
```

### Buttons
```css
.btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover { background: var(--accent2); }
.btn-secondary { background: var(--surface3); color: var(--text); border: 1px solid var(--border); }
.btn-sm { padding: 6px 14px; font-size: 12px; }
.btn-danger { background: var(--red); color: white; }
```

### Inputs
```css
input, textarea, select {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  color: var(--text);
  font-size: 14px;
  width: 100%;
}
input:focus { outline: none; border-color: var(--accent); }
/* IMPORTANT: Use font-size: 16px on mobile to prevent iOS zoom */
```

### Status Badges
```css
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.badge-running { background: rgba(0,184,148,0.15); color: var(--green); }
.badge-completed { background: rgba(108,92,231,0.15); color: var(--accent2); }
.badge-failed { background: rgba(255,107,107,0.15); color: var(--red); }
```

### Stat Cards
```css
.stat-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}
.stat-card .number { font-size: 32px; font-weight: 700; color: var(--accent2); }
.stat-card .label { font-size: 12px; color: var(--text2); }
```

### Tabs
```css
.tabs { display: flex; border-bottom: 1px solid var(--border); background: var(--surface); overflow-x: auto; }
.tab { padding: 12px 24px; cursor: pointer; font-size: 14px; color: var(--text2); border-bottom: 2px solid transparent; }
.tab.active { color: var(--accent2); border-bottom-color: var(--accent); }
```

### Animated Status Dot
```css
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: var(--green); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
```

## Layout Rules

1. **Max content width**: 1400px centered
2. **Grid**: `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))`
3. **Spacing**: 16px between cards, 20px content padding
4. **Border radius**: 12px for cards, 8px for inputs/buttons, 10px for badges

## Mobile Rules (MANDATORY)

```css
@media (max-width: 768px) {
  /* Stack grids to single column or 1fr 1fr */
  /* Inputs must be 16px font-size (prevents iOS zoom) */
  /* Hide sidebars, show toggle button */
  /* Tabs: overflow-x: auto for horizontal scroll */
  /* Min touch target: 44px */
}
```

## Dark Theme Principles

- Never use pure white (#fff) — use var(--text) (#e0e0f0)
- Never use pure black (#000) — use var(--bg) (#0a0a0f)
- Status colors at 15% opacity for backgrounds: `rgba(color, 0.15)`
- Borders subtle: #2a2a40 (barely visible, adds depth)
- Hover: shift border to accent color, slight translateY(-2px)
- Active/selected: accent border + surface3 background

## Page Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1">
<title>Page Title</title>
<style>
/* Paste design tokens above */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

.header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
.header h1 { font-size: 20px; font-weight: 700; }
.header h1 span { color: var(--accent2); }

.tabs { display: flex; border-bottom: 1px solid var(--border); background: var(--surface); overflow-x: auto; }
.tab { padding: 12px 24px; cursor: pointer; font-size: 14px; color: var(--text2); border-bottom: 2px solid transparent; }
.tab:hover { color: var(--text); background: var(--surface2); }
.tab.active { color: var(--accent2); border-bottom-color: var(--accent); }

.content { padding: 20px; max-width: 1400px; margin: 0 auto; }

/* Add component styles as needed from the patterns above */

@media (max-width: 768px) {
  .content { padding: 12px; }
  input, textarea, select { font-size: 16px; }
}
</style>
</head>
<body>
  <div class="header">
    <h1>🎯 <span>Page Title</span></h1>
  </div>
  <div class="tabs">
    <div class="tab active" data-tab="main">Main</div>
  </div>
  <div class="content">
    <!-- Content here -->
  </div>
</body>
</html>
```

## Do's and Don'ts

✅ **Do:**
- Use the design tokens — never hardcode colors
- Test on mobile (iPhone via Tailscale)
- Build as a NEW page first (iterate), get approval before replacing
- Keep all CSS inline (single HTML file per dashboard)
- Use `esc()` helper for all user-generated content

❌ **Don't:**
- Use pure white or pure black
- Skip mobile responsiveness
- Edit existing working dashboards directly
- Use external CSS/JS dependencies
- Use markdown tables (Discord/WhatsApp) — use bullet lists
- Forget 16px font-size on mobile inputs
