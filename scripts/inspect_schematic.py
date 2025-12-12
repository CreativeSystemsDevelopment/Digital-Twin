#!/usr/bin/env python3
"""
Inspect electrical schematic pages - convert to images and analyze structure.
This helps us understand what components/symbols we're dealing with.
"""
from pathlib import Path
import sys

from pdf2image import convert_from_path
from PIL import Image

def extract_page_image(pdf_path: Path, page_num: int, output_dir: Path, dpi: int = 200):
    """Convert a single PDF page to high-res image."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting page {page_num} at {dpi} DPI...")
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        first_page=page_num,
        last_page=page_num,
        fmt='png'
    )
    
    if not images:
        print(f"Failed to convert page {page_num}")
        return None
    
    img = images[0]
    output_path = output_dir / f"page_{page_num:03d}_dpi{dpi}.png"
    img.save(output_path, 'PNG')
    print(f"Saved: {output_path} ({img.width}x{img.height})")
    return output_path


def main():
    workspace = Path(__file__).resolve().parent.parent
    pdf_path = workspace / "src/data/raw/1650/20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf"
    output_dir = workspace / "src/data/inspection"
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)
    
    # Extract a few sample pages - let's look at pages with actual ladder content
    # Page 1 is usually title/cover, so try 4, 10, 20
    sample_pages = [4, 10, 20]
    
    print(f"Source PDF: {pdf_path}")
    print(f"Output dir: {output_dir}\n")
    
    for page_num in sample_pages:
        extract_page_image(pdf_path, page_num, output_dir, dpi=200)
        print()
    
    print("Done! Check the images to identify:")
    print("  - Component symbols (relays, contactors, switches, motors)")
    print("  - Wire numbering scheme")
    print("  - Component designators (K1, S1, M1, F1, etc.)")
    print("  - Power rail labels and voltage levels")


if __name__ == "__main__":
    main()
