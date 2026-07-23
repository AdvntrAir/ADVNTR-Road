#!/usr/bin/env python3
"""
ADVNTR Road Guide PDF Builder — v2.0 (schema 3.0)

Usage:
  python build.py --guide crater-lake-np --no-maps
  python build.py --guide olympic-np --no-maps
  python build.py --guide olympic-np --font-test
"""

import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
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
LOGO_DIR = TEMPLATE_DIR / "assets" / "logos"
MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
NPS_API_KEY = os.getenv("NPS_API_KEY", "DEMO_KEY")
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

# NPS park codes by guide slug
PARK_CODES = {
    "crater-lake-np": "crla",
    "olympic-np": "olym",
    "mount-rainier-np": "mora",
    "north-cascades": "noca",
    "oregon-coast": None,
}

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
            STATIC_FONTS_BASE / "Inter/static/Inter_18pt-Black.ttf",
            ALT_FONTS_BASE / "Inter/static/Inter_18pt-Black.ttf",
        ],
        "Inter",
        "normal",
        "900",
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
    (
        [
            DS_FONTS / "MeowScript-Regular.ttf",
            ALT_FONTS_BASE / "Meow_Script/MeowScript-Regular.ttf",
        ],
        "Meow Script",
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

# Schema 3.0 section metadata — maps display_number to display properties
SECTION_META_V3 = {
    "01": {
        "title": "Orientation",
        "eyebrow": "Park Overview",
        "visual_word": "ORIENT",
        "visual_theme": "photo",
        "visual_label": "Field Orientation",
        "section_type": "orientation",
        "subhead": "",
    },
    "02": {
        "title": "Before You Arrive",
        "eyebrow": "Pre-Trip Planning",
        "visual_word": "PLAN",
        "visual_theme": "cream",
        "visual_label": "Pre-Trip Brief",
        "section_type": "before-you-arrive",
        "subhead": "",
    },
    "02B": {
        "title": "Itineraries",
        "eyebrow": "Day Plans",
        "visual_word": "ROUTE",
        "visual_theme": "dark",
        "visual_label": "Itinerary Guide",
        "section_type": "itineraries",
        "subhead": "",
    },
    "03": {
        "title": "Where to Sleep",
        "eyebrow": "Camping & Lodging",
        "visual_word": "CAMP",
        "visual_theme": "blue",
        "visual_label": "Lodging Guide",
        "section_type": "where-to-sleep",
        "subhead": "",
    },
    "05": {
        "title": "What To Do",
        "eyebrow": "Activities",
        "visual_word": "DO",
        "visual_theme": "dark",
        "visual_label": "Activity Guide",
        "section_type": "what-to-do",
        "subhead": "",
    },
    "06": {
        "title": "Eat & Resupply",
        "eyebrow": "Food & Supplies",
        "visual_word": "EAT",
        "visual_theme": "cream",
        "visual_label": "Dining & Resupply",
        "section_type": "eat-resupply",
        "subhead": "",
    },
    "07": {
        "title": "Field Notes",
        "eyebrow": "Practical Details",
        "visual_word": "NOTES",
        "visual_theme": "dark",
        "visual_label": "Field Notes",
        "section_type": "field-notes",
        "subhead": "",
    },
    "08": {
        "title": "Before You Leave",
        "eyebrow": "Departure Brief",
        "visual_word": "LEAVE",
        "visual_theme": "cream",
        "visual_label": "Departure Brief",
        "section_type": "before-you-leave",
        "subhead": "",
    },
}


# ── Font & CSS helpers ────────────────────────────────────────────────────────

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
        print("WARNING — Missing font files:")
        for path in missing:
            print(f"  {path}")
    return "\n".join(css)


def read_css():
    files = [
        TEMPLATE_DIR / "styles" / "tokens.css",
        TEMPLATE_DIR / "styles" / "layout.css",
        TEMPLATE_DIR / "styles" / "components.css",
        TEMPLATE_DIR / "styles" / "print.css",
        TEMPLATE_DIR / "styles" / "components-v2.css",
    ]
    parts = []
    for path in files:
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
        else:
            print(f"WARNING: CSS file missing: {path}")
    return "\n".join(parts)


# ── Map helpers ───────────────────────────────────────────────────────────────

def build_map_url(cfg):
    style_params = "".join("&style=" + urllib.parse.quote(json.dumps(style)) for style in MAP_STYLE)
    return (
        "https://maps.googleapis.com/maps/api/staticmap"
        f'?center={cfg["center_lat"]},{cfg["center_lng"]}'
        f'&zoom={cfg["zoom"]}&size={cfg["size"]}&scale=2&maptype=terrain'
        f"{style_params}&key={MAPS_KEY}"
    )


def fetch_map_image(cfg, cache_path):
    response = requests.get(build_map_url(cfg), timeout=20)
    response.raise_for_status()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(response.content)
    return response.content


def map_image_uri(png_bytes, web_preview, rel_path):
    if web_preview:
        return str(rel_path)
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")


def coord_to_pixel(lat, lng, bounds, img_w, img_h):
    x = (lng - bounds["west"]) / (bounds["east"] - bounds["west"]) * img_w
    y = (bounds["north"] - lat) / (bounds["north"] - bounds["south"]) * img_h
    return round(x), round(y)


def build_overlay_svg(cfg):
    if "bounds" not in cfg:
        return ""
    width, height = [int(value) for value in cfg["size"].split("x")]
    parts = []

    def label_text(x, y, label, color, dx=0, dy=24, anchor="middle"):
        lx = x + dx
        ly = y + dy
        return (
            f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" font-family="Space Mono,monospace" '
            f'font-size="8.5" font-weight="700" letter-spacing="0.35" fill="none" '
            f'stroke="#F9E4C5" stroke-width="2.2" stroke-linejoin="round">{label}</text>'
            f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" font-family="Space Mono,monospace" '
            f'font-size="8.5" font-weight="700" letter-spacing="0.35" fill="{color}">{label}</text>'
        )

    for marker in cfg.get("markers", []):
        x, y = coord_to_pixel(marker["lat"], marker["lng"], cfg["bounds"], width, height)
        label = marker["label"]
        marker_type = marker["type"]
        dx = marker.get("dx", 0)
        dy = marker.get("dy", 24)
        anchor = marker.get("anchor", "middle")
        if marker_type == "campground":
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="9" fill="#1B4436" stroke="#F9E4C5" stroke-width="1.5"/>'
                + label_text(x, y, label, "#1B4436", dx, dy, anchor)
            )
        elif marker_type == "gateway":
            parts.append(
                f'<rect x="{x - 8}" y="{y - 8}" width="16" height="16" fill="#DDAD8A" stroke="#1B4436" stroke-width="1.5"/>'
                + label_text(x, y, label, "#1B4436", dx, dy, anchor)
            )
        elif marker_type == "trailhead":
            points = f"{x},{y - 10} {x - 8},{y + 6} {x + 8},{y + 6}"
            parts.append(
                f'<polygon points="{points}" fill="#88A33B" stroke="#F9E4C5" stroke-width="1.5"/>'
                + label_text(x, y, label, "#1B4436", dx, dy, anchor)
            )
        elif marker_type == "closure":
            parts.append(
                f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" transform="rotate(45 {x} {y})" fill="#8C3D2D" stroke="#F9E4C5" stroke-width="1.5"/>'
                + label_text(x, y, label, "#8C3D2D", dx, dy, anchor)
            )
        elif marker_type == "viewpoint":
            points = f"{x},{y - 9} {x + 9},{y} {x},{y + 9} {x - 9},{y}"
            parts.append(
                f'<polygon points="{points}" fill="#4A7FA5" stroke="#F9E4C5" stroke-width="1.5"/>'
                + label_text(x, y, label, "#4A7FA5", dx, dy, anchor)
            )
        else:
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#5B768C" stroke-width="2.5"/>'
                + label_text(x, y, label, "#5B768C", dx, dy, anchor)
            )
    return "\n".join(parts)


# ── Prose helpers ─────────────────────────────────────────────────────────────

def linkify_plain_urls(text):
    def replace(match):
        url = match.group(0)
        trailing = ""
        while url[-1] in ".,;)":
            trailing = url[-1] + trailing
            url = url[:-1]
        return f"[{url}]({url}){trailing}"

    return re.sub(r"(?<!href=\")(?<!\]\()https?://[^\s<]+", replace, text)


def format_prose_markdown(text):
    def replace_resource_link(match):
        label = match.group(1).strip()
        url = match.group(2).strip()
        button_label = {
            "URL": "Open Resource",
            "Website": "Website",
            "Booking URL": "Book",
        }.get(label, label)
        return (
            f'\n<p class="resource-action-line">'
            f'<a class="link-pill link-pill--resource" href="{html.escape(url, quote=True)}">'
            f'{html.escape(button_label)}</a></p>\n'
        )

    text = re.sub(
        r"(?m)^-\s+\*\*(URL|Website|Booking URL):\*\*\s+(https?://[^\s]+)\s*$",
        replace_resource_link,
        text,
    )
    text = linkify_plain_urls(text)

    def replace_note(match):
        body = html.escape(match.group(1).strip(), quote=False)
        return (
            '\n<aside class="advntr-road-note">'
            '<div class="advntr-road-note__label">ADVNTR Road Note</div>'
            f'<p>{body}</p>'
            '</aside>\n'
        )

    return re.sub(r"(?m)^-\s+\*\*Editorial note:\*\*\s+(.+)$", replace_note, text)


def render_prose(prose_file: Path) -> str:
    if not prose_file.exists():
        return ""
    rendered = markdown.markdown(
        format_prose_markdown(prose_file.read_text(encoding="utf-8")),
        extensions=["extra", "tables", "smarty"],
    )
    rendered = re.sub(r"(<li>)(\s*<p>)?\[ \]\s+", r'<li class="check-item">\2', rendered)
    rendered = re.sub(r"<h([23])>(.*?)</h\1>", r"<h\1><span>\2</span></h\1>", rendered)
    return rendered


# ── Schema detection ──────────────────────────────────────────────────────────

def is_schema_v3(content: dict) -> bool:
    """Schema 3.0: zones/lodging/seasonal are top-level siblings of guide:."""
    return "sections" not in content.get("guide", {})


# ── Schema 3.0 loader ─────────────────────────────────────────────────────────

def discover_sections_v3(guide_dir: Path, guide: dict, content: dict) -> list:
    """Build ordered section list from prose files + zone data for schema 3.0."""
    prose_dir = guide_dir / "prose"
    if not prose_dir.exists():
        print(f"WARNING: prose/ directory not found at {prose_dir}")
        return []

    zones = content.get("zones", [])
    zone_index = 0
    sections = []

    prose_files = sorted(prose_dir.glob("*.md"), key=lambda p: p.stem)

    for prose_file in prose_files:
        stem = prose_file.stem
        m = re.match(r'^(\d+)([a-z]?)-(.+)$', stem)
        if not m:
            continue
        num_str, letter, slug_part = m.group(1), m.group(2), m.group(3)
        num = int(num_str)
        display_number = f"{num:02d}{letter.upper() if letter else ''}"

        is_zone_section = (num == 4 and bool(letter))

        if is_zone_section and zone_index < len(zones):
            zone = zones[zone_index]
            zone_index += 1
            # Derive theme from zone index: A=cream, B=dark, C=blue
            theme_cycle = ["cream", "dark", "blue"]
            theme = theme_cycle[min(zone_index - 1, len(theme_cycle) - 1)]
            first_word = zone["name"].split()[0].upper()
            meta = {
                "title": zone["name"],
                "subhead": zone.get("subhead", zone.get("one_line", "")),
                "eyebrow": zone.get("one_line", "Zone Guide"),
                "visual_word": first_word[:7],
                "visual_theme": theme,
                "visual_label": "Zone Guide",
                "section_type": "zone",
                "zone": zone,
            }
        else:
            base = SECTION_META_V3.get(display_number, SECTION_META_V3.get(f"{num:02d}", None))
            if base:
                meta = dict(base)
            else:
                slug_title = slug_part.replace("-", " ").title()
                meta = {
                    "title": slug_title,
                    "subhead": "",
                    "eyebrow": "Field Guide",
                    "visual_word": slug_part.split("-")[0].upper()[:7],
                    "visual_theme": "cream",
                    "visual_label": "Field Guide",
                    "section_type": "generic",
                }
            meta["zone"] = None

        section = {
            "file": stem,
            "display_number": display_number,
            "section_id": f"section-{display_number.lower()}",
            "prose_html": render_prose(prose_file),
            **meta,
        }
        sections.append(section)

    return sections


def load_guide_v3(guide_id: str, content: dict, web_preview: bool = False) -> dict:
    """Load and enrich a schema 3.0 guide for template rendering."""
    guide_dir = ROOT / "guides" / guide_id
    guide = content["guide"]

    # Attach all top-level structured blocks to guide dict
    guide["zones"] = content.get("zones", [])
    guide["itineraries"] = content.get("itineraries", {})
    guide["seasonal"] = content.get("seasonal", [])
    guide["drive_times"] = content.get("drive_times", [])
    guide["lodging"] = content.get("lodging", [])
    guide["businesses"] = content.get("businesses", [])
    guide["fees"] = content.get("fees", {})
    guide["permits"] = content.get("permits", {})
    guide["cell_service"] = content.get("cell_service", {})
    guide["checklist"] = content.get("checklist", [])
    guide["resources"] = content.get("resources", [])
    guide["links"] = content.get("links", [])
    guide["photos"] = content.get("photos", [])
    guide["visual_moments"] = content.get("visual_moments", [])

    # Cover photo
    cover_photo = guide.get("cover_photo")
    if cover_photo and cover_photo != "null":
        if web_preview:
            guide["cover_photo_uri"] = f"guides/{guide_id}/{cover_photo}"
        else:
            guide["cover_photo_uri"] = str((guide_dir / cover_photo).resolve())
    elif guide["photos"]:
        first = guide["photos"][0]
        photo_file = first.get("file", "")
        if web_preview:
            guide["cover_photo_uri"] = f"guides/{guide_id}/{photo_file}"
        else:
            guide["cover_photo_uri"] = str((guide_dir / photo_file).resolve())
    else:
        guide["cover_photo_uri"] = ""

    # Cover word (derived from title)
    if not guide.get("cover_word"):
        clean = re.sub(r"\b(National Park|National Monument|State Park|National Seashore)\b", "", guide["title"])
        words = clean.strip().split()
        guide["cover_word"] = [w.upper() for w in words[:2]] if words else [guide["title"].upper()]

    # Guide URL
    guide_url = guide.get("url", "")
    guide["url_href"] = guide_url if guide_url.startswith(("http://", "https://")) else f"https://{guide_url}"

    # Logos
    if web_preview:
        guide["logos"] = {
            "rust": "template/assets/logos/advntr-road-rust.png",
            "white": "template/assets/logos/advntr-road-white.png",
            "green": "template/assets/logos/advntr-road-green.png",
        }
    else:
        guide["logos"] = {
            "rust": str((LOGO_DIR / "advntr-road-rust.png").resolve()),
            "white": str((LOGO_DIR / "advntr-road-white.png").resolve()),
            "green": str((LOGO_DIR / "advntr-road-green.png").resolve()),
        }

    # Series cross-links
    series_path = ROOT / "series.yaml"
    if series_path.exists():
        series = yaml.safe_load(series_path.read_text(encoding="utf-8")) or {}
        guide["other_guides"] = [g for g in series.get("series", []) if g.get("id") != guide_id]
    else:
        guide["other_guides"] = []

    # Sections from prose directory
    guide["sections"] = discover_sections_v3(guide_dir, guide, content)

    # Enrich lodging photo URIs
    for item in guide["lodging"]:
        img = item.get("image")
        if img:
            if web_preview:
                item["image_uri"] = f"guides/{guide_id}/{img}"
            else:
                item["image_uri"] = str((guide_dir / img).resolve())
        else:
            item["image_uri"] = ""

    # QR codes placeholder (populated in build())
    guide["qr_codes"] = {}

    return guide


# ── Schema 1 loader (backward compat) ────────────────────────────────────────

def load_guide_v1(guide_id: str, web_preview: bool = False) -> dict:
    """Load a schema v1 guide. Preserves existing behavior for shipped guides."""
    guide_dir = ROOT / "guides" / guide_id
    content_path = guide_dir / "content.yaml"
    if not content_path.exists():
        raise FileNotFoundError(f"Guide content not found: {content_path}")

    content = yaml.safe_load(content_path.read_text(encoding="utf-8"))
    guide = content["guide"]

    def asset_ref(value):
        if not value:
            return ""
        if str(value).startswith(("http://", "https://", "/", "guides/")):
            return value
        return f"guides/{guide_id}/{value}"

    cover_photo = guide.get("cover_photo")
    if cover_photo:
        if web_preview:
            guide["cover_photo_uri"] = f"guides/{guide_id}/{cover_photo}"
        else:
            guide["cover_photo_uri"] = str((guide_dir / cover_photo).resolve())
    else:
        guide["cover_photo_uri"] = ""

    guide_url = guide.get("url", "")
    guide["url_href"] = guide_url if guide_url.startswith(("http://", "https://")) else f"https://{guide_url}"

    if not guide.get("cover_word"):
        title_words = guide["title"].replace("National Park", "").strip().split()
        guide["cover_word"] = [title_words[0]] if title_words else [guide["title"]]
        print(f"WARNING — no cover_word; defaulting to {guide['cover_word']!r}")

    if web_preview:
        guide["logos"] = {
            "rust": "template/assets/logos/advntr-road-rust.png",
            "white": "template/assets/logos/advntr-road-white.png",
            "green": "template/assets/logos/advntr-road-green.png",
        }
    else:
        guide["logos"] = {
            "rust": str((LOGO_DIR / "advntr-road-rust.png").resolve()),
            "white": str((LOGO_DIR / "advntr-road-white.png").resolve()),
            "green": str((LOGO_DIR / "advntr-road-green.png").resolve()),
        }

    sections = guide.get("sections", [])
    zones = guide.get("zones", [])
    if zones:
        insert_at = min(3, len(sections))
        sections = sections[:insert_at] + zones + sections[insert_at:]
        guide["sections"] = sections

    chapter_num = 0
    zone_letter = 0
    for i, section in enumerate(sections):
        is_zone = bool(zones) and insert_at <= i < insert_at + len(zones)
        if is_zone:
            if zone_letter == 0:
                chapter_num += 1
            section["display_number"] = (
                f"{chapter_num:02d}{chr(ord('A') + zone_letter)}" if len(zones) > 1 else f"{chapter_num:02d}"
            )
            zone_letter += 1
        else:
            chapter_num += 1
            section["display_number"] = f"{chapter_num:02d}"

    for section in guide.get("sections", []):
        visual = section.get("visual", {})
        section["visual_word"] = visual.get("word", section["title"].split()[0]).upper()
        section["visual_theme"] = visual.get("theme", "cream")
        section["visual_image"] = asset_ref(visual.get("image", ""))
        section["visual_label"] = visual.get("label", section.get("eyebrow", "Field Guide"))
        section["section_type"] = None  # v1 sections have no section_type
        section["section_id"] = f"section-{section['display_number'].lower()}"
        prose_file = guide_dir / "prose" / f"{section['file']}.md"
        section["prose_html"] = render_prose(prose_file)

    series_path = ROOT / "series.yaml"
    other_guides = []
    if series_path.exists():
        series = yaml.safe_load(series_path.read_text(encoding="utf-8")) or {}
        other_guides = [g for g in series.get("series", []) if g.get("id") != guide_id]
    guide["other_guides"] = other_guides
    guide["qr_codes"] = {}

    return guide


# ── Photo sourcing ────────────────────────────────────────────────────────────

def source_nps_photos(guide_id: str, park_code: str, target_dir: Path, limit: int = 5) -> list:
    # Images are not returned by default — fields=images is required.
    api_url = "https://developer.nps.gov/api/v1/parks"
    params = {"parkCode": park_code, "fields": "images", "api_key": NPS_API_KEY}

    try:
        resp = requests.get(api_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"NPS API unavailable: {exc}")
        return []

    park_data = data.get("data", [])
    if not park_data:
        print(f"NPS returned no park data for code: {park_code}")
        return []

    raw_images = park_data[0].get("images", [])[:limit]

    photos = []
    target_dir.mkdir(parents=True, exist_ok=True)

    for item in raw_images:
        title = item.get("title", "")
        alt = item.get("altText", title)
        credit = item.get("credit", "NPS")
        image_url = item.get("url", "")

        if not image_url or not image_url.startswith("http"):
            continue

        try:
            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()
            ct = img_resp.headers.get("content-type", "image/jpeg")
            ext = "jpg" if "jpeg" in ct else ("png" if "png" in ct else "jpg")
            filename = f"{guide_id}-nps-{len(photos)+1:02d}.{ext}"
            filepath = target_dir / filename
            filepath.write_bytes(img_resp.content)
            photos.append({
                "file": f"assets/photos/{filename}",
                "title": title,
                "alt": alt,
                "credit": credit,
                "license": "Public Domain (NPS)",
                "source": "NPS Media API",
                "source_url": image_url,
            })
            print(f"  NPS photo: {filename}")
        except Exception as exc:
            print(f"  WARNING: NPS photo download failed: {exc}")

    return photos


def source_wikimedia_photos(guide_id: str, search_term: str, target_dir: Path, limit: int = 3) -> list:
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {search_term}",
        "gsrlimit": limit * 4,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mediatype",
        "iiurlwidth": 1600,
        "format": "json",
    }

    try:
        resp = requests.get(api_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"Wikimedia API unavailable: {exc}")
        return []

    photos = []
    target_dir.mkdir(parents=True, exist_ok=True)
    pages = data.get("query", {}).get("pages", {})

    for _, page in sorted(pages.items(), key=lambda x: x[0]):
        if len(photos) >= limit:
            break

        imageinfo = page.get("imageinfo", [{}])[0]
        if imageinfo.get("mediatype") not in ("BITMAP", None):
            continue

        extmeta = imageinfo.get("extmetadata", {})
        license_short = extmeta.get("LicenseShortName", {}).get("value", "")
        # Accept PD, CC0, CC-BY, CC-BY-SA
        if not any(t in license_short.upper() for t in ["PD", "CC0", "CC BY", "CC-BY"]):
            continue

        image_url = imageinfo.get("thumburl") or imageinfo.get("url", "")
        if not image_url:
            continue

        title = extmeta.get("ObjectName", {}).get("value", page.get("title", "").replace("File:", ""))
        artist_raw = extmeta.get("Artist", {}).get("value", "Wikimedia Commons")
        artist = re.sub(r"<[^>]+>", "", artist_raw).strip()

        try:
            img_resp = requests.get(image_url, timeout=30)
            img_resp.raise_for_status()
            ct = img_resp.headers.get("content-type", "image/jpeg")
            ext = "jpg" if "jpeg" in ct else ("png" if "png" in ct else "jpg")
            filename = f"{guide_id}-wm-{len(photos)+1:02d}.{ext}"
            filepath = target_dir / filename
            filepath.write_bytes(img_resp.content)
            photos.append({
                "file": f"assets/photos/{filename}",
                "title": title[:80],
                "alt": title[:80],
                "credit": artist[:60],
                "license": license_short,
                "source": "Wikimedia Commons",
                "source_url": image_url,
            })
            print(f"  Wikimedia photo: {filename} ({license_short})")
        except Exception as exc:
            print(f"  WARNING: Wikimedia photo download failed: {exc}")

    return photos


def source_photos(guide_id: str, guide_dir: Path, content: dict) -> list:
    """Source photos for schema 3.0 guide. Updates content.yaml photos[] if successful."""
    existing = content.get("photos", [])
    if existing:
        print(f"Photos already populated ({len(existing)} entries). Skipping sourcing.")
        return existing

    park_code = PARK_CODES.get(guide_id)
    photos_dir = guide_dir / "assets" / "photos"
    photos = []

    if park_code:
        print(f"Sourcing photos from NPS API (park code: {park_code})...")
        photos = source_nps_photos(guide_id, park_code, photos_dir, limit=5)

    if not photos:
        park_name = content.get("guide", {}).get("title", guide_id)
        print(f"NPS returned no photos. Trying Wikimedia Commons for '{park_name}'...")
        photos = source_wikimedia_photos(guide_id, park_name, photos_dir, limit=3)

    if not photos:
        print("WARNING: No photos sourced. Guide renders without images.")
        print("  Add NPS_API_KEY=<key> to .env, or manually add photos to content.yaml.")
        return []

    # Write photo_manifest.json
    manifest = guide_dir / "assets" / "photo_manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(photos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Photo manifest: {manifest} ({len(photos)} photos)")

    # Update content.yaml photos: [] block
    content_path = guide_dir / "content.yaml"
    content_text = content_path.read_text(encoding="utf-8")
    photo_block_lines = ["photos:"]
    for p in photos:
        photo_block_lines.append(f'  - file: {p["file"]}')
        photo_block_lines.append(f'    title: "{p["title"]}"')
        photo_block_lines.append(f'    credit: "{p["credit"]}"')
        photo_block_lines.append(f'    license: "{p["license"]}"')
        photo_block_lines.append(f'    source: "{p["source"]}"')
    new_block = "\n".join(photo_block_lines)
    updated = re.sub(r'^photos:\s*\[\]\s*$', new_block, content_text, flags=re.MULTILINE)
    if updated != content_text:
        content_path.write_text(updated, encoding="utf-8")
        print(f"Updated content.yaml photos[] block.")
    else:
        print("NOTE: photos: [] not found verbatim — content.yaml photos block not updated.")

    return photos


# ── QR code generation ────────────────────────────────────────────────────────

def generate_qr_codes(guide_id: str, links: list, zones: list) -> dict:
    """Generate QR codes for all link slugs. Returns {slug: data_uri}."""
    try:
        import segno
    except ImportError:
        print("WARNING: segno not installed — skipping QR generation. Run: pip install segno")
        return {}

    qr_dir = OUTPUT_DIR / "qr"
    qr_dir.mkdir(parents=True, exist_ok=True)
    qr_codes = {}

    slugs = [link["slug"] for link in links if link.get("slug")]
    for zone in zones:
        for trail in zone.get("trails", []):
            slug = trail.get("link_slug")
            if slug and slug not in slugs:
                slugs.append(slug)

    for slug in slugs:
        url = f"https://road.advntr.io/r/{slug}"
        try:
            qr = segno.make_qr(url)
            qr_path = qr_dir / f"{slug}.png"
            qr.save(str(qr_path), scale=8, border=2, dark="#1B4436", light="#F9E4C5")
            encoded = base64.b64encode(qr_path.read_bytes()).decode("utf-8")
            qr_codes[slug] = f"data:image/png;base64,{encoded}"
        except Exception as exc:
            print(f"WARNING: QR generation failed for {slug}: {exc}")

    print(f"QR codes: {len(qr_codes)} generated → {qr_dir}")
    return qr_codes


# ── Redirects fragment ────────────────────────────────────────────────────────

def write_redirects_fragment(guide_id: str, links: list, zones: list) -> int:
    lines = []
    guide_url = f"https://road.advntr.io/{guide_id}"

    for link in links:
        slug = link.get("slug", "")
        url = link.get("url", "")
        if slug and url and link.get("status") == "URL VERIFIED":
            lines.append(f"/r/{slug}\t{url}\t302")

    for zone in zones:
        for trail in zone.get("trails", []):
            slug = trail.get("link_slug", "")
            if slug and not any(line.startswith(f"/r/{slug}") for line in lines):
                lines.append(f"/r/{slug}\t{guide_url}\t302")

    frag_path = OUTPUT_DIR / "_redirects_fragment.txt"
    frag_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Redirects fragment: {frag_path} ({len(lines)} entries)")
    return len(lines)


# ── Gate 3 QA ─────────────────────────────────────────────────────────────────

def run_gate3_qa(guide: dict, content: dict, html_str: str, pdf_path: Path) -> list:
    """Gate 3 QA checklist. Returns list of (check, status, detail) tuples."""
    results = []

    def check(name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        results.append((name, status, detail))
        return passed

    def warn(name, detail=""):
        results.append((name, "WARN", detail))

    sections = guide.get("sections", [])

    # 1. All prose sections have rendered content
    empty = [s["display_number"] for s in sections if not s.get("prose_html", "").strip()]
    check(
        "Prose rendered in all sections",
        not empty,
        f"Empty sections: {', '.join(empty)}" if empty else f"All {len(sections)} sections have prose",
    )

    # 2. Lodging count integrity
    lodging = content.get("lodging", [])
    lodging_rows = html_str.count('data-lodging-row="1"')
    check(
        "Lodging table row count",
        lodging_rows == len(lodging),
        f"{lodging_rows} rendered rows == {len(lodging)} content.yaml entries",
    )

    # 3. Seasonal matrix completeness
    seasonal = content.get("seasonal", [])
    check(
        "Seasonal matrix (12 months)",
        len(seasonal) == 12,
        f"{len(seasonal)}/12 months",
    )

    # 4. QR codes generated
    qr_dir = OUTPUT_DIR / "qr"
    qr_count = len(list(qr_dir.glob("*.png"))) if qr_dir.exists() else 0
    verified_links = [l for l in content.get("links", []) if l.get("status") == "URL VERIFIED"]
    check(
        "QR codes generated",
        qr_count >= len(verified_links),
        f"{qr_count} QR codes for {len(verified_links)} verified links",
    )

    # 5. Redirects fragment exists
    frag_path = OUTPUT_DIR / "_redirects_fragment.txt"
    check(
        "_redirects_fragment.txt written",
        frag_path.exists(),
        str(frag_path.relative_to(ROOT)) if frag_path.exists() else "File missing",
    )

    # 6. PDF written
    if pdf_path is not None:
        check(
            "PDF rendered",
            pdf_path.exists(),
            str(pdf_path.relative_to(ROOT)) if pdf_path.exists() else "File missing",
        )
    else:
        warn("PDF rendered", "--html-only mode; PDF skipped")

    # 7. Photos (advisory — missing photos don't block Gate 3)
    photos = content.get("photos", [])
    if not photos:
        warn("Photos sourced", "photos: [] — image render blocked until photos are supplied")
    else:
        check("Photos sourced", True, f"{len(photos)} photo(s) available")

    # 8. Drive times present
    drive_times = content.get("drive_times", [])
    check(
        "Drive times table",
        len(drive_times) >= 1,
        f"{len(drive_times)} entries",
    )

    # 9. HTML non-trivial size
    check(
        "HTML content size",
        len(html_str) > 50_000,
        f"{len(html_str):,} bytes",
    )

    return results


def write_build_summary(guide_id: str, qa_results: list, html_path: Path, pdf_path: Path) -> str:
    failures = [r for r in qa_results if r[1] == "FAIL"]
    warnings = [r for r in qa_results if r[1] == "WARN"]

    overall = "PASS" if not failures else "FAIL"

    lines = [
        f"# ADVNTR Road Build Summary — {guide_id}",
        f"### Build date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"### Schema: 3.0",
        "",
        f"## GATE 3 STATUS: {overall}",
        "",
    ]

    if failures:
        lines += ["### Blocking failures", ""]
        for name, status, detail in failures:
            lines.append(f"- **FAIL** — {name}: {detail}")
        lines.append("")

    if warnings:
        lines += ["### Advisory warnings", ""]
        for name, status, detail in warnings:
            lines.append(f"- **WARN** — {name}: {detail}")
        lines.append("")

    lines += ["## QA Checklist", ""]
    icons = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}
    for name, status, detail in qa_results:
        lines.append(f"- [{icons[status]}] **{name}** ({status}): {detail}")

    lines += ["", "## Output", ""]
    if html_path.exists():
        lines.append(f"- HTML: `{html_path.relative_to(ROOT)}`  ({html_path.stat().st_size:,} bytes)")
    if pdf_path and pdf_path.exists():
        lines.append(f"- PDF: `{pdf_path.relative_to(ROOT)}`  ({pdf_path.stat().st_size:,} bytes)")
    frag = OUTPUT_DIR / "_redirects_fragment.txt"
    if frag.exists():
        lines.append(f"- Redirects: `{frag.relative_to(ROOT)}`")
    qr_dir = OUTPUT_DIR / "qr"
    if qr_dir.exists():
        qr_count = len(list(qr_dir.glob("*.png")))
        lines.append(f"- QR codes: `{qr_dir.relative_to(ROOT)}/` ({qr_count} files)")

    summary_path = OUTPUT_DIR / "build_summary.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"GATE 3 STATUS: {overall}")
    if failures:
        print(f"  {len(failures)} FAIL(s):")
        for name, _, detail in failures:
            print(f"    ✗ {name}: {detail}")
    if warnings:
        print(f"  {len(warnings)} warning(s).")
    print(f"Build summary: {summary_path}")
    print(f"{'='*60}\n")

    return overall


# ── PDF renderer ──────────────────────────────────────────────────────────────

def write_pdf(html_str: str, pdf_path: Path) -> str | None:
    try:
        from weasyprint import HTML as WP_HTML
        WP_HTML(string=html_str, base_url=str(ROOT)).write_pdf(str(pdf_path))
        return "weasyprint"
    except Exception as exc:
        print(f"WARNING — WeasyPrint failed: {exc}")
        try:
            return write_pdf_with_chrome(html_str, pdf_path)
        except Exception as chrome_exc:
            print(f"WARNING — Chrome fallback failed: {chrome_exc}")
            return None


def write_pdf_with_chrome(html_str: str, pdf_path: Path) -> str:
    if not CHROME.exists():
        raise RuntimeError("No PDF renderer available.")

    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html_str)
        tmp_path = Path(tmp.name)
    profile_dir = Path(tempfile.mkdtemp(prefix="advntr-chrome-"))

    try:
        subprocess.run(
            [
                str(CHROME), "--headless", "--no-sandbox", "--disable-gpu",
                "--no-first-run", "--disable-extensions",
                f"--user-data-dir={profile_dir}",
                f"--print-to-pdf={pdf_path}",
                f"file://{tmp_path}",
            ],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
        import shutil
        shutil.rmtree(profile_dir, ignore_errors=True)
    return "chrome"


# ── Font test ─────────────────────────────────────────────────────────────────

def render_font_test(font_css: str, css: str):
    html_str = f"""<!doctype html>
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
    write_pdf(html_str, path)
    print(f"Font test written to {path}")


# ── Main build ────────────────────────────────────────────────────────────────

def build(guide_id: str, no_maps: bool = False, html_only: bool = False):
    guide_dir = ROOT / "guides" / guide_id
    content_path = guide_dir / "content.yaml"
    if not content_path.exists():
        raise FileNotFoundError(f"Guide not found: {content_path}")

    content = yaml.safe_load(content_path.read_text(encoding="utf-8"))
    schema_v3 = is_schema_v3(content)

    print(f"\nBuilding: {guide_id} (schema {'3.0' if schema_v3 else '1'})")
    print(f"Output: {OUTPUT_DIR}/")

    if schema_v3:
        # Source photos if none exist
        photos = source_photos(guide_id, guide_dir, content)
        if photos:
            content["photos"] = photos  # use freshly sourced photos in-memory

        guide = load_guide_v3(guide_id, content, web_preview=html_only)

        # Generate QR codes
        qr_codes = generate_qr_codes(guide_id, content.get("links", []), content.get("zones", []))
        guide["qr_codes"] = qr_codes
        for link in guide.get("links", []):
            link["qr_uri"] = qr_codes.get(link.get("slug", ""), "")
        for zone in guide.get("zones", []):
            for trail in zone.get("trails", []):
                trail["qr_uri"] = qr_codes.get(trail.get("link_slug", ""), "")

        # Write _redirects_fragment.txt
        write_redirects_fragment(guide_id, content.get("links", []), content.get("zones", []))

        template_name = "guide_template.html"
    else:
        guide = load_guide_v1(guide_id, web_preview=html_only)

        # v1 maps
        maps = guide.get("maps", {})
        maps_dir = guide_dir / "assets" / "maps"
        for name, cfg in maps.items():
            cache_path = maps_dir / f"{name}.png"
            rel_path = f"guides/{guide_id}/assets/maps/{name}.png"
            cfg["overlay_svg"] = build_overlay_svg(cfg)
            if cache_path.exists():
                png_bytes = cache_path.read_bytes()
                cfg["image_uri"] = map_image_uri(png_bytes, html_only, rel_path)
                print(f"Map '{name}': loaded from cache.")
            elif no_maps or not MAPS_KEY:
                reason = "--no-maps" if no_maps else "GOOGLE_MAPS_API_KEY not set"
                print(f"Map '{name}': skipped ({reason}).")
                cfg["image_uri"] = ""
            else:
                print(f"Map '{name}': fetching...")
                try:
                    png_bytes = fetch_map_image(cfg, cache_path)
                    cfg["image_uri"] = map_image_uri(png_bytes, html_only, rel_path)
                except Exception as exc:
                    print(f"WARNING — Map '{name}' failed: {exc}")
                    cfg["image_uri"] = ""

        template_name = "guide_template.html"

    font_css = build_font_css()
    css = read_css()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)
    html_str = template.render(guide=guide, font_css=font_css, css=css, schema_v3=schema_v3)

    OUTPUT_DIR.mkdir(exist_ok=True)
    html_path = OUTPUT_DIR / f"{guide_id}.html"
    html_path.write_text(html_str, encoding="utf-8")
    print(f"HTML: {html_path} ({len(html_str):,} bytes)")

    pdf_path = None
    if not html_only:
        pdf_path = OUTPUT_DIR / f"{guide_id}-2026.pdf"
        renderer = write_pdf(html_str, pdf_path)
        if renderer:
            print(f"PDF: {pdf_path} ({renderer})")
        else:
            pdf_path = None
            print("PDF not written. HTML available for review.")

    if schema_v3:
        qa_results = run_gate3_qa(guide, content, html_str, pdf_path)
        overall = write_build_summary(guide_id, qa_results, html_path, pdf_path)
        if overall == "FAIL":
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build an ADVNTR Road guide PDF.")
    parser.add_argument("--guide", required=True)
    parser.add_argument("--no-maps", action="store_true")
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--font-test", action="store_true")
    args = parser.parse_args()

    if args.font_test:
        render_font_test(build_font_css(), read_css())
    else:
        build(args.guide, no_maps=args.no_maps, html_only=args.html_only)


if __name__ == "__main__":
    main()
