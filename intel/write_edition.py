#!/usr/bin/env python3
"""
Stage B — resolves the CTA and writes the final content file for the ADVNTR
Road Weekly Intel Pack. No LLM call; this only derives ctaPlaceSlug /
ctaSuppressed from data already in the edition and the registry, per
intel-render-spec.md section 3. See intel_pipeline_lib.resolve_cta.

Runs the same deterministic gates as validate.py (imported from
intel_pipeline_lib, not reimplemented) before writing anything — if this is
ever run standalone without validate.py first, it still refuses to write a
file that wouldn't have passed. It does not take --guides or --archive
separately: --out doubles as the archive directory (apps/web/src/content/intel/
already holds every published edition), matching how the workflow invokes it.

Usage:
    python write_edition.py --edition ./incoming/ --registry ./intel-place-registry.yaml \
        --out ../apps/web/src/content/intel/ --queue ./out/intel_guide_updates.md
"""

import argparse
import json
import os
import pathlib
import sys

import yaml

from intel_pipeline_lib import (
    EditionError,
    append_guide_update_queue,
    build_guide_update_rows,
    edition_date_from_filename,
    find_edition_file,
    load_archive_story_ids,
    load_registry,
    parse_edition,
    resolve_cta,
    run_gates,
)


def _str_representer(dumper: yaml.Dumper, data: str):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


yaml.add_representer(str, _str_representer, Dumper=yaml.SafeDumper)

# Field order mirrors the schema in apps/web/src/content.config.ts / the
# intel-run-prompt.md section 15 output template, for a readable diff.
FIELD_ORDER = [
    "title", "coverageWindowStart", "coverageWindowEnd", "publishedDate",
    "thinWeek", "ctaPlaceSlug", "ctaSuppressed", "trailheadSummary",
    "topStories", "affectedGuides", "recommendedContentAngles", "sourceUrls",
    "optionalJson", "beehiivUrl", "status", "harvestStats", "watchList",
]

STORY_FIELD_ORDER = [
    "storyRank", "storyId", "parkOrRegion", "placeSlug", "topic", "topicSlug",
    "tier", "action", "take", "explorerImpact", "adventureRoadAngle",
    "confidence", "storyDate", "primarySourceUrl", "primarySourcePublisher",
    "primarySourceConfirmed", "corroboratingUrls", "severity",
    "involvesFatality", "involvesInjury", "involvesSearchAndRescue",
    "involvesActiveEvacuation", "relevanceScore", "impactScore",
    "urgencyScore", "visitorValueScore", "affectsGuides",
]


def _ordered(d: dict, order: list[str]) -> dict:
    out = {k: d[k] for k in order if k in d}
    # Anything not in the known order still gets written, just at the end —
    # better than silently dropping a field the schema allows but this list
    # forgot about.
    out.update({k: v for k, v in d.items() if k not in out})
    return out


def build_output_frontmatter(fm: dict, kept_stories: list[dict], cta_place_slug, cta_suppressed: bool) -> dict:
    out = dict(fm)
    out["topStories"] = [_ordered(s, STORY_FIELD_ORDER) for s in kept_stories]
    out["affectedGuides"] = sorted({
        ag["guideSlug"] for s in kept_stories for ag in (s.get("affectsGuides") or [])
    })
    out["sourceUrls"] = []
    out["status"] = "draft"
    out["ctaSuppressed"] = cta_suppressed
    if cta_place_slug:
        out["ctaPlaceSlug"] = cta_place_slug
    else:
        out.pop("ctaPlaceSlug", None)
    return _ordered(out, FIELD_ORDER)


def write_edition_file(out_dir: pathlib.Path, edition_date: str, frontmatter: dict, body: str) -> pathlib.Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{edition_date}-weekly-intel.md"
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False)
    content = f"---\n{yaml_text}---\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", type=pathlib.Path, required=True)
    ap.add_argument("--registry", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True,
                    help="apps/web/src/content/intel/ — destination AND archive for dedupe")
    ap.add_argument("--queue", type=pathlib.Path, required=True)
    ap.add_argument("--skip-url-check", action="store_true",
                    help="Skip live HTTP HEAD checks (fast local iteration; never use in CI)")
    args = ap.parse_args()

    try:
        edition_path = find_edition_file(args.edition)
        fm, body = parse_edition(edition_path)
        registry = load_registry(args.registry)
        archive_ids = load_archive_story_ids(args.out)
        edition_date = edition_date_from_filename(edition_path)
    except EditionError as e:
        print(f"WRITE_EDITION FAILED (before gates could run): {e}", file=sys.stderr)
        return 1

    # guide_slugs=None: that cross-check is validate.py's job (it has --guides;
    # this script doesn't, matching the workflow's actual invocation). If run
    # standalone, an unknown guideSlug will still be caught by validate.py
    # earlier in the same job.
    report = run_gates(
        fm, registry, guide_slugs=None, archive_ids=archive_ids,
        check_urls=not args.skip_url_check,
    )

    if not report.passed:
        print("WRITE_EDITION FAILED — gates did not pass, refusing to write a file:", file=sys.stderr)
        for e in report.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    cta_place_slug, cta_suppressed = resolve_cta(report.kept_stories, registry)

    # edition_date came from the filename above, not fm["publishedDate"]:
    # the filename/URL slug stay on the Monday edition date Stage A already
    # assigned, while publishedDate is the run date (intel-run-prompt.md
    # section 4) and can fall later in the week.
    out_fm = build_output_frontmatter(fm, report.kept_stories, cta_place_slug, cta_suppressed)
    out_path = write_edition_file(args.out, edition_date, out_fm, body)

    rows = build_guide_update_rows(report.kept_stories)
    append_guide_update_queue(args.queue, rows, edition_date)

    print(f"  edition:        {edition_date}")
    print(f"  stories:        {len(report.kept_stories)}")
    print(f"  ctaPlaceSlug:   {cta_place_slug or '(none)'}")
    print(f"  ctaSuppressed:  {cta_suppressed}")
    print(f"  written to:     {out_path}")
    print(f"  guide updates:  {len(rows)} row(s) appended to {args.queue}")

    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        tier_counts = {"lead": 0, "feature": 0, "brief": 0}
        for s in report.kept_stories:
            tier_counts[s["tier"]] = tier_counts.get(s["tier"], 0) + 1
        summary = {
            "edition_date": edition_date,
            "title": fm.get("title", ""),
            "tier_counts": tier_counts,
            "cta_place_slug": cta_place_slug,
            "cta_suppressed": cta_suppressed,
            "thin_week": bool(fm.get("thinWeek", False)),
            "harvest_stats": fm.get("harvestStats") or {},
            "content_file_path": str(out_path),
        }
        with open(gh_out, "a") as f:
            f.write(f"edition_date={edition_date}\n")
            f.write("summary_json<<GHADELIM\n")
            f.write(json.dumps(summary))
            f.write("\nGHADELIM\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
