#!/usr/bin/env python3
"""
ADVNTR Road Guide PDF Builder

Usage:
  python build.py --guide olympic-np
  python build.py --guide olympic-np --no-maps
  python build.py --guide olympic-np --font-test
"""

import argparse
import base64
import json
import os
import urllib.parse
from pathlib import Path

import markdown
import requests
import yaml
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()

ROOT = Path(__file__).parent
DESIGN_SYSTEM = ROOT / "design_system"
DS_FONTS = DESIGN_SYSTEM / "assets" / "fonts"
ALT_FONTS_BASE = DESIGN_SYSTEM / "fonts"
STATIC_FONTS_BASE = DESIGN_SYSTEM / "uploads" / "Inter,Playfair_Display,Space_Mono,Titan_One"
TEMPLATE_DIR = ROOT / "template"
OUTPUT_DIR = ROOT / "output"
MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

FONTS = [
    (
        [
            STATIC_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Regular.ttf",
            ALT_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Regular.ttf",
        ],
        "Playfair Display",
        "normal",
        "400",
    ),
    (
        [
            STATIC_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Bold.ttf",
            ALT_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Bold.ttf",
        ],
        "Playfair Display",
        "normal",
        "700",
    ),
    (
        [
            STATIC_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Italic.ttf",
            ALT_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-Italic.ttf",
        ],
        "Playfair Display",
        "italic",
        "400",
    ),
    (
        [
            STATIC_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-BoldItalic.ttf",
            ALT_FONTS_BASE / "Playfair_Display/static/PlayfairDisplay-BoldItalic.ttf",
        ],
        "Playfair Display",
        "italic",
        "700",
    ),
    (
        [
            STATIC_FONTS_BASE / "Inter/static/Inter_18pt-Regular.ttf",
            ALT_FONTS_BASE / "Inter/static/Inter_18pt-Regular.ttf",
        ],
        "Inter",
        "normal",
        "400",
    ),
    (
        [
            STATIC_FONTS_BASE / "Inter/static/Inter_18pt-Medium.ttf",
            ALT_FONTS_BASE / "Inter/static/Inter_18pt-Medium.ttf",
        ],
        "Inter",
        "normal",
        "500",
    ),
    (
        [
            STATIC_FONTS_BASE / "Inter/static/Inter_18pt-Bold.ttf",
            ALT_FONTS_BASE / "Inter/static/Inter_18pt-Bold.ttf",
        ],
        "Inter",
        "normal",
        "700",
    ),
    (
        [
            DS_FONTS / "SpaceMono-Regular.ttf",
            ALT_FONTS_BASE / "Space_Mono/SpaceMono-Regular.ttf",
        ],
        "Space Mono",
        "normal",
        "400",
    ),
    (
        [
            DS_FONTS / "SpaceMono-Bold.ttf",
            ALT_FONTS_BASE / "Space_Mono/SpaceMono-Bold.ttf",
        ],
        "Space Mono",
        "normal",
        "700",
    ),
    (
        [
            DS_FONTS / "TitanOne-Regular.ttf",
            ALT_FONTS_BASE / "Titan_One/TitanOne-Regular.ttf",
        ],
        "Titan One",
        "normal",
        "400",
    ),
]

MAP_STYLE = [
    {"featureType": "all", "elementType": "labels.text.fill", "stylers": [{"color": "#1B4436"}]},
    {"featureType": "all", "elementType": "labels.text.stroke", "stylers": [{"color": "#F9E4C5"}, {"weight": 2}]},
    {"featureType": "water", "elementType": "geometry", "stylers": [{"color": "#4A7FA5"}]},
    {"featureType": "landscape.natural", "elementType": "geometry", "stylers": [{"color": "#E8D9B8"}]},
    {"featureType": "landscape.man_made", "elementType": "geometry", "stylers": [{"color": "#F9E4C5"}]},
    {"featureType": "road.highway", "elementType": "geometry", "stylers": [{"color": "#DDAD8A"}, {"weight": 1.5}]},
    {"featureType": "road.local", "elementType": "geometry", "stylers": [{"color": "#EDD5B0"}, {"weight": 0.8}]},
    {"featureType": "poi", "elementType": "all", "stylers": [{"visibility": "off"}]},
    {"featureType": "transit", "elementType": "all", "stylers": [{"visibility": "off"}]},
    {"featureType": "administrative", "elementType": "geometry.stroke", "stylers": [{"color": "#DDAD8A"}, {"weight": 0.8}]},
]


def build_font_css():
    css = []
    missing = []
    for paths, family, style, weight in FONTS:
        path = next((candidate for candidate in paths if candidate.exists()), None)
        if path is None:
            missing.append(paths[0])
            continue
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        css.append(
            f"""
@font-face {{
  font-family: '{family}';
  font-style: {style};
  font-weight: {weight};
  src: url('data:font/truetype;base64,{encoded}') format('truetype');
  font-display: block;
}}
"""
        )
    if missing:
        print("WARNING - Missing font files. Copy design_system into the project root for final typography:")
        for path in missing:
            print(f"  {path}")
    return "\n".join(css)


def read_css():
    files = [
        TEMPLATE_DIR / "styles" / "tokens.css",
        TEMPLATE_DIR / "styles" / "layout.css",
        TEMPLATE_DIR / "styles" / "components.css",
        TEMPLATE_DIR / "styles" / "print.css",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def build_map_url(cfg):
    style_params = "".join("&style=" + urllib.parse.quote(json.dumps(style)) for style in MAP_STYLE)
    marker_params = ""
    marker_colors = {"campground": "0x1B4436", "gateway": "0xDDAD8A", "trailhead": "0x88A33B"}
    for marker in cfg.get("markers", []):
        color = marker_colors.get(marker["type"], "0x5B768C")
        label = marker["label"][0]
        marker_params += f'&markers=color:{color}|label:{label}|{marker["lat"]},{marker["lng"]}'
    return (
        "https://maps.googleapis.com/maps/api/staticmap"
        f'?center={cfg["center_lat"]},{cfg["center_lng"]}'
        f'&zoom={cfg["zoom"]}&size={cfg["size"]}&scale=2&maptype=terrain'
        f"{style_params}{marker_params}&key={MAPS_KEY}"
    )


def fetch_map_uri(cfg):
    response = requests.get(build_map_url(cfg), timeout=20)
    response.raise_for_status()
    return "data:image/png;base64," + base64.b64encode(response.content).decode("utf-8")


def coord_to_pixel(lat, lng, bounds, img_w, img_h):
    x = (lng - bounds["west"]) / (bounds["east"] - bounds["west"]) * img_w
    y = (bounds["north"] - lat) / (bounds["north"] - bounds["south"]) * img_h
    return round(x), round(y)


def build_overlay_svg(cfg):
    if "bounds" not in cfg:
        return ""
    width, height = [int(value) for value in cfg["size"].split("x")]
    parts = []
    for marker in cfg.get("markers", []):
        x, y = coord_to_pixel(marker["lat"], marker["lng"], cfg["bounds"], width, height)
        label = marker["label"]
        marker_type = marker["type"]
        if marker_type == "campground":
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="9" fill="#1B4436" stroke="#F9E4C5" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y + 22}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
        elif marker_type == "gateway":
            parts.append(
                f'<rect x="{x - 8}" y="{y - 8}" width="16" height="16" fill="#DDAD8A" stroke="#1B4436" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y + 24}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
        elif marker_type == "trailhead":
            points = f"{x},{y - 10} {x - 8},{y + 6} {x + 8},{y + 6}"
            parts.append(
                f'<polygon points="{points}" fill="#88A33B" stroke="#F9E4C5" stroke-width="1.5"/>'
                f'<text x="{x}" y="{y + 22}" text-anchor="middle" font-family="Space Mono,monospace" font-size="8" letter-spacing="0.8" fill="#1B4436">{label}</text>'
            )
    return "\n".join(parts)


def load_guide(guide_id):
    guide_dir = ROOT / "guides" / guide_id
    content_path = guide_dir / "content.yaml"
    if not content_path.exists():
        raise FileNotFoundError(f"Guide content not found: {content_path}")

    content = yaml.safe_load(content_path.read_text(encoding="utf-8"))
    guide = content["guide"]
    cover_map = guide.get("cover_map")
    if cover_map:
        guide["cover_map_uri"] = str((guide_dir / cover_map).resolve())
    else:
        guide["cover_map_uri"] = ""

    for section in guide.get("sections", []):
        prose_file = guide_dir / "prose" / f"{section['file']}.md"
        if prose_file.exists():
            section["prose_html"] = markdown.markdown(
                prose_file.read_text(encoding="utf-8"),
                extensions=["extra", "tables", "smarty"],
            )
        else:
            section["prose_html"] = ""
    return guide


def render_font_test(font_css, css):
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>{font_css}{css}</style></head>
<body style="padding:40px">
  <div class="section-header">
    <div class="section-header__eyebrow">FONT TEST</div>
    <h1 class="section-header__title" style="font-size:34px">Hurricane Ridge</h1>
    <p class="section-header__subhead">Where the road ends and the view begins.</p>
  </div>
  <p>The road into the park from Port Angeles climbs fast. This line should render in Inter.</p>
  <p style="font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:0.15em;color:var(--text-secondary)">RESERVABLE · FIRST-COME · 35FT MAX · FULL HOOKUPS</p>
  <p style="font-family:var(--font-brand);font-size:32px;letter-spacing:2px">ADV NTR ROAD</p>
</body></html>"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "font-test.pdf"
    write_pdf(html, path)
    print(f"Font test written to {path}")


def write_pdf(html, pdf_path):
    try:
        from weasyprint import HTML

        HTML(string=html, base_url=str(ROOT)).write_pdf(str(pdf_path))
        return "weasyprint"
    except Exception as exc:
        print(f"WARNING - WeasyPrint PDF render unavailable: {exc}")
        try:
            return write_pdf_with_chrome(html, pdf_path)
        except Exception as chrome_exc:
            print(f"WARNING - Chrome PDF fallback unavailable: {chrome_exc}")
            return None


def write_pdf_with_chrome(html, pdf_path):
    if not CHROME.exists():
        raise RuntimeError("No PDF renderer available. Install WeasyPrint native dependencies or Google Chrome.")

    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)
    profile_dir = Path(tempfile.mkdtemp(prefix="advntr-chrome-"))

    try:
        subprocess.run(
            [
                str(CHROME),
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--no-first-run",
                "--disable-extensions",
                f"--user-data-dir={profile_dir}",
                f"--print-to-pdf={pdf_path}",
                f"file://{tmp_path}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
        import shutil

        shutil.rmtree(profile_dir, ignore_errors=True)
    return "chrome"


def build(guide_id, no_maps=False):
    guide = load_guide(guide_id)
    font_css = build_font_css()
    css = read_css()

    maps = guide.get("maps", {})
    if no_maps or not MAPS_KEY:
        reason = "--no-maps" if no_maps else "GOOGLE_MAPS_API_KEY is not set"
        print(f"Maps skipped ({reason}).")
        for cfg in maps.values():
            cfg["image_uri"] = ""
            cfg["overlay_svg"] = build_overlay_svg(cfg)
    else:
        for name, cfg in maps.items():
            print(f"Fetching map: {name}")
            try:
                cfg["image_uri"] = fetch_map_uri(cfg)
                cfg["overlay_svg"] = build_overlay_svg(cfg)
            except Exception as exc:
                print(f"WARNING - Map '{name}' failed: {exc}")
                cfg["image_uri"] = ""
                cfg["overlay_svg"] = build_overlay_svg(cfg)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("guide_template.html")
    html = template.render(guide=guide, font_css=font_css, css=css)

    OUTPUT_DIR.mkdir(exist_ok=True)
    html_path = OUTPUT_DIR / f"{guide_id}.html"
    pdf_path = OUTPUT_DIR / f"{guide_id}-2026.pdf"
    html_path.write_text(html, encoding="utf-8")
    renderer = write_pdf(html, pdf_path)
    print(f"HTML written to {html_path}")
    if renderer:
        print(f"PDF written to {pdf_path} ({renderer})")
    else:
        print("PDF not written. HTML output is available for layout review.")


def main():
    parser = argparse.ArgumentParser(description="Build an ADVNTR Road guide PDF.")
    parser.add_argument("--guide", required=True)
    parser.add_argument("--no-maps", action="store_true")
    parser.add_argument("--font-test", action="store_true")
    args = parser.parse_args()

    if args.font_test:
        font_css = build_font_css()
        css = read_css()
        render_font_test(font_css, css)
    else:
        build(args.guide, no_maps=args.no_maps)


if __name__ == "__main__":
    main()
