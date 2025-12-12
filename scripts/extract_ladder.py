from __future__ import annotations

import argparse
import json
from pathlib import Path

import pdfplumber


def extract_pdf(src: Path, out_dir: Path, limit: int | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "source": str(src),
        "pages": [],
    }
    with pdfplumber.open(src) as pdf:
        num_pages = len(pdf.pages)
        summary["num_pages"] = num_pages
        for i, page in enumerate(pdf.pages, start=1):
            if limit and i > limit:
                break
            words = page.extract_words(keep_blank_chars=False, use_text_flow=True)
            lines = page.lines
            rects = page.rects
            page_rec = {
                "page": i,
                "width": page.width,
                "height": page.height,
                "words": words,
                "lines": lines,
                "rects": rects,
            }
            (out_dir / f"page_{i:03}.json").write_text(json.dumps(page_rec, indent=2), encoding="utf-8")
            summary["pages"].append({"page": i, "word_count": len(words), "line_count": len(lines), "rect_count": len(rects)})
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract ladder PDF geometry and text to JSON")
    parser.add_argument("pdf", type=Path, nargs="?", default=Path(__file__).resolve().parent.parent / "src/data/raw/1650/20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "src/data/processed/1650")
    parser.add_argument("--limit", type=int, default=None, help="Optional page limit for sampling")
    args = parser.parse_args()

    summary = extract_pdf(args.pdf, args.out, args.limit)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
