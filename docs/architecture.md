# Architecture Outline

The platform centers on converting production line documents stored on a local drive into structured metadata suitable for a digital twin. The initial components focus on discovery and description; later iterations can add parsing, indexing, and analytics.

## Key Concepts

* **Production line root**: A directory whose name identifies a production line. All documents beneath it (nested folders included) belong to that line.
* **Document metadata**: Basic facts about each file (path, size, modified time, extension) used to drive inventory, quality checks, and downstream parsers.
* **Snapshots**: A point-in-time view of a production line directory with counts, sizes, and file mix summaries.

## Components

1. **Ingestion (local scan)**
   * Recursively walks each production line directory.
   * Captures file size, extension, and timestamps to support change detection.
   * Produces JSON snapshots so other services (indexers, QA checks, parsers) can consume the data without re-reading the file system.

2. **Modeling**
   * Dataclasses in `digital_twin.models` represent documents and production line snapshots.
   * Conversion helpers in `digital_twin.ingestion` convert snapshots to JSON-friendly dictionaries.

3. **Reporting**
   * Utility functions in `digital_twin.reporting` aggregate extension counts and sizes per production line.
   * Future reports can surface missing documents, age-of-files metrics, or schema compliance.

4. **Extensibility Hooks**
   * The CLI accepts a root directory path and writes JSON output; downstream tools can enrich the metadata with parsed content, embeddings, or graph links.
   * Additional storage targets (object store, databases, search engines) can be added by plugging into the JSON output.

## Execution Flow

1. User runs `python scripts/scan_documents.py /root/of/production_lines --output metadata.json`.
2. The scanner iterates each production line folder (direct children of the provided root), gathers file metadata, and builds snapshots.
3. A summary JSON file is written to disk (or printed), ready for indexing, QA, or synchronization tasks.
