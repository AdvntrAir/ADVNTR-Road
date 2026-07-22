#!/usr/bin/env python3
"""
Stage A — research run for the ADVNTR Road Weekly Intel Pack.

Calls the Anthropic API with server-side web search, then writes a Markdown
file with YAML frontmatter matching the site's Astro `intel` collection.

This is the ONLY place in the pipeline that makes an LLM call. Everything
downstream is deterministic.

Usage:
    python stage_a_research.py --out ./incoming/ --archive ../apps/web/src/content/intel/
"""

import argparse
import datetime as dt
import os
import pathlib
import re
import sys
import time

import anthropic
import yaml

HERE = pathlib.Path(__file__).parent
MODEL = os.environ.get("INTEL_MODEL", "claude-opus-4-8")
MAX_TOKENS = 32000
MAX_CONTINUATIONS = 20   # ceiling on pause_turn resumes; a runaway loop is a cost bug
ARCHIVE_LOOKBACK = 4

# Transient-failure retry policy for the streaming call (on top of whatever
# the SDK's own max_retries already absorbed before ever raising to us).
# Anthropic capacity issues, not our code -- but an unattended weekly run
# has to survive them. Sum of delays is ~185s (~3 min), comfortably inside
# the "~10 minutes of added wait" budget against the 45-minute job timeout.
TRANSIENT_BACKOFF_SECONDS = [5, 15, 45, 120]
TRANSIENT_STATUS_CODES = {429, 529}
TRANSIENT_ERROR_TYPES = {"overloaded_error", "rate_limit_error"}


def is_transient_error(exc: BaseException) -> bool:
    """Anthropic capacity/rate-limit issues worth retrying ourselves.

    Deliberately an allowlist, not a denylist: authentication errors,
    invalid_request_error, and billing/insufficient-credits errors don't
    match anything here and so are never retried -- they won't fix
    themselves, and retrying just burns the backoff budget. Anything
    unrecognized also falls through to "not transient" and fails fast,
    which is the safe default.
    """
    if isinstance(exc, anthropic.APIConnectionError):
        return True
    if isinstance(exc, anthropic.APIStatusError):
        if exc.status_code in TRANSIENT_STATUS_CODES:
            return True
        if exc.type in TRANSIENT_ERROR_TYPES:
            return True
    return False


def monday_on_or_before(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def load_recent_story_ids(archive_dir: pathlib.Path, n: int) -> list[str]:
    """storyId values from the last n editions, for cross-edition dedupe."""
    if not archive_dir.exists():
        return []
    editions = sorted(archive_dir.glob("*.md"), reverse=True)[:n]
    ids = []
    for path in editions:
        try:
            text = path.read_text()
            m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            ids += [s.get("storyId") for s in fm.get("topStories", []) if s.get("storyId")]
        except yaml.YAMLError as e:
            print(f"  warn: could not parse {path.name}: {e}", file=sys.stderr)
    return ids


def extract_markdown(text: str) -> str:
    """
    The prompt says emit a bare Markdown file. Models wrap it in fences anyway,
    sometimes with a preamble line. Be maximally forgiving: throw away anything
    that isn't the frontmatter block and what follows it.
    """
    lines = text.strip().split("\n")

    def is_fence(s: str) -> bool:
        return s.strip().startswith("```")

    # Drop leading fences, blanks, and any preamble prose before the opening ---
    while lines and lines[0].strip() != "---":
        if is_fence(lines[0]) or not lines[0].strip() or not any(
            l.strip() == "---" for l in lines[1:]
        ):
            if not any(l.strip() == "---" for l in lines):
                raise ValueError("no YAML frontmatter delimiter found in output")
        lines.pop(0)

    if not lines:
        raise ValueError("no YAML frontmatter found in output")

    # Drop trailing fences and blanks
    while lines and (is_fence(lines[-1]) or not lines[-1].strip()):
        lines.pop()

    # Locate the closing delimiter
    close_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        raise ValueError("frontmatter opened but never closed")

    # Strip any stray fence lines from the body
    body = [l for l in lines[close_idx + 1:] if not is_fence(l)]

    return "\n".join(lines[: close_idx + 1] + body).strip() + "\n"


def validate_frontmatter_parses(md: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", md, re.DOTALL)
    if not m:
        raise ValueError("output has no parseable frontmatter block")
    fm = yaml.safe_load(m.group(1))
    if not isinstance(fm, dict):
        raise ValueError("frontmatter did not parse to a mapping")
    return fm


def stream_once(client: anthropic.Anthropic, **kwargs) -> tuple["anthropic.types.Message", int]:
    """One client.messages.stream(...) call: drains it, prints the
    search-count heartbeat, and returns (final_message, searches). Raises
    on any error, transient or not — retry policy lives in the caller."""
    searches = 0
    with client.messages.stream(**kwargs) as stream:
        for event in stream:
            # Heartbeat so a 10-15 minute run doesn't look hung in the
            # Actions log, and so search volume is visible live.
            if event.type == "content_block_start":
                block_type = getattr(event.content_block, "type", None)
                if block_type == "server_tool_use":
                    searches += 1
                    print(f"  search {searches}...", file=sys.stderr, flush=True)
        return stream.get_final_message(), searches


def stream_with_retry(client: anthropic.Anthropic, **kwargs) -> tuple["anthropic.types.Message", int]:
    """Runs stream_once, retrying from scratch on a transient failure with
    TRANSIENT_BACKOFF_SECONDS backoff. Never resumes a partial stream — a
    transient failure restarts the whole request, discarding that attempt's
    partial search count entirely. Losing a couple of searches to a retry
    is cheap next to failing an unattended weekly run. Non-transient errors
    (auth, invalid request, billing) propagate on the first attempt."""
    last_exc: BaseException | None = None
    total_attempts = 1 + len(TRANSIENT_BACKOFF_SECONDS)

    for attempt_num in range(total_attempts):
        if attempt_num > 0:
            delay = TRANSIENT_BACKOFF_SECONDS[attempt_num - 1]
            print(
                f"  transient error ({last_exc!r}), retrying in {delay}s "
                f"(attempt {attempt_num + 1}/{total_attempts})...",
                file=sys.stderr, flush=True,
            )
            time.sleep(delay)
        try:
            return stream_once(client, **kwargs)
        except Exception as e:
            if not is_transient_error(e):
                raise
            last_exc = e

    raise RuntimeError(
        f"exhausted {total_attempts} attempts after repeated transient API errors: {last_exc!r}"
    ) from last_exc


def run(edition_date: dt.date, out_dir: pathlib.Path, archive_dir: pathlib.Path) -> pathlib.Path:
    window_end = dt.date.today()
    window_start = window_end - dt.timedelta(days=7)

    system_prompt = (HERE / "intel-run-prompt.md").read_text()
    registry = (HERE / "intel-place-registry.yaml").read_text()
    recent_ids = load_recent_story_ids(archive_dir, ARCHIVE_LOOKBACK)

    user_msg = f"""Produce the Weekly Intel Pack.

RUN PARAMETERS
  edition_date: {edition_date.isoformat()}
  window_start: {window_start.isoformat()}
  window_end:   {window_end.isoformat()}

storyId VALUES FROM THE LAST {ARCHIVE_LOOKBACK} EDITIONS — do not re-report these:
{yaml.safe_dump(recent_ids) if recent_ids else "  (none — this is the first edition)"}

PLACE REGISTRY — authoritative. placeSlug and topicSlug must come from here:
```yaml
{registry}
```

Research the window, verify against primary sources, and emit the Markdown file
with YAML frontmatter per section 15. Nothing before it, nothing after it."""

    # max_retries=5: explicit and generous. The SDK retries some errors
    # (connection issues, 429, 5xx) itself before ever raising to us;
    # stream_with_retry above is the second layer, for a stream that dies
    # after already starting to receive events, which the SDK's own
    # pre-request retry doesn't cover.
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], max_retries=5)
    messages = [{"role": "user", "content": user_msg}]
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 40}]

    # STREAMING IS REQUIRED. The SDK rejects a non-streaming request whose
    # max_tokens implies a possible >10 minute response, which this always does.
    #
    # Server-side tools execute inside the API. The only continuation case is
    # stop_reason == "pause_turn" on a long-running search sequence: send the
    # assistant content straight back, with no synthetic user turn.
    total_searches = 0
    for attempt in range(MAX_CONTINUATIONS):
        resp, searches = stream_with_retry(
            client,
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )
        total_searches += searches

        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            print(f"  paused mid-research, resuming ({attempt + 1})...", file=sys.stderr)
            continue

        if resp.stop_reason == "max_tokens":
            raise RuntimeError(
                "model hit max_tokens before finishing. Reduce the story ceiling "
                "or raise MAX_TOKENS."
            )

        text = "".join(b.text for b in resp.content if b.type == "text")
        print(f"  research complete — {total_searches} searches", file=sys.stderr, flush=True)
        break
    else:
        raise RuntimeError(f"hit MAX_CONTINUATIONS ({MAX_CONTINUATIONS}) without completing")

    # Save the raw model output FIRST. If parsing then fails, the run still
    # leaves an artifact to read — a failed parse should never cost the
    # research that produced it.
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"RAW-{edition_date.isoformat()}.txt"
    raw_path.write_text(text)
    print(f"  raw output saved: {raw_path}", file=sys.stderr, flush=True)

    md = extract_markdown(text)
    fm = validate_frontmatter_parses(md)

    stories = fm.get("topStories", [])
    if not stories:
        raise RuntimeError("output contains no topStories")

    out_path = out_dir / f"{edition_date.isoformat()}-weekly-intel.md"
    out_path.write_text(md)

    stats = fm.get("harvestStats", {}) or {}
    tiers = {}
    for s in stories:
        tiers[s.get("tier", "?")] = tiers.get(s.get("tier", "?"), 0) + 1

    print(f"\n  edition:    {edition_date.isoformat()}")
    print(f"  stories:    {len(stories)}  {tiers}")
    print(f"  watchList:  {len(fm.get('watchList', []) or [])}")
    print(f"  candidates: {stats.get('candidatesFound', '?')}")
    print(f"  status:     {fm.get('status')}")
    print(f"  written to: {out_path}")

    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "incoming")
    ap.add_argument("--archive", type=pathlib.Path,
                    default=HERE.parent / "apps/web/src/content/intel")
    ap.add_argument("--edition-date", type=str, default="")
    args = ap.parse_args()

    edition = (dt.date.fromisoformat(args.edition_date) if args.edition_date
               else monday_on_or_before(dt.date.today()))

    try:
        path = run(edition, args.out, args.archive)
    except Exception as e:
        print(f"STAGE A FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a") as f:
            f.write(f"edition_date={edition.isoformat()}\n")
            f.write(f"edition_path={path}\n")


if __name__ == "__main__":
    main()
