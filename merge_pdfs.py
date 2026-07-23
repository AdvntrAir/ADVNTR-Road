#!/usr/bin/env python3
"""
Merge cover + interior + back page into the final deliverable PDF.

Usage:
    python merge_pdfs.py --guide <slug>

Expects:
    assets/covers/<slug>-cover.pdf
    output/<slug>-interior.pdf
    assets/covers/<slug>-back.pdf

Writes:
    output/<slug>-2026.pdf
"""

import argparse
import sys
from pathlib import Path

from pypdf import PdfWriter, PdfReader


def merge(slug: str) -> None:
    cover = Path(f"assets/covers/{slug}-cover.pdf")
    interior = Path(f"output/{slug}-interior.pdf")
    back = Path(f"assets/covers/{slug}-back.pdf")
    output = Path(f"output/{slug}-2026.pdf")

    for path in (cover, interior, back):
        if not path.exists():
            print(f"ERROR: Required file not found: {path}", file=sys.stderr)
            sys.exit(1)

    writer = PdfWriter()

    for path in (cover, interior, back):
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)

    with open(output, "wb") as f:
        writer.write(f)

    total = sum(len(PdfReader(str(p)).pages) for p in (cover, interior, back))
    print(f"Merged {total} pages → {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge cover/interior/back PDFs")
    parser.add_argument("--guide", required=True, help="Guide slug (e.g. crater-lake-np)")
    args = parser.parse_args()
    merge(args.guide)


if __name__ == "__main__":
    main()
