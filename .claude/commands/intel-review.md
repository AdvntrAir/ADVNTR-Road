---
description: Review the most recent draft Intel Pack edition and publish it on approval.
allowed-tools: Bash, Read, Edit, AskUserQuestion
---

This is Gate 4 for the Intel Pack pipeline: a human reads the edition Stage B
already validated and CI already committed as a draft, and decides whether it
goes out. You are not re-validating anything and you are not authoring
anything — `intel_pipeline_lib.py` already did the gate work; this command is
the read-and-decide step.

## 1. Find the most recent draft

Run this from the repo root:

```bash
python3 -c "
import sys, pathlib
sys.path.insert(0, 'intel')
from intel_pipeline_lib import parse_edition, edition_date_from_filename

content_dir = pathlib.Path('apps/web/src/content/intel')
drafts = []
for p in sorted(content_dir.glob('*.md'), reverse=True):
    fm, _ = parse_edition(p)
    if fm.get('status') == 'draft':
        drafts.append(p)

if not drafts:
    print('NO_DRAFT_FOUND')
    sys.exit(0)

path = drafts[0]
fm, _ = parse_edition(path)

print(f'FILE: {path}')
print(f'EDITION_DATE: {edition_date_from_filename(path)}')
if len(drafts) > 1:
    print(f'NOTE: {len(drafts) - 1} older draft(s) also exist; reviewing only the most recent.')
print()
print(f\"TITLE: {fm['title']}\")
print()
print('TRAILHEAD SUMMARY:')
print(fm['trailheadSummary'].strip())
print()
print('STORIES:')
for s in sorted(fm['topStories'], key=lambda s: s['storyRank']):
    print(f\"  [{s['tier'].upper()}] {s['parkOrRegion']}\")
    print(f\"    {s['take'].strip()}\")
    print()

print(f\"ctaPlaceSlug: {fm.get('ctaPlaceSlug') or '(none)'}\")
print(f\"ctaSuppressed: {fm.get('ctaSuppressed', False)}\")
print()
print('affectsGuides:')
any_ag = False
for s in fm['topStories']:
    for ag in (s.get('affectsGuides') or []):
        any_ag = True
        print(f\"  - {ag['guideSlug']} ({ag['impact']}) — from story: {s['storyId']}\")
        if ag.get('note'):
            print(f\"    note: {ag['note']}\")
if not any_ag:
    print('  (none)')
"
```

If this prints `NO_DRAFT_FOUND`, tell the user there's nothing to review and stop — do not proceed to any later step.

## 2–3. Present the read pass

Show the user exactly what the script printed: title, trailhead summary, and
each story's tier/place/take, then the CTA resolution and any `affectsGuides`
entries. **Nothing else** — this is a read pass, not a dump of the whole
file. Do not show `explorerImpact`, `adventureRoadAngle`, source URLs,
`harvestStats`, or `watchList`; the script above deliberately doesn't
surface them and you shouldn't go digging for them separately.

## 4. Stop and ask

Ask the user directly whether to publish this edition. Wait for an explicit
yes. Anything else — no, silence, "let me think," a question back — means
decline: skip straight to the **If declined** section below and do nothing
else.

## 5. On approval

Using the `FILE` and `EDITION_DATE` values from step 1:

1. **Flip status.** Use the Edit tool to change exactly the line
   `status: draft` (or `status: "draft"`, if it was written quoted) to
   `status: published` in `FILE`. Touch nothing else in the file — don't
   re-parse and re-dump the YAML, which would risk reformatting the rest of
   it away from what CI committed.

2. **Commit and push:**
   ```bash
   git add <FILE>
   git commit -m "Intel Pack: publish edition <EDITION_DATE>"
   git push
   ```
   Add only `<FILE>` — never a broad `git add -A` — and never `--no-verify`.

3. **Close the matching issue:**
   ```bash
   gh issue list --label intel --state open --json number,title
   ```
   Find the open issue whose title contains `<EDITION_DATE>` (titled
   `Intel Pack draft ready — <EDITION_DATE>` by the workflow that opened
   it), then:
   ```bash
   gh issue close <number> --comment "Published — see the <EDITION_DATE> edition on main."
   ```
   If no matching open issue exists, say so and move on — that's a missing
   notification, not a reason to stop the publish.

Report back: the file published, the commit, and the issue closed (or the
note that none matched).

## If declined

Change nothing — no edit, no commit, no push, no issue action. Tell the user
concretely what you would have done: the file that would have been flipped
to `published`, the exact commit message, and the issue (number and title)
that would have been closed, or that no matching issue was found.
