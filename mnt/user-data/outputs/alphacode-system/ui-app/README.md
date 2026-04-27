# AlphaCode OS — System Interface

> The full interactive companion to the GitHub Profile README.

## Quick Start

```bash
# Serve locally (required for module imports + fetch)
npx serve .
# or
python3 -m http.server 8080
# then open http://localhost:8080
```

> ⚠️ Must be served over HTTP — ES modules and `fetch()` don't work on `file://`.

## Deploy to GitHub Pages

```bash
# From repo root
git subtree push --prefix ui-app origin gh-pages
```

Then update the README "Launch System Interface" button URL to:
`https://yourusername.github.io/alphacode-system/`

## Structure

```
ui-app/
├── index.html          Main entry point
├── style.css           Full design system
├── script.js           App boot + orchestration
├── components/
│   ├── header.js       Navigation header
│   ├── dashboard.js    Metrics + node status
│   └── terminal.js     Interactive terminal sim
├── data/
│   └── systems.json    All app data (single source of truth)
└── assets/             SVG assets
```

## Features

- **Boot Screen** — Animated OS-style boot sequence
- **Dashboard** — Live metrics, node status, system cards
- **Architecture Canvas** — Animated WebGL-style architecture diagram
- **Systems Gallery** — Featured project cards with metrics
- **Terminal** — Fully interactive CLI simulation (try `help`)
- **AlphaBot** — AI layer interface with inference log + chat
- **Background Particles** — Subtle animated network overlay

## Customization

All data lives in `data/systems.json`. Update:
- `meta` — version, build, operator name
- `metrics` — your real GitHub stats
- `nodes` — your actual tech stack services
- `systems` — your real projects
- `alphabot` — AI layer config

## Tech

Pure vanilla JS (ES modules) + Canvas API. No frameworks, no build step.
