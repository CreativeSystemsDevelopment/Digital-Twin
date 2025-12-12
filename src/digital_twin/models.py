from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List


@dataclass
class DocumentInfo:
    """Represents a single document discovered in a production line directory."""

    production_line: str
    relative_path: Path
    absolute_path: Path
    size_bytes: int
    modified_time: datetime

    @property
    def extension(self) -> str:
        return self.relative_path.suffix.lower()


@dataclass
class ProductionLineSnapshot:
    """A collection of documents for a specific production line directory."""

    name: str
    root_path: Path
    documents: List[DocumentInfo]

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def total_size_bytes(self) -> int:
        return sum(doc.size_bytes for doc in self.documents)

    def iter_documents(self) -> Iterable[DocumentInfo]:
        return iter(self.documents)
