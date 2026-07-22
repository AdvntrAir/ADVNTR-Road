#!/usr/bin/env python3
"""
Stage A — research run for the ADVNTR Road Weekly Intel Pack.

Calls the Anthropic API with web search enabled, runs the agentic tool loop to
completion, and writes intel-YYYY-MM-DD.json.

This is the ONLY place in the pipeline that makes an LLM call. Everything
downstream (validate, render, deploy) is deterministic.

Usage:
    python stage_a_research.py --out ./incoming/ [--edition-date YYYY-MM-DD]
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

import anthropic

HERE = pathlib.Path(__file__).parent
MODEL = os.environ.get("INTEL_MODEL", "claude-opus-4-8")
MAX_TOKENS = 32000
MAX_TURNS = 40          # hard ceiling on the tool loop; a runaway run is a cost bug
ARCHIVE_LOOKBACK = 4    # editions to dedupe against


def monday_on_or_before(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def load_recent_story_ids(archive_dir: pathlib.Path, n: int) -> list[str]:
    """Story ids from the last n editions, for cross-edition dedupe."""
    if not archive_dir.exists():
        return []
    editions = sorted(archive_dir.glob("intel-*.json"), reverse=True)[:n]
    ids = []
    for path in editions:
        try:
            data = json.loads(path.read_text())
            ids += [s["id"] for s in data.get("stories", [])]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  warn: could not read {path.name}: {e}", file=sys.stderr)
    return ids


def extract_json(text: str) -> dict:
    """
    The prompt says emit bare JSON. Models sometimes wrap it anyway.
    Strip fences, then take the outermost object.
    """
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found in model output")
    return json.loads(text[start:end + 1])


def run(edition_date: dt.date, out_dir: pathlib.Path, archive_dir: pathlib.Path) -> pathlib.Path:
    window_end = dt.date.today()
    window_start = window_end - dt.timedelta(days=7)

    system_prompt = (HERE / "intel-run-prompt.md").read_text()
    registry = (HERE / "intel-place-registry.yaml").read_text()
    schema = (HERE / "intel-schema.json").read_text()
    recent_ids = load_recent_story_ids(archive_dir, ARCHIVE_LOOKBACK)

    user_msg = f"""Produce the Weekly Intel Pack.

RUN PARAMETERS
  edition_date: {edition_date.isoformat()}
  window_start: {window_start.isoformat()}
  window_end:   {window_end.isoformat()}

STORY IDS FROM THE LAST {ARCHIVE_LOOKBACK} EDITIONS — do not re-report these:
{json.dumps(recent_ids, indent=2) if recent_ids else "  (none — this is the first edition)"}

PLACE REGISTRY (authoritative — places, topics, and actions must come from here):
```yaml
{registry}
```

OUTPUT SCHEMA (your output must validate against this):
```json
{schema}
```

Research the window, verify against primary sources, and emit the JSON object.
Nothing before it, nothing after it."""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": user_msg}]
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 40}]

    for turn in range(MAX_TURNS):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            break

        # Server-side web search results come back attached to the response;
        # continue the loop so the model can keep researching.
        print(f"  turn {turn + 1}: researching...", file=sys.stderr)
        messages.append({"role": "user", "content": "Continue."})
    else:
        raise RuntimeError(f"tool loop hit MAX_TURNS ({MAX_TURNS}) without completing")

    data = extract_json(text)

    # Trust but verify the two fields everything downstream keys off.
    if data.get("edition_date") != edition_date.isoformat():
        print(f"  warn: model returned edition_date={data.get('edition_date')}, "
              f"overriding to {edition_date.isoformat()}", file=sys.stderr)
        data["edition_date"] = edition_date.isoformat()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"intel-{edition_date.isoformat()}.json"
    out_path.write_text(json.dumps(data, indent=2))

    stats = data.get("harvest_stats", {})
    print(f"\n  edition:    {edition_date.isoformat()}")
    print(f"  stories:    {len(data.get('stories', []))}")
    print(f"  watch_list: {len(data.get('watch_list', []))}")
    print(f"  candidates: {stats.get('candidates_found', '?')}")
    print(f"  written to: {out_path}")

    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "incoming")
    ap.add_argument("--archive", type=pathlib.Path, default=HERE / "archive")
    ap.add_argument("--edition-date", type=str, default="")
    args = ap.parse_args()

    if args.edition_date:
        edition = dt.date.fromisoformat(args.edition_date)
    else:
        edition = monday_on_or_before(dt.date.today())

    try:
        path = run(edition, args.out, args.archive)
    except Exception as e:
        print(f"STAGE A FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    # Hand the edition date to later workflow steps.
    if gh_out := os.environ.get("GITHUB_OUTPUT"):
        with open(gh_out, "a") as f:
            f.write(f"edition_date={edition.isoformat()}\n")
            f.write(f"edition_path={path}\n")


if __name__ == "__main__":
    main()
