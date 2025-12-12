# Data Model

## Entities

### ProductionLineSnapshot
Represents the contents of a single production line directory at a given moment.

Fields:
- `name`: Production line identifier (directory name).
- `root_path`: Absolute path to the production line root.
- `documents`: List of `DocumentInfo` entries discovered under the root.
- `document_count`: Derived count of documents.
- `total_size_bytes`: Derived total size for all documents.

### DocumentInfo
Describes a single file within a production line.

Fields:
- `production_line`: Name of the production line the file belongs to.
- `relative_path`: Path of the file relative to its production line root.
- `absolute_path`: Full resolved path on disk.
- `size_bytes`: File size (bytes).
- `modified_time`: Last modification timestamp (UTC).
- `extension`: Lowercase file extension (derived).

## Relationships

* Every `DocumentInfo` belongs to exactly one `ProductionLineSnapshot`.
* Snapshots are meant to be regenerated whenever the underlying directories change; downstream systems should treat them as immutable records of a point in time.

## Extensibility

Future iterations can attach parsed content, structured fields (e.g., part numbers, revision IDs), and relationships across production lines or shared assets.
