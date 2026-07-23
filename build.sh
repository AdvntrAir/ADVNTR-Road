#!/usr/bin/env bash
# ADVNTR Road — production build script
# Usage: ./build.sh <guide-slug>
# Runs build.py --no-maps, then triggers visual-qa and voice-risk subagents on success.
# Exits with build.py exit code.
set -euo pipefail

GUIDE="${1:-}"
if [[ -z "$GUIDE" ]]; then
  echo "Usage: ./build.sh <guide-slug>" >&2
  echo "Example: ./build.sh crater-lake-np" >&2
  exit 1
fi

# Capture as SLUG for readability in cover merge block
SLUG="$GUIDE"

read -p "Include cover and back page? (y/n) [n]: " include_cover
include_cover=${include_cover:-n}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "ERROR: .venv not found. Run: python -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

echo "=== ADVNTR Road Build: ${GUIDE} ==="
echo "Note: Maps skipped (--no-maps). Ask before dropping this flag."
echo ""

"$VENV_PYTHON" build.py --guide "$GUIDE" --no-maps
BUILD_EXIT=$?

if [[ $BUILD_EXIT -ne 0 ]]; then
  echo "" >&2
  echo "BUILD FAILED (exit $BUILD_EXIT). Check output/build_summary.md for details." >&2
  exit $BUILD_EXIT
fi

echo ""
echo "=== Build complete. Triggering QA subagents... ==="
echo "visual-qa and voice-risk run read-only against output/."
echo "Their reports write to output/visual_qa_report.md and output/voice_risk_report.md."
echo ""

# Subagents are triggered by the /goal loop in Stage 3b.
# When running build.sh standalone (not under /goal), they don't auto-invoke.
# The build_summary.md is the Gate 3 automated check; visual-qa/voice-risk add detail.

if [ "$include_cover" = "y" ]; then
    if [ -f "assets/covers/${SLUG}-cover.pdf" ] && \
       [ -f "assets/covers/${SLUG}-back.pdf" ]; then
        echo "Merging cover and back page..."
        "$VENV_PYTHON" merge_pdfs.py --guide "$SLUG"
        echo "Final PDF: output/${SLUG}-2026.pdf"
    else
        echo "WARNING: Missing cover or back page for ${SLUG}."
        echo "Expected:"
        echo "  assets/covers/${SLUG}-cover.pdf"
        echo "  assets/covers/${SLUG}-back.pdf"
        echo "Skipping merge. Interior-only PDF is in output/."
    fi
fi

exit 0
