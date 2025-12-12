# Digital Twin Documentation Pipeline

This project ingests all documentation for a specific diecast machine and converts it into a searchable database/vector store for semantic querying. Initial scope is to intake and persist all raw documentation locally, then focus on schematic extraction.

## Current focus
- Provide a simple upload API to store source documents locally (organized per machine).
- Track basic metadata for each upload (filename, machine id, doc type, checksum, size, timestamp).
- Keep raw docs available in the workspace while avoiding accidental commits.

## Setup
1) Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
2) Install dependencies: `pip install -e .`
3) (Optional) To use Gemini locally, copy `.env.example` to `.env` and set `GEMINI_API_KEY` (kept out of git).

## Run the local intake API + web UI
- Start the service: `uvicorn src.digital_twin.app:app --reload --port 8000`
- Open the web UI: http://127.0.0.1:5173 (Frontend)
- Health check: `curl http://127.0.0.1:8000/health`

### API examples (optional)
- Single file: `curl -X POST -F "file=@/path/to/doc.pdf" -F "machine_id=machine-001" -F "doc_type=schematic" http://127.0.0.1:8000/upload`
- List stored files (optionally filter): `curl "http://127.0.0.1:8000/files?machine_id=machine-001"`

## Storage layout
- Uploaded files: `data/raw/<machine_id>/<timestamp>_<original_name>`
- Metadata log: `data/metadata.json`
- Git ignores raw uploads and metadata by default to prevent accidental commits.

## Next steps
- Define the structured schema for schematic elements (symbols, nets, references, parameters).
- Add parsers for the diecast machine schematic formats and emit normalized JSON.
- Generate embeddings for structured + text fields and push to a vector store for semantic queries.
- Add a minimal UI/CLI for querying once extraction is in place.

## Visibility
- Make the GitHub repo private via Settings → General → Danger Zone → Change visibility.
