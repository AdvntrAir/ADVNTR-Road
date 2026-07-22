# ADVNTR Road — Intel Pack · Stage B Render Spec
**v0.1 · July 2026 · The contract Claude Code builds against**

---

## 0. THE ONE RULE

**Stage B renders. It does not author.**

No LLM call anywhere in this pipeline. Zero AI tokens per weekly run. If a field
is missing or wrong, the build fails loudly and a human fixes Stage A — it is never
patched, inferred, or generated at render time. This is the same boundary that
governs the guide build, for the same reason.

If a rendering decision seems to require judgment, that judgment belongs in the
schema or the registry, not in the renderer.

---

## 1. INPUTS

| Input | Source | Notes |
|---|---|---|
| `YYYY-MM-DD-weekly-intel.md` | `intel/incoming/` | Markdown + YAML frontmatter, written by Stage A earlier in the same workflow run |
| `intel-place-registry.yaml` | Repo | Single source of truth for places, tags, CTA rules |
| Astro `intel` collection schema | `apps/web/src/content.config.ts` | Validation contract — there is no second schema. `intel-schema.json` is retired; the Zod schema on the live collection is authoritative |
| Last 4 published editions | `apps/web/src/content/intel/` | Dedupe reference, passed into Stage A. This is also the site's own archive — there is no separate `intel/archive/` for validated output |

**No Google Drive.** Stage A and Stage B run in the same GitHub Actions job, so the
edition file is passed on disk. There is no message queue, no indexing lag, and no
exact-path fetch logic to get wrong. Google Drive is out of this pipeline entirely —
it was never wired in and nothing here depends on it.

**Fetch discipline:** read the file matching the edition date. If it is not there,
fail with "edition not found for YYYY-MM-DD" — never fall back to the most recent
file. Rendering last week's edition as this week's is worse than rendering nothing.

---

## 2. VALIDATION GATE — fail closed

Run in order. Any failure aborts the entire build non-zero. No partial publish.

1. **Schema validation** against `intel-schema.json`.
2. **Tag validation** — every `places`, `topics`, `action` value exists in the
   registry. Unknown value = fail. Log `proposed_tags` to the build report for
   human review; do not auto-add.
3. **Date window** — hard-filter every story where `published_date` falls outside
   `[window_start, window_end]`. Dropped stories are logged, not rendered. If this
   drops the count below 3, fail.
4. **URL resolution** — HTTP HEAD (following redirects, 10s timeout) on every
   `primary_source.url` and every `corroborating_sources[].url`.
   - Primary source dead → drop the story, log it.
   - All corroborators dead but primary live → keep, log warning.
   - More than 30% of URLs dead → fail the build; something is wrong upstream.
5. **Tier constraints** — exactly one `lead`; no `brief` carries `context`;
   every story carries a `take`.
6. **Cross-edition dedupe** — any `id` present in the last 4 editions is dropped
   and logged.

Emit `intel_build_report.md` with counts at each gate. This is the audit trail.

---

## 3. CTA RESOLUTION — derived, never authored

### 3.1 Score

```
for each story:
    weight = {lead: 3, feature: 2, brief: 1}[story.tier]
    for place in story.places:
        score[place] += weight
```

### 3.2 Suppress

A place is **ineligible to anchor the CTA** if its highest-weighted story matches
any suppression condition in `cta_rules.suppression`:

- `topic` includes `safety` AND `severity` is `high`
- any of `involves_fatality`, `involves_injury`,
  `involves_search_and_rescue`, `involves_active_evacuation` is true

Also ineligible: any place with `cta_eligible: false` (currently
`national-park-system`).

### 3.3 Select

Highest remaining score anchors the edition. Ties break by `guide_status` rank:
`published` > `in-progress` > `roadmap` > `out-of-scope`.

**If every candidate place is suppressed, render NO CTA.** Do not fall back to
generic. A week heavy enough to suppress everything is a week to say nothing
promotional. This is expected behavior, not an error.

### 3.4 Resolve

Walk `cta_rules.ladder` top-down against the winning place:

| `guide_status` | `guide_type` | CTA |
|---|---|---|
| published | free | Email-gated download. **Never a purchase ask** — free anchors are free forever. |
| published | paid | Gumroad product link |
| in-progress | — | Guide preview + honest "shipping [ship_month]" |
| roadmap | — | **Waitlist capture**, not a generic guides link |
| out-of-scope / none | — | Guides index |

### 3.5 Place and track

- **One primary CTA per edition.** Never per story — per-story CTAs turn a
  publication into an ad unit.
- Web: rendered after the lead story and in the edition footer. Same CTA, two placements.
- Newsletter: footer only.
- UTM per `cta_rules.utm` template.

---

## 4. WEB RENDERER

### 4.1 Routes

| Route | Content | Index? |
|---|---|---|
| `/intel/` | Latest edition + archive list | **index** |
| `/intel/YYYY-MM-DD/` | Full edition, all tiers | **noindex** |
| `/intel/tag/[place-slug]/` | Every story ever tagged that place, reverse chron | **index** |
| `/intel/tag/[topic]/` | Every story ever tagged that topic | **index** |

**The SEO logic:** weekly editions are dated and thin and age badly. Tag hubs
accumulate and strengthen every week. The hubs are the asset — they are also the
natural internal link into the corresponding guide, which every place hub must
carry when `guide_status` is `published` or `in-progress`.

`<meta name="robots" content="noindex, follow">` on editions. `follow` matters —
link equity still flows to the hubs and guides.

### 4.2 Rendering

- Reuse the guide design tokens from `ADVNTR_Road_Build_Spec_FINAL.md` §2. Do not
  reinvent. Champagne background, Brunswick Green, Playfair/Inter/Space Mono,
  contour motif.
- `confidence: reported` renders a visible marker on the story. The reader should
  be able to see what is confirmed and what is circulating. This is a feature.
- `action` renders as a chip: `plan-change` / `book-now` / `awareness-only`.
- Tag hubs paginate at 25 stories.
- `trailhead.thin_week` → narrower layout, no attempt to fill space.

---

## 5. NEWSLETTER RENDERER

**Selects from the same JSON. Rewrites nothing.**

Structure:
1. Trailhead
2. Lead story — `take` + `context`
3. Features — `take` only
4. Briefs — scannable list, headline + `take`
5. "Read the full edition" → web edition
6. CTA (footer, one)

**Sequencing is mandatory:** web deploys first, newsletter links to it. A
newsletter that ships before the page it points at is a dead link to every
subscriber simultaneously.

**Stage the Beehiiv post as a DRAFT. Never send.** This is Gate 4 for this
pipeline. The renderer's job ends at a draft sitting in Beehiiv waiting for a
human to read it.

Publication ID: `pub_deb2e42d-316d-4040-aad7-01ca6aa0189e`

---

## 6. GUIDE-UPDATE QUEUE

For every story with a non-empty `affects_guides`:

- `impact` in `[content-stale, fee-changed, access-changed, link-broken]`
  → emit a task row to `intel_guide_updates.md`
- `impact: monitor` → log only, no task

Output a markdown table: guide slug, impact, story id, source URL, note, edition date.
Manual triage from there for now. Later this can feed Notion directly — but not
until the pipeline has run clean for a month.

This is the mechanism behind the living-edition promise: the `_redirects` layer
lets a URL be fixed without a rebuild, and this queue is what tells you a fix is needed.

---

## 7. ARCHIVE

Commit every validated edition JSON to `/intel/archive/intel-YYYY-MM-DD.json`.

Append-only. This becomes a longitudinal dataset — closure timing by park by
season, fee-change cadence, reservation-system churn. That is the raw material
for the Reservation Almanac, and it costs nothing to accumulate now.

---

## 8. FAILURE BEHAVIOR

| Condition | Behavior |
|---|---|
| Any validation gate fails | Abort non-zero. No deploy, no Beehiiv draft. Notify. |
| Drive file missing | Abort. Do not render a stale edition. |
| <3 stories after filtering | Abort with `THIN_EDITION`. Human decides whether to skip the week. |
| Beehiiv API fails after web deploy | Web stays up. Log and notify. Draft can be staged manually. |
| Unknown tag | Abort. This is how vocabulary rot is prevented. |

**Never publish partially.** A half-rendered edition under this brand is worse
than a missed week.

---

## 9. BUILD ORDER FOR CLAUDE CODE

Build in this sequence. Do not build ahead.

1. Registry loader + schema validator + `intel_build_report.md`
2. Date/URL verification gates
3. CTA resolver, including suppression
4. Web renderer — editions + tag hubs
5. GitHub Actions workflow, dry-run mode
6. **Stop. Run one real edition end to end. Publish it.**
7. Beehiiv draft renderer
8. Guide-update queue

Social renderer is out of scope entirely. Do not build three renderers before one
edition has published.
