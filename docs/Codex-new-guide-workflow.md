# ADVNTR Road New Guide Workflow

Use this workflow for every new ADVNTR Road destination guide after the reusable build system is in place.

## 1. Prepare the Destination Research File

Start from `docs/ADVNTR_Road_Destination_Template.md`.

Create one completed `destination.md` file for the new guide. Fill in as much verified research as possible:

- Guide metadata: destination name, guide slug, region, edition, verified date, stats, map bounds
- Experience zones: 1 to 5 distinct destination areas
- Section research and prose notes for Sections 01 through 08
- Campground data with verified reservation, hookup, pet, length, fee, and source details
- Gateway towns, businesses, fees, permits, checklist, and resources
- Map markers for overview, gateway towns, campgrounds, and zones
- Research quality flags and any known data gaps

Do not invent missing information. Mark unknown fields clearly so they can be verified before publication.

## 2. Start a New Build Chat

Open a new Codex chat in the `advntr-road-guides` project/workspace.

Upload or point Codex to the completed `destination.md` file.

Use a short request like:

```text
Build this as a new ADVNTR Road guide using the existing guide system.
Guide slug: [destination-id]
```

If the guide slug is obvious from the file, Codex can infer it. Otherwise provide it explicitly, for example:

```text
north-cascades
mount-rainier
oregon-coast
columbia-river-gorge
```

## 3. Codex Creates the Guide Files

Codex should create:

```text
guides/[destination-id]/
├── content.yaml
├── prose/
│   ├── 01-orientation.md
│   ├── 02-before-you-arrive.md
│   ├── 03-where-to-sleep.md
│   ├── 04a-[zone].md
│   ├── 04b-[zone].md
│   ├── 04c-[zone].md
│   ├── 04d-[zone].md
│   ├── 04e-[zone].md
│   ├── 05-what-to-do.md
│   ├── 06-eat-resupply.md
│   ├── 07-field-notes.md
│   └── 08-before-you-leave-home.md
└── assets/
    ├── cover-photo.png
    └── image-attributions.json
```

Only create the `04x` zone files that match the destination's actual zone count.

The cover is a full-bleed photo, not an illustration — pick the single strongest, most
recognizable shot of the destination (same licensing rules as every other photo in the
guide; see Image Sourcing in the destination template). Set it as `guide.cover_photo` in
`content.yaml`. If no cover photo is ready yet, omit `cover_photo` and the guide still
builds — the cover just renders without an image.

`content.yaml` must set `guide.cover_word` (a list of 1-2 short lines for the cover's big
display type — e.g. `["North", "Cascades"]`). If it's missing, the build still succeeds but
falls back to just the first word of the title, which reads wrong. `guide.cover_footer` is
optional. Every prose-sourced photo and every `campgrounds[].image` /
`businesses[].image` must be public domain or CC-licensed, with the source recorded in
`assets/image-attributions.json` — see the destination template's Image Sourcing section.

## 4. Update Shared Series Data

Update `series.yaml` only when the new guide should appear in the shared back-cover "More from ADVNTR Road" list.

This file is project-level. Changing it affects every guide rebuilt afterward.

## 5. Run Build Checks

Use the project virtual environment:

```bash
.venv/bin/python build.py --guide [destination-id] --font-test
.venv/bin/python build.py --guide [destination-id] --no-maps
```

Check the generated HTML and PDF:

```text
output/[destination-id].html
output/[destination-id]-2026.pdf
```

Confirm:

- Section order is `01`, `02`, `03`, `04A` through `04x`, then `05`, `06`, `07`, `08`
- Gateway cards render only if `gateway_towns` exists
- Zone highlights render only if `zone.highlights` exists
- Business cards render only if `businesses` exists
- Fees and permits render only if those blocks exist
- Checklist and resources render only if those blocks exist
- No missing prose warnings appear for required files

## 6. Run the Full Map Build

The full build calls Google Static Maps using the API key in `.env` and the guide's map coordinates.

Run only after approving that network/API step:

```bash
.venv/bin/python build.py --guide [destination-id]
```

Confirm the final HTML contains embedded map images and the final PDF renders correctly.

## 6a. Known WeasyPrint Gotcha — Read This Before Touching `template/styles/*.css`

**Never combine `display: grid` with `page-break-inside: avoid` / `break-inside: avoid` on the
same element, especially on something that's the first element rendered after a section
opener's page-type transition.** This combination has caused two separate, hard-to-diagnose
bugs in this codebase (a section-opener photo collapsing to half-height, and a heading/card
losing its left margin and going flush to the page edge several pages into a section). Both
took hours to trace because the symptom (a missing margin or a corrupted photo box) appears
on a *different* element than the one with the broken CSS.

If a layout element needs both a multi-column layout and "don't split this across a page
break," use `display: flex` for the columns instead of `display: grid`. Flexbox has not
shown this bug in this codebase; grid has, every time it's been tried in this exact
combination. `.callout-grid` and `.business-card` were both converted from grid to flex for
exactly this reason — don't convert them back without re-testing across a full rebuild.

If you ever see a heading, card, or photo on a content page lose its left margin and sit
flush against the page edge: that's this bug. Find whichever `display: grid` element appears
earliest after the most recent page break/section-opener and convert it to flex.

## 7. Final QA

Before publication, review the PDF manually:

- Fonts render correctly: Playfair Display, Inter, Space Mono, Titan One
- Page background is Champagne `#F9E4C5`
- Accent color is Buff `#DDAD8A`
- Cover is a full-bleed photo (not Brunswick solid) with legible title text over it; back
  cover is full-bleed Brunswick
- No cards split awkwardly across pages (campground cards, business cards, and the rig-size
  table should each move whole to the next page rather than split mid-card/mid-row — render
  every page to PNG and check, don't just skim the text extraction)
- No card is exiled onto its own mostly-blank page (a sign of the grid+break-inside bug above)
- No orphaned section headers, and no heading/card sitting flush against the page edge with
  no left margin (the same bug, different symptom)
- Section openers: confirm headline text is legible against the photo on *every* theme used
  (photo/blue/dark/cream) — a transparent or weak wash gradient lets dark or light text
  disappear into a busy photo
- Campground cards include reservation method, hookups, max length, pets, verified date, and editorial note
- Maps are not blank and markers are approximately correct
- No source names appear in published prose
- Fees, permits, and campground data are verified for the guide edition

## 8. Publish Handoff

Final deliverable:

```text
output/[destination-id]-2026.pdf
```

Use this PDF for Gumroad upload.

Keep the HTML output for layout debugging:

```text
output/[destination-id].html
```

After publishing, update any external launch systems: Gumroad product page, Beehiiv post, UTM links, affiliate links, and internal traffic tracking.

## Repeatable Prompt

Use this prompt in a new Codex chat:

```text
I uploaded a completed ADVNTR Road destination.md file.
Build it as a new guide using the existing advntr-road-guides system.

Please:
1. Extract content.yaml and prose files from the destination file.
2. Create guides/[destination-id]/ with the correct schema.
3. Run the font test and no-map build.
4. Ask for approval before running the full Google Maps build.
5. Report the final output files and any QA issues.
```
