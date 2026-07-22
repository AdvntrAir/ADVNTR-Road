#!/usr/bin/env python3
"""
Proves CTA suppression works: a high-severity safety story on the
edition's only real candidate place must produce NO CTA at all — never a
fallback to a generic guides link. See intel-place-registry.yaml
cta_rules.suppression and intel-render-spec.md section 3.2.

Plain assertions, no pytest — the repo doesn't carry that dependency and
this doesn't need a framework. Run directly:

    python intel/tests/test_cta_suppression.py

Uses a fake head_fn so it never makes a real network call — this test is
about CTA math, not link liveness (that's exercised separately, live,
by validate.py itself).
"""

import copy
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

from intel_pipeline_lib import (  # noqa: E402
    load_registry,
    parse_edition,
    resolve_cta,
    run_gates,
)
from write_edition import build_output_frontmatter  # noqa: E402

FIXTURE = HERE / "fixtures" / "2026-08-03-cta-suppression.md"
REGISTRY = HERE.parent / "intel-place-registry.yaml"

ALWAYS_ALIVE = lambda url: True  # noqa: E731 — deliberately not testing link liveness here


def test_all_candidates_suppressed_means_no_cta():
    fm, _ = parse_edition(FIXTURE)
    registry = load_registry(REGISTRY)

    report = run_gates(fm, registry, guide_slugs=None, archive_ids=set(), head_fn=ALWAYS_ALIVE)
    assert report.passed, f"fixture should validate cleanly, got errors: {report.errors}"
    assert len(report.kept_stories) == 3, f"expected all 3 stories kept, got {len(report.kept_stories)}"

    cta_place_slug, cta_suppressed = resolve_cta(report.kept_stories, registry)

    assert cta_suppressed is True, "the only scoring, eligible place has a high-severity safety story — must suppress"
    assert cta_place_slug is None, "must not fall back to any place, generic or otherwise"

    out_fm = build_output_frontmatter(fm, report.kept_stories, cta_place_slug, cta_suppressed)
    assert out_fm["ctaSuppressed"] is True
    assert "ctaPlaceSlug" not in out_fm, "ctaPlaceSlug must be omitted entirely, not set to null/empty"

    print("PASS: all-candidates-suppressed -> ctaSuppressed=true, ctaPlaceSlug omitted")


def test_suppression_is_per_place_not_global():
    """Regression guard: suppressing the Narrows story should not suppress a
    *different*, unsuppressed place that also has stories this week."""
    fm, _ = parse_edition(FIXTURE)
    registry = load_registry(REGISTRY)

    fm = copy.deepcopy(fm)
    stories = fm["topStories"]

    # Remove the safety flags on the Zion lead story...
    stories[0]["severity"] = "moderate"
    stories[0]["involvesSearchAndRescue"] = False
    # ...and move the feature story to a real, cta_eligible place scoring
    # lower than Zion's lead weight (2 vs 3), so Zion should still win, now
    # unsuppressed, rather than the edition falling through by accident.
    stories[1]["placeSlug"] = "oregon-coast"

    report = run_gates(fm, registry, guide_slugs=None, archive_ids=set(), head_fn=ALWAYS_ALIVE)
    assert report.passed, f"errors: {report.errors}"

    cta_place_slug, cta_suppressed = resolve_cta(report.kept_stories, registry)
    assert cta_suppressed is False
    assert cta_place_slug == "zion-national-park", f"expected zion-national-park to win, got {cta_place_slug}"

    print("PASS: suppression is scoped to the flagged place, not the whole edition")


if __name__ == "__main__":
    test_all_candidates_suppressed_means_no_cta()
    test_suppression_is_per_place_not_global()
    print("\nAll CTA suppression tests passed.")
