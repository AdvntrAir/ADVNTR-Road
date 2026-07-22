# ADVNTR Road — Intel Pack pipeline

Weekly national-park intel: Stage A researches and writes one Markdown file
with YAML frontmatter; Stage B validates it, resolves the CTA, and commits
it into the site's `intel` content collection. Full contract:
[`intel-render-spec.md`](intel-render-spec.md). Voice and output format for
Stage A: [`intel-run-prompt.md`](intel-run-prompt.md). Places and closed
vocabularies: [`intel-place-registry.yaml`](intel-place-registry.yaml).

**The one rule:** `stage_a_research.py` is the only thing here that calls a
model. `validate.py` and `write_edition.py` are deterministic — no network
call except the HTTP HEAD/GET link checks, no inference, no generated text.
If a field is missing or malformed, they fail loudly instead of guessing.

## Setup

```bash
pip install -r intel/requirements.txt
```

Needs Python 3.9+ (matches the `python-version: "3.12"` pinned in
`.github/workflows/intel-pipeline.yml`; anything 3.9+ works locally).

## Running Stage B locally

Stage A's job is to drop a `YYYY-MM-DD-weekly-intel.md` file into
`intel/incoming/`. For local Stage B work you can either run Stage A for
real (needs `ANTHROPIC_API_KEY`) or hand-place a fixture there — the
`--skip-research` workflow input does the latter in CI.

### Validate

```bash
python intel/validate.py \
  --edition ./intel/incoming/ \
  --registry ./intel/intel-place-registry.yaml \
  --guides ./apps/web/src/data/guides.ts \
  --archive ./apps/web/src/content/intel/ \
  --report ./intel/out/intel_build_report.md
```

Runs every gate in order — schema, tags (`placeSlug`/`affectsGuides.guideSlug`
against the registry and `guides.ts`), date window, URL resolution, tier
constraints, cross-edition dedupe — and writes `intel/out/intel_build_report.md`
with counts at each step. Exits non-zero on any failure; the report is
written either way, so a failed run still leaves something to read.

Add `--skip-url-check` to skip the live HTTP HEAD/GET checks for fast local
iteration. **Never use this in CI** — dead-link detection is a real gate,
not decoration.

### Write the edition

```bash
python intel/write_edition.py \
  --edition ./intel/incoming/ \
  --registry ./intel/intel-place-registry.yaml \
  --out ./apps/web/src/content/intel/ \
  --queue ./intel/out/intel_guide_updates.md
```

Re-runs the same gates (imported from `intel_pipeline_lib.py`, not
reimplemented), resolves `ctaPlaceSlug`/`ctaSuppressed` (tier-weighted
scoring + suppression, see below), and writes the final
`YYYY-MM-DD-weekly-intel.md` into `apps/web/src/content/intel/` with
`status: "draft"`. A human promotes it to `"published"` by hand — this
script never does. It also appends any `affectsGuides` rows (excluding
`impact: monitor`) to `intel/out/intel_guide_updates.md`.

`--out` doubles as the archive directory for cross-edition dedupe — it's
the same folder as the destination, since every past edition already lives
there. There's no separate `--archive` flag on this script, matching how
`.github/workflows/intel-pipeline.yml` actually calls it.

It refuses to write anything if the gates don't pass, even run standalone
without `validate.py` first — it just won't catch an unknown
`affectsGuides.guideSlug` in that case, since that specific check needs
`--guides`, which only `validate.py` receives from the workflow.

### Both scripts, dry run

```bash
python intel/validate.py --edition ./intel/incoming/ --registry ./intel/intel-place-registry.yaml \
  --guides ./apps/web/src/data/guides.ts --archive ./apps/web/src/content/intel/ \
  --report ./intel/out/intel_build_report.md --skip-url-check

python intel/write_edition.py --edition ./intel/incoming/ --registry ./intel/intel-place-registry.yaml \
  --out /tmp/intel-dry-run --queue /tmp/intel-dry-run-queue.md --skip-url-check
```

Point `--out` at a scratch directory to see what would be written without
touching `apps/web/src/content/intel/`.

## CTA resolution

`intel_pipeline_lib.resolve_cta()` sums tier weight (lead=3, feature=2,
brief=1, from the registry's `cta_rules.selection.tier_weights`) per
`placeSlug`, drops any place that's `cta_eligible: false` or whose
highest-weighted story matches a `cta_rules.suppression` condition (high
severity + `safety` topic, or any `involvesFatality` /`involvesInjury` /
`involvesSearchAndRescue` /`involvesActiveEvacuation` flag), and picks the
highest remaining score. If every candidate is suppressed or ineligible,
the edition gets `ctaSuppressed: true` and no `ctaPlaceSlug` at all —
**never** a fallback to a generic guides link. That's tested directly in
[`tests/test_cta_suppression.py`](tests/test_cta_suppression.py):

```bash
python intel/tests/test_cta_suppression.py
```

Uses the fixture at
[`tests/fixtures/2026-08-03-cta-suppression.md`](tests/fixtures/2026-08-03-cta-suppression.md) —
a search-and-rescue story on the edition's only real candidate place — and
asserts both that no CTA renders in that case, and (regression guard) that
suppressing one place doesn't suppress a different, unrelated place in the
same edition. Plain `assert` statements, no pytest dependency; run it
directly with `python3`.

## Files

| File | Role |
|---|---|
| `stage_a_research.py` | Stage A — the only model call. Not modified by this work. |
| `intel_pipeline_lib.py` | Shared gate + CTA logic used by both Stage B scripts. |
| `validate.py` | Stage B, part 1 — runs the gates, writes the build report. |
| `write_edition.py` | Stage B, part 2 — resolves the CTA, writes the content file + guide-update queue rows. |
| `intel-place-registry.yaml` | Places, closed tag vocabularies, CTA ladder. Human-edited only. |
| `intel-run-prompt.md` | Stage A's system prompt — voice, verification rules, output format. |
| `intel-render-spec.md` | The contract Stage B builds against. |
| `tests/` | `test_cta_suppression.py` + its fixture. |
| `incoming/`, `out/` | Gitignored working directories — Stage A drops, Stage B reports. |

## What this validator can't check

`validate.py`'s schema gate is a hand-kept mirror of the Zod schema in
`apps/web/src/content.config.ts` — there's no way to invoke that Zod schema
from Python directly (`astro:content` is a virtual module, only resolvable
inside an Astro build). The two are kept in sync by hand. Astro's own build
re-validates with the real schema once a file lands in
`apps/web/src/content/intel/`, which is the final backstop if they ever
drift — run `astro check` / `astro build` in `apps/web/` after any schema
change on either side.
