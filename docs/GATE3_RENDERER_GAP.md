# Gate 3 renderer gap — handoff note
### Discovered: 2026-07-17, during first autonomous-loop run against crater-lake-np
### Status: blocking. Not fixed. Documented per Matt's direction — no renderer code written.

---

## One-line summary

`build.py` and `template/guide_template.html` only understand the **v1 content.yaml
schema**. The Gate 2 pipeline (Claude Bridge Prompt v3.0) now produces **schema 3.0**
packages, which this renderer cannot parse correctly. It doesn't error — it silently
renders an empty shell and exits 0.

## How this was found

Ran the new `/goal`-driven build loop (per `KICKOFF.md` Step 3) against a fresh
Gate-2-passed package for **crater-lake-np**, pulled from Drive:
`2. Stage 2 - Claude - Prose Files/260717-crater-lake-np/`. Gate 2 status: **PASS**
(see `guides/crater-lake-np/build_report.md`, now in the repo).

```
.venv/bin/python build.py --guide crater-lake-np --no-maps --html-only
```

exited 0 and wrote `output/crater-lake-np.html` (3.98 MB — looks plausible at a
glance). But:

- Real place names from the guide's own prose (`Watchman`, `Mazama`) appear **zero
  times** in the rendered HTML.
- Stripped of embedded base64 fonts/images, the actual markup is ~47 KB — versus
  ~10 MB+ of real markup for a working guide like `olympic-np.html`.
- `section-header` appears only 6 times (cover/shell chrome), not once per the 11+
  sections the guide actually has.

The build produced what looks like a cover page and nothing else. No warning, no
non-zero exit, no error in the log.

## Root cause

`load_guide()` in `build.py` (line ~337) does:

```python
content = yaml.safe_load(content_path.read_text(...))
guide = content["guide"]
...
sections = guide.get("sections", [])
zones = guide.get("zones", [])
```

This assumes the **v1 schema**: everything — `sections:`, `zones:`, `campgrounds:`,
etc. — nested as children of a single top-level `guide:` block. That's what all four
currently-shipped guides (`mount-rainier-np`, `north-cascades`, `olympic-np`,
`oregon-coast`) still use, which is why they build correctly today.

`crater-lake-np/content.yaml` (schema 3.0, per
`ADVNTR_Road_Claude_Code_Build_Instructions_v2_0.md` §1 and §3) has a fundamentally
different shape:

```
top-level keys: guide, zones, itineraries, seasonal, drive_times, lodging,
                 businesses, fees, permits, cell_service, checklist, resources,
                 links, photos, visual_moments
guide sub-keys: id, format, title, subtitle, region, edition, url, published,
                verified_date, anchor, stats, map_bounds, cover_photo
```

`zones`, `itineraries`, `seasonal`, `drive_times`, `lodging`, `links`, `photos` are
**siblings** of `guide:`, not children of it. And **there is no `sections:` key at
all** — v1's explicit, author-written section list (each entry carrying `file`,
`title`, `eyebrow`, `visual: {theme, word, image, label}`) has been replaced by a
fixed 01–08 naming convention plus new structured blocks, per the spec.

So `guide.get("sections", [])` and `guide.get("zones", [])` both silently return
`[]`. The section-splicing loop never runs. Nothing under `prose/` ever gets read.
The template renders cover chrome and stops.

## What's missing (confirmed by direct inspection, not just spec-reading)

Checked `template/` for any trace of v2.0 work — none exists:

```
grep -rl "itineraries\|seasonal\|drive_times\|lodging\|trail_table\|section_opener\|Trail Table\|Seasonal Matrix" template/
# zero matches
```

Per `ADVNTR_Road_Claude_Code_Build_Instructions_v2_0.md` (pulled from Drive, full
text read this session), a real v2.0 renderer needs, beyond the schema remapping
above:

1. **Section Opener v2** (§4.1) — replaces the old divider + map-reference pair.
2. **Five new components** (§4.2–4.7): Trail Table, Complete Lodging Table
   (with a `len(rendered_rows) == len(content['lodging'])` assertion), Itinerary Day
   Plan, Seasonal Matrix, Drive Times Table, Mileage Log (corridor guides).
3. **QR code generation** (§4.8) — `segno`-based, round-trip-verified, writing
   `output/_redirects_fragment.txt`. Not implemented; `segno` isn't even imported
   anywhere in `build.py`.
4. **Two-pass page-number resolution** (§5) — needed for itinerary `refs:` and the
   TOC. Not implemented; this is a single-pass renderer.
5. **Gate 3 automated QA checklist + `build_summary.md` writer** (§6–8). Not
   implemented — confirmed separately earlier this session: no guide in `output/`,
   old or new, has ever had a `build_summary.md`, `_redirects_fragment.txt`, or QR
   assets produced.

None of this is a targeted bug. It's the entire v1→v2.0 build-system migration
described in the spec's §2 ("What's new in v2.0"), never done.

## What's in place, ready for whenever this gets fixed

The crater-lake-np Gate-2 package has been pulled into the repo (additive, no
renderer changes):

```
guides/crater-lake-np/
  content.yaml       (schema 3.0, from Drive Stage 2 output)
  build_report.md    (Gate 2 status: PASS, with 2 flags — see below)
  prose/
    01-orientation.md, 02-before-you-arrive.md, 02b-itineraries.md,
    03-where-to-sleep.md, 04a-rim-caldera-route.md, 04b-mazama-forest.md,
    04c-volcanic-outskirts.md, 05-what-to-do.md, 06-eat-resupply.md,
    07-field-notes.md, 08-before-you-leave.md
  assets/            (empty — see photo gap below)
```

Two things flagged in Gate 2's own `build_report.md`, independent of the renderer
gap, worth carrying into whatever fixes this:

- **`photos: []`** — zero photos supplied, by design. Gate 2's own report calls
  this out as blocking Gate 3 image render. Not something Stage 3 can patch by
  hand-editing `content.yaml` — needs a licensed photo set from a gap-fill pass.
- **`06-eat-resupply` word count** — 460 words vs. a 500–800 budget (8% under
  floor). Flagged as within-tolerance by Gate 2, not blocking.

## Recommendation

Scope the v1→v2.0 renderer migration as its own project — realistically a
multi-session effort (schema remapping + 5 new components + QR system + two-pass
resolution + QA checklist), not a same-session fix. The spec documents
(`ADVNTR_Road_Claude_Code_Build_Instructions_v2_0.md`, cross-referenced against
`ADVNTR_Road_Build_Spec_FINAL.md` and `ADVNTR_Road_Guide_v2_System_Spec.md`, all in
the Drive `ADVNTR Road/` folder) already specify this in enough detail to plan
directly from — start there rather than re-deriving requirements.

Until that lands, any new Gate-2 package built against Claude Bridge Prompt v3.0
(schema 3.0) will hit this same silent-empty-render failure. The four existing
guides are unaffected since their `content.yaml` files still use the v1 schema.
