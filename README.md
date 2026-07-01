# ADVNTR Road Guides

Production pipeline for ADVNTR Road guide PDFs.

## Current Status

This is a reusable guide-build system, not a one-off script. Two guides exist so far:

- `guides/mount-rainier-np/` — complete, full first draft, including campground/business
  photos and live map panels.
- `guides/olympic-np/` — scaffolded content only; missing section photo assets.

To add a new destination, follow `docs/Codex-new-guide-workflow.md`, starting from
`docs/ADVNTR_Road_Destination_Template.md`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

`requirements.txt` pins `fonttools==4.62.0` — do not let `pip` upgrade it past that on this
Python version. `fonttools==4.63.0` has a packaging bug that crashes WeasyPrint's import on
Python 3.14 (`ModuleNotFoundError: fontTools.otlLib.optimize.gpos`). If you ever see that
error, reinstall with the pinned version.

If the project folder is ever moved (e.g. relocated within Google Drive), the `.venv`'s
shebang lines still point at the old path and `pip`/console scripts will silently fail while
`python` itself still works. Delete and recreate `.venv` after a move:

```bash
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Add a Google Maps Static API key to `.env` when live maps are ready:

```bash
GOOGLE_MAPS_API_KEY=your_key_here
```

## Build

```bash
.venv/bin/python build.py --guide mount-rainier-np --no-maps
```

Run with live maps after the API key is present (this hits the paid Google Maps Static API —
confirm with the user before running for a new guide):

```bash
.venv/bin/python build.py --guide mount-rainier-np
```

## Required Assets Before Final PDF

Drop the design system folder at the project root:

```text
design_system/
```

The font paths must match the spec, especially:

```text
design_system/uploads/Inter,Playfair_Display,Space_Mono,Titan_One/
design_system/assets/fonts/
```

Covers are full-bleed photos, not illustrations. Drop the chosen cover photo into the guide's
assets folder and set `cover_photo` in `guides/[slug]/content.yaml`.

## Local Renderer Note

WeasyPrint renders natively on this machine (confirmed working, version 69.0) — no Chrome
fallback needed in normal operation. `build.py` will fall back to headless Chrome
(`/Applications/Google Chrome.app`) only if WeasyPrint itself fails to import or render.

## Visual QA Tooling

`pdftoppm` (from Homebrew's `poppler`) is used throughout development to rasterize PDF pages
for visual review — install it with `brew install poppler` if it's missing. Pillow (`PIL`,
already in `requirements.txt` via WeasyPrint's dependency chain) is used for pixel-level
margin/alignment checks when debugging layout issues.
