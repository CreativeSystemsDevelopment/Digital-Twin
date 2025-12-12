# Digital Twin Platform

This repository will host our platform for representing production line documentation as a digital twin. The goal is to ingest and model the full set of documents for each production line, keep metadata synchronized, and provide a navigable representation of the data.

## Vision

* Treat each production line directory as a source of truth for documents (drawings, specifications, maintenance logs, etc.).
* Ingest documents from the local drive while preserving relationships between production lines, subassemblies, and supporting assets.
* Produce structured metadata that downstream services can use for search, quality checks, reporting, and knowledge graph creation.

## Repository Layout

* `src/digital_twin/` – Python package for ingestion, modeling, and reporting.
  * `models.py` – Dataclasses for production lines and documents.
  * `ingestion.py` – Functions to scan local directories and build metadata snapshots.
  * `reporting.py` – Utilities to summarize scanned data.
* `scripts/` – Entry points for local use.
  * `scan_documents.py` – CLI to scan production line folders and emit a JSON summary.
* `docs/` – Architectural notes, data model decisions, and future planning.

## Getting Started

1. Ensure Python 3.11+ is available.
2. (Optional) Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
3. Install the package locally in editable mode:

```bash
pip install -e .
```

4. Run the scanner against the root directory that contains production line folders:

```bash
python scripts/scan_documents.py /path/to/production_lines --output metadata.json
```

5. Use the generated JSON to feed downstream indexing, QA, or knowledge graph steps.

## Next Steps

* Connect ingestion results to vector stores or graph databases.
* Add document content extraction and parsing for common file types.
* Automate scheduled rescans and change detection.
