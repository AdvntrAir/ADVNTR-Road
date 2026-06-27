# ADVNTR Road Guides

Production pipeline for ADVNTR Road guide PDFs.

## Current Status

This workspace contains the first scaffolded guide build:

- Python build script with YAML, Markdown, Jinja2, map, font, HTML, and PDF paths.
- Print-oriented template and CSS from the locked spec.
- Starter Olympic National Park content in `guides/olympic-np/`.
- Generated debug HTML at `output/olympic-np.html`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Add a Google Maps Static API key to `.env` when live maps are ready:

```bash
GOOGLE_MAPS_API_KEY=your_key_here
```

## Build

```bash
.venv/bin/python build.py --guide olympic-np --no-maps
```

Run with live maps after the API key is present:

```bash
.venv/bin/python build.py --guide olympic-np
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

Drop the illustrated cover map into the guide assets folder and set `cover_map`
in `guides/olympic-np/content.yaml`.

## Local Renderer Note

The Python package install succeeds, but this machine currently lacks the native
libraries WeasyPrint needs for PDF rendering. The builder still writes HTML for
layout review. Install the WeasyPrint native dependencies before final PDF QA.
