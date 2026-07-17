---
name: advntr-road
description: >-
  Build ADVNTR Road travel guide PDFs — Stage 3 of the four-gate pipeline, where a Gate-2-passed
  content.yaml plus prose file set (already produced, sitting in a guides repo) is rendered to
  PDF, HTML, QR codes, and a redirects fragment via WeasyPrint. Use when there is an actual
  ADVNTR Road guides repo present (build.py, .venv, or a content.yaml on disk) and the work
  touches: running or debugging build.py, a failed Gate 3 QA item, WeasyPrint or font errors, QR
  generation, a v1→v2 guide migration, or the autonomous /goal build loop. Do NOT use for
  `BUILD DESTINATION:`, `FILL GAP:`, `VERIFY FIELD:`, or `REBUILD:` commands, or for any raw
  destination.md / Gemini research file — those are Stage 2 (Claude Bridge Prompt v3.0) and are
  handled directly in the ADVNTR Road project chat, no repo and no skill required. If a
  Stage-2-shaped input shows up with no repo in the environment, that is this skill's cue to
  redirect, not to activate.
---

# ADVNTR Road — Stage 3 Build

This is **Stage 3** of a four-gate pipeline. Its entire job is to turn a build-ready package into
a finished guide. Nothing more.

```
Gemini Gem ──GATE 1──▶ Claude Bridge ──GATE 2──▶ [ YOU ARE HERE ] ──GATE 3──▶ Manual QA ──GATE 4──▶ Publish
 research               content.yaml               PDF · HTML                   Matt reads it        Netlify
                        + prose set                QR · _redirects
```

## First: is this actually Stage 3?

Before doing anything else, check the environment for a real guides repo — `build.py`, a
`.venv`, or an existing `content.yaml` on disk. If none of those are present, this is not a
Stage 3 task, regardless of what triggered this skill.

**If the input is a `destination.md` file, a `BUILD DESTINATION:` / `FILL GAP:` /
`VERIFY FIELD:` / `REBUILD:` command, or otherwise looks like Gate 1 research or a Gate 2
trigger, and there is no repo here: stop and say so.** Tell the user this belongs in the ADVNTR
Road project chat, using the Claude Bridge Prompt v3.0 trigger, and that no skill or repo is
needed for that step.

**Do not offer to draft `content.yaml` or prose files yourself as a "best-effort Gate 2" fallback,
even with caveats, even offering to let the user QA it against the real schema.** That is the
exact authorship violation this skill exists to prevent — see "The line" below — and it does not
stop being a violation just because the real Gate 2 tool isn't available in this environment. The
absence of a repo is information that this is the wrong tool, not a gap to fill in by
approximating the right one.

## Read the specs first — they are authoritative, this file is not

Before rendering anything, read both, from the repo:

- **`ADVNTR_Road_Claude_Code_Build_Instructions_v2_0.md`** — input contract, schema 3.0 renderer
  expectations, v2.0 components, QR system, the Gate 3 QA checklist, build summary format
- **`ADVNTR_Road_Build_Spec_FINAL.md`** — design tokens, fonts, base components, typography,
  page-break conventions, WeasyPrint invocation

**This skill deliberately does not restate their contents.** The QA checklist, the schema, the
word budgets, the component specs — all live there and get revised there. A copy in this file
would be a second source of truth that silently drifts out of date, which is worse than no copy
at all. If the specs and this file ever disagree about the *build*, the specs win.

What this file carries is the stuff that exists nowhere else: the machine's failure modes, and
the line Stage 3 must not cross.

## The line: Stage 3 builds, it does not author

`content.yaml` and the prose files are **produced at Gate 2** by Claude Bridge Prompt v3.0, in a
Claude project chat. They arrive here finished.

**Never hand-edit `content.yaml` or a prose file to make a build pass — and never generate them
from scratch either, no matter how the request is framed.** Not to add a missing section, not to
fill an empty field, not to fix a word count, not to soften a QA failure, not to "help out" when
the real Gate 2 tool isn't in reach. Every one of those produces content that never passed
word-budget checks, never got an opinionated `take`, never got a verified link registry entry,
never got a photo credit — a guide that renders correctly and is editorially unfit. That's the
exact failure the gates exist to prevent, whether the shortcut is taken inside a build or offered
as a favor when Gate 2 isn't available.

When content is missing or wrong, the build **fails backward**: report the specific gap and say
it belongs at Gate 2. Matt takes it to the project chat and runs `FILL GAP: [item]`.

The one thing you may edit is a **template**, when the template is the actual bug — e.g. an
optional field's wrapper rendering unconditionally and producing an empty page. That's a Stage 3
defect and fixing it is Stage 3's job.

This line holds inside the autonomous build loop exactly as it holds in a manual session — see
`references/build-loop.md` for how the loop is worded to keep it that way.

## Before rendering: check the input contract

Per Build Instructions §1. Verify all four, in order, and stop on the first failure:

1. `content.yaml` parses and validates against schema 3.0
2. Every prose file referenced in `sections:` exists on disk
3. Every `photos[].file` path exists in `assets/photos/`
4. **`build_report.md` shows `GATE 2 STATUS: PASS`**

A FAIL on any of these is not something to work around. Do not omit a section to route around a
missing prose file. Report the specific failure and stop.

## Running the build

Always invoke Python through the venv binary. `python3` alone silently uses the system
interpreter with none of the dependencies.

```bash
.venv/bin/python build.py --guide <slug> --no-maps
```

`--no-maps` is the working default. Use it for every iteration, every debug loop, every QA pass.

```bash
.venv/bin/python build.py --guide <slug>
```

Dropping `--no-maps` calls the **paid** Google Maps Static API, which bills per request — and a
guide has many locations, and a debug loop multiplies them. **Never run this on your own
initiative.** Ask Matt, in this conversation, for this guide. Permission does not carry over from
a previous guide, a previous session, or a stated intent to "finish the guide." This holds
**inside an active `/goal` loop too** — a loop running unattended is not standing permission to
drop `--no-maps`; the loop must stop and ask, same as a manual session would.

`GOOGLE_MAPS_API_KEY` lives in `.env`.

## Gate 3

`build.py` runs the automated QA checklist (Build Instructions §7) and exits non-zero if any item
fails. Read `output/build_summary.md` for `GATE 3 STATUS`.

**Do not hand a FAIL to Matt.** A failing build is not a build with caveats — it's a build that
doesn't ship. Report the blocking items and fix them, or bounce them back to Gate 2 if they're
content gaps rather than render defects.

A PASS is not the same as "looks right." Gate 3 is automated and it does not have eyes. Rasterize
and look at the pages before handing off — the environment reference explains what to look for
and why a clean exit code proves less than it seems.

## Autonomous build loop (recommended default)

Gate 3's automated checklist is data-driven — it has no eyes and no ear for voice. Two subagents
close that gap without crossing the authorship line above, and `/goal` runs the whole
render → check → fix → re-render cycle without a prompt between every step:

- **`visual-qa`** (`.claude/agents/visual-qa.md`) — rasterizes the rendered PDF and reviews it
  against the design spec and known failure modes, especially empty-furniture pages (a heading
  with nothing under it — this has shipped before, in North Cascades v1). Read-only; reports to
  `output/visual_qa_report.md`.
- **`voice-risk`** (`.claude/agents/voice-risk.md`) — reads the prose set against the voice
  standard and flags generic or padded language, especially in the itineraries, the component
  the System Spec already identifies as carrying the most voice risk. Read-only, advisory only;
  reports to `output/voice_risk_report.md`. A flag here is a Gate 2 bounce candidate, never
  something this skill edits into shape.

Full setup, the exact `/goal` command, and why it's worded the way it is (particularly why
voice-risk is deliberately non-blocking in the completion condition): **`references/build-loop.md`**.

Manual, single-shot builds still work exactly as documented above — the loop is a wrapper around
the same `build.py` invocation and the same Gate 3 check, not a replacement for either.

## Environment

WeasyPrint fails in ways that don't look like WeasyPrint failing. Two known traps account for
most lost time, and a third — the silent Chrome fallback — will ship a guide that doesn't match
the design system while looking fine.

**Read `references/environment.md` before debugging any build failure, font oddity, or venv
weirdness.** It is short, and it will save an hour.

## v1 → v2 migration

Migration order (System Spec Part 6): Olympic → Oregon Coast → Mount Rainier → North Cascades.

A v1 guide lacks `itineraries:`, a 12-row `seasonal:`, `drive_times:`, most `trails:`, and
`links:` entirely. These are REQUIRED in v2.0. **The build must fail Gate 3 until Gate 2 supplies
them** — even when the old guide "looks done" by v1 standards, and even when shipping is close.
Do not relax a requirement to get an old guide through the new pipeline faster. That is the one
shortcut that quietly undoes the whole upgrade.

`campgrounds:` is a deprecated alias for `lodging:` — accept it, emit a deprecation warning, flag
it for migration. Don't require a rewrite before the build will run.
