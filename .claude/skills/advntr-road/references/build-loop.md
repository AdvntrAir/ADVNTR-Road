# ADVNTR Road — Autonomous Build Loop (Stage 3)
### Companion to the `advntr-road` skill · addresses: self-check, visual QA, voice-risk
### advisory, and refinement without manual babysitting between steps

---

## Where these files go

```
your-repo/
├── .claude/
│   └── agents/
│       ├── visual-qa.md      ← drop in as-is
│       └── voice-risk.md     ← drop in as-is
├── build.py
├── output/
│   ├── build_summary.md      (already produced by build.py)
│   ├── visual_qa_report.md   (new — from visual-qa subagent)
│   └── voice_risk_report.md  (new — from voice-risk subagent)
└── ...
```

Subagents are picked up automatically from `.claude/agents/` at session start — no registration
step. `/agents` will list them once the files are in place.

## Why `/goal`, not `/loop`

`/loop` reruns a prompt on a time interval — it's for polling, not "keep working until this
build is actually right." `/goal` is the fit: you state a completion condition once, and after
every turn a separate evaluator model (not the one doing the work) checks the transcript and
either lets Claude stop or sends it back for another turn. That's the render → check → fix →
re-render cycle, automated.

## The command

Run this in the Claude Code session, in the guides repo, once a Gate-2-passed package is in
place for a guide:

```
/goal build_summary.md shows GATE 3 STATUS: PASS, output/visual_qa_report.md shows VISUAL QA
STATUS: PASS, and output/voice_risk_report.md has been generated (its findings do not need to be
zero — FLAGGED is an acceptable stopping state, not a failure, since voice gaps bounce to Gate 2
rather than blocking here). Stop after 12 turns regardless of outcome. You may edit
template/render code in this repo to fix a confirmed template bug. You do NOT edit content.yaml
or any file under prose/ — a content or voice gap gets reported and the loop stops with a
bounce-to-Gate-2 note, never patched in place. Do not drop --no-maps from any build.py invocation
without asking me directly, even mid-loop.
```

A few things worth understanding about why it's worded this way, not just copying it verbatim:

- **The measurable end state is two file contents, not a feeling.** `/goal`'s evaluator only
  sees what's in the transcript — it can't independently judge "does this guide look done." It
  can read `GATE 3 STATUS: PASS` in a file Claude just printed. Write conditions the evaluator
  can actually verify from output, the same way you'd write an assertion.
- **Voice-risk is deliberately non-blocking in the condition.** The skill's scope line — Stage 3
  builds, it doesn't author — means a voice flag can't be something Claude "fixes" its way past
  in this loop. Making `VOICE RISK STATUS: PASS` a hard condition would create exactly the
  pressure the scope boundary exists to prevent: an incentive to quietly improve prose to make
  the loop terminate. Let it flag and stop; the bounce decision is Matt's or the parent
  session's, made once, deliberately — not something an automated loop talks itself into.
- **The turn cap is not optional.** `/goal` has no built-in ceiling; an unsatisfiable condition
  (e.g., a Gate 2 content gap that visual QA keeps re-surfacing because the underlying data is
  actually missing) burns turns indefinitely without one.
- **The Maps API line exists because loops erase the moment you'd normally notice and ask.** The
  skill's standing rule — never drop `--no-maps` without asking, permission doesn't carry over
  — is easy to lose once nothing is stopping between turns to give you the chance to say no.

## What actually happens during a run

1. `build.py --guide <slug> --no-maps` runs (or re-runs after a template fix).
2. The parent session invokes `visual-qa` (rasterize + review) and `voice-risk` (prose review)
   as subagents — they run read-only, in their own context, and can execute in parallel since
   neither depends on the other's output.
3. Both write their report files. The evaluator checks the three files after the turn ends.
4. If `GATE 3 STATUS` or `VISUAL QA STATUS` is FAIL, the parent session reads the specific
   finding, decides if it's a template bug (fixes it, re-renders) or a content gap (stops,
   reports the bounce), and the loop either continues or ends.
5. Once both automated conditions hold and the voice report exists, `/goal` clears and control
   returns to you with three reports waiting — not just a PDF and a hope.

## What this changes about Gate 4

Nothing removed, one thing sharpened. The Operational Workflow's four manual checks — itinerary
read-through, QR phone-scan, Recreation.gov spot-check, redirects-merged confirmation — stay
exactly as they are; none of them are things a build-time loop can verify (two need a phone and
a browser outside the repo, two are independent-verification-by-design). What changes is that
`voice_risk_report.md` gives you a head start on check #1 — you're confirming a flagged
itinerary reads right in context, not reading cold seven sections deep for a problem that might
not be there.

## Before the first real run

Test the loop on a guide you don't care about shipping, or on a `REBUILD:` of an existing v1
guide where a bad outcome costs nothing. Confirm `visual-qa` and `voice-risk` actually produce
useful, specific findings (not generic "looks fine" reports — a subagent that always passes is
worse than no subagent) before trusting a 12-turn unattended run on Route 66 West against a hard
deadline.
