from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


def page_has_images(page) -> bool:
    try:
        xobjs = page["/Resources"]["/XObject"]
    except Exception:
        return False
    return bool(xobjs)


def main() -> None:
    pdf_path = Path(__file__).resolve().parent.parent / "src/data/raw/1650/20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf"
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    sample_indices = [0, min(1, num_pages - 1), min(10, num_pages - 1)]

    samples = []
    for idx in sample_indices:
        page = reader.pages[idx]
        text = page.extract_text() or ""
        samples.append(
            {
                "page": idx + 1,
                "has_text": bool(text.strip()),
                "text_preview": text.strip()[:500],
                "has_images": page_has_images(page),
                "mediabox": list(map(float, page.mediabox)),
            }
        )

    summary = {
        "path": str(pdf_path),
        "num_pages": num_pages,
        "samples": samples,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
