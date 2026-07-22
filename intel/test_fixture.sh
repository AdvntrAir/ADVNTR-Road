#!/usr/bin/env bash
# Runs validate.py and write_edition.py against the committed fixture edition
# (intel/fixtures/sample-edition.md) with no GitHub Actions, no API key, and
# no network by default — for testing a schema, gate, CTA, or template change
# for zero dollars. Only genuine research changes need a real Stage A run.
#
# sample-edition.md is a test asset, not content: this script writes to
# intel/out/fixture-content/ (gitignored), never to
# apps/web/src/content/intel/.
#
# Usage:
#   intel/test_fixture.sh          # fast, no live HTTP checks
#   intel/test_fixture.sh --live   # also exercises the real URL-resolution gate

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."   # repo root

INCOMING="./intel/incoming"
FIXTURE_TARGET="$INCOMING/2026-07-20-weekly-intel.md"
OUT_DIR="./intel/out/fixture-content"
REPORT="./intel/out/intel_build_report.md"
QUEUE="./intel/out/intel_guide_updates.md"

SKIP_URL_FLAG="--skip-url-check"
if [ "${1:-}" = "--live" ]; then
  SKIP_URL_FLAG=""
  echo "Running with live HTTP checks — this hits real URLs and is slower."
fi

echo "== Copying fixture into $INCOMING =="
mkdir -p "$INCOMING"
rm -f "$INCOMING"/*.md
cp ./intel/fixtures/sample-edition.md "$FIXTURE_TARGET"

echo
echo "== validate.py =="
python3 intel/validate.py \
  --edition "$INCOMING" \
  --registry ./intel/intel-place-registry.yaml \
  --guides ./apps/web/src/data/guides.ts \
  --archive ./apps/web/src/content/intel \
  --report "$REPORT" \
  $SKIP_URL_FLAG

echo
echo "== write_edition.py (writing to $OUT_DIR, NOT the real content dir) =="
rm -rf "$OUT_DIR"
python3 intel/write_edition.py \
  --edition "$INCOMING" \
  --registry ./intel/intel-place-registry.yaml \
  --out "$OUT_DIR" \
  --queue "$QUEUE" \
  $SKIP_URL_FLAG

echo
echo "== Done =="
echo "Build report:      $REPORT"
echo "Guide-update rows:  $QUEUE"
echo "Rendered edition:   $OUT_DIR"
