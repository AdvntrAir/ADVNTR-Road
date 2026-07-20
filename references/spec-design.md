# ADVNTR Road — Build Spec: Design Tokens, Typography & Fonts
### Use when: fixing brand colors, typography drift, font embedding issues
### For layout bugs: use spec-components.md instead
### Buff color canonical value: #DDAD8A (NOT #DDADBA)

# ADVNTR Road — Guide PDF Build Specification
### Version FINAL · June 2026 · Tool-Agnostic
 
---
 
## PURPOSE AND USAGE
 
This document is a complete, self-contained specification for building the
ADVNTR Road guide PDF pipeline. It is written for any capable AI coding
environment or human developer — Claude Code, Codex, Cursor, Copilot, a local
model, or a developer working directly.
 
**To use this spec:** Open it in your coding environment of choice. Read it
fully before writing a single line of code. Then follow Section 11 (Build
Order) step by step. Every value, every component, every piece of logic needed
is contained in this document. The only things you need to supply externally
are:
 
- A Google Maps Static API key (stored in `.env`)
- The guide content files (prose `.md` files + `content.yaml`)
- An illustrated cover map image per guide (external, drop-in)
Do not invent token values, font names, or color codes. Everything is specified
here exactly. When in doubt, refer back to this document rather than
interpolating.
 
---
 
## CRITICAL VALUE — LOCKED
 
**Buff color:** `#DDAD8A` (warm tan/gold)
This is the canonical value. Use it everywhere `--color-buff` appears.
The design system CSS shipped with `#DDADBA` — that value is incorrect.
`#DDAD8A` is authoritative and final.
 
---
 
## TABLE OF CONTENTS
 
1. Project Overview
2. Design Tokens — Complete Reference
3. Typography System
4. Font Embedding Procedure
5. Logo Assets
6. Component Library — HTML/CSS
7. Template Structure
8. Content Schema (YAML)
9. Map Pipeline
10. Build System
11. Build Order — Step by Step
12. Error Recovery Guide
13. QA Checklist
14. New Guide Checklist
---
 
## 1. PROJECT OVERVIEW
 
### What this builds
 
A production PDF travel guide sold at $15 on Gumroad. Each guide covers one
destination in the American West or Pacific Northwest. The Olympic National
Park guide is the pilot — it establishes the template that every subsequent
guide inherits.
 
### Output
 
```
output/[guide-id]-2026.pdf    ← Final deliverable (upload to Gumroad)
output/[guide-id].html        ← Intermediate (use for debugging layout)
```
 
### Technology stack
 
| Layer | Tool |
|---|---|
| PDF renderer | WeasyPrint (Python) |
| HTML templating | Jinja2 |
| Content data | YAML + Markdown |
| Maps | Google Maps Static API |
| Font embedding | Base64 data URIs in @font-face |
| Build script | Python 3.10+ |
 
### Project directory structure
 
```
advntr-road-guides/
├── .env                             ← GOOGLE_MAPS_API_KEY (never commit)
├── .gitignore
├── build.py                         ← Main build script
├── requirements.txt
├── series.yaml                      ← Shared series list — back cover "coming next" block
│
├── design_system/                   ← Copied from ADVNTR_Road_Design_System.zip
│   ├── assets/
│   │   ├── fonts/                   ← Variable TTFs
│   │   │   ├── Inter-Variable.ttf
│   │   │   ├── Inter-Italic-Variable.ttf
│   │   │   ├── PlayfairDisplay-Variable.ttf
│   │   │   ├── PlayfairDisplay-Italic-Variable.ttf
│   │   │   ├── SpaceMono-Regular.ttf
│   │   │   ├── SpaceMono-Bold.ttf
│   │   │   └── TitanOne-Regular.ttf
│   │   └── logos/                   ← SVG logo files
│   │       ├── editorial-wordmark-dark.svg
│   │       ├── editorial-wordmark-light.svg
│   │       ├── stacked-mark-dark.svg
│   │       └── stacked-mark-light.svg
│   └── uploads/
│       └── Inter,Playfair_Display,Space_Mono,Titan_One/
│           ├── Inter/static/        ← Static Inter TTFs (preferred for WeasyPrint)
│           ├── Playfair_Display/static/  ← Static Playfair TTFs
│           ├── Space_Mono/          ← Static Space Mono TTFs
│           └── Titan_One/           ← Static Titan One TTF
│
├── template/
│   ├── guide_template.html          ← Master Jinja2 template (Section 7)
│   ├── styles/
│   │   ├── tokens.css               ← All CSS custom properties
│   │   ├── typography-embed.css     ← @font-face with base64 data URIs
│   │   ├── layout.css               ← @page rules, page margins, grid
│   │   ├── components.css           ← All components
│   │   ├── maps.css                 ← Map container and overlay
│   │   └── print.css                ← WeasyPrint page break control
│   └── assets/
│       ├── topo-lines.svg           ← Decorative topo contour SVG
│       └── icons/                   ← Inline SVG icons for PDF use
│
├── guides/
│   └── olympic-np/
│       ├── content.yaml             ← All guide data (Section 8)
│       ├── prose/
│       │   ├── 01-orientation.md
│       │   ├── 02-getting-there.md
│       │   ├── 03-where-to-camp.md
│       │   ├── 04-what-to-do.md
│       │   ├── 05-eat-resupply.md
│       │   ├── 06-coastal.md
│       │   ├── 07-field-notes.md
│       │   ├── 08-checklist.md
│       │   └── 09-before-you-go.md
│       └── assets/
│           └── cover-map.jpg        ← Illustrated map (external, drop-in)
│
└── output/                          ← Generated files (gitignore this)
```
 
---
 
## 2. DESIGN TOKENS — COMPLETE REFERENCE
 
All tokens are CSS custom properties. Define them in `template/styles/tokens.css`.
Import this file first in every HTML file.
 
```css
/* ============================================================
   ADVNTR Road Design System — Complete Token Reference
   Source: Brand Guide v1.1 + Design System export, June 2026
   ============================================================ */
 
:root {
 
  /* ── BRAND COLORS ──────────────────────────────────────────
     Never deviate from these values.
     Buff = #DDAD8A (warm tan/gold) — this is canonical.     */
 
  --color-brunswick:           #1B4436;   /* Primary identity — headings, body text */
  --color-brunswick-dark:      #122D24;   /* Hover, pressed states */
  --color-brunswick-light:     #255A47;   /* Secondary headers */
 
  --color-moss-green:          #88A33B;   /* Verified consensus — use sparingly */
  --color-moss-green-dark:     #6E8530;
  --color-moss-green-light:    #A0BF48;
 
  --color-champagne:           #F9E4C5;   /* MANDATORY page background — never white */
  --color-champagne-dark:      #F0D4A8;
  --color-champagne-light:     #FDF2E0;
 
  --color-buff:                #DDAD8A;   /* Accent ONLY — borders, rules, wordmark italic */
  --color-buff-dark:           #C49060;
  --color-buff-light:          #EDD5B0;
 
  --color-paynes-gray:         #5B768C;   /* Secondary — metadata, labels, captions */
  --color-paynes-gray-dark:    #465E72;
  --color-paynes-gray-light:   #7A96AD;
 
  --color-lake-crescent:       #4A7FA5;   /* Water features on maps */
 
  /* ── SEMANTIC TEXT ─────────────────────────────────────── */
  --text-primary:              var(--color-brunswick);
  --text-secondary:            var(--color-paynes-gray);
  --text-muted:                #8FA0A8;
  --text-accent:               var(--color-buff);
  --text-verified:             var(--color-moss-green);
  --text-on-dark:              var(--color-champagne);
  --text-on-dark-secondary:    rgba(249, 228, 197, 0.60);
 
  /* ── SEMANTIC SURFACES ─────────────────────────────────── */
  --surface-page:              var(--color-champagne);
  --surface-card:              #FFFFFF;
  --surface-dark:              var(--color-brunswick);
  --surface-moss-subtle:       #EFF5E5;
  --surface-buff-subtle:       #FAF5EE;
  --surface-gray-subtle:       #F2F5F7;
 
  /* ── SEMANTIC BORDERS ──────────────────────────────────── */
  --border-accent:             var(--color-buff);
  --border-subtle:             rgba(221, 173, 138, 0.40);
  --border-card:               #EDE0D4;
  --border-dark:               var(--color-brunswick);
 
  /* ── CONTENT TAG SEMANTICS ─────────────────────────────── */
  --tag-consensus-text:        var(--color-moss-green);
  --tag-consensus-bg:          var(--surface-moss-subtle);
  --tag-consensus-border:      rgba(136, 163, 59, 0.25);
  --tag-editorial-text:        #A06830;
  --tag-editorial-bg:          var(--surface-buff-subtle);
  --tag-editorial-border:      rgba(221, 173, 138, 0.40);
  --tag-neutral-text:          var(--color-paynes-gray);
  --tag-neutral-bg:            var(--surface-gray-subtle);
  --tag-neutral-border:        var(--border-card);
 
  /* ── TYPOGRAPHY ────────────────────────────────────────── */
  --font-display:              'Playfair Display', Georgia, 'Times New Roman', serif;
  --font-body:                 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono:                 'Space Mono', 'Courier New', Courier, monospace;
  --font-brand:                'Titan One', Impact, sans-serif;
 
  /* Type scale */
  --text-xs:     10px;   --text-sm:   12px;   --text-base: 15px;
  --text-md:     16px;   --text-lg:   18px;   --text-xl:   20px;
  --text-2xl:    24px;   --text-3xl:  28px;   --text-4xl:  34px;
  --text-5xl:    42px;   --text-6xl:  52px;
 
  /* Named role sizes */
  --text-h1:     34px;   /* PDF: fixed px, not clamp */
  --text-h2:     26px;
  --text-h3:     20px;
  --text-body:   16px;
  --text-body-sm:15px;
  --text-label:  10px;
  --text-caption:12px;
 
  /* Font weights */
  --weight-regular:  400;
  --weight-medium:   500;
  --weight-semibold: 600;
  --weight-bold:     700;
 
  /* Line heights */
  --leading-tight:   1.2;
  --leading-snug:    1.4;
  --leading-normal:  1.5;
  --leading-body:    1.7;
  --leading-loose:   1.9;
 
  /* Letter spacing */
  --tracking-tight:  -0.02em;
  --tracking-normal: 0em;
  --tracking-wide:   0.05em;
  --tracking-label:  0.15em;   /* Space Mono labels — always */
  --tracking-caps:   0.12em;
 
  /* Prose measure */
  --measure-prose:   68ch;
  --measure-narrow:  48ch;
 
  /* ── SPACING — 4px base unit ───────────────────────────── */
  --space-1:   4px;   --space-2:   8px;   --space-3:  12px;
  --space-4:  16px;   --space-5:  20px;   --space-6:  24px;
  --space-7:  28px;   --space-8:  32px;   --space-9:  36px;
  --space-10: 40px;   --space-12: 48px;   --space-14: 56px;
  --space-16: 64px;   --space-20: 80px;   --space-24: 96px;
 
  /* Semantic spacing */
  --gap-xs:      4px;    --gap-sm:     8px;    --gap-md:    16px;
  --gap-lg:     24px;    --gap-xl:    32px;    --gap-2xl:   48px;
  --pad-card:   24px;    --pad-section:64px;   --pad-page:  32px;
  --stack-xs:    8px;    --stack-sm:  12px;    --stack-md:  24px;
  --stack-lg:   40px;    --stack-xl:  64px;
 
  /* ── EFFECTS ───────────────────────────────────────────── */
 
  /* Border radii */
  --radius-xs:   3px;    --radius-sm:  4px;    --radius-md:  8px;
  --radius-lg:  12px;    --radius-xl: 16px;    --radius-pill:9999px;
 
  /* Border widths */
  --border-thin: 1px;    --border-base:1.5px;  --border-thick:2px;
 
  /* Accent rules */
  --rule-accent: 2px solid var(--color-buff);
  --rule-subtle: 1px solid var(--border-card);
  --rule-dark:   2px solid var(--color-brunswick);
 
  /* Shadows — Brunswick-tinted (not neutral gray) */
  --shadow-xs:   0 1px 2px rgba(27, 68, 54, 0.06);
  --shadow-sm:   0 1px 4px rgba(27, 68, 54, 0.08), 0 2px 8px rgba(27, 68, 54, 0.04);
  --shadow-card: 0 1px 3px rgba(27, 68, 54, 0.07), 0 4px 12px rgba(27, 68, 54, 0.06);
  --shadow-md:   0 2px 8px rgba(27, 68, 54, 0.10), 0 8px 24px rgba(27, 68, 54, 0.07);
 
  /* Icons */
  --icon-xs: 12px;  --icon-sm: 16px;  --icon-md: 20px;
  --icon-lg: 24px;  --icon-xl: 32px;
  --icon-stroke: 1.5;
 
}
```
 
---
 
## 3. TYPOGRAPHY SYSTEM
 
### Font roles — strictly enforced
 
| Font | Role | Never use for |
|---|---|---|
| Titan One | Stacked ADV/NTR/ROAD brand mark ONLY | Anything editorial, body, or UI |
| Playfair Display | All display headings (H1–H3), pull quotes, italic subheads | Body text, utility labels |
| Inter | All body text, running prose, descriptions | Headings, labels |
| Space Mono | ALL utility labels — UPPERCASE, letter-spacing 0.15em, always | Body text, headings |
 
### Scale in use (PDF — fixed px, not clamp)
 
```
Cover title:          42px  Playfair 700
Section H1:           34px  Playfair 700
Section H2:           26px  Playfair 700
Section subhead:      20px  Playfair 400 italic
Card name:            22px  Playfair 700
Pull quote:           20px  Playfair 400 italic
Body:                 16px  Inter 400, line-height 1.7
Body small:           15px  Inter 400, line-height 1.7
Utility label:        10px  Space Mono 400, uppercase, tracking 0.15em
Caption / meta:       11px  Space Mono 400, uppercase, tracking 0.12em
Brand mark:           varies  Titan One 400
```
 
### Space Mono rule — no exceptions
 
Every instance of Space Mono must be:
- `text-transform: uppercase`
- `letter-spacing: 0.15em` (labels) or `0.12em` (captions)
- `color: var(--text-secondary)` or `var(--text-muted)`
Never sentence-case. Never use as body text. Never use for headings.
 
---
 
## 4. FONT EMBEDDING PROCEDURE
 
### Why this is required
 
WeasyPrint runs in a sandboxed environment. Google Fonts `@import` URLs are
silently ignored — fonts fall back to system defaults with no error. All fonts
must be base64-encoded and embedded as data URIs in `@font-face` declarations.
 
### Variable font issue
 
Inter and Playfair Display are variable fonts. WeasyPrint may throw OS/2 table
subsetting errors when embedding them. **Use the static TTF files from
`design_system/uploads/.../static/` — they are pre-built at fixed weights and
require no fontTools processing.**
 
Titan One and Space Mono are already static — embed directly from
`design_system/assets/fonts/`.
 
### Font files to embed (use these exact paths)
 
```python
STATIC_BASE = Path('design_system/uploads/Inter,Playfair_Display,Space_Mono,Titan_One')
DS_BASE     = Path('design_system/assets/fonts')
 
FONTS = [
    # (path,                                                          family,           style,    weight)
    (STATIC_BASE/'Playfair_Display/static/PlayfairDisplay-Bold.ttf',       'Playfair Display','normal','700'),
    (STATIC_BASE/'Playfair_Display/static/PlayfairDisplay-Italic.ttf',     'Playfair Display','italic','400'),
    (STATIC_BASE/'Playfair_Display/static/PlayfairDisplay-BoldItalic.ttf', 'Playfair Display','italic','700'),
    (STATIC_BASE/'Playfair_Display/static/PlayfairDisplay-Regular.ttf',    'Playfair Display','normal','400'),
    (STATIC_BASE/'Inter/static/Inter_18pt-Regular.ttf',                    'Inter',           'normal','400'),
    (STATIC_BASE/'Inter/static/Inter_18pt-Bold.ttf',                       'Inter',           'normal','700'),
    (STATIC_BASE/'Inter/static/Inter_18pt-Medium.ttf',                     'Inter',           'normal','500'),
    (DS_BASE/'SpaceMono-Regular.ttf',                                       'Space Mono',      'normal','400'),
    (DS_BASE/'SpaceMono-Bold.ttf',                                          'Space Mono',      'normal','700'),
    (DS_BASE/'TitanOne-Regular.ttf',                                        'Titan One',       'normal','400'),
]
```
 
### Embedding function
 
```python
import base64
from pathlib import Path
 
def build_font_css(fonts):
    css = ""
    for path, family, style, weight in fonts:
        p = Path(path)
        if not p.exists():
            print(f"WARNING: Font not found: {path}")
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
    return css
```
 
### Validation test
 
Before building a full guide, render a single test page:
 
```html
<!DOCTYPE html>
<html>
<head>
<style>
  {{ font_css }}
  body { background: #F9E4C5; padding: 40px; }
  .t1 { font-family: 'Playfair Display'; font-size: 34px; font-weight: 700; }
  .t2 { font-family: 'Playfair Display'; font-size: 20px; font-style: italic; }
  .t3 { font-family: 'Inter'; font-size: 16px; line-height: 1.7; }
  .t4 { font-family: 'Space Mono'; font-size: 10px; text-transform: uppercase; letter-spacing: 0.15em; }
  .t5 { font-family: 'Titan One'; font-size: 28px; }
</style>
</head>
<body>
  <p class="t1">Hurricane Ridge</p>
  <p class="t2">Where the road ends and the view begins.</p>
  <p class="t3">The road into the park from Port Angeles climbs fast.</p>
  <p class="t4">RESERVABLE · FIRST-COME · 35FT MAX · FULL HOOKUPS</p>
  <p class="t5">ADV NTR ROAD</p>
</body>
</html>
```
 
Render it with WeasyPrint and visually confirm all 5 type styles. Do not
proceed to full template build until all fonts render correctly.
 
---
 
## 5. LOGO ASSETS
 
These SVGs are embedded inline in the HTML template. Do not use `<img src>` for
logos — WeasyPrint handles inline SVG more reliably.
 
### Editorial Wordmark — Dark (use in cover, back cover, section headers on dark bg)
 
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="280" height="48"
     viewBox="0 0 280 48" role="img" aria-label="ADVNTR Road">
  <text x="0" y="38" font-family="'Playfair Display', Georgia, serif"
        font-weight="700" font-size="32" fill="#F9E4C5">ADVNTR</text>
  <text x="194" y="38" font-family="'Playfair Display', Georgia, serif"
        font-style="italic" font-size="32" fill="#DDAD8A">Road</text>
</svg>
```
 
### Editorial Wordmark — Light (use in interior, TOC, footer on Champagne bg)
 
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="280" height="48"
     viewBox="0 0 280 48" role="img" aria-label="ADVNTR Road">
  <text x="0" y="38" font-family="'Playfair Display', Georgia, serif"
        font-weight="700" font-size="32" fill="#1B4436">ADVNTR</text>
  <text x="194" y="38" font-family="'Playfair Display', Georgia, serif"
        font-style="italic" font-size="32" fill="#DDAD8A">Road</text>
</svg>
```
 
### Stacked Mark — Dark (use on cover, back cover — NOT in editorial/body contexts)
 
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="160" height="120"
     viewBox="0 0 160 120" role="img" aria-label="ADVNTR Road">
  <text text-anchor="middle" x="80" y="42" font-family="'Titan One', Impact, sans-serif"
        font-size="38" fill="#F9E4C5" letter-spacing="2">ADV</text>
  <text text-anchor="middle" x="80" y="80" font-family="'Titan One', Impact, sans-serif"
        font-size="38" fill="#F9E4C5" letter-spacing="2">NTR</text>
  <text text-anchor="middle" x="80" y="112" font-family="'Titan One', Impact, sans-serif"
        font-size="28" fill="#DDAD8A" letter-spacing="8">ROAD</text>
</svg>
```
 
---
 
## 6. COMPONENT LIBRARY — HTML/CSS
 
All components are static HTML/CSS for WeasyPrint. No JavaScript. No React.
