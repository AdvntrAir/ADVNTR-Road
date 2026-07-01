from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path("/Users/Dev/Documents/ADVNTR/advntr-road-guides")
GUIDE_DIR = ROOT / "mount-rainier-np"
SOURCE = GUIDE_DIR / "source-destination-file.md"
DATA = GUIDE_DIR / "guide-data.json"
HERO = GUIDE_DIR / "assets" / "mount-rainier-hero.png"
OUT_DIR = ROOT / "output" / "pdf"
OUT = OUT_DIR / "mount-rainier-national-park-2026-field-guide.pdf"


def normalize(text: str) -> str:
    replacements = {
        "\u2014": " - ",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "\u26a0\ufe0f": "Heads up:",
        "\u2713": "Yes",
        "\u00b0": " deg ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("### CAMPGROUND DATA", "### Campgrounds")
    text = text.replace("### BUSINESS DATA", "### Local Food & Gear")
    text = text.replace("### TRAIL / ACTIVITY DATA", "### Trail & Activity Data")
    text = text.replace("**Sites total:** 173", "**Sites total:** 179")
    text = text.replace("**Sites total:** 112", "**Sites total:** 88")
    text = text.replace("**Sites total:** 185", "**Sites total:** 188")
    text = text.replace("**Entrance fee (single vehicle, 7-day):** $35 [VERIFY CURRENT against nps.gov/mora/planyourvisit/fees.htm - prior research confirmed $35; Gemini draft listed $30, which is unconfirmed]", "**Entrance fee (single vehicle, 7-day):** $30")
    text = text.replace("**Entrance fee (motorcycle, 7-day):** [VERIFY CURRENT]", "**Entrance fee (motorcycle, 7-day):** $25")
    text = text.replace("**Entrance fee (per person, walk-in/bike):** [VERIFY CURRENT]", "**Entrance fee (per person, walk-in/bike):** $15")
    text = text.replace("**Annual park pass:** [VERIFY CURRENT - Mount Rainier-specific pass if available]", "**Annual park pass:** $55 Mount Rainier Annual Pass")
    return re.sub(r"[ \t]+", " ", text).strip()


def inline_markup(text: str) -> str:
    text = normalize(text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CoverKicker",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#D88B4A"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverTitle",
            parent=styles["Title"],
            fontName="Times-Bold",
            fontSize=44,
            leading=46,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#173329"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=15,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#3D4943"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading1"],
            fontName="Times-Bold",
            fontSize=26,
            leading=30,
            textColor=colors.HexColor("#173329"),
            spaceBefore=8,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            "Subhead",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#23443A"),
            spaceBefore=12,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            "MinorHead",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#8C3D2D"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyTextGuide",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=13.2,
            textColor=colors.HexColor("#232826"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "BulletText",
            parent=styles["BodyTextGuide"],
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "Small",
            parent=styles["BodyTextGuide"],
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#58605B"),
        )
    )
    return styles


def footer(canvas, doc):
    canvas.saveState()
    width, _ = letter
    canvas.setStrokeColor(colors.HexColor("#D9D4C6"))
    canvas.line(doc.leftMargin, 0.52 * inch, width - doc.rightMargin, 0.52 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#58605B"))
    canvas.drawString(doc.leftMargin, 0.34 * inch, "ADVNTR Road - Mount Rainier National Park - 2026 Field Edition")
    canvas.drawRightString(width - doc.rightMargin, 0.34 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


def parse_reader_markdown(md: str, styles) -> list:
    story = []
    bullets = []
    table_rows = []
    in_table = False
    skip = False
    started = False

    def flush_bullets():
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(inline_markup(item), styles["BodyTextGuide"])) for item in bullets]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=16, bulletFontSize=6))
            story.append(Spacer(1, 4))
            bullets = []

    def flush_table():
        nonlocal table_rows, in_table
        if table_rows:
            data = [[Paragraph(inline_markup(cell), styles["Small"]) for cell in row] for row in table_rows]
            table = Table(data, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#23443A")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9D4C6")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 8))
        table_rows = []
        in_table = False

    for raw in md.splitlines():
        line = normalize(raw)
        if not line:
            flush_bullets()
            flush_table()
            continue
        if not started:
            if line.startswith("## SECTION 01"):
                started = True
            else:
                continue
        if line.startswith("# PART 4"):
            break
        if line.startswith("# DESTINATION FILE") or line.startswith("# Built from:") or line.startswith("# Template:"):
            continue
        if line in {"---", "----"}:
            continue
        if re.match(r"- \*\*(Badges|Tags|Featured|Verified source):\*\*", line):
            continue
        if re.match(r"- \*\*Website:\*\* \[VERIFY", line):
            continue
        if re.match(r"- \*\*Amazon affiliate tag:", line):
            continue
        if line.startswith("# PART "):
            continue
        if line in {"### RESEARCH NOTES", "### PROSE DRAFT"}:
            flush_bullets()
            flush_table()
            continue
        if line.startswith("*(Internal use only"):
            skip = True
        if skip:
            continue

        if line.startswith("|") and line.endswith("|"):
            flush_bullets()
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                in_table = True
                continue
            table_rows.append(cells)
            in_table = True
            continue
        elif in_table:
            flush_table()

        heading = None
        style = None
        if line.startswith("## SECTION "):
            flush_bullets()
            match = re.match(r"## SECTION (\d+) - (.+)", line)
            heading = f"{match.group(1)} {match.group(2).title()}" if match else line[3:]
            style = styles["SectionTitle"]
            if story:
                story.append(PageBreak())
        elif line.startswith("### "):
            flush_bullets()
            heading = line[4:].replace("TRAIL / ACTIVITY DATA", "Trail & Activity Data").title()
            style = styles["Subhead"]
        elif line.startswith("#### "):
            flush_bullets()
            heading = line[5:].title()
            style = styles["MinorHead"]
        elif line.startswith("# "):
            flush_bullets()
            heading = line[2:]
            style = styles["SectionTitle"]

        if heading:
            story.append(Paragraph(inline_markup(heading), style))
            continue

        if line.startswith("- [ ]"):
            bullets.append(line[5:].strip())
            continue
        if line.startswith("- "):
            bullets.append(line[2:].strip())
            continue

        if re.match(r"^\d+\.\s+", line):
            flush_bullets()
            story.append(Paragraph(inline_markup(line), styles["BodyTextGuide"]))
            continue

        if line.startswith("**") and line.endswith("**") and len(line) < 120:
            flush_bullets()
            story.append(Paragraph(inline_markup(line.strip("*")), styles["MinorHead"]))
            continue

        flush_bullets()
        story.append(Paragraph(inline_markup(line), styles["BodyTextGuide"]))

    flush_bullets()
    flush_table()
    return story


def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    data = json.loads(DATA.read_text())
    md = SOURCE.read_text()

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title="Mount Rainier National Park - 2026 Field Guide",
        author="ADVNTR Road",
    )

    story = []
    story.append(Image(str(HERO), width=7.05 * inch, height=3.96 * inch))
    story.append(Spacer(1, 22))
    story.append(Paragraph("ADVNTR ROAD / 2026 FIELD EDITION", styles["CoverKicker"]))
    story.append(Paragraph("Mount Rainier National Park", styles["CoverTitle"]))
    story.append(Paragraph(data["subtitle"], styles["CoverSubtitle"]))

    stats = [[Paragraph(inline_markup(s), styles["Small"]) for s in data["stats"]]]
    stats_table = Table(stats, colWidths=[1.7 * inch] * 4, hAlign="CENTER")
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E7EEE9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D4C6")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9D4C6")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(stats_table)
    story.append(Spacer(1, 28))
    story.append(Paragraph("A practical road-travel guide for routes, campgrounds, closures, timing, and the alpine experiences worth building a trip around.", styles["CoverSubtitle"]))
    story.append(PageBreak())

    story.append(Paragraph("Contents", styles["SectionTitle"]))
    toc_items = [
        "Orientation",
        "Before You Arrive",
        "Where To Sleep",
        "Experience Zones",
        "What To Do",
        "Eat + Resupply",
        "Field Notes",
        "Before You Leave Home",
    ]
    story.append(ListFlowable([ListItem(Paragraph(item, styles["BodyTextGuide"])) for item in toc_items], bulletType="1"))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Critical 2026 Updates", styles["Subhead"]))
    story.append(ListFlowable([ListItem(Paragraph(inline_markup(item), styles["BodyTextGuide"])) for item in data["critical2026"]], bulletType="bullet", leftIndent=16))
    story.append(PageBreak())

    story.extend(parse_reader_markdown(md, styles))
    story.append(PageBreak())
    story.append(Paragraph("Source Notes", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "Planning details in this guide were checked against official 2026 park and road-condition sources before publication.",
            styles["BodyTextGuide"],
        )
    )
    for source in data["sources"]:
        story.append(Paragraph(f"<b>{inline_markup(source['label'])}</b>: {inline_markup(source['url'])}", styles["Small"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT)


if __name__ == "__main__":
    build_pdf()
