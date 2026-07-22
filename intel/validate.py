#!/usr/bin/env python3
"""
Stage B — validation gate for the ADVNTR Road Weekly Intel Pack.

Parses the Stage-A edition sitting in --edition, runs it through every gate
in intel_pipeline_lib.run_gates (schema, tags, date window, URL resolution,
tier constraints, cross-edition dedupe), and writes an audit-trail report.
No LLM call. If a field is missing or malformed, this fails loudly instead
of silently patching it — see intel-render-spec.md section 0.

Usage:
    python validate.py --edition ./incoming/ --registry ./intel-place-registry.yaml \
        --guides ../apps/web/src/data/guides.ts --archive ../apps/web/src/content/intel/ \
        --report ./out/intel_build_report.md
"""

import argparse
import pathlib
import sys

from intel_pipeline_lib import (
    EditionError,
    find_edition_file,
    load_archive_story_ids,
    load_guide_slugs,
    load_registry,
    parse_edition,
    run_gates,
)

HERE = pathlib.Path(__file__).parent


def build_report(edition_path: pathlib.Path, report) -> str:
    lines = [
        f"# Intel Build Report — {edition_path.name}",
        "",
        f"**Result: {'PASS' if report.passed else 'FAIL'}**",
        "",
        "## Gate counts",
        "",
        f"- Raw stories in edition: {report.counts.get('raw_story_count', '?')}",
        f"- Passed schema validation: {report.counts.get('schema_valid_count', '?')}",
        f"- Tag/registry errors: {report.counts.get('tag_errors', '?')}",
        f"- Dropped, outside coverage window: {report.counts.get('dropped_outside_window', '?')}",
        f"- Kept after date window: {report.counts.get('kept_after_date_window', '?')}",
    ]
    if "urls_checked" in report.counts:
        lines += [
            f"- URLs checked: {report.counts.get('urls_checked')}",
            f"- URLs dead: {report.counts.get('urls_dead')} ({report.counts.get('dead_url_pct')}%)",
            f"- Dropped, dead primary source: {report.counts.get('dropped_dead_primary', '?')}",
        ]
    lines += [
        f"- Kept after URL check: {report.counts.get('kept_after_url_check', '?')}",
        f"- Lead stories after filtering: {report.counts.get('lead_count', '?')}",
        f"- Dropped, duplicate of a prior edition: {report.counts.get('dropped_duplicate', '?')}",
        f"- **Final story count: {report.counts.get('final_kept_count', '?')}**",
        "",
    ]

    if report.dropped:
        lines.append("## Dropped stories")
        lines.append("")
        for reason, ids in report.dropped.items():
            lines.append(f"- **{reason}**: {', '.join(ids)}")
        lines.append("")

    if report.errors:
        lines.append("## Errors (build fails)")
        lines.append("")
        for e in report.errors:
            lines.append(f"- {e}")
        lines.append("")

    if report.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in report.warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", type=pathlib.Path, required=True,
                    help="Directory containing exactly one Stage-A edition .md file")
    ap.add_argument("--registry", type=pathlib.Path, required=True)
    ap.add_argument("--guides", type=pathlib.Path, default=None,
                    help="apps/web/src/data/guides.ts, for a soft warning when a registry-valid "
                         "affectsGuides.guideSlug hasn't reached the site's public list yet")
    ap.add_argument("--archive", type=pathlib.Path, required=True,
                    help="apps/web/src/content/intel/, for cross-edition dedupe")
    ap.add_argument("--report", type=pathlib.Path, required=True)
    ap.add_argument("--skip-url-check", action="store_true",
                    help="Skip live HTTP HEAD checks (fast local iteration; never use in CI)")
    args = ap.parse_args()

    try:
        edition_path = find_edition_file(args.edition)
        fm, _ = parse_edition(edition_path)
        registry = load_registry(args.registry)
        guide_slugs = load_guide_slugs(args.guides) if args.guides else None
        archive_ids = load_archive_story_ids(args.archive)
    except EditionError as e:
        print(f"VALIDATE FAILED (before gates could run): {e}", file=sys.stderr)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(f"# Intel Build Report\n\n**Result: FAIL**\n\n- {e}\n")
        return 1

    report = run_gates(
        fm, registry, guide_slugs, archive_ids,
        check_urls=not args.skip_url_check,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(build_report(edition_path, report))

    print(f"  edition:  {edition_path.name}")
    print(f"  result:   {'PASS' if report.passed else 'FAIL'}")
    print(f"  stories:  {report.counts.get('final_kept_count', '?')} kept "
          f"of {report.counts.get('raw_story_count', '?')} raw")
    print(f"  report:   {args.report}")

    if not report.passed:
        print("\n  errors:", file=sys.stderr)
        for e in report.errors:
            print(f"    - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
