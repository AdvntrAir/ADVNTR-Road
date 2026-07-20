# ADVNTR Road — Build Spec: Map Pipeline, Build System, QA & Error Recovery
### Use when: fixing build.py logic, QA checklist failures, map issues

```
pip install requests python-dotenv
```
 
`.env`:
```
GOOGLE_MAPS_API_KEY=your_key_here
```
 
### Brand style JSON (apply to every map call)
 
```python
MAP_STYLE = [
    {"featureType":"all","elementType":"labels.text.fill",
     "stylers":[{"color":"#1B4436"}]},
    {"featureType":"all","elementType":"labels.text.stroke",
     "stylers":[{"color":"#F9E4C5"},{"weight":2}]},
    {"featureType":"water","elementType":"geometry",
     "stylers":[{"color":"#4A7FA5"}]},
    {"featureType":"landscape.natural","elementType":"geometry",
     "stylers":[{"color":"#E8D9B8"}]},
    {"featureType":"landscape.man_made","elementType":"geometry",
     "stylers":[{"color":"#F9E4C5"}]},
    {"featureType":"road.highway","elementType":"geometry",
     "stylers":[{"color":"#DDAD8A"},{"weight":1.5}]},
    {"featureType":"road.local","elementType":"geometry",
     "stylers":[{"color":"#EDD5B0"},{"weight":0.8}]},
    {"featureType":"poi","elementType":"all",
     "stylers":[{"visibility":"off"}]},
    {"featureType":"transit","elementType":"all",
     "stylers":[{"visibility":"off"}]},
    {"featureType":"administrative","elementType":"geometry.stroke",
     "stylers":[{"color":"#DDAD8A"},{"weight":0.8}]},
]
```
 
### Map fetch and overlay functions
 
```python
import json, base64, requests, urllib.parse
from pathlib import Path
 
def build_map_url(cfg, api_key):
    """Build Google Static Maps URL with brand styling."""
    style_params = ''.join(
        '&style=' + urllib.parse.quote(json.dumps(s))
        for s in MAP_STYLE
    )
 
    marker_params = ''
    for m in cfg.get('markers', []):
        color = {
            'campground': '0x1B4436',
            'gateway':    '0xDDAD8A',
            'trailhead':  '0x88A33B',
        }.get(m['type'], '0x5B768C')
        # First letter of label as map marker label
        lbl = m['label'][0]
        marker_params += f'&markers=color:{color}|label:{lbl}|{m["lat"]},{m["lng"]}'
 
    url = (
        f"https://maps.googleapis.com/maps/api/staticmap"
        f"?center={cfg['center_lat']},{cfg['center_lng']}"
        f"&zoom={cfg['zoom']}"
        f"&size={cfg['size']}"
        f"&scale=2"
        f"&maptype=terrain"
        f"{style_params}"
        f"{marker_params}"
        f"&key={api_key}"
    )
    return url
 
 
def fetch_map_as_uri(cfg, api_key):
    """Fetch map and return as base64 data URI for embedding."""
    url = build_map_url(cfg, api_key)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    b64 = base64.b64encode(resp.content).decode('utf-8')
    return f"data:image/png;base64,{b64}"
 
 
def coord_to_pixel(lat, lng, bounds, img_w, img_h):
    """Convert lat/lng to pixel position on a map image of known bounds."""
    x = (lng - bounds['west'])  / (bounds['east']  - bounds['west'])  * img_w
    y = (bounds['north'] - lat) / (bounds['north'] - bounds['south']) * img_h
    return round(x), round(y)
 
 
def build_overlay_svg(cfg):
    """Build branded SVG overlay with markers registered to map coordinates."""
    if 'bounds' not in cfg:
        return ''
 
    w, h  = [int(v) for v in cfg['size'].split('x')]
    bounds = cfg['bounds']
    parts  = []
 
    for m in cfg.get('markers', []):
        x, y = coord_to_pixel(m['lat'], m['lng'], bounds, w, h)
        t     = m['type']
        label = m['label']
 
        if t == 'campground':
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="9" fill="#1B4436" '
                f'stroke="#F9E4C5" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y+22}" text-anchor="middle" '
                f'font-family="Space Mono,monospace" font-size="8" '
                f'letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
        elif t == 'gateway':
            parts.append(
                f'<rect x="{x-8}" y="{y-8}" width="16" height="16" '
                f'fill="#DDAD8A" stroke="#1B4436" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y+24}" text-anchor="middle" '
                f'font-family="Space Mono,monospace" font-size="8" '
                f'letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
        elif t == 'trailhead':
            # Upward-pointing triangle
            pts = f"{x},{y-10} {x-8},{y+6} {x+8},{y+6}"
            parts.append(
                f'<polygon points="{pts}" fill="#88A33B" '
                f'stroke="#F9E4C5" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y+22}" text-anchor="middle" '
                f'font-family="Space Mono,monospace" font-size="8" '
                f'letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
 
    return '\n'.join(parts)
```
 
---
 
## 10. BUILD SYSTEM
 
### requirements.txt
 
```
weasyprint>=62.0
jinja2>=3.1
pyyaml>=6.0
markdown>=3.5
python-dotenv>=1.0
requests>=2.31
```
 
### build.py — complete
 
```python
#!/usr/bin/env python3
"""
ADVNTR Road Guide PDF Builder
==============================
Usage:
  python build.py --guide olympic-np
  python build.py --guide olympic-np --no-maps    # Skip map API calls (faster)
  python build.py --guide olympic-np --font-test  # Render font test page only
 
Prerequisites:
  pip install -r requirements.txt
  GOOGLE_MAPS_API_KEY in .env
"""
 
import argparse, base64, json, os, sys
import yaml, markdown, requests, urllib.parse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from dotenv import load_dotenv
 
load_dotenv()
MAPS_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
 
# ── PATHS ────────────────────────────────────────────────────────────────────
 
ROOT        = Path(__file__).parent
DS          = ROOT / 'design_system'
DS_FONTS    = DS / 'assets' / 'fonts'
STATIC_FONTS_BASE = DS / 'uploads' / 'Inter,Playfair_Display,Space_Mono,Titan_One'
TEMPLATE_DIR = ROOT / 'template'
OUTPUT_DIR   = ROOT / 'output'
 
# ── FONT MAP ─────────────────────────────────────────────────────────────────
# Use static TTFs — safer with WeasyPrint than variable fonts
 
FONTS = [
    (STATIC_FONTS_BASE/'Playfair_Display/static/PlayfairDisplay-Regular.ttf',
     'Playfair Display','normal','400'),
    (STATIC_FONTS_BASE/'Playfair_Display/static/PlayfairDisplay-Bold.ttf',
     'Playfair Display','normal','700'),
    (STATIC_FONTS_BASE/'Playfair_Display/static/PlayfairDisplay-Italic.ttf',
     'Playfair Display','italic','400'),
    (STATIC_FONTS_BASE/'Playfair_Display/static/PlayfairDisplay-BoldItalic.ttf',
     'Playfair Display','italic','700'),
    (STATIC_FONTS_BASE/'Inter/static/Inter_18pt-Regular.ttf',
     'Inter','normal','400'),
    (STATIC_FONTS_BASE/'Inter/static/Inter_18pt-Medium.ttf',
     'Inter','normal','500'),
    (STATIC_FONTS_BASE/'Inter/static/Inter_18pt-Bold.ttf',
     'Inter','normal','700'),
    (DS_FONTS/'SpaceMono-Regular.ttf',
     'Space Mono','normal','400'),
    (DS_FONTS/'SpaceMono-Bold.ttf',
     'Space Mono','normal','700'),
    (DS_FONTS/'TitanOne-Regular.ttf',
     'Titan One','normal','400'),
]
 
# ── MAP STYLE ────────────────────────────────────────────────────────────────
 
MAP_STYLE = [
    {"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#1B4436"}]},
    {"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#F9E4C5"},{"weight":2}]},
    {"featureType":"water","elementType":"geometry","stylers":[{"color":"#4A7FA5"}]},
    {"featureType":"landscape.natural","elementType":"geometry","stylers":[{"color":"#E8D9B8"}]},
    {"featureType":"landscape.man_made","elementType":"geometry","stylers":[{"color":"#F9E4C5"}]},
    {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#DDAD8A"},{"weight":1.5}]},
    {"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#EDD5B0"},{"weight":0.8}]},
    {"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},
    {"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},
    {"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#DDAD8A"},{"weight":0.8}]},
]
 
# ── FONT FUNCTIONS ───────────────────────────────────────────────────────────
 
def build_font_css():
    css = ""
    missing = []
    for path, family, style, weight in FONTS:
        p = Path(path)
        if not p.exists():
            missing.append(str(path))
            continue
        b64 = base64.b64encode(p.read_bytes()).decode('utf-8')
        css += f"""
@font-face {{
    font-family: '{family}';
    font-style: {style};
    font-weight: {weight};
    src: url('data:font/truetype;base64,{b64}') format('truetype');
    font-display: block;
}}
"""
    if missing:
        print("WARNING — Missing font files:")
        for m in missing:
            print(f"  {m}")
    return css
 
# ── MAP FUNCTIONS ────────────────────────────────────────────────────────────
 
def fetch_map_uri(cfg):
    style_params = ''.join(
        '&style=' + urllib.parse.quote(json.dumps(s)) for s in MAP_STYLE
    )
    marker_params = ''
    for m in cfg.get('markers', []):
        color = {'campground':'0x1B4436','gateway':'0xDDAD8A','trailhead':'0x88A33B'}.get(m['type'],'0x5B768C')
        marker_params += f'&markers=color:{color}|label:{m["label"][0]}|{m["lat"]},{m["lng"]}'
 
    url = (
        f'https://maps.googleapis.com/maps/api/staticmap'
        f'?center={cfg["center_lat"]},{cfg["center_lng"]}'
        f'&zoom={cfg["zoom"]}&size={cfg["size"]}&scale=2&maptype=terrain'
        f'{style_params}{marker_params}&key={MAPS_KEY}'
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return 'data:image/png;base64,' + base64.b64encode(r.content).decode()
 
 
def build_overlay(cfg):
    if 'bounds' not in cfg:
        return ''
    w, h = [int(v) for v in cfg['size'].split('x')]
    b = cfg['bounds']
    parts = []
    for m in cfg.get('markers', []):
        x = round((m['lng'] - b['west'])  / (b['east']  - b['west'])  * w)
        y = round((b['north'] - m['lat']) / (b['north'] - b['south']) * h)
        lbl, t = m['label'], m['type']
        if t == 'campground':
            parts += [
                f'<circle cx="{x}" cy="{y}" r="9" fill="#1B4436" stroke="#F9E4C5" stroke-width="1.5"/>',
                f'<text x="{x}" y="{y+22}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{lbl}</text>',
            ]
        elif t == 'gateway':
            parts += [
                f'<rect x="{x-8}" y="{y-8}" width="16" height="16" fill="#DDAD8A" stroke="#1B4436" stroke-width="1.5"/>',
                f'<text x="{x}" y="{y+24}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{lbl}</text>',
            ]
        elif t == 'trailhead':
            pts = f"{x},{y-10} {x-8},{y+6} {x+8},{y+6}"
            parts += [
                f'<polygon points="{pts}" fill="#88A33B" stroke="#F9E4C5" stroke-width="1.5"/>',
                f'<text x="{x}" y="{y+22}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{lbl}</text>',
            ]
    return '\n'.join(parts)
 
# ── GUIDE LOADING ────────────────────────────────────────────────────────────
 
def load_guide(guide_id):
    guide_dir = ROOT / 'guides' / guide_id
    with open(guide_dir / 'content.yaml') as f:
        content = yaml.safe_load(f)
 
    guide = content['guide']
 
    # Load prose for fixed sections (01–03, 05–08)
    for section in guide.get('sections', []):
        prose_file = guide_dir / 'prose' / f"{section['file']}.md"
        if prose_file.exists():
            section['prose_html'] = markdown.markdown(
                prose_file.read_text(), extensions=['extra', 'tables']
            )
        else:
            section['prose_html'] = ''
            print(f"  WARNING: Missing prose file: {section['file']}.md")
 
    # Load prose for experience zones (04a–04e)
    for zone in guide.get('zones', []):
        prose_file = guide_dir / 'prose' / f"{zone['file']}.md"
        if prose_file.exists():
            zone['prose_html'] = markdown.markdown(
                prose_file.read_text(), extensions=['extra', 'tables']
            )
        else:
            zone['prose_html'] = ''
            print(f"  WARNING: Missing zone prose file: {zone['file']}.md")
 
    # Load topo SVG
    topo_path = TEMPLATE_DIR / 'assets' / 'topo-lines.svg'
    content['topo_svg'] = topo_path.read_text() if topo_path.exists() else ''
 
    # Load series from project-level series.yaml (shared across all guides)
    series_path = ROOT / 'series.yaml'
    series = []
    if series_path.exists():
        with open(series_path) as f:
            series_data = yaml.safe_load(f)
            # Exclude the current guide from the series list on its own back cover
            series = [
                g for g in series_data.get('series', [])
                if g.get('id') != guide_id
            ]
 
    return guide, series
 
# ── BUILD ────────────────────────────────────────────────────────────────────
 
def font_test(font_css):
    """Render a single font test page to verify all typefaces."""
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
{font_css}
body {{ background:#F9E4C5; padding:40px; margin:0; }}
.r {{ margin-bottom:20px; border-bottom:1px solid #EDE0D4; padding-bottom:20px; }}
.label {{ font-family:'Space Mono'; font-size:9px; text-transform:uppercase;
          letter-spacing:0.15em; color:#5B768C; margin-bottom:6px; }}
</style></head><body>
<div class="r"><div class="label">Playfair Display 700 — H1</div>
<div style="font-family:'Playfair Display';font-size:34px;font-weight:700;color:#1B4436">
  Hurricane Ridge</div></div>
<div class="r"><div class="label">Playfair Display 400 Italic — Subhead</div>
<div style="font-family:'Playfair Display';font-size:20px;font-style:italic;color:#5B768C">
  Where the road ends and the view begins.</div></div>
<div class="r"><div class="label">Inter 400 — Body</div>
<div style="font-family:'Inter';font-size:16px;line-height:1.7;color:#1B4436;max-width:60ch">
  The road into the park from Port Angeles climbs fast. By the time you clear 
  the treeline, you're above the clouds.</div></div>
<div class="r"><div class="label">Space Mono 400 — Utility Labels</div>
<div style="font-family:'Space Mono';font-size:10px;text-transform:uppercase;
            letter-spacing:0.15em;color:#5B768C">
  RESERVABLE · FIRST-COME · 35FT MAX · FULL HOOKUPS</div></div>
<div class="r"><div class="label">Titan One 400 — Brand Mark Only</div>
<div style="font-family:'Titan One';font-size:32px;color:#1B4436;letter-spacing:2px">
  ADV NTR ROAD</div></div>
</body></html>"""
 
    OUTPUT_DIR.mkdir(exist_ok=True)
    test_path = OUTPUT_DIR / 'font-test.pdf'
    HTML(string=html).write_pdf(str(test_path))
    print(f"Font test: {test_path}")
    print("Open and visually verify all 5 typefaces before proceeding.")
 
 
def build_pdf(guide_id, skip_maps=False):
    print(f"\nBuilding: {guide_id}")
    guide, series = load_guide(guide_id)
    font_css = build_font_css()
 
    # Fetch maps — iterates over all maps defined in content.yaml
    maps = guide.get('maps', {})
    if not skip_maps and MAPS_KEY:
        for key, cfg in maps.items():
            print(f"  Map: {key}")
            try:
                cfg['image_uri']   = fetch_map_uri(cfg)
                cfg['overlay_svg'] = build_overlay(cfg)
            except Exception as e:
                print(f"  WARNING: Map '{key}' failed: {e}")
                cfg['image_uri']   = ''
                cfg['overlay_svg'] = ''
    else:
        for cfg in maps.values():
            cfg['image_uri']   = ''
            cfg['overlay_svg'] = ''
        if skip_maps:
            print("  Maps skipped (--no-maps)")
        else:
            print("  WARNING: GOOGLE_MAPS_API_KEY not set — maps skipped")
 
    # Render template — pass guide, series, and font_css
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    env.globals['topo_svg'] = guide.get('topo_svg', '')
    template = env.get_template('guide_template.html')
    html_out = template.render(guide=guide, series=series, font_css=font_css)
 
    # Write output
    OUTPUT_DIR.mkdir(exist_ok=True)
 
    html_path = OUTPUT_DIR / f"{guide_id}.html"
    html_path.write_text(html_out, encoding='utf-8')
    print(f"  HTML → {html_path}")
 
    pdf_path = OUTPUT_DIR / f"{guide_id}-2026.pdf"
    HTML(string=html_out, base_url=str(ROOT)).write_pdf(str(pdf_path))
    print(f"  PDF  → {pdf_path}")
    print("Done.\n")
 
 
# ── ENTRY POINT ──────────────────────────────────────────────────────────────
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ADVNTR Road Guide PDF Builder')
    parser.add_argument('--guide',      required=True, help='Guide ID, e.g. olympic-np')
    parser.add_argument('--no-maps',    action='store_true', help='Skip Google Maps API calls')
    parser.add_argument('--font-test',  action='store_true', help='Render font test page only')
    args = parser.parse_args()
 
    font_css = build_font_css()
    if args.font_test:
        font_test(font_css)
    else:
        build_pdf(args.guide, skip_maps=args.no_maps)
```
 
---
 
## 11. BUILD ORDER — STEP BY STEP
 
Follow this sequence exactly. Do not skip ahead.
 
### Phase A — Environment
 
```bash
# 1. Create project directory
mkdir advntr-road-guides && cd advntr-road-guides
 
# 2. Copy design_system from zip into project root
# (design_system/ directory must sit at project root)
 
# 3. Install dependencies
pip install weasyprint jinja2 pyyaml markdown python-dotenv requests
 
# 4. Create .env
echo "GOOGLE_MAPS_API_KEY=your_key_here" > .env
 
# 5. Create directory structure
mkdir -p template/styles template/assets/icons
mkdir -p guides/olympic-np/prose guides/olympic-np/assets
mkdir output
```
 
### Phase B — Token layer
 
```bash
# 6. Create template/styles/tokens.css
#    Paste complete CSS from Section 2 of this spec.
#    Verify --color-buff is #DDAD8A (warm tan).
 
# 7. Run font embed test
python build.py --guide olympic-np --font-test
#    Open output/font-test.pdf
#    STOP if any typeface renders as system font (serif/sans fallback)
#    If fonts are wrong, verify font file paths in FONTS array in build.py
```
 
### Phase C — Print layout
 
```bash
# 8. Create template/styles/layout.css
#    @page, @page cover, @page back-cover rules from Section 6.1
 
# 9. Create template/styles/print.css
#    All page-break rules from Section 6.10
 
# 10. Create template/styles/components.css
#     All components from Section 6.2 through 6.9
 
# 11. Create template/assets/topo-lines.svg
#     Topo line SVG from Section 6.9
```
 
### Phase D — Template
 
```bash
# 12. Create template/guide_template.html
#     Full Jinja2 template from Section 7
#     Inline all CSS (paste tokens + layout + components + print into <style> tag)
 
# 13. Create guides/olympic-np/content.yaml
#     Full schema from Section 8
 
# 14. Create 9 prose .md files in guides/olympic-np/prose/
#     01-orientation.md through 09-before-you-go.md
```
 
### Phase E — First build (no maps)
 
```bash
# 15. Run without maps to verify layout
python build.py --guide olympic-np --no-maps
 
# 16. Open output/olympic-np.html in browser
#     Check: section headers, campground cards, badges, pull quotes, fonts, colors
 
# 17. Open output/olympic-np-2026.pdf
#     Check: page breaks, no orphaned headers, no split cards, topo lines on cover
```
 
### Phase F — Maps
 
```bash
# 18. Confirm GOOGLE_MAPS_API_KEY is set in .env
 
# 19. Run with maps
python build.py --guide olympic-np
 
# 20. Verify maps render with correct colors (Champagne landscape, Buff roads, Brunswick text)
# 21. Verify SVG overlays are registered — markers sit on correct locations
# 22. Verify Space Mono labels on all markers
```
 
### Phase G — QA and iterate
 
```bash
# 23. Run full QA checklist (Section 13)
# 24. Fix any CSS issues — re-run build after each change
# 25. Final PDF — run build.py one last time on clean content
```
 
---
 
## 12. ERROR RECOVERY GUIDE
 
### Font renders as system default (serif or sans-serif fallback)
 
**Cause:** Base64 encoding failed, font file not found, or font-family name mismatch.
 
**Fix:**
1. Run `python build.py --guide olympic-np --font-test`
2. Check console for "WARNING — Missing font files" messages
3. Verify path strings in FONTS array exactly match actual files on disk
4. Verify `font-family` name in @font-face matches exactly what CSS uses
   (`'Playfair Display'` not `'Playfair-Display'`)
### WeasyPrint OS/2 table subsetting error on variable font
 
**Error text:** `WARNING: Failed to subset font / OS/2 table`
 
**Fix:** Switch from variable TTF to static TTF. In FONTS array, change:
```python
# FROM (variable):
DS_FONTS/'PlayfairDisplay-Variable.ttf'
# TO (static):
STATIC_FONTS_BASE/'Playfair_Display/static/PlayfairDisplay-Bold.ttf'
```
 
### Cards split across pages
 
**Cause:** Missing one of the two required page-break properties.
 
**Fix:** Ensure both are present on every container that must not split:
```css
.camp-card {
    page-break-inside: avoid;   /* Required */
    break-inside: avoid;        /* Also required — WeasyPrint needs both */
}
```
 
### Map image is blank or missing
 
**Cause:** API key invalid, quota exceeded, or URL too long (style params).
 
**Fix:**
1. Test API key directly: `curl "https://maps.googleapis.com/maps/api/staticmap?center=47.86,-123.93&zoom=10&size=400x300&key=YOUR_KEY"` — should return a PNG
2. If URL too long: reduce MAP_STYLE to 4–5 entries, or use a style ID from Google Cloud Console
3. Build with `--no-maps` to isolate map issues from layout issues
### Champagne background not appearing in PDF
 
**Cause:** WeasyPrint requires explicit `background` on `@page` rule.
 
**Fix:**
```css
@page {
    background: #F9E4C5;   /* Must be literal hex, not var() */
}
```
WeasyPrint does not resolve CSS custom properties inside `@page` rules in all versions.
 
### Topo SVG not appearing
 
**Cause:** SVG `position:absolute` requires parent to have `position:relative`.
 
**Fix:**
```html
<div style="position:relative; overflow:hidden; ...">
  <!-- topo SVG here with position:absolute -->
</div>
```
 
### Jinja2 template error on `section.split('x')`
 
**Cause:** YAML value parsed as integer not string.
 
**Fix:** Quote the size value in content.yaml:
```yaml
size: "760x440"   # Quotes required — not 760x440
```
 
---
 
## 13. QA CHECKLIST
 
Run before every deployment. Every item must pass.
 
### Typography
- [ ] Cover title: Playfair Display 700, ~42px, Champagne on Brunswick
- [ ] Section H2: Playfair Display 700, ~26px, Brunswick
- [ ] Subheads: Playfair Display 400 italic, ~20px, Payne's Gray
- [ ] Body prose: Inter 400, 16px, line-height 1.7, Brunswick
- [ ] ALL Space Mono labels: uppercase, letter-spacing 0.15em, Payne's Gray
- [ ] No Space Mono in sentence case anywhere
- [ ] Pull quotes: Playfair italic, Buff left border rule, 20px
### Colors
- [ ] Page background: Champagne #F9E4C5 (not white)
- [ ] All headings: Brunswick #1B4436
- [ ] Section header top rule: Buff #DDAD8A
- [ ] Card borders: #EDE0D4
- [ ] Consensus/verified badges: Moss Green #88A33B text, #EFF5E5 bg
- [ ] Editorial/urgency badges: warm tan accent text, #FAF5EE bg
- [ ] Cover background: Brunswick #1B4436
- [ ] Back cover background: Brunswick #1B4436
### Campground Cards (every card, no exceptions)
- [ ] Reservation method and platform listed
- [ ] Hookup status listed (none / electric / full)
- [ ] Max vehicle length listed
- [ ] Pet policy listed (allowed yes/no + restrictions)
- [ ] Verified date listed
- [ ] Editorial note present (2–4 sentences)
- [ ] All required badge variants render correctly
### Maps
- [ ] All 3–4 maps present (orientation, campground reference, coastal, gateway)
- [ ] Map base image renders (not blank)
- [ ] All markers visible and approximately correct position
- [ ] Marker types visually distinct (circle/square/triangle)
- [ ] All marker labels in Space Mono uppercase
- [ ] No decorative cartographic flourishes
### Page Layout
- [ ] Cover: full bleed, no margins
- [ ] TOC: editorial wordmark present, section list complete
- [ ] Each section starts on new page
- [ ] No card or block splits across a page break
- [ ] No orphaned section headers at bottom of page
- [ ] Back cover: full bleed Brunswick, stacked mark centered
### Brand
- [ ] Stacked mark (ADV/NTR/ROAD) on cover and back cover
- [ ] Editorial wordmark (ADVNTR Road) on TOC and interior
- [ ] Titan One used ONLY for stacked mark — not anywhere else
- [ ] "Tools don't have opinions — we do." NOT in guide prose
- [ ] No source names in published content
---
 
## 14. NEW GUIDE CHECKLIST
 
Every guide after Olympic NP follows this sequence exactly.
The destination.md → Gemini step replaces all manual YAML and prose authoring.
 
### Phase 0 — Research
 
```
□ Complete destination.md using ADVNTR_Road_Destination_Template.md
    □ All campground data verified against NPS.gov or Recreation.gov
    □ Fees verified against official source for current year
    □ Permit info verified
    □ Part 5 (Research Quality Flags) filled out honestly
□ Feed destination.md to Gemini with the ADVNTR Road extraction prompt
□ Review Gemini output:
    □ content.yaml — check all REQUIRED fields are populated
    □ Prose .md files — verify voice matches ADVNTR Road register
    □ Flag any UNKNOWN fields for manual verification before build
```
 
### Phase 1 — File setup
 
```
□ Create guides/[destination-id]/ directory
□ Place Gemini-generated content.yaml at guides/[destination-id]/content.yaml
□ Place Gemini-generated prose files at guides/[destination-id]/prose/
    □ 01-orientation.md           [REQUIRED]
    □ 02-before-you-arrive.md     [REQUIRED]
    □ 03-where-to-sleep.md        [REQUIRED]
    □ 04a-[zone-slug].md          [REQUIRED — one per zone]
    □ 04b-[zone-slug].md          [CONDITIONAL]
    □ 04c through 04e             [CONDITIONAL]
    □ 05-what-to-do.md            [REQUIRED]
    □ 06-eat-resupply.md          [REQUIRED]
    □ 07-field-notes.md           [REQUIRED]
    □ 08-before-you-leave.md      [REQUIRED]
□ Add destination to series.yaml at project root (for back cover series block)
□ Source or commission illustrated cover map → guides/[id]/assets/cover-map.jpg
    (omit cover_map field from content.yaml if not ready — cover renders without it)
```
 
### Phase 2 — Build and verify
 
```
□ python build.py --guide [id] --font-test   (verify fonts first if new environment)
□ python build.py --guide [id] --no-maps     (layout check — faster, no API calls)
□ Open output/[id].html in browser
    □ Section order correct: 01 → 02 → 03 → 04a…04x → 05 → 06 → 07 → 08
    □ Zone count matches destination (1–5 zones rendered)
    □ Conditional blocks present only where data exists:
        □ Gateway town cards — only if gateway_towns[] populated
        □ Zone highlights sidebars — only if zone.highlights[] populated
        □ Business listing cards — only if businesses[] populated
        □ Fees block — only if fees{} populated
        □ Permits block — only if permits{} populated
        □ Checklist — only if checklist[] populated
        □ Resource links — only if resources[] populated
        □ Series block on back cover — only if series.yaml exists
□ python build.py --guide [id]               (full build with maps)
□ Open output/[id]-2026.pdf
    □ All maps render (not blank)
    □ No page break issues — no split cards, no orphaned headers
```
 
### Phase 3 — QA
 
```
□ Run full QA checklist (Section 13)
□ Campground cards — every card verified:
    □ Reservation method and platform
    □ Hookup status (none / electric / full)
    □ Max vehicle length
    □ Pet policy
    □ Verified date and source
    □ Editorial note present (2–4 sentences)
□ No source names anywhere in published prose
□ Buff color #DDAD8A on all accent elements (not #DDADBA)
□ Page background Champagne #F9E4C5 throughout (not white)
```
 
### Phase 4 — Deployment
 
```
□ Upload output/[id]-2026.pdf to Gumroad ($15)
□ Configure Gumroad thank-you page:
    □ Beehiiv subscribe URL with UTM parameters (?utm_source=gumroad&utm_medium=purchase&utm_campaign=[id])
□ Publish Beehiiv post at road.advntr.io announcing the guide
□ Activate UTM-tagged affiliate links in Gumroad product description
□ Do NOT contact featured businesses until 4–8 weeks of documented traffic
```
 
---
 
*ADVNTR Road Build Spec FINAL · June 2026 · road.advntr.io*
*Buff = #DDAD8A · Brunswick = #1B4436 · Champagne = #F9E4C5*