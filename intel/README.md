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

## Running Stage B locally — for zero dollars

```bash
intel/test_fixture.sh          # fast, no live HTTP checks
intel/test_fixture.sh --live   # also exercises the real URL-resolution gate
```

Copies the committed [`fixtures/sample-edition.md`](fixtures/sample-edition.md)
— real, once-published Stage A output (the July 20, 2026 edition, pulled
from the `intel-raw-5` CI artifact) — into `intel/incoming/`, then runs both
`validate.py` and `write_edition.py` against it. No `ANTHROPIC_API_KEY`, no
network by default, instant feedback. This is how a schema, gate, CTA, or
template change gets tested: only a genuine research change needs a real
Stage A run.

`write_edition.py` writes to `intel/out/fixture-content/` here, **never**
`apps/web/src/content/intel/` — `sample-edition.md` is a test asset, not
content, and must never reach the real collection. The gate logic runs
entirely against the fixture's own embedded `coverageWindowStart`/`End`, not
today's actual date, so this works identically no matter when it's run.

The same path exists in CI: the `use_fixture` workflow input skips Stage A,
copies the fixture in, and redirects `write_edition.py`'s `--out` to
`intel/out/fixture-content/` — the "Commit edition" step stages
`apps/web/src/content/intel/` specifically, so with output redirected there
it naturally has nothing to commit, regardless of `dry_run`.

## Running Stage B against a real edition

Stage A's job is to drop a `YYYY-MM-DD-weekly-intel.md` file into
`intel/incoming/`. You can either run Stage A for real (needs
`ANTHROPIC_API_KEY`) or hand-place an edition there — the `--skip-research`
workflow input does the latter in CI, for reusing a real edition already
sitting in `intel/incoming/` from a prior run in the same environment.

**`--skip-research` doesn't help in CI on its own** — `intel/incoming/` is
gitignored and every workflow run starts from a fresh checkout, so there is
never a prior edition sitting there to reuse; `skip_research: true` with
nothing in `incoming/` just fails at `find_edition_file()`. That gap is
exactly why every Stage B bug in this pipeline's first weeks cost a full
Opus research run to surface — `use_fixture` above is the actual fix.

### Validate

```bash
python intel/validate.py \
  --edition ./intel/incoming/ \
  --registry ./intel/intel-place-registry.yaml \
  --guides ./apps/web/src/data/guides.ts \
  --archive ./apps/web/src/content/intel/ \
  --report ./intel/out/intel_build_report.md
```

Runs every gate in order — schema, tags, date window, URL resolution, tier
constraints, cross-edition dedupe — and writes `intel/out/intel_build_report.md`
with counts at each step. Exits non-zero on any failure; the report is
written either way, so a failed run still leaves something to read.

The tag gate checks `placeSlug` and `affectsGuides.guideSlug` against
**`intel-place-registry.yaml`**, not `guides.ts` — the registry is the
pipeline's source of truth and includes guides that are `in-progress` or
otherwise real but not yet on the public site (Crater Lake, for example).
A `guideSlug` is a hard error unless its registry `guide_status` is
`published`, `paid-guide-coming`, `pending-verification`, or `in-progress`
— `roadmap`/`coming-soon`/`out-of-scope` means there's no guide to update
yet, which is a real mistake, not a lag. `--guides` is only used for a
**warning** when a registry-valid slug hasn't reached `guides.ts` yet;
that's expected for in-progress guides and never fails the build.

**URL resolution is tri-state, not a bool.** Every `primarySourceUrl` and
`corroboratingUrl` gets HEAD'd with a browser-like User-Agent (following
redirects), retrying with GET on a 403/405/429 — but only a hard 404/410,
DNS failure, or connection refusal counts as **dead**. A 5xx, a persistent
403/429, a timeout, or an SSL quirk is **inconclusive** and gets logged,
never treated as a kill signal — news sites and CDNs routinely bot-block a
bare request from a CI IP, and that isn't the same as the article being
gone. A dead `primarySourceUrl` drops that story (same treatment as an
over-length take); a dead `corroboratingUrl` just gets stripped from the
story with a warning, the story itself survives. There's no aggregate
dead-link percentage that fails the whole edition — per-story handling
does that job instead, so one flaky outlet doesn't take four unrelated
stories down with it.

Add `--skip-url-check` to skip live checks entirely for fast local
iteration. **Never use this in CI for a real edition** — dead-link
detection is a real gate, not decoration. (The `use_fixture` path is the
one exception: `sample-edition.md`'s links were already verified when it
was captured, so its CI run always skips live checks — see below.)

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
| `fixtures/sample-edition.md` | Real Stage A output (July 20, 2026 edition), committed for zero-cost local/CI testing. Test asset, never content. |
| `test_fixture.sh` | Runs `validate.py` + `write_edition.py` against the fixture, no GitHub Actions, no API key. |
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
