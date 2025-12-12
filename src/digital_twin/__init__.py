"""Digital Twin platform package."""

from digital_twin.ingestion import main, parse_args, scan_production_line, scan_root_directory
from digital_twin.models import DocumentInfo, ProductionLineSnapshot
from digital_twin.reporting import summarize_extensions, summarize_snapshots

__all__ = [
    "DocumentInfo",
    "ProductionLineSnapshot",
    "scan_production_line",
    "scan_root_directory",
    "summarize_extensions",
    "summarize_snapshots",
    "parse_args",
    "main",
]
