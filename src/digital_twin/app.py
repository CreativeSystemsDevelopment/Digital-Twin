from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from .config import get_gemini_api_key
from .agent_monitor import get_monitor, AgentStatus, TaskPriority

app = FastAPI(title="Digital Twin Document Intake", version="0.1.0")

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
METADATA_PATH = DATA_ROOT / "metadata.json"
metadata_lock = threading.Lock()


def ensure_storage() -> None:
    """Create storage directories and metadata file if missing."""
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if not METADATA_PATH.exists():
        METADATA_PATH.write_text("[]", encoding="utf-8")


def load_metadata() -> List[dict]:
    if not METADATA_PATH.exists():
        return []
    try:
        with METADATA_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Metadata file is not valid JSON.") from exc


def save_metadata(records: List[dict]) -> None:
    METADATA_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")


def persist_upload(upload: UploadFile, dest_path: Path) -> tuple[str, int]:
    """Stream upload to disk while computing SHA-256."""
    hasher = hashlib.sha256()
    bytes_written = 0
    with dest_path.open("wb") as out:
        for chunk in iter(lambda: upload.file.read(1024 * 1024), b""):
            hasher.update(chunk)
            out.write(chunk)
            bytes_written += len(chunk)
    return hasher.hexdigest(), bytes_written


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def normalize_machine_id(machine_label: str) -> str:
    machine_label = (machine_label or "").strip()
    if not machine_label:
        raise HTTPException(status_code=400, detail="Machine name is required.")
    normalized = []
    for ch in machine_label:
        if ch.isalnum() or ch in ("-", "_", "."):
            normalized.append(ch)
        elif ch.isspace():
            normalized.append("_")
        else:
            normalized.append("_")
    machine_id = "".join(normalized).strip("._-")
    if not machine_id:
        raise HTTPException(status_code=400, detail="Machine name is not valid.")
    return machine_id[:64]


def get_machine_dirs(machine_id: str) -> tuple[Path, Path]:
    machine_dir = DATA_ROOT / machine_id
    raw_dir = machine_dir / "raw_data"
    imported_dir = machine_dir / "imported"
    raw_dir.mkdir(parents=True, exist_ok=True)
    imported_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, imported_dir


def parse_manual_contents_text(text: str) -> dict:
    """
    Return a mapping usable for categorization, e.g.
    {"major": {"1": "schematic"}, "minor": {"2(4)": "terminal_box_wiring_diagram"}}.
    """
    import re

    upper = text.upper()
    major: dict[str, str] = {}
    minor: dict[str, str] = {}

    for m in re.finditer(r"(?m)^\s*(\d+)\s*[\.．]\s*(.+?)\s*$", text):
        num = m.group(1)
        title = m.group(2).upper()
        if "SCHEMATIC DIAGRAM" in title:
            major[num] = "schematic"
        elif "ELECTRICAL CONSTRUCTION DRAWINGS" in title:
            major[num] = "electrical_construction_drawings"
        elif "PANEL OUTLINE" in title:
            major[num] = "panel_outline"
        elif "ELECTRICAL PARTS LIST" in title:
            major[num] = "electrical_parts_list"
        elif "ERROR LIST" in title:
            major[num] = "error_list"

    # Try to learn common sub-items under section 2 from the contents page.
    # This is intentionally conservative and best-effort.
    if "ELECTRICAL CONSTRUCTION DRAWINGS" in upper or "電気工事図" in text:
        if "CABLE LIST" in upper:
            # 2(1) + 2(3) often cable lists in this manual set.
            minor["2(1)"] = "cable_list"
            minor["2(3)"] = "cable_list"
        if "TERMINAL BOX WIRING DIAGRAM" in upper:
            # 2(2) + 2(4) often terminal box wiring diagrams.
            minor["2(2)"] = "terminal_box_wiring_diagram"
            minor["2(4)"] = "terminal_box_wiring_diagram"
        if "ELECTRICAL PARTS ARRANGEMENT" in upper:
            minor["2(5)"] = "electrical_parts_arrangement"
        if "GENERAL ARRANGEMENT" in upper:
            minor["2(6)"] = "general_arrangement"

    return {"major": major, "minor": minor}


def try_parse_contents_pdf(pdf_path: Path) -> Optional[dict]:
    try:
        from pypdf import PdfReader
    except Exception:
        return None

    try:
        reader = PdfReader(str(pdf_path))
        # Contents is usually near the front.
        pages = reader.pages[:3]
        extracted = "\n".join((p.extract_text() or "") for p in pages)
        if not extracted.strip():
            return None
        if "CONTENTS" not in extracted.upper() and "目" not in extracted:
            return None
        return parse_manual_contents_text(extracted)
    except Exception:
        return None


def detect_doc_category(filename: str, contents_map: Optional[dict]) -> str:
    name = (filename or "").upper()
    if "CONTENTS" in name or "MANUAL CONTENT" in name or "目次" in filename or "目 次" in filename:
        return "manual_contents"
    if "SCHEMATIC" in name:
        return "schematic"
    if "ELECTRICAL CONSTRUCTION" in name or "CONSTRUCTION DRAWING" in name:
        return "electrical_construction_drawings"
    if "ELECTRICAL PARTS LIST" in name or "PARTS LIST" in name:
        return "electrical_parts_list"
    if "CABLE LIST" in name:
        return "cable_list"
    if "ERROR LIST" in name or "ERROR" in name:
        return "error_list"
    if "TERMINAL BOX WIRING" in name:
        return "terminal_box_wiring_diagram"
    if "GENERAL ARRANGEMENT" in name:
        return "general_arrangement"
    if "PANEL OUTLINE" in name or "OUTLINE" in name:
        return "panel_outline"

    if contents_map:
        import re

        m = re.match(r"^\s*(\d{1,2})\s*\((\d+)\)", filename)
        if m:
            key = f"{int(m.group(1))}({int(m.group(2))})"
            if key in contents_map.get("minor", {}):
                return contents_map["minor"][key]
        m2 = re.match(r"^\s*(\d{1,2})\D", filename)
        if m2:
            key2 = str(int(m2.group(1)))
            if key2 in contents_map.get("major", {}):
                return contents_map["major"][key2]

    return "unknown"


@app.on_event("startup")
def _startup() -> None:
    ensure_storage()


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


HTML_PAGE = """
<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Digital Twin Document Intake</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 32px; max-width: 960px; }
        h1 { margin-bottom: 8px; }
        form { border: 1px solid #ddd; padding: 16px; border-radius: 8px; margin-bottom: 16px; background: #fafafa; }
        label { display: block; margin: 8px 0 4px; font-weight: 600; }
        input, select { width: 100%; padding: 8px; box-sizing: border-box; }
        button { margin-top: 12px; padding: 10px 16px; cursor: pointer; }
        #status { margin-top: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 8px; border-bottom: 1px solid #eee; text-align: left; }
        .muted { color: #666; }
        .chip { display: inline-block; padding: 2px 8px; border-radius: 12px; background: #eef; }
        .status-pill { display: inline-block; padding: 2px 8px; border-radius: 12px; background: #f0f0f0; color: #333; font-size: 12px; text-transform: capitalize; }
        #selected-files { margin: 8px 0; padding-left: 16px; }
        #selected-files li { margin: 4px 0; }
        .toolbar { display: flex; align-items: center; gap: 12px; margin: 16px 0; }
        .primary { background: #1f6feb; border: 0; color: #fff; border-radius: 8px; }
        .primary:hover { filter: brightness(0.95); }
        .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: none; align-items: center; justify-content: center; padding: 24px; }
        .modal { width: min(720px, 100%); background: #fff; border-radius: 12px; border: 1px solid #ddd; padding: 16px; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { margin: 0; font-size: 18px; }
        .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
        .row { display: grid; grid-template-columns: 1fr; gap: 12px; }
        .import-grid { margin-top: 16px; border: 1px solid #eee; border-radius: 10px; overflow: hidden; display: none; }
        .import-grid-header { padding: 12px 14px; background: #f6f8fa; border-bottom: 1px solid #eee; font-weight: 700; }
        .machine-row { display: flex; gap: 10px; align-items: end; }
        .machine-row input { flex: 1; }
    </style>
</head>
<body>
    <h1>Digital Twin Document Intake</h1>
    <p>Import machine documentation first. Each upload must be assigned to a machine so files land in the correct directory.</p>

    <div class=\"toolbar\">
        <button type=\"button\" class=\"primary\" id=\"open-import\">Upload / Import</button>
        <button type=\"button\" id=\"refresh\">Refresh List</button>
        <div id=\"status\" class=\"muted\"></div>
    </div>

    <div class=\"modal-backdrop\" id=\"modal-backdrop\" role=\"dialog\" aria-modal=\"true\">
        <div class=\"modal\">
            <div class=\"modal-header\">
                <h2>Import documents</h2>
                <button type=\"button\" id=\"close-modal\">Close</button>
            </div>

            <div class=\"row\">
                <div>
                    <label for=\"machine_label\">Machine / Line Name</label>
                    <div class=\"machine-row\">
                        <input type=\"text\" id=\"machine_label\" placeholder=\"e.g. UH1650\" required />
                        <button type=\"button\" class=\"primary\" id=\"confirm-import\">Upload</button>
                    </div>
                    <div class=\"muted\">Creates <code>src/data/&lt;machine&gt;/raw_data</code> and <code>src/data/&lt;machine&gt;/imported</code>.</div>
                    <div id=\"modal-status\" class=\"muted\" style=\"margin-top:8px;\"></div>
                </div>
            </div>

            <div class=\"modal-actions\">
                <button type=\"button\" id=\"cancel-import\">Cancel</button>
            </div>

            <input type=\"file\" id=\"file\" name=\"files\" multiple style=\"display:none\" />
            <ul id=\"selected-files\" class=\"muted\"></ul>

            <div class=\"import-grid\" id=\"modal-import-grid\">
                <div class=\"import-grid-header\" id=\"modal-import-grid-header\"></div>
                <div style=\"padding: 0 0 12px 0;\">
                    <table style=\"margin-top: 0;\">
                        <thead>
                            <tr>
                                <th>Original filename</th>
                                <th>Uploaded</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id=\"modal-import-grid-body\"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <h2>Stored Files</h2>
    <div id=\"files\" class=\"muted\">Loading…</div>

    <script>
        async function fetchFiles() {
            const filesEl = document.getElementById('files');
            filesEl.textContent = 'Loading…';
            try {
                const res = await fetch('/files');
                if (!res.ok) throw new Error('Request failed');
                const data = await res.json();
                if (!data.length) {
                    filesEl.textContent = 'No files uploaded yet.';
                    return;
                }
                const rows = data.map(f => `
                    <tr>
                        <td><span class=\"chip\">${f.doc_category || f.doc_type || 'unknown'}</span></td>
                        <td>${f.original_name}</td>
                        <td>${f.machine_id}</td>
                        <td>${(f.size_bytes/1024).toFixed(1)} KB</td>
                        <td><span class=\"status-pill\">${(f.status || 'uploaded').replace('_', ' ')}</span></td>
                        <td class=\"muted\">${f.uploaded_at}</td>
                    </tr>
                `).join('');
                filesEl.innerHTML = `<table><thead><tr><th>Category</th><th>Name</th><th>Machine</th><th>Size</th><th>Status</th><th>Uploaded</th></tr></thead><tbody>${rows}</tbody></table>`;
            } catch (err) {
                filesEl.textContent = 'Failed to load files.';
            }
        }

        const status = document.getElementById('status');
        const modal = document.getElementById('modal-backdrop');
        const openBtn = document.getElementById('open-import');
        const closeBtn = document.getElementById('close-modal');
        const cancelBtn = document.getElementById('cancel-import');
        const confirmBtn = document.getElementById('confirm-import');
        const machineInput = document.getElementById('machine_label');
        const fileInput = document.getElementById('file');
        const selectedList = document.getElementById('selected-files');
        let uploadInProgress = false;
        const importGrid = document.getElementById('modal-import-grid');
        const importGridHeader = document.getElementById('modal-import-grid-header');
        const importGridBody = document.getElementById('modal-import-grid-body');
        const modalStatus = document.getElementById('modal-status');
        const rowByName = new Map();

        function formatUploadedAt(iso) {
            try {
                const d = new Date(iso);
                return d.toLocaleString(undefined, {
                    year: '2-digit',
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                });
            } catch (_) {
                return iso || '';
            }
        }

        function setRow(name, uploadedAt, statusText) {
            let row = rowByName.get(name);
            if (!row) {
                row = document.createElement('tr');
                row.innerHTML = `
                    <td></td>
                    <td class="muted"></td>
                    <td><span class="status-pill"></span></td>
                `;
                importGridBody.appendChild(row);
                rowByName.set(name, row);
            }
            row.children[0].textContent = name || '';
            row.children[1].textContent = uploadedAt ? formatUploadedAt(uploadedAt) : '';
            row.children[2].querySelector('.status-pill').textContent = (statusText || '').replace('_', ' ');
        }

        function openModal() {
            modal.style.display = 'flex';
            status.textContent = '';
            modalStatus.textContent = '';
            importGrid.style.display = 'none';
            machineInput.focus();
        }
        function closeModal() {
            if (uploadInProgress) return;
            modal.style.display = 'none';
            machineInput.value = '';
            fileInput.value = '';
            selectedList.innerHTML = '';
            uploadInProgress = false;
            confirmBtn.disabled = false;
            closeBtn.disabled = false;
            cancelBtn.disabled = false;
        }

        openBtn.addEventListener('click', openModal);
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'flex') closeModal();
        });

        function setModalBusy(busy) {
            uploadInProgress = busy;
            confirmBtn.disabled = busy;
            closeBtn.disabled = busy;
            cancelBtn.disabled = busy;
        }

        async function doUploadStream() {
            if (uploadInProgress) return;
            const form = new FormData();
            const machineLabel = (machineInput.value || '').trim();
            if (!machineLabel) {
                status.textContent = 'Please enter a machine / line name.';
                return;
            }
            if (!fileInput.files.length) {
                status.textContent = 'Please choose one or more files.';
                return;
            }
            Array.from(fileInput.files).forEach(f => form.append('files', f));
            form.append('machine_label', machineLabel);

            status.textContent = 'Uploading…';
            modalStatus.textContent = 'Uploading…';
            setModalBusy(true);
            importGrid.style.display = 'block';
            importGridHeader.textContent = `Importing to: ${machineLabel}`;
            importGridBody.innerHTML = '';
            rowByName.clear();
            Array.from(fileInput.files).forEach(f => setRow(f.name, '', 'queued'));

            try {
                const res = await fetch('/upload/stream', { method: 'POST', body: form });
                if (!res.ok || !res.body) {
                    const maybe = await res.json().catch(() => null);
                    throw new Error(maybe?.detail || `Upload failed: ${res.status}`);
                }

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\\n\\n');
                    buffer = parts.pop() || '';

                    for (const part of parts) {
                        const lines = part.split('\\n');
                        let evt = 'message';
                        let dataLine = '';
                        for (const line of lines) {
                            if (line.startsWith('event:')) evt = line.slice(6).trim();
                            if (line.startsWith('data:')) dataLine += line.slice(5).trim();
                        }
                        if (!dataLine) continue;
                        const payload = JSON.parse(dataLine);
                        if (evt === 'file_started') {
                            setRow(payload.original_name, payload.uploaded_at, 'uploading');
                        } else if (evt === 'file_completed') {
                            setRow(payload.original_name, payload.uploaded_at, payload.status || 'uploaded_raw');
                        } else if (evt === 'file_failed') {
                            setRow(payload.original_name, payload.uploaded_at, 'failed');
                        } else if (evt === 'done') {
                            modalStatus.textContent = `Uploaded ${payload.uploaded} file(s).`;
                            status.textContent = `Uploaded ${payload.uploaded} file(s).`;
                        }
                    }
                }

                fetchFiles();
            } catch (err) {
                modalStatus.textContent = err.message;
                status.textContent = err.message;
            } finally {
                setModalBusy(false);
            }
        }

        confirmBtn.addEventListener('click', () => {
            const machineLabel = (machineInput.value || '').trim();
            if (!machineLabel) {
                status.textContent = 'Please enter a machine / line name.';
                machineInput.focus();
                return;
            }
            // Trigger the file picker only after machine name is provided.
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (!fileInput.files.length) {
                selectedList.innerHTML = '';
                return;
            }
            const items = Array.from(fileInput.files).map(f => `<li>${f.name} <span class=\"muted\">(${(f.size/1024).toFixed(1)} KB)</span></li>`);
            selectedList.innerHTML = items.join('');
            doUploadStream();
        });

        document.getElementById('refresh').addEventListener('click', fetchFiles);
        fetchFiles();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    ensure_storage()
    return HTMLResponse(content=HTML_PAGE)


@app.post("/upload")
def upload_documents(
    files: List[UploadFile] = File(...),
    machine_label: str = Form(...),
) -> dict:
    """Upload one or more documents and append them to metadata."""
    ensure_storage()
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    machine_id = normalize_machine_id(machine_label)
    raw_dir, imported_dir = get_machine_dirs(machine_id)

    # Save files first so we can parse an optional "contents" PDF for categorization hints.
    saved: List[dict] = []
    contents_path: Optional[Path] = None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Each upload must include a filename.")

        safe_name = Path(file.filename).name
        dest_path = raw_dir / f"{timestamp}_{safe_name}"
        sha256, size_bytes = persist_upload(file, dest_path)
        saved.append(
            {
                "safe_name": safe_name,
                "dest_path": dest_path,
                "sha256": sha256,
                "size_bytes": size_bytes,
            }
        )
        upper = safe_name.upper()
        if contents_path is None and dest_path.suffix.lower() == ".pdf" and (
            "CONTENTS" in upper or "MANUAL CONTENT" in upper or "目次" in safe_name or "目 次" in safe_name
        ):
            contents_path = dest_path

    contents_map = try_parse_contents_pdf(contents_path) if contents_path else None

    uploaded_records: List[dict] = []
    with metadata_lock:
        existing = load_metadata()

        for item in saved:
            safe_name = item["safe_name"]
            dest_path: Path = item["dest_path"]
            sha256 = item["sha256"]
            size_bytes = item["size_bytes"]
            doc_category = detect_doc_category(safe_name, contents_map)

            record = {
                "id": str(uuid4()),
                "machine_id": machine_id,
                "machine_label": machine_label,
                "doc_category": doc_category,
                "original_name": safe_name,
                "stored_path": str(dest_path.relative_to(DATA_ROOT.parent)),
                "sha256": sha256,
                "size_bytes": size_bytes,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "status": "uploaded_raw",
                "raw_dir": str(raw_dir.relative_to(DATA_ROOT.parent)),
                "imported_dir": str(imported_dir.relative_to(DATA_ROOT.parent)),
            }

            existing.append(record)
            uploaded_records.append(record)

        save_metadata(existing)

    return {"uploaded": len(uploaded_records), "records": uploaded_records}


@app.post("/upload/stream")
def upload_documents_stream(
    files: List[UploadFile] = File(...),
    machine_label: str = Form(...),
) -> StreamingResponse:
    """Upload documents and stream per-file progress events (SSE)."""
    ensure_storage()
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    machine_id = normalize_machine_id(machine_label)
    raw_dir, imported_dir = get_machine_dirs(machine_id)

    def event_stream():
        uploaded_count = 0
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        yield sse_event(
            "start",
            {
                "machine_id": machine_id,
                "machine_label": machine_label,
                "raw_dir": str(raw_dir.relative_to(DATA_ROOT.parent)),
                "imported_dir": str(imported_dir.relative_to(DATA_ROOT.parent)),
                "file_count": len(files),
            },
        )

        # First pass: save files so we can optionally parse a manual contents PDF.
        saved: List[dict] = []
        contents_path: Optional[Path] = None
        for file in files:
            if not file.filename:
                yield sse_event("file_failed", {"original_name": None, "error": "Missing filename"})
                continue

            safe_name = Path(file.filename).name
            yield sse_event(
                "file_started",
                {"original_name": safe_name, "uploaded_at": datetime.now(timezone.utc).isoformat()},
            )

            try:
                dest_path = raw_dir / f"{timestamp}_{safe_name}"
                sha256, size_bytes = persist_upload(file, dest_path)
                saved.append(
                    {
                        "safe_name": safe_name,
                        "dest_path": dest_path,
                        "sha256": sha256,
                        "size_bytes": size_bytes,
                    }
                )
                upper = safe_name.upper()
                if contents_path is None and dest_path.suffix.lower() == ".pdf" and (
                    "CONTENTS" in upper or "MANUAL CONTENT" in upper or "目次" in safe_name or "目 次" in safe_name
                ):
                    contents_path = dest_path
            except Exception as exc:
                yield sse_event(
                    "file_failed",
                    {
                        "original_name": safe_name,
                        "uploaded_at": datetime.now(timezone.utc).isoformat(),
                        "error": str(exc),
                    },
                )

        contents_map = try_parse_contents_pdf(contents_path) if contents_path else None

        # Second pass: append metadata and emit completion per file.
        for item in saved:
            safe_name = item["safe_name"]
            dest_path: Path = item["dest_path"]
            sha256 = item["sha256"]
            size_bytes = item["size_bytes"]
            doc_category = detect_doc_category(safe_name, contents_map)

            record = {
                "id": str(uuid4()),
                "machine_id": machine_id,
                "machine_label": machine_label,
                "doc_category": doc_category,
                "original_name": safe_name,
                "stored_path": str(dest_path.relative_to(DATA_ROOT.parent)),
                "sha256": sha256,
                "size_bytes": size_bytes,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "status": "uploaded_raw",
                "raw_dir": str(raw_dir.relative_to(DATA_ROOT.parent)),
                "imported_dir": str(imported_dir.relative_to(DATA_ROOT.parent)),
            }

            with metadata_lock:
                existing = load_metadata()
                existing.append(record)
                save_metadata(existing)

            uploaded_count += 1
            yield sse_event("file_completed", record)

        yield sse_event("done", {"uploaded": uploaded_count})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/files")
def list_files(machine_id: Optional[str] = None) -> List[dict]:
    ensure_storage()
    records = load_metadata()
    if machine_id:
        records = [rec for rec in records if rec.get("machine_id") == machine_id]
    return records


# ============================================================================
# GEMINI EXTRACTION ENDPOINTS
# ============================================================================

EXTRACTION_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Gemini Schematic Extraction</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 24px;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        h1 { color: #00d4ff; margin-bottom: 8px; }
        h2 { color: #00d4ff; margin-top: 32px; font-size: 1.2em; }
        .subtitle { color: #888; margin-bottom: 24px; }
        
        .container { max-width: 1200px; margin: 0 auto; }
        
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #0f3460;
        }
        
        .status-bar {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #444;
        }
        .status-dot.ready { background: #00ff88; }
        .status-dot.running { background: #ffaa00; animation: pulse 1s infinite; }
        .status-dot.error { background: #ff4444; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        button {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: transform 0.1s, box-shadow 0.1s;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
        }
        button:disabled {
            background: #444;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .step-list {
            font-family: 'Consolas', monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
            background: #0d1b2a;
            border-radius: 8px;
            padding: 12px;
        }
        
        .step {
            display: flex;
            align-items: flex-start;
            padding: 8px 0;
            border-bottom: 1px solid #1a3a5c;
        }
        .step:last-child { border-bottom: none; }
        
        .step-icon {
            width: 20px;
            height: 20px;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .step-icon.pending { color: #666; }
        .step-icon.running { color: #ffaa00; }
        .step-icon.completed { color: #00ff88; }
        .step-icon.failed { color: #ff4444; }
        
        .step-content { flex: 1; }
        .step-name { font-weight: bold; color: #00d4ff; }
        .step-message { color: #aaa; margin-top: 2px; }
        .step-duration { 
            color: #888; 
            font-size: 11px;
            margin-left: 12px;
        }
        
        .step-details {
            background: #0a1628;
            padding: 8px;
            margin-top: 8px;
            border-radius: 4px;
            font-size: 11px;
            color: #888;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .results-section {
            margin-top: 24px;
        }
        
        .extraction-result {
            background: #0d1b2a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .extraction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .page-badge {
            background: #00d4ff;
            color: #000;
            padding: 4px 12px;
            border-radius: 16px;
            font-weight: bold;
        }
        
        .token-info {
            color: #888;
            font-size: 12px;
        }
        
        pre.json-output {
            background: #0a1628;
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 12px;
            color: #00ff88;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }
        
        .metric {
            background: #0d1b2a;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
        }
        .metric-label {
            color: #888;
            font-size: 12px;
            margin-top: 4px;
        }
        
        .api-key-status {
            font-size: 12px;
            padding: 8px 12px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .api-key-status.valid {
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
        }
        .api-key-status.invalid {
            background: rgba(255, 68, 68, 0.1);
            color: #ff4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Gemini Schematic Extraction</h1>
        <p class="subtitle">UBE 1650 Die Casting Machine - Visual Step-by-Step Workflow</p>
        
        <div class="card">
            <div class="status-bar">
                <div class="status-dot" id="status-dot"></div>
                <span id="status-text">Ready</span>
                <div id="api-key-status" class="api-key-status">Checking API key...</div>
            </div>
            
            <button id="run-btn" onclick="runExtraction()">
                🚀 Run Sample Extraction (2 Random Pages)
            </button>
            
            <div class="metrics" id="metrics" style="display: none;">
                <div class="metric">
                    <div class="metric-value" id="metric-duration">--</div>
                    <div class="metric-label">Total Duration (ms)</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="metric-pages">--</div>
                    <div class="metric-label">Pages Extracted</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="metric-tokens">--</div>
                    <div class="metric-label">Tokens Used</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="metric-cached">--</div>
                    <div class="metric-label">Cached Tokens</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Workflow Steps</h2>
            <div class="step-list" id="step-list">
                <div class="step">
                    <span class="step-icon pending">○</span>
                    <div class="step-content">
                        <div class="step-name">Waiting to start...</div>
                        <div class="step-message">Click the button above to begin extraction</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card results-section" id="results-section" style="display: none;">
            <h2>📄 Extraction Results</h2>
            <div id="extraction-results"></div>
        </div>
    </div>
    
    <script>
        const icons = {
            pending: '○',
            running: '◉',
            completed: '✓',
            failed: '✗'
        };
        
        async function checkApiKey() {
            const statusEl = document.getElementById('api-key-status');
            try {
                const res = await fetch('/gemini/status');
                const data = await res.json();
                if (data.api_key_configured) {
                    statusEl.className = 'api-key-status valid';
                    statusEl.textContent = '✓ API Key: ' + data.api_key_preview;
                } else {
                    statusEl.className = 'api-key-status invalid';
                    statusEl.textContent = '✗ No API Key configured';
                }
            } catch (e) {
                statusEl.className = 'api-key-status invalid';
                statusEl.textContent = '✗ Error checking API key';
            }
        }
        
        function updateStatus(status, text) {
            const dot = document.getElementById('status-dot');
            const textEl = document.getElementById('status-text');
            dot.className = 'status-dot ' + status;
            textEl.textContent = text;
        }
        
        function renderSteps(steps) {
            const container = document.getElementById('step-list');
            container.innerHTML = steps.map(step => `
                <div class="step">
                    <span class="step-icon ${step.status}">${icons[step.status]}</span>
                    <div class="step-content">
                        <div class="step-name">${step.name}</div>
                        <div class="step-message">${step.message}</div>
                        ${step.details && Object.keys(step.details).length > 0 ? 
                            `<div class="step-details">${JSON.stringify(step.details, null, 2)}</div>` : ''}
                    </div>
                    ${step.duration_ms ? `<span class="step-duration">${step.duration_ms.toFixed(0)}ms</span>` : ''}
                </div>
            `).join('');
            container.scrollTop = container.scrollHeight;
        }
        
        function renderResults(extractions) {
            const container = document.getElementById('extraction-results');
            container.innerHTML = extractions.map(ext => `
                <div class="extraction-result">
                    <div class="extraction-header">
                        <span class="page-badge">Page ${ext.page}</span>
                        <span class="token-info">
                            Prompt: ${ext.usage?.prompt_tokens || '?'} | 
                            Response: ${ext.usage?.response_tokens || '?'} |
                            Cached: ${ext.usage?.cached_tokens || 0}
                        </span>
                    </div>
                    <pre class="json-output">${ext.parsed ? JSON.stringify(ext.parsed, null, 2) : ext.raw_response}</pre>
                </div>
            `).join('');
        }
        
        async function runExtraction() {
            const btn = document.getElementById('run-btn');
            btn.disabled = true;
            updateStatus('running', 'Running extraction...');
            
            document.getElementById('metrics').style.display = 'none';
            document.getElementById('results-section').style.display = 'none';
            
            renderSteps([{
                status: 'running',
                name: 'Starting...',
                message: 'Initializing extraction workflow'
            }]);
            
            try {
                const res = await fetch('/gemini/extract-sample', { method: 'POST' });
                const data = await res.json();
                
                renderSteps(data.steps || []);
                
                if (data.success) {
                    updateStatus('ready', 'Extraction complete!');
                    
                    // Show metrics
                    document.getElementById('metrics').style.display = 'grid';
                    document.getElementById('metric-duration').textContent = data.total_duration_ms?.toFixed(0) || '--';
                    document.getElementById('metric-pages').textContent = data.extractions?.length || 0;
                    
                    let totalTokens = 0;
                    let cachedTokens = 0;
                    (data.extractions || []).forEach(ext => {
                        totalTokens += (ext.usage?.prompt_tokens || 0) + (ext.usage?.response_tokens || 0);
                        cachedTokens += ext.usage?.cached_tokens || 0;
                    });
                    document.getElementById('metric-tokens').textContent = totalTokens;
                    document.getElementById('metric-cached').textContent = cachedTokens;
                    
                    // Show results
                    if (data.extractions?.length) {
                        document.getElementById('results-section').style.display = 'block';
                        renderResults(data.extractions);
                    }
                } else {
                    updateStatus('error', 'Extraction failed');
                }
            } catch (e) {
                updateStatus('error', 'Error: ' + e.message);
                renderSteps([{
                    status: 'failed',
                    name: 'Error',
                    message: e.message
                }]);
            }
            
            btn.disabled = false;
        }
        
        // Check API key on load
        checkApiKey();
    </script>
</body>
</html>
"""


@app.get("/gemini", response_class=HTMLResponse)
def gemini_ui() -> HTMLResponse:
    """Serve the Gemini extraction UI."""
    return HTMLResponse(content=EXTRACTION_HTML)


@app.get("/gemini/status")
def gemini_status() -> dict:
    """Check Gemini API configuration status."""
    api_key = get_gemini_api_key()
    return {
        "api_key_configured": bool(api_key),
        "api_key_preview": f"{api_key[:8]}...{api_key[-4:]}" if api_key else None
    }


@app.post("/gemini/extract-sample")
def extract_sample() -> dict:
    """Run a sample extraction on 2 random pages."""
    from .gemini_service import GeminiExtractor, StepLogger
    
    logger = StepLogger()
    extractor = GeminiExtractor(logger=logger)
    
    # Paths to required files
    legacy_schematic_path = DATA_ROOT / "raw" / "1650" / "20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf"
    new_schematic_path = DATA_ROOT / "1650" / "raw_data" / "20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf"
    schematic_path = legacy_schematic_path if legacy_schematic_path.exists() else new_schematic_path
    legend_path = DATA_ROOT / "inspection" / "legend.png"
    reading_path = DATA_ROOT / "inspection" / "reading_instructions.png"
    system_path = DATA_ROOT / "inspection" / "system_instructions.txt"
    
    # Verify files exist
    missing = []
    for path, name in [(schematic_path, "schematic"), (legend_path, "legend"), 
                       (reading_path, "reading_instructions"), (system_path, "system_instructions")]:
        if not path.exists():
            missing.append(name)
    
    if missing:
        return {
            "success": False,
            "steps": [{
                "step": 1,
                "name": "File Check",
                "status": "failed",
                "message": f"Missing files: {', '.join(missing)}"
            }],
            "extractions": []
        }
    
    result = extractor.run_sample_extraction(
        schematic_path=schematic_path,
        legend_path=legend_path,
        reading_instructions_path=reading_path,
        system_instructions_path=system_path,
        num_pages=2
    )
    
    return result


# ============================================================================
# Agent Monitoring Endpoints
# ============================================================================

@app.get("/monitor/agents")
async def list_agents():
    """Get a list of all registered agents."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    agents = monitor.get_all_agents()
    return {
        "agents": [agent.to_dict() for agent in agents],
        "total": len(agents)
    }


@app.get("/monitor/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    summary = monitor.get_agent_summary(agent_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return summary


@app.post("/monitor/agents/register")
async def register_agent(name: str, agent_type: str, metadata: Optional[dict] = None):
    """Register a new agent with the monitoring system."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    agent_id = monitor.register_agent(name, agent_type, metadata)
    
    return {
        "agent_id": agent_id,
        "message": f"Agent '{name}' registered successfully"
    }


@app.put("/monitor/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str, activity: Optional[str] = None):
    """Update an agent's status."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    try:
        agent_status = AgentStatus(status)
        monitor.update_agent_status(agent_id, agent_status, activity)
        return {"message": f"Agent {agent_id} status updated to {status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/monitor/agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, current_task_id: Optional[str] = None):
    """Record an agent heartbeat."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    try:
        monitor.heartbeat(agent_id, current_task_id)
        return {"message": "Heartbeat recorded"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/monitor/tasks")
async def list_tasks(agent_id: Optional[str] = None, status: Optional[str] = None):
    """Get a list of all tasks, optionally filtered by agent or status."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    task_status = AgentStatus(status) if status else None
    tasks = monitor.get_all_tasks(agent_id, task_status)
    
    return {
        "tasks": [task.to_dict() for task in tasks],
        "total": len(tasks)
    }


@app.get("/monitor/tasks/{task_id}")
async def get_task_details(task_id: str):
    """Get detailed information about a specific task."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    task = monitor.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task.to_dict()


@app.post("/monitor/tasks/assign")
async def assign_task(
    agent_id: str,
    description: str,
    task_type: str,
    priority: str = "normal",
    pages: Optional[List[int]] = None,
    metadata: Optional[dict] = None
):
    """Assign a new task to an agent."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    try:
        task_priority = TaskPriority(priority)
        task_id = monitor.assign_task(
            agent_id, description, task_type, task_priority, pages, metadata
        )
        return {
            "task_id": task_id,
            "message": f"Task assigned to agent {agent_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/monitor/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: str, error: Optional[str] = None):
    """Update a task's status."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    try:
        task_status = AgentStatus(status)
        monitor.update_task_status(task_id, task_status, error)
        return {"message": f"Task {task_id} status updated to {status}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/monitor/tasks/{task_id}/progress")
async def update_task_progress(task_id: str, progress: float, pages_completed: Optional[List[int]] = None):
    """Update a task's progress."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    
    try:
        monitor.update_task_progress(task_id, progress, pages_completed)
        return {"message": f"Task {task_id} progress updated to {progress:.1%}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/monitor/summary")
async def get_monitor_summary():
    """Get an overall summary of all agents and tasks."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    return monitor.get_overall_summary()


@app.get("/monitor/incomplete")
async def get_incomplete_tasks():
    """Get all tasks that are not yet completed."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    tasks = monitor.get_incomplete_tasks()
    
    return {
        "incomplete_tasks": [task.to_dict() for task in tasks],
        "total": len(tasks)
    }


@app.get("/monitor/stalled")
async def check_stalled_agents(timeout_seconds: float = 300):
    """Check for agents that haven't sent a heartbeat recently."""
    monitor = get_monitor(DATA_ROOT / "monitor_state.json")
    stalled = monitor.check_stalled_agents(timeout_seconds)
    
    return {
        "stalled_agents": stalled,
        "total": len(stalled),
        "timeout_seconds": timeout_seconds
    }


@app.get("/monitor/dashboard", response_class=HTMLResponse)
async def monitor_dashboard():
    """Display a monitoring dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Monitor Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a1628 0%, #1a2a3a 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: rgba(0, 212, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        h1 {
            color: #00d4ff;
            font-size: 32px;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #888;
            font-size: 14px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: rgba(13, 27, 42, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 8px;
        }
        
        .stat-label {
            color: #888;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section {
            background: rgba(13, 27, 42, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        .section-title {
            color: #00d4ff;
            font-size: 20px;
            margin-bottom: 16px;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
            padding-bottom: 8px;
        }
        
        .agent-list, .task-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .agent-item, .task-item {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-pending { border-left-color: #666; }
        .status-running { border-left-color: #ffaa00; }
        .status-completed { border-left-color: #00ff88; }
        .status-failed { border-left-color: #ff4444; }
        .status-paused { border-left-color: #888; }
        
        .agent-info, .task-info {
            flex: 1;
        }
        
        .agent-name, .task-description {
            font-weight: bold;
            color: #fff;
            margin-bottom: 4px;
        }
        
        .agent-type, .task-type {
            color: #888;
            font-size: 12px;
        }
        
        .status-badge {
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-badge.pending { background: #666; color: #fff; }
        .status-badge.running { background: #ffaa00; color: #000; }
        .status-badge.completed { background: #00ff88; color: #000; }
        .status-badge.failed { background: #ff4444; color: #fff; }
        .status-badge.paused { background: #888; color: #fff; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            transition: width 0.3s ease;
        }
        
        .refresh-btn {
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #00ff88;
            transform: translateY(-2px);
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        
        .last-updated {
            color: #666;
            font-size: 12px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Agent Monitor Dashboard</h1>
            <p class="subtitle">Real-time monitoring of schematic extraction agents</p>
            <p class="last-updated" id="lastUpdated">Loading...</p>
        </header>
        
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-value" id="totalAgents">-</div>
                <div class="stat-label">Total Agents</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="runningAgents">-</div>
                <div class="stat-label">Running</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalTasks">-</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="completedTasks">-</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="overallProgress">-</div>
                <div class="stat-label">Overall Progress</div>
            </div>
        </div>
        
        <div style="margin-bottom: 24px; text-align: center;">
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
        </div>
        
        <div class="section">
            <h2 class="section-title">Agents</h2>
            <div class="agent-list" id="agentList">
                <div class="loading">Loading agents...</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Recent Tasks</h2>
            <div class="task-list" id="taskList">
                <div class="loading">Loading tasks...</div>
            </div>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                // Load summary
                const summaryResp = await fetch('/monitor/summary');
                const summary = await summaryResp.json();
                
                // Update stats
                document.getElementById('totalAgents').textContent = summary.total_agents;
                document.getElementById('runningAgents').textContent = summary.agents_by_status.running || 0;
                document.getElementById('totalTasks').textContent = summary.total_tasks;
                document.getElementById('completedTasks').textContent = summary.tasks_by_status.completed || 0;
                document.getElementById('overallProgress').textContent = 
                    (summary.overall_progress * 100).toFixed(1) + '%';
                
                // Update agents
                const agentList = document.getElementById('agentList');
                if (summary.agents.length === 0) {
                    agentList.innerHTML = '<div class="empty-state">No agents registered yet</div>';
                } else {
                    agentList.innerHTML = summary.agents.map(agent => `
                        <div class="agent-item status-${agent.status}">
                            <div class="agent-info">
                                <div class="agent-name">${agent.name}</div>
                                <div class="agent-type">${agent.agent_type} • Completed: ${agent.tasks_completed} • Failed: ${agent.tasks_failed}</div>
                                ${agent.last_activity ? `<div class="agent-type">Latest: ${agent.last_activity}</div>` : ''}
                            </div>
                            <span class="status-badge ${agent.status}">${agent.status}</span>
                        </div>
                    `).join('');
                }
                
                // Load and display tasks
                const tasksResp = await fetch('/monitor/tasks');
                const tasksData = await tasksResp.json();
                
                const taskList = document.getElementById('taskList');
                if (tasksData.tasks.length === 0) {
                    taskList.innerHTML = '<div class="empty-state">No tasks yet</div>';
                } else {
                    // Sort by created_at desc, show latest 20
                    const recentTasks = tasksData.tasks
                        .sort((a, b) => b.created_at - a.created_at)
                        .slice(0, 20);
                    
                    taskList.innerHTML = recentTasks.map(task => {
                        const progressPercent = (task.progress * 100).toFixed(0);
                        return `
                            <div class="task-item status-${task.status}">
                                <div class="task-info">
                                    <div class="task-description">${task.description}</div>
                                    <div class="task-type">
                                        ${task.task_type} • Priority: ${task.priority}
                                        ${task.pages_assigned.length > 0 ? `• Pages: ${task.pages_assigned.length}` : ''}
                                    </div>
                                    ${task.status === 'running' ? `
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${progressPercent}%"></div>
                                        </div>
                                    ` : ''}
                                    ${task.error_message ? `<div style="color: #ff4444; font-size: 12px; margin-top: 4px;">${task.error_message}</div>` : ''}
                                </div>
                                <span class="status-badge ${task.status}">${task.status}</span>
                            </div>
                        `;
                    }).join('');
                }
                
                document.getElementById('lastUpdated').textContent = 
                    `Last updated: ${new Date().toLocaleTimeString()}`;
                    
            } catch (error) {
                console.error('Error loading data:', error);
                alert('Error loading dashboard data. Please check console.');
            }
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
    </script>
</body>
</html>
    """
