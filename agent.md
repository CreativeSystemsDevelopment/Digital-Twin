# Agent Handoff Notes

## Repo Quick Facts
- Name: Digital-Twin (main branch)
- Stack: FastAPI + Uvicorn, Google Gemini (google-genai SDK), python-dotenv
- Key paths:
  - Schematic PDF: src/data/raw/1650/20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf
  - Legend/reading refs: src/data/inspection/legend.png, reading_instructions.png
  - System instructions (clean text): src/data/inspection/system_instructions.txt
  - Gemini service: src/digital_twin/gemini_service.py
  - App server/UI: src/digital_twin/app.py

## Environment
- .env at repo root with GEMINI_API_KEY (already present locally). config.py now checks project root first.
- Install deps: `pip install -e .`

## Running the App
- Start server: `uvicorn src.digital_twin.app:app --host 0.0.0.0 --port 8000 --reload`
- Upload UI: http://localhost:8000/
- Gemini extraction UI: http://localhost:8000/gemini

## Gemini Extraction Flow (UI)
- Endpoint: POST /gemini/extract-sample
- Steps shown live: init client -> upload legend/reading/schematic -> create cache (gemini-2.5-flash-001) with system instructions -> pick 2 random pages (6-129) -> extract pages using structured JSON prompt -> display timings/token usage.
- Uses context cache + structured outputs (response_mime_type=application/json).

## Key Files Added
- src/digital_twin/gemini_service.py: handles logging, cache creation, sample extraction.
- src/digital_twin/app.py: added Gemini UI/REST endpoints, status check, visualization.
- src/data/inspection/system_instructions.txt: clean legend + reading rules text.

## Notes
- system_instructions combine both text and images for accuracy; cache created with legend.png + reading_instructions.png + schematic.pdf.
- Prompt template in gemini_service.py extracts components/wires/cross_refs per page.
- Total tokens for full schematic ~33k (129 pages × 258). Context window OK.

## Next Steps (if continuing)
- Extend extraction to full batch instead of sample pages.
- Store outputs to disk/DB; add download endpoint.
- Optionally add page selection input in UI.
- Add error handling for API/network timeouts.
