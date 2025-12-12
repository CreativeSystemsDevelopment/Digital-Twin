from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploaded_documents"
METADATA_FILE = UPLOAD_DIR / "uploads.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Digital Twin Document Uploads")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def _contains_schematic_keyword(file_name: str) -> bool:
    return "schematic diagram" in file_name.lower()


def _load_metadata() -> List[dict]:
    if not METADATA_FILE.exists():
        return []
    return json.loads(METADATA_FILE.read_text())


def _save_metadata(records: List[dict]) -> None:
    METADATA_FILE.write_text(json.dumps(records, indent=2))


def _record_upload(original_name: str, stored_name: str, content_type: str, size: int) -> dict:
    uploaded_at = datetime.utcnow().isoformat() + "Z"
    flagged_for_processing = _contains_schematic_keyword(original_name)
    return {
        "original_name": original_name,
        "stored_name": stored_name,
        "content_type": content_type,
        "size": size,
        "uploaded_at": uploaded_at,
        "flagged_for_processing": flagged_for_processing,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, message: str | None = None):
    documents = _load_metadata()
    flagged_count = sum(1 for item in documents if item["flagged_for_processing"])
    context = {
        "request": request,
        "documents": list(reversed(documents)),
        "message": message,
        "flagged_count": flagged_count,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    records = _load_metadata()
    for upload_file in files:
        stored_name = f"{datetime.utcnow().timestamp():.0f}_{upload_file.filename.replace(' ', '_')}"
        destination = UPLOAD_DIR / stored_name
        content = await upload_file.read()
        destination.write_bytes(content)
        record = _record_upload(
            original_name=upload_file.filename,
            stored_name=stored_name,
            content_type=upload_file.content_type or "application/octet-stream",
            size=len(content),
        )
        records.append(record)
    _save_metadata(records)
    return RedirectResponse(url="/?message=Upload%20complete", status_code=303)


@app.get("/files/{stored_name}")
async def get_file(stored_name: str):
    file_path = UPLOAD_DIR / stored_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    records = _load_metadata()
    original_name = next((item["original_name"] for item in records if item["stored_name"] == stored_name), stored_name)
    return FileResponse(file_path, media_type="application/pdf", filename=original_name)


def run() -> None:
    import uvicorn

    uvicorn.run("digital_twin.webapp:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
