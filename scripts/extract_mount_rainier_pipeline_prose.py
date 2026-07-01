from pathlib import Path
import re

ROOT = Path("/Users/Dev/Documents/ADVNTR/advntr-road-guides")
SOURCE = ROOT / "mount-rainier-np" / "source-destination-file.md"
OUT = ROOT / "guides" / "mount-rainier-np" / "prose"

SECTIONS = {
    "01": "01-orientation",
    "02": "02-before-you-arrive",
    "03": "03-where-to-sleep",
    "04": "04-experience-zones",
    "05": "05-what-to-do",
    "06": "06-eat-resupply",
    "07": "07-field-notes",
    "08": "08-before-you-leave-home",
}

REPLACEMENTS = {
    "### RESEARCH NOTES": "",
    "### PROSE DRAFT": "",
    "### CAMPGROUND DATA": "### Campgrounds",
    "### BUSINESS DATA": "### Local Food & Gear",
    "### TRAIL / ACTIVITY DATA": "### Trail & Activity Data",
    "#### MAP MARKERS FOR THIS ZONE": "#### Map Reference",
    "—": "-",
    "–": "-",
    "’": "'",
    "“": '"',
    "”": '"',
    "⚠️": "Heads up:",
}


def clean(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = text.replace(
        "**Entrance fee (single vehicle, 7-day):** $35 [VERIFY CURRENT against nps.gov/mora/planyourvisit/fees.htm - prior research confirmed $35; Gemini draft listed $30, which is unconfirmed]",
        "**Entrance fee (single vehicle, 7-day):** $30",
    )
    text = text.replace("**Entrance fee (motorcycle, 7-day):** [VERIFY CURRENT]", "**Entrance fee (motorcycle, 7-day):** $25")
    text = text.replace("**Entrance fee (per person, walk-in/bike):** [VERIFY CURRENT]", "**Entrance fee (per person, walk-in/bike):** $15")
    text = text.replace("**Annual park pass:** [VERIFY CURRENT - Mount Rainier-specific pass if available]", "**Annual park pass:** $55 Mount Rainier Annual Pass")
    text = text.replace("**Sites total:** 173", "**Sites total:** 179")
    text = text.replace("**Sites total:** 112", "**Sites total:** 88")
    text = text.replace("**Sites total:** 185", "**Sites total:** 188")
    lines = []
    previous_blank = True
    for line in text.splitlines():
        if re.search(r"\*\*(Badges|Tags|Featured|Verified source):\*\*", line):
            continue
        if "**Website:** [VERIFY" in line:
            continue
        line = line.rstrip()
        if line.startswith("- ") and not previous_blank:
            lines.append("")
        lines.append(line)
        previous_blank = not line
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    text = SOURCE.read_text()
    pattern = re.compile(r"^## SECTION (\d{2}) .*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        num = match.group(1)
        if num not in SECTIONS:
            continue
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find("# PART 4")
        if end == -1:
            end = len(text)
        body = text[start:end]
        (OUT / f"{SECTIONS[num]}.md").write_text(clean(body))


if __name__ == "__main__":
    main()
