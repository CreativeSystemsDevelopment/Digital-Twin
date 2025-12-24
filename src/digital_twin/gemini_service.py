"""Gemini API service for schematic extraction with step-by-step logging."""
from __future__ import annotations

import time
import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Callable
import json

from google import genai
from google.genai import types

from .config import get_gemini_api_key
from .agent_monitor import get_monitor, AgentStatus


@dataclass
class ExtractionStep:
    """Represents a single step in the extraction process."""
    step_number: int
    name: str
    status: str  # pending, running, completed, failed
    message: str = ""
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    details: dict = field(default_factory=dict)


class StepLogger:
    """Logs extraction steps and can notify callbacks."""
    
    def __init__(self, callback: Optional[Callable[[ExtractionStep], None]] = None):
        self.steps: List[ExtractionStep] = []
        self.callback = callback
        self.step_counter = 0
    
    def log(self, name: str, status: str, message: str = "", **details) -> ExtractionStep:
        self.step_counter += 1
        step = ExtractionStep(
            step_number=self.step_counter,
            name=name,
            status=status,
            message=message,
            details=details
        )
        if status == "running":
            step.started_at = time.time()
        elif status in ("completed", "failed"):
            step.completed_at = time.time()
            # Find matching running step to calculate duration
            for prev in reversed(self.steps):
                if prev.name == name and prev.status == "running":
                    step.started_at = prev.started_at
                    step.duration_ms = (step.completed_at - prev.started_at) * 1000
                    break
        
        self.steps.append(step)
        if self.callback:
            self.callback(step)
        return step
    
    def get_all_steps(self) -> List[dict]:
        return [
            {
                "step": s.step_number,
                "name": s.name,
                "status": s.status,
                "message": s.message,
                "duration_ms": round(s.duration_ms, 2) if s.duration_ms else None,
                "details": s.details
            }
            for s in self.steps
        ]


class GeminiExtractor:
    """Handles Gemini API interactions for schematic extraction."""
    
    def __init__(self, logger: Optional[StepLogger] = None, agent_id: Optional[str] = None):
        self.logger = logger or StepLogger()
        self.client: Optional[genai.Client] = None
        self.cache: Optional[types.CachedContent] = None
        self.uploaded_files: dict = {}
        self.agent_id = agent_id
        self.current_task_id: Optional[str] = None
        
        # Register with monitor if agent_id provided
        if not self.agent_id:
            monitor = get_monitor()
            self.agent_id = monitor.register_agent(
                name=f"GeminiExtractor-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                agent_type="gemini_extractor",
                metadata={"created_at": datetime.now().isoformat()}
            )
    
    def _log(self, name: str, status: str, message: str = "", **details):
        return self.logger.log(name, status, message, **details)
    
    def initialize_client(self) -> bool:
        """Initialize the Gemini client with API key."""
        self._log("Initialize Client", "running", "Loading API key from environment...")
        
        api_key = get_gemini_api_key()
        if not api_key:
            self._log("Initialize Client", "failed", "No GEMINI_API_KEY found in environment")
            return False
        
        try:
            self.client = genai.Client(api_key=api_key)
            self._log("Initialize Client", "completed", 
                     f"Client initialized (key: {api_key[:8]}...)")
            return True
        except Exception as e:
            self._log("Initialize Client", "failed", str(e))
            return False
    
    def upload_file(self, file_path: Path, display_name: str) -> Optional[types.File]:
        """Upload a file to Gemini Files API."""
        self._log("Upload File", "running", f"Uploading {display_name}...", 
                 file_path=str(file_path), size_bytes=file_path.stat().st_size)
        
        try:
            uploaded = self.client.files.upload(
                file=str(file_path),
                config={"display_name": display_name}
            )
            self.uploaded_files[display_name] = uploaded
            self._log("Upload File", "completed", 
                     f"Uploaded: {uploaded.name}",
                     file_name=uploaded.name,
                     uri=uploaded.uri if hasattr(uploaded, 'uri') else None)
            return uploaded
        except Exception as e:
            self._log("Upload File", "failed", str(e))
            return None
    
    def create_cache(self, 
                    model: str,
                    display_name: str,
                    system_instruction: str,
                    files: List[types.File],
                    ttl_seconds: int = 3600) -> Optional[types.CachedContent]:
        """Create a context cache with uploaded files."""
        self._log("Create Cache", "running", 
                 f"Creating cache '{display_name}' with {len(files)} files...",
                 model=model, ttl_seconds=ttl_seconds)
        
        try:
            self.cache = self.client.caches.create(
                model=model,
                config=types.CreateCachedContentConfig(
                    display_name=display_name,
                    system_instruction=system_instruction,
                    contents=files,
                    ttl=f"{ttl_seconds}s",
                )
            )
            self._log("Create Cache", "completed",
                     f"Cache created: {self.cache.name}",
                     cache_name=self.cache.name,
                     expire_time=str(self.cache.expire_time) if hasattr(self.cache, 'expire_time') else None)
            return self.cache
        except Exception as e:
            self._log("Create Cache", "failed", str(e))
            return None
    
    def extract_page(self, 
                    page_number: int,
                    prompt: str,
                    use_cache: bool = True) -> Optional[dict]:
        """Extract data from a specific page using the cached context."""
        self._log("Extract Page", "running", 
                 f"Extracting page {page_number}...",
                 page_number=page_number, use_cache=use_cache)
        
        try:
            config = {}
            if use_cache and self.cache:
                config["cached_content"] = self.cache.name
            
            # Request structured JSON output
            config["response_mime_type"] = "application/json"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro" if not use_cache else self.cache.model,
                contents=prompt,
                config=types.GenerateContentConfig(**config) if config else None
            )
            
            # Parse response
            result = {
                "page": page_number,
                "raw_response": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else None,
                    "response_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else None,
                    "cached_tokens": response.usage_metadata.cached_content_token_count if response.usage_metadata else None,
                }
            }
            
            # Try to parse JSON from response
            try:
                result["parsed"] = json.loads(response.text)
            except json.JSONDecodeError:
                result["parsed"] = None
            
            self._log("Extract Page", "completed",
                     f"Page {page_number} extracted ({result['usage']['response_tokens']} tokens)",
                     **result["usage"])
            return result
            
        except Exception as e:
            self._log("Extract Page", "failed", str(e))
            return None
    
    def run_sample_extraction(self, 
                             schematic_path: Path,
                             legend_path: Path,
                             reading_instructions_path: Path,
                             system_instructions_path: Path,
                             num_pages: int = 2,
                             total_pages: int = 129) -> dict:
        """Run a complete sample extraction workflow with logging."""
        
        monitor = get_monitor()
        start_time = time.time()
        results = {
            "success": False,
            "steps": [],
            "extractions": [],
            "total_duration_ms": 0,
            "agent_id": self.agent_id
        }
        
        # Create a task in the monitor
        try:
            self.current_task_id = monitor.assign_task(
                agent_id=self.agent_id,
                description=f"Extract {num_pages} sample pages from schematic",
                task_type="sample_extraction",
                metadata={
                    "num_pages": num_pages,
                    "total_pages": total_pages,
                    "schematic": str(schematic_path)
                }
            )
            monitor.update_task_status(self.current_task_id, AgentStatus.RUNNING)
            monitor.update_agent_status(self.agent_id, AgentStatus.RUNNING, 
                                       "Starting extraction workflow")
        except Exception:
            pass  # Continue even if monitoring fails
        
        # Step 1: Initialize client
        self._log("Workflow Start", "running", "Starting extraction workflow...")
        
        if not self.initialize_client():
            monitor.update_task_status(self.current_task_id, AgentStatus.FAILED, 
                                      "Failed to initialize Gemini client")
            monitor.update_agent_status(self.agent_id, AgentStatus.FAILED)
            results["steps"] = self.logger.get_all_steps()
            return results
        
        monitor.heartbeat(self.agent_id, self.current_task_id)
        monitor.update_task_progress(self.current_task_id, 0.1)
        
        # Step 2: Upload files
        self._log("Upload Files", "running", "Uploading reference documents...")
        
        legend_file = self.upload_file(legend_path, "legend.png")
        reading_file = self.upload_file(reading_instructions_path, "reading_instructions.png")
        schematic_file = self.upload_file(schematic_path, "schematic.pdf")
        
        if not all([legend_file, reading_file, schematic_file]):
            monitor.update_task_status(self.current_task_id, AgentStatus.FAILED, 
                                      "Failed to upload files")
            monitor.update_agent_status(self.agent_id, AgentStatus.FAILED)
            results["steps"] = self.logger.get_all_steps()
            return results
        
        self._log("Upload Files", "completed", "All files uploaded successfully")
        monitor.heartbeat(self.agent_id, self.current_task_id)
        monitor.update_task_progress(self.current_task_id, 0.3)
        
        # Step 3: Load system instructions
        self._log("Load System Instructions", "running", "Loading system instructions...")
        system_instructions = system_instructions_path.read_text(encoding="utf-8")
        self._log("Load System Instructions", "completed", 
                 f"Loaded {len(system_instructions)} characters")
        
        monitor.heartbeat(self.agent_id, self.current_task_id)
        monitor.update_task_progress(self.current_task_id, 0.4)
        
        # Step 4: Create cache
        cache = self.create_cache(
            model="models/gemini-2.5-flash-001",  # Use specific version for caching
            display_name=f"UBE-1650-Schematic-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system_instruction=system_instructions,
            files=[legend_file, reading_file, schematic_file],
            ttl_seconds=1800  # 30 minutes
        )
        
        if not cache:
            monitor.update_task_status(self.current_task_id, AgentStatus.FAILED, 
                                      "Failed to create cache")
            monitor.update_agent_status(self.agent_id, AgentStatus.FAILED)
            results["steps"] = self.logger.get_all_steps()
            return results
        
        monitor.heartbeat(self.agent_id, self.current_task_id)
        monitor.update_task_progress(self.current_task_id, 0.5)
        
        # Step 5: Random page selection
        self._log("Select Pages", "running", f"Selecting {num_pages} random pages...")
        
        # Skip first 5 pages (TOC, legend, reading instructions)
        available_pages = list(range(6, total_pages + 1))
        selected_pages = random.sample(available_pages, min(num_pages, len(available_pages)))
        
        self._log("Select Pages", "completed", 
                 f"Selected pages: {selected_pages}",
                 selected_pages=selected_pages)
        
        monitor.update_agent_status(self.agent_id, AgentStatus.RUNNING, 
                                   f"Extracting {len(selected_pages)} pages")
        
        # Step 6: Extract each page
        extraction_prompt_template = """
Analyze page {page_num} of the schematic.

Extract all components and connections visible on this page. Return as JSON:

{{
  "page": {page_num},
  "title": "page title if visible",
  "components": [
    {{"id": "component_id", "type": "from_legend", "grid_position": "col-row"}}
  ],
  "wires": [
    {{"wire_number": "XXXX", "from": "component", "to": "component"}}
  ],
  "cross_references": [
    {{"direction": "to/from", "page": N, "line": N}}
  ]
}}
"""
        
        for i, page_num in enumerate(selected_pages):
            prompt = extraction_prompt_template.format(page_num=page_num)
            extraction = self.extract_page(page_num, prompt, use_cache=True)
            if extraction:
                results["extractions"].append(extraction)
            
            # Update progress based on pages extracted
            progress = 0.5 + (0.4 * (i + 1) / len(selected_pages))
            monitor.update_task_progress(
                self.current_task_id, 
                progress,
                pages_completed=[p for p in selected_pages[:i+1]]
            )
            monitor.heartbeat(self.agent_id, self.current_task_id)
        
        # Finalize
        total_duration = (time.time() - start_time) * 1000
        self._log("Workflow Complete", "completed", 
                 f"Extraction complete in {total_duration:.0f}ms",
                 total_pages_extracted=len(results["extractions"]))
        
        # Update monitor with completion
        monitor.update_task_progress(self.current_task_id, 1.0, 
                                    pages_completed=selected_pages)
        monitor.update_task_status(self.current_task_id, AgentStatus.COMPLETED)
        monitor.update_agent_status(self.agent_id, AgentStatus.COMPLETED, 
                                   "Extraction workflow completed")
        
        results["success"] = True
        results["steps"] = self.logger.get_all_steps()
        results["total_duration_ms"] = round(total_duration, 2)
        results["task_id"] = self.current_task_id
        
        return results


def run_test_extraction() -> dict:
    """Run a test extraction with default paths."""
    base_path = Path(__file__).parent.parent / "data"
    
    logger = StepLogger(callback=lambda s: print(f"[{s.status.upper()}] {s.name}: {s.message}"))
    extractor = GeminiExtractor(logger=logger)
    
    return extractor.run_sample_extraction(
        schematic_path=base_path / "raw" / "1650" / "20251212T144026Z_01_SCHEMATIC_DIAGRAM_151-E8810-202-0.pdf",
        legend_path=base_path / "inspection" / "legend.png",
        reading_instructions_path=base_path / "inspection" / "reading_instructions.png",
        system_instructions_path=base_path / "inspection" / "system_instructions.txt",
        num_pages=2
    )
