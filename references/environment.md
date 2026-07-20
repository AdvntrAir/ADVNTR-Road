# ADVNTR Road — Build Environment Reference

Read this before debugging any font, layout, or render issue in WeasyPrint.

## WeasyPrint Known Failure Modes

**Silent failures** — WeasyPrint exits 0 but the output is wrong:
- Missing font → falls back to system sans-serif with no warning
- `target-counter()` in TOC → only resolves on second render pass; single-pass builds show blank page numbers
- SVG `include` fails silently → topo lines missing on back cover
- Very large HTML (>5MB) → some pages may drop content without error

**Font embedding**
- Fonts must be embedded as base64 data URIs in the `{{ font_css | safe }}` block
- Playfair Display requires explicit weight declarations: 400, 700 (bold). Weight 900 falls back to 700.
- If a section shows bold sans instead of Playfair Display, check CSS specificity — a bare `h2 {}` rule can override `.section-banner__title { font-family: var(--font-display); }`

**WeasyPrint version**
- Pinned to ≥62.0 in requirements.txt
- Session builds have used WeasyPrint 69.0 (confirmed in PDF metadata)
- `target-counter(attr(href), page)` is supported from 52+

## Python Environment

```bash
# Activate venv before any build command
source .venv/bin/activate

# Install / sync dependencies
.venv/bin/pip install -r requirements.txt

# Run a build
.venv/bin/python build.py --guide crater-lake-np --no-maps
# or via build.sh (handles venv activation)
./build.sh crater-lake-np
```

## API Keys

- `NPS_API_KEY` — add to `.env` for NPS Media API photo sourcing
- Without it, build uses `DEMO_KEY` which hits rate limits and will 404
- Photo failures are WARN (not FAIL) — guide renders without images

## Output Artifacts

| File | Description |
|---|---|
| `output/[slug].html` | Jinja2-rendered HTML (source for WeasyPrint) |
| `output/[slug]-2026.pdf` | Final print-ready PDF |
| `output/build_summary.md` | Gate 3 QA results — read this first on any failure |
| `output/visual_qa_report.md` | Visual QA subagent findings |
| `output/voice_risk_report.md` | Voice risk subagent findings |
| `output/qr/` | QR code PNGs (one per link slug + trail slugs) |
| `output/_redirects_fragment.txt` | Netlify redirect entries for road.advntr.io/r/[slug] |
