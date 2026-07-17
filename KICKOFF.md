# ADVNTR Road — Kickoff Checklist
### From "Gemini finished" to "PDF on my screen"

This is the literal sequence to run. Steps 1–2 are unchanged from the Operational Workflow;
step 3 is the new autonomous loop. Nothing about Gate 1, Gate 2, or Gate 4 changed today — only
what happens *inside* Gate 3 got faster and more self-checking.

---

## Step 1 — Gemini (unchanged)

Run the Gem against the destination. Don't proceed until its closing RESEARCH QUALITY REPORT
shows `BUILD-READY STATUS: YES`. If NO, either answer the Gem's follow-ups or knowingly accept
the gap before moving on.

## Step 2 — This project chat (unchanged)

In any Claude chat inside this project:

```
BUILD DESTINATION: [name]
[paste the full destination.md content]
```

Wait for `GATE 2 STATUS: PASS`. If FAIL, run `FILL GAP: [item]` for each blocking item and
re-check — don't hand a Gate 2 FAIL to Claude Code. Once it passes, `content.yaml` + the full
prose set + `build_report.md` are saved to the Drive project folder.

## Step 3 — Claude Code (new: one command instead of a manual multi-pass)

**One-time setup**, if not already done in this repo:

1. Copy `agents/visual-qa.md` and `agents/voice-risk.md` into `.claude/agents/` in the guides
   repo.
2. Copy `references/build-loop.md` into the `advntr-road` skill's `references/` folder.
3. Replace the `advntr-road` skill's `SKILL.md` with the updated version in this package (it
   adds one section — "Autonomous build loop" — and two cross-references; nothing else changed).
4. Pull the Gate-2 package (`content.yaml` + `prose/` + `assets/`) from Drive into the repo,
   same as always.

**Every build after that**, in the Claude Code session, in the guides repo:

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

Then walk away. When `/goal` clears, three reports are waiting: `build_summary.md`,
`visual_qa_report.md`, `voice_risk_report.md`, plus the PDF and HTML in `output/`.

**Read the reports before opening the PDF.** If either automated check is FAIL, the loop
already stopped and told you why in the transcript — you're not starting from zero, you're
starting from a named gap. If `voice_risk_report.md` shows FLAGGED items, decide whether they're
worth a Gate 2 bounce now or a closer look during Gate 4's itinerary read-through.

## Step 4 — Gate 4, Manual QA (unchanged, but faster)

Same four checks as always — itinerary read-through, 5 QR phone-scans, 3 lodging rows against
Recreation.gov, redirects merged before publish. The itinerary read is the one that benefits
most: you're checking specific flagged lines against context, not reading cold for a problem
that might not be there.

---

## First run: don't trust it blind

Run the full loop once on a low-stakes guide — a `REBUILD:` of an existing v1 guide is ideal,
since a bad outcome costs nothing — before pointing it at Route 66 West. Confirm `visual-qa` and
`voice-risk` are actually catching real issues (not just returning a clean report every time)
before letting a 12-turn unattended run make the call on a guide with a hard deadline behind it.

## If something needs to change later

- QA thresholds, word budgets, schema fields → edit the specs (`Build Instructions`,
  `System Spec`), not this package. This package wraps the specs; it doesn't restate them.
- The `/goal` condition itself, the turn cap, or what counts as a blocking vs. advisory
  check → `references/build-loop.md` in the skill, and this file.
- A subagent missing an obvious defect class → edit that subagent's `.md` file directly; it's
  plain markdown, no rebuild step needed.
