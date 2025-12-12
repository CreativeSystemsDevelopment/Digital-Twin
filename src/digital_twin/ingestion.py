from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from digital_twin.models import DocumentInfo, ProductionLineSnapshot


def scan_production_line(root: Path) -> ProductionLineSnapshot:
    """Scan a single production line directory and gather document metadata."""
    documents: List[DocumentInfo] = []

    for path in root.rglob("*"):
        if path.is_file():
            stat = path.stat()
            relative_path = path.relative_to(root)
            documents.append(
                DocumentInfo(
                    production_line=root.name,
                    relative_path=relative_path,
                    absolute_path=path.resolve(),
                    size_bytes=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                )
            )

    return ProductionLineSnapshot(name=root.name, root_path=root.resolve(), documents=documents)


def scan_root_directory(root: Path) -> List[ProductionLineSnapshot]:
    """Scan a root directory that contains production line folders."""
    snapshots: List[ProductionLineSnapshot] = []

    for entry in sorted(root.iterdir()):
        if entry.is_dir():
            snapshots.append(scan_production_line(entry))

    return snapshots


def snapshot_to_dict(snapshot: ProductionLineSnapshot) -> dict:
    return {
        "production_line": snapshot.name,
        "root_path": str(snapshot.root_path),
        "document_count": snapshot.document_count,
        "total_size_bytes": snapshot.total_size_bytes,
        "documents": [
            {
                "relative_path": str(doc.relative_path),
                "absolute_path": str(doc.absolute_path),
                "size_bytes": doc.size_bytes,
                "modified_time": doc.modified_time.isoformat(),
                "extension": doc.extension,
            }
            for doc in snapshot.documents
        ],
    }


def snapshots_to_json(snapshots: Iterable[ProductionLineSnapshot]) -> str:
    payload = [snapshot_to_dict(snapshot) for snapshot in snapshots]
    return json.dumps(payload, indent=2)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan production line directories and emit a JSON summary of all documents "
            "found in each line."
        )
    )
    parser.add_argument(
        "root",
        type=Path,
        help="Root directory that contains production line folders",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the JSON summary. If omitted, prints to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root path {root} does not exist or is not a directory")

    snapshots = scan_root_directory(root)
    payload = snapshots_to_json(snapshots)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"Wrote metadata for {len(snapshots)} production lines to {args.output}")
    else:
        print(payload)


if __name__ == "__main__":  # pragma: no cover
    main()
