from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable

from digital_twin.models import ProductionLineSnapshot


def summarize_extensions(snapshot: ProductionLineSnapshot) -> Dict[str, int]:
    """Count file extensions within a production line snapshot."""
    counts: Counter[str] = Counter()
    for document in snapshot.documents:
        counts[document.extension] += 1
    return dict(counts)


def summarize_snapshots(snapshots: Iterable[ProductionLineSnapshot]) -> Dict[str, dict]:
    """Provide high-level summary statistics for multiple production lines."""
    summary: Dict[str, dict] = {}
    for snapshot in snapshots:
        summary[snapshot.name] = {
            "documents": snapshot.document_count,
            "total_size_bytes": snapshot.total_size_bytes,
            "extensions": summarize_extensions(snapshot),
        }
    return summary
