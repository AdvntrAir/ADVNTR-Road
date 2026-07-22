"""
Shared deterministic core for the ADVNTR Road Intel Pack, Stage B.

validate.py and write_edition.py both import this module so the gate logic
that decides which stories survive an edition — and which place anchors the
CTA — lives in exactly one place. Neither script calls a model. Per
intel-render-spec.md section 0: Stage B renders, it does not author. If a
field is missing or malformed, fail loudly; never infer or generate content
here.

The story-level schema mirrored below (REQUIRED_STORY_STR_FIELDS, the enum
sets, etc.) must stay in sync with the `intel` collection in
apps/web/src/content.config.ts. There is no way to run that Zod schema from
Python directly (astro:content is a virtual module, only resolvable inside
an Astro build), so this is a second, hand-kept copy of the same contract —
Astro's own build re-validates with the real Zod schema once a file lands in
apps/web/src/content/intel/, which is the final backstop against the two
drifting.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

import requests
import yaml

# ---------------------------------------------------------------------------
# Constants mirroring the Zod enums in apps/web/src/content.config.ts
# ---------------------------------------------------------------------------

TIER_VALUES = {"lead", "feature", "brief"}
ACTION_VALUES = {"plan-change", "book-now", "awareness-only"}
TOPIC_SLUGS = {
    "closures", "wildfire", "weather", "wildlife", "fees",
    "reservations", "legislation", "infrastructure", "crowding",
    "conservation", "safety", "access",
}
CONFIDENCE_VALUES = {"confirmed", "reported"}
SEVERITY_VALUES = {"low", "medium", "high"}
IMPACT_VALUES = {"content-stale", "fee-changed", "access-changed", "link-broken", "monitor"}
WATCHLIST_REASONS = {
    "single-source", "date-unverifiable", "url-unresolvable",
    "outside-window", "awaiting-primary",
}
STATUS_VALUES = {"placeholder", "draft", "published"}

DEAD_URL_ABORT_PCT = 0.30
MIN_STORIES_AFTER_FILTERING = 3
HTTP_TIMEOUT_SECONDS = 10


class EditionError(Exception):
    """Raised for conditions that make the edition impossible to process at all."""


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def find_edition_file(edition_dir: Path) -> Path:
    if not edition_dir.exists():
        raise EditionError(f"edition directory not found: {edition_dir}")
    files = sorted(edition_dir.glob("*.md"))
    if not files:
        raise EditionError(f"no edition file found in {edition_dir}")
    if len(files) > 1:
        names = ", ".join(f.name for f in files)
        raise EditionError(
            f"expected exactly one edition file in {edition_dir}, found {len(files)}: {names}"
        )
    return files[0]


EDITION_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-weekly-intel\.md$")


def edition_date_from_filename(path: Path) -> str:
    """The Monday edition date, from the filename Stage A already assigned —
    not from the frontmatter's publishedDate, which (per intel-run-prompt.md
    section 4) is the run date and can fall later in the week. The
    filename/URL slug are meant to stay on the Monday date regardless of
    when publishedDate says the edition actually went out."""
    m = EDITION_FILENAME_RE.match(path.name)
    if not m:
        raise EditionError(
            f"{path.name}: filename doesn't match YYYY-MM-DD-weekly-intel.md, "
            "can't derive the edition date"
        )
    return m.group(1)


def parse_edition(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        raise EditionError(f"{path}: no parseable YAML frontmatter block")
    fm = yaml.safe_load(m.group(1))
    if not isinstance(fm, dict):
        raise EditionError(f"{path}: frontmatter did not parse to a mapping")
    body = m.group(2) or ""
    return fm, body


def load_registry(path: Path) -> dict:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "places" not in raw:
        raise EditionError(f"{path}: does not look like the intel place registry")
    return raw


def places_index(registry: dict) -> dict[str, dict]:
    return {p["slug"]: p for p in registry.get("places", [])}


def load_guide_slugs(guides_ts_path: Path) -> set[str]:
    """guides.ts is TypeScript, not JSON — pull `slug: '...'` literals with a regex
    rather than pretend Python can import it."""
    text = guides_ts_path.read_text(encoding="utf-8")
    return set(re.findall(r"slug:\s*'([^']+)'", text))


def load_archive_story_ids(archive_dir: Path) -> set[str]:
    if not archive_dir.exists():
        return set()
    ids: set[str] = set()
    for path in sorted(archive_dir.glob("*.md")):
        try:
            fm, _ = parse_edition(path)
        except EditionError:
            continue
        for story in fm.get("topStories", []) or []:
            sid = story.get("storyId")
            if sid:
                ids.add(sid)
    return ids


# ---------------------------------------------------------------------------
# Gate report
# ---------------------------------------------------------------------------

@dataclass
class GateReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, object] = field(default_factory=dict)
    kept_stories: list[dict] = field(default_factory=list)
    dropped: dict[str, list[str]] = field(default_factory=dict)  # reason -> [storyId or headline]
    cta_place_slug: Optional[str] = None
    cta_suppressed: bool = False

    @property
    def passed(self) -> bool:
        return not self.errors

    def drop(self, reason: str, story_id: str) -> None:
        self.dropped.setdefault(reason, []).append(story_id)


def _coerce_date(value, field_name: str, errors: list[str]) -> Optional[dt.date]:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value[:10])
        except ValueError:
            errors.append(f"{field_name}: invalid date {value!r}")
            return None
    errors.append(f"{field_name}: expected a date, got {type(value).__name__} ({value!r})")
    return None


def _is_url(value) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


# ---------------------------------------------------------------------------
# Gate 1 — schema
# ---------------------------------------------------------------------------

def run_schema_gate(fm: dict) -> list[str]:
    """Validates + normalizes `fm` in place. Returns issue-level errors.

    Per-story errors are folded into the returned list too, but a story that
    fails here is also dropped from fm['topStories'] so later gates never see
    a malformed object — one bad story shouldn't crash the date/URL/tier
    gates for the rest of the edition. The build still aborts overall,
    though: a dropped-for-malformed story always leaves at least one error.
    """
    errors: list[str] = []

    for f in ("title", "trailheadSummary"):
        if not isinstance(fm.get(f), str) or not fm[f].strip():
            errors.append(f"{f}: required non-empty string")

    for f in ("coverageWindowStart", "coverageWindowEnd", "publishedDate"):
        if f in fm:
            fm[f] = _coerce_date(fm[f], f, errors)
        else:
            errors.append(f"{f}: required date, missing")

    if "ctaPlaceSlug" in fm:
        errors.append(
            "ctaPlaceSlug is set in the incoming edition — Stage A must never set this, "
            "it is derived downstream by write_edition.py (scope violation, see intel-run-prompt.md section 15)"
        )
    if "ctaSuppressed" in fm:
        errors.append(
            "ctaSuppressed is set in the incoming edition — same scope violation as ctaPlaceSlug"
        )

    stories = fm.get("topStories")
    if not isinstance(stories, list) or not stories:
        errors.append("topStories: required non-empty array")
        fm["topStories"] = []
        return errors

    valid_stories = []
    for i, story in enumerate(stories):
        story_errors = _validate_story_schema(story, i)
        if story_errors:
            errors.extend(story_errors)
            # Malformed — excluded from every later gate, but still counted
            # against the edition via the errors list above.
            continue
        valid_stories.append(story)
    fm["topStories"] = valid_stories

    status = fm.get("status", "draft")
    if status not in STATUS_VALUES:
        errors.append(f"status: invalid value {status!r}")
    elif status != "draft":
        pass  # Stage A should always emit "draft"; write_edition.py enforces it regardless.

    watch_list = fm.get("watchList") or []
    for i, item in enumerate(watch_list):
        label = f"watchList[{i}]"
        if not isinstance(item.get("storyId"), str):
            errors.append(f"{label}.storyId: required string")
        if not isinstance(item.get("headline"), str):
            errors.append(f"{label}.headline: required string")
        if item.get("reason") not in WATCHLIST_REASONS:
            errors.append(f"{label}.reason: invalid value {item.get('reason')!r}")
        if "firstSeen" in item:
            item["firstSeen"] = _coerce_date(item["firstSeen"], f"{label}.firstSeen", errors)
        else:
            errors.append(f"{label}.firstSeen: required date, missing")

    harvest = fm.get("harvestStats")
    if harvest is not None:
        for f in ("candidatesFound", "clearedVerification", "droppedSingleSource",
                   "droppedOutsideWindow", "droppedDuplicate"):
            if not isinstance(harvest.get(f), (int, float)):
                errors.append(f"harvestStats.{f}: required number")

    return errors


def _validate_story_schema(story: dict, index: int) -> list[str]:
    errors: list[str] = []
    label = f"topStories[{index}]"
    story_id_for_messages = story.get("storyId") or f"{label} (no storyId)"

    def req_str(f):
        if not isinstance(story.get(f), str) or not story[f].strip():
            errors.append(f"{story_id_for_messages}: {f} required non-empty string")

    def req_bool(f):
        if not isinstance(story.get(f), bool):
            errors.append(f"{story_id_for_messages}: {f} required boolean")

    def req_enum(f, allowed):
        if story.get(f) not in allowed:
            errors.append(f"{story_id_for_messages}: {f} invalid value {story.get(f)!r}, expected one of {sorted(allowed)}")

    if not isinstance(story.get("storyRank"), (int, float)):
        errors.append(f"{story_id_for_messages}: storyRank required number")
    req_str("parkOrRegion")
    req_str("topic")
    req_str("storyId")
    req_str("placeSlug")
    req_enum("topicSlug", TOPIC_SLUGS)
    req_enum("tier", TIER_VALUES)
    req_enum("action", ACTION_VALUES)

    take = story.get("take")
    if not isinstance(take, str) or not take.strip():
        errors.append(f"{story_id_for_messages}: take required non-empty string")
    elif len(take) > 260:
        errors.append(f"{story_id_for_messages}: take exceeds 260 characters ({len(take)})")

    req_enum("confidence", CONFIDENCE_VALUES)

    if "storyDate" in story:
        story["storyDate"] = _coerce_date(story["storyDate"], f"{story_id_for_messages}.storyDate", errors)
    else:
        errors.append(f"{story_id_for_messages}: storyDate required, missing")

    if not _is_url(story.get("primarySourceUrl")):
        errors.append(f"{story_id_for_messages}: primarySourceUrl required valid http(s) URL")
    req_str("primarySourcePublisher")
    req_bool("primarySourceConfirmed")

    corroborating = story.get("corroboratingUrls", []) or []
    if not isinstance(corroborating, list) or any(not _is_url(u) for u in corroborating):
        errors.append(f"{story_id_for_messages}: corroboratingUrls must be an array of valid URLs")

    severity = story.setdefault("severity", "low")
    if severity not in SEVERITY_VALUES:
        errors.append(f"{story_id_for_messages}: severity invalid value {severity!r}")

    for f in ("involvesFatality", "involvesInjury", "involvesSearchAndRescue", "involvesActiveEvacuation"):
        story.setdefault(f, False)
        if not isinstance(story[f], bool):
            errors.append(f"{story_id_for_messages}: {f} must be boolean")

    affects = story.get("affectsGuides", []) or []
    for j, ag in enumerate(affects):
        if not isinstance(ag.get("guideSlug"), str) or not ag["guideSlug"].strip():
            errors.append(f"{story_id_for_messages}: affectsGuides[{j}].guideSlug required string")
        if ag.get("impact") not in IMPACT_VALUES:
            errors.append(f"{story_id_for_messages}: affectsGuides[{j}].impact invalid value {ag.get('impact')!r}")
    story["affectsGuides"] = affects

    # tier-dependent field: brief must not carry explorerImpact/context.
    if story.get("tier") == "brief" and story.get("explorerImpact"):
        errors.append(f"{story_id_for_messages}: brief tier must not include explorerImpact (context)")

    return errors


# ---------------------------------------------------------------------------
# Gate 2 — tags (placeSlug against the registry, guideSlug against the
# registry's guide_status — NOT against guides.ts, which is the site's public
# display list and deliberately lags the registry for in-progress guides)
# ---------------------------------------------------------------------------

# guide_status values that mean "there is an actual guide to update" —
# roadmap/coming-soon/out-of-scope places have no guide yet, so a story
# pointing affectsGuides at one of those is a real error, not a lag.
GUIDE_UPDATE_ELIGIBLE_STATUSES = {
    "published", "paid-guide-coming", "pending-verification", "in-progress",
}


def run_tag_gate(
    stories: list[dict], registry: dict, guide_slugs: Optional[set[str]]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    places = places_index(registry)

    for s in stories:
        if s["placeSlug"] not in places:
            errors.append(
                f"{s['storyId']}: placeSlug '{s['placeSlug']}' is not in intel-place-registry.yaml "
                "(unknown place — Stage A may only propose, never mint, a slug)"
            )

        for ag in s.get("affectsGuides", []) or []:
            guide_slug = ag["guideSlug"]
            place = places.get(guide_slug)
            if place is None or place.get("guide_status") not in GUIDE_UPDATE_ELIGIBLE_STATUSES:
                errors.append(
                    f"{s['storyId']}: affectsGuides.guideSlug '{guide_slug}' is not a registry "
                    "place with an active guide (guide_status must be published, "
                    "paid-guide-coming, pending-verification, or in-progress)"
                )
                continue
            # Registry says this guide is real; guides.ts is just the site's
            # public list and legitimately hasn't caught up yet for
            # in-progress guides (Crater Lake is the live example) — warn,
            # don't fail.
            if guide_slugs is not None and guide_slug not in guide_slugs:
                warnings.append(
                    f"guideSlug '{guide_slug}' is in the registry but not yet in guides.ts "
                    "(expected for in-progress guides)"
                )

    return errors, warnings


# ---------------------------------------------------------------------------
# Gate 3 — date window
# ---------------------------------------------------------------------------

def run_date_window_gate(
    stories: list[dict], window_start: dt.date, window_end: dt.date
) -> tuple[list[dict], list[str]]:
    kept, dropped = [], []
    for s in stories:
        d = s["storyDate"]
        if d is None or d < window_start or d > window_end:
            dropped.append(s["storyId"])
        else:
            kept.append(s)
    return kept, dropped


# ---------------------------------------------------------------------------
# Gate 4 — URL resolution
# ---------------------------------------------------------------------------

def default_head_check(url: str) -> bool:
    """True if the URL resolves. Falls back to GET when a host rejects HEAD
    (NPS.gov and similar CDNs sometimes 403/405 HEAD but serve GET fine)."""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=HTTP_TIMEOUT_SECONDS)
        if resp.status_code in (405, 403):
            resp = requests.get(url, allow_redirects=True, timeout=HTTP_TIMEOUT_SECONDS, stream=True)
            resp.close()
        return resp.status_code < 400
    except requests.RequestException:
        return False


def run_url_gate(
    stories: list[dict], head_fn: Callable[[str], bool] = default_head_check
) -> tuple[list[dict], list[str], int, int]:
    """Returns (kept, dropped_dead_primary, dead_url_count, total_url_count)."""
    kept, dropped = [], []
    dead_count = 0
    total_count = 0

    for s in stories:
        primary_alive = head_fn(s["primarySourceUrl"])
        total_count += 1
        if not primary_alive:
            dead_count += 1

        corroborating = s.get("corroboratingUrls", []) or []
        for url in corroborating:
            total_count += 1
            if not head_fn(url):
                dead_count += 1

        if not primary_alive:
            dropped.append(s["storyId"])
        else:
            kept.append(s)

    return kept, dropped, dead_count, total_count


# ---------------------------------------------------------------------------
# Gate 5 — tier constraints
# ---------------------------------------------------------------------------

def run_tier_gate(stories: list[dict]) -> list[str]:
    errors = []
    lead_count = sum(1 for s in stories if s["tier"] == "lead")
    if lead_count != 1:
        errors.append(f"expected exactly one lead story after filtering, found {lead_count}")
    for s in stories:
        if s["tier"] == "brief" and s.get("explorerImpact"):
            errors.append(f"{s['storyId']}: brief tier must not carry explorerImpact (context)")
    return errors


# ---------------------------------------------------------------------------
# Gate 6 — cross-edition dedupe
# ---------------------------------------------------------------------------

def run_dedupe_gate(stories: list[dict], archive_ids: set[str]) -> tuple[list[dict], list[str]]:
    kept, dropped = [], []
    for s in stories:
        if s["storyId"] in archive_ids:
            dropped.append(s["storyId"])
        else:
            kept.append(s)
    return kept, dropped


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_gates(
    fm: dict,
    registry: dict,
    guide_slugs: Optional[set[str]],
    archive_ids: set[str],
    head_fn: Callable[[str], bool] = default_head_check,
    check_urls: bool = True,
) -> GateReport:
    report = GateReport()

    report.counts["raw_story_count"] = len(fm.get("topStories") or [])
    schema_errors = run_schema_gate(fm)
    report.errors.extend(schema_errors)
    stories = fm["topStories"]  # schema gate has already dropped malformed entries
    report.counts["schema_valid_count"] = len(stories)

    if fm.get("sourceUrls"):
        report.warnings.append("sourceUrls is non-empty; primarySourceUrl per story supersedes it now")

    tag_errors, tag_warnings = run_tag_gate(stories, registry, guide_slugs)
    report.errors.extend(tag_errors)
    report.warnings.extend(tag_warnings)
    report.counts["tag_errors"] = len(tag_errors)

    window_start = fm.get("coverageWindowStart")
    window_end = fm.get("coverageWindowEnd")
    if window_start is None or window_end is None:
        # Already recorded as a schema error; nothing more to filter safely.
        report.kept_stories = []
        return report

    kept, dropped_window = run_date_window_gate(stories, window_start, window_end)
    for sid in dropped_window:
        report.drop("outside_window", sid)
    report.counts["dropped_outside_window"] = len(dropped_window)
    report.counts["kept_after_date_window"] = len(kept)

    if check_urls:
        kept, dropped_dead, dead_count, total_count = run_url_gate(kept, head_fn)
        for sid in dropped_dead:
            report.drop("dead_primary_source", sid)
        report.counts["dropped_dead_primary"] = len(dropped_dead)
        report.counts["urls_checked"] = total_count
        report.counts["urls_dead"] = dead_count
        dead_pct = (dead_count / total_count) if total_count else 0.0
        report.counts["dead_url_pct"] = round(dead_pct * 100, 1)
        if total_count and dead_pct > DEAD_URL_ABORT_PCT:
            report.errors.append(
                f"{dead_count}/{total_count} URLs ({dead_pct:.0%}) dead, exceeds the 30% threshold"
            )
    report.counts["kept_after_url_check"] = len(kept)

    tier_errors = run_tier_gate(kept)
    report.errors.extend(tier_errors)
    report.counts["lead_count"] = sum(1 for s in kept if s["tier"] == "lead")

    kept, dropped_dupe = run_dedupe_gate(kept, archive_ids)
    for sid in dropped_dupe:
        report.drop("duplicate_prior_edition", sid)
    report.counts["dropped_duplicate"] = len(dropped_dupe)

    report.kept_stories = kept
    report.counts["final_kept_count"] = len(kept)

    if len(kept) < MIN_STORIES_AFTER_FILTERING:
        report.errors.append(
            f"THIN_EDITION: only {len(kept)} stories survived filtering "
            f"(minimum {MIN_STORIES_AFTER_FILTERING}) — a human decides whether to skip this edition"
        )

    return report


# ---------------------------------------------------------------------------
# CTA resolution — derived, never authored (render-spec section 3)
# ---------------------------------------------------------------------------

def _story_matches_condition(story: dict, cond: dict) -> bool:
    severity_order = {"low": 0, "medium": 1, "high": 2}
    for key, expected in cond.items():
        if key == "severity_gte":
            if severity_order.get(story.get("severity", "low"), 0) < severity_order.get(expected, 0):
                return False
        elif key == "topic":
            if story.get("topicSlug") != expected:
                return False
        elif key.startswith("involves_"):
            camel = "involves" + "".join(w.capitalize() for w in key.split("_")[1:])
            if story.get(camel) != expected:
                return False
        else:
            return False
    return True


def _story_is_suppressing(story: dict, conditions: list[dict]) -> bool:
    return any(_story_matches_condition(story, c) for c in conditions)


def _status_rank(registry: dict, status: Optional[str]) -> int:
    ladder = registry.get("cta_rules", {}).get("ladder", [])
    for i, entry in enumerate(ladder):
        if entry.get("status") == status:
            return i
    return len(ladder)


def score_places(stories: list[dict], registry: dict) -> tuple[dict[str, int], dict[str, dict]]:
    """Sums tier weight per placeSlug. Each story carries exactly one
    placeSlug, so its full tier weight goes there — no secondary-place
    halving (intel-render-spec.md section 3.1)."""
    tier_weights = registry.get("cta_rules", {}).get("selection", {}).get("tier_weights", {
        "lead": 3, "feature": 2, "brief": 1,
    })
    scores: dict[str, int] = {}
    top_story: dict[str, dict] = {}
    for s in stories:
        w = tier_weights.get(s["tier"], 0)
        slug = s["placeSlug"]
        scores[slug] = scores.get(slug, 0) + w
        current = top_story.get(slug)
        if current is None or w > tier_weights.get(current["tier"], 0):
            top_story[slug] = s
    return scores, top_story


def resolve_cta(stories: list[dict], registry: dict) -> tuple[Optional[str], bool]:
    """Returns (ctaPlaceSlug, ctaSuppressed). If every scored place is
    suppressed or ineligible, returns (None, True) — no fallback to a
    generic CTA, per intel-place-registry.yaml cta_rules.suppression."""
    places = places_index(registry)
    scores, top_story = score_places(stories, registry)
    conditions = registry.get("cta_rules", {}).get("suppression", {}).get("conditions", [])

    candidates = []
    for slug, score in scores.items():
        place = places.get(slug)
        if place is None or not place.get("cta_eligible", True):
            continue
        if _story_is_suppressing(top_story[slug], conditions):
            continue
        candidates.append((slug, score, place))

    if not candidates:
        return None, True

    candidates.sort(key=lambda c: (-c[1], _status_rank(registry, c[2].get("guide_status"))))
    return candidates[0][0], False


# ---------------------------------------------------------------------------
# Guide-update queue
# ---------------------------------------------------------------------------

def build_guide_update_rows(stories: list[dict]) -> list[dict]:
    rows = []
    for s in stories:
        for ag in s.get("affectsGuides", []) or []:
            if ag["impact"] == "monitor":
                continue
            rows.append({
                "guideSlug": ag["guideSlug"],
                "impact": ag["impact"],
                "storyId": s["storyId"],
                "sourceUrl": s["primarySourceUrl"],
                "note": ag.get("note", ""),
            })
    return rows


def append_guide_update_queue(path: Path, rows: list[dict], edition_date: str) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", encoding="utf-8") as f:
        if is_new:
            f.write("# Intel Guide Update Queue\n\n")
            f.write("| Edition | Guide slug | Impact | Story ID | Source URL | Note |\n")
            f.write("|---|---|---|---|---|---|\n")
        for r in rows:
            note = (r["note"] or "").replace("|", "\\|").replace("\n", " ")
            f.write(
                f"| {edition_date} | {r['guideSlug']} | {r['impact']} | {r['storyId']} | "
                f"{r['sourceUrl']} | {note} |\n"
            )
