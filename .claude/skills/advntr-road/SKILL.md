---
name: advntr-road
description: >-
  ADVNTR Road Stage 3 — two sub-steps: (3a) one-time renderer build when build.py needs
  to be written or fixed, and (3b) production builds where build.py runs autonomously as
  a Python script with no AI involvement. Trigger on: "build the guide", "run the build",
  "build.py failed", "fix the renderer", "Stage 3", or any named guide (Olympic, Oregon
  Coast, Mount Rainier, North Cascades, Crater Lake, Route 66 West). Do NOT trigger on
  BUILD DESTINATION:, FILL GAP:, VERIFY FIELD:, or REBUILD: commands — those are Stage 2
  and run in the Claude project chat, no repo required. If a Stage-2-shaped input arrives
  with no repo present, redirect to the project chat and stop.
---

# ADVNTR Road — Stage 3

Stage 3 has two sub-steps with completely different scopes.

## Step 3a — Renderer Build (one-time, not per guide)

Spec files — load ONLY what the specific task requires:

| Problem type | Load this file | Do NOT load |
|---|---|---|
| Layout bug, component rendering | references/spec-components.md | all others |
| Brand color, font, typography | references/spec-design.md | all others |
| Schema field, YAML parsing | references/spec-schema.md | all others |
| Build system, QA checklist | references/spec-build.md | all others |

NEVER load ADVNTR_Road_Build_Spec_FINAL.md directly. That file is 112KB.
Loading it caused 16.7M cache-read tokens and $4 per session.
Read spec docs once at session start. Do not re-read them mid-session.

## Step 3b — Production Build (every guide, no AI)

./build.sh [slug]

Zero AI tokens. No decisions required.

If build.py exits non-zero:
- Read output/build_summary.md for the specific failing item
- Load ONLY the spec file relevant to that failure (see table above)
- Fix the specific bug
- Re-run ./build.sh [slug]
- Do not edit content.yaml or prose files

The only question to ask: permission to drop --no-maps.

## The line that never moves

content.yaml and prose files are produced at Gate 2. Never edit them.
A content gap bounces to Gate 2: FILL GAP: [item].

Stage 3 may only write:
- build.py, guide_template.html, build.sh (3a only)
- Everything under output/
- assets/photos/ and photo_manifest.json
- content.yaml photos[] block only (from photo_manifest.json)

## Environment
Read references/environment.md before debugging any font or render issue.

## Is this actually Stage 3?
Check for build.py, .venv, or content.yaml on disk. If none present:
redirect to the ADVNTR Road project chat. Do not offer to draft content.
