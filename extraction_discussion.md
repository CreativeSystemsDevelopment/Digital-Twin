# Schematic Data Extraction Strategy Discussion

## Project Vision

**Ultimate Goal**: Create a comprehensive database of ALL plant documentation exposed to troubleshooting and maintenance engineering applications.

**Key Architecture Decision**: The **SCHEMATIC is the master index**. Every component ID in the schematic (SOL1B, CR200, MCB10, etc.) becomes a foreign key that links to:
- Electrical Parts List → detailed specs, part numbers, manufacturers
- General Arrangement → physical location, mounting
- Terminal Box Wiring → field wiring details
- Cable Lists → wire runs, lengths, routing
- Panel Outlines → cabinet locations
- Parameter Lists → servo settings, sensor configs
- Error Lists → fault codes, diagnostics

**Proven Approach**: Gemini 2.5 Pro / 3.0 vision models have been successfully tracing circuits across multiple pages with natural language queries like:
> "Trace the circuit the shot forward solenoid valve is in. Trace each wire to the solenoid to where it terminates/originates, being sure to give wire numbers, terminal box wiring if there are any, any other information about components in the circuit."

**Key Insight**: The vision AI approach WORKS. Now we need to scale it systematically.

---

## Current Assets

### Line 1650 Document Set

| Doc # | Document | Purpose | Links Via |
|-------|----------|---------|-----------|
| 01 | **SCHEMATIC DIAGRAM** (129 pages) | Master circuit reference | Component IDs |
| 02(4) | Terminal Box Wiring (Vacuum System) | Field terminations | Wire numbers, TB refs |
| 02(5) | Electrical Parts Arrangement (DCM) | Physical layout | Component IDs |
| 02(6) | General Arrangement | Machine overview | Component IDs |
| 03 | Panel Outline | Cabinet layouts | Panel refs (PP, etc.) |
| 04 | Electrical Parts List | BOM, specs, part numbers | Component IDs |
| 08 | Error List | Fault codes, diagnostics | Alarm refs |
| 09(1-6) | Parameter/Setting Lists | Inverter, servo, sensor configs | Device refs |

### Extracted Data (So Far)

| Asset | Location | Status |
|-------|----------|--------|
| Schematic PDF | `src/data/raw/1650/` | ✓ Raw |
| Page JSONs | `src/data/processed/1650/page_*.json` | ✓ 129 pages extracted |
| Legend | `src/data/inspection/legend.png/.json` | ✓ Ready |
| Reading Instructions | `src/data/inspection/reading_instructions.png/.json` | ✓ Ready |
| Other PDFs | `src/data/raw/1650/` | Raw only - need processing |

## The Data Model: Schematic as Master Index

```
                    ┌─────────────────────────────────────┐
                    │         SCHEMATIC (Master)          │
                    │  Components: SOL1B, CR200, MCB10... │
                    │  Wires: R101, 3042, 2001...         │
                    │  Cross-refs: Page/Line pointers     │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  PARTS LIST      │    │  TERMINAL BOX    │    │  GENERAL         │
│  - Part numbers  │    │  WIRING          │    │  ARRANGEMENT     │
│  - Manufacturers │    │  - Field wiring  │    │  - Physical loc  │
│  - Specs/ratings │    │  - Terminal IDs  │    │  - Mounting      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
           │                       │                       │
           ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  PANEL OUTLINE   │    │  CABLE LIST      │    │  PARAM SETTINGS  │
│  - Cabinet layout│    │  - Wire runs     │    │  - Servo params  │
│  - Panel refs    │    │  - Lengths       │    │  - Sensor config │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Example: SOL1B (Acc Charge Solenoid)

Query: "Tell me everything about SOL1B"

**From Schematic**: Circuit path, controlling relays, wire numbers, page/line location
**From Parts List**: Manufacturer, part number, voltage rating, coil resistance
**From Terminal Box**: Field wiring terminals, cable entry point
**From General Arrangement**: Physical location on machine
**From Cable List**: Cable run from panel to device

---

## The Scaling Challenge

You've proven Gemini can trace circuits. Now we need to:

1. **Extract systematically** - Process all 129 pages with consistent structure
2. **Store for queryability** - Database schema that supports maintenance app queries
3. **Preserve cross-references** - "TO PAGE 5 LINE 10" must be resolvable
4. **Enable circuit tracing** - Follow a wire from solenoid → through relays → to power source

---

## Key Questions for Database Design

### Q1: What queries will maintenance apps need to run?

Examples that would drive schema design:
- "What controls SOL-215?" → Find all relays/switches in that circuit
- "CR200 faulted - what's affected?" → Find all downstream components
- "Show me the injection sequence" → Timeline of activations
- "Wire 3042 is broken - trace both ends" → Full path tracing

**Your input**: What are the top 5-10 queries your apps will need?

---

### Q2: What's the right extraction unit?

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Per-page** | Extract each page independently | Simple, parallelizable | Cross-page circuits fragmented |
| **Per-circuit** | Follow each circuit across pages | Complete traces | Complex, overlapping |
| **Per-component** | One record per device | Good for inventory | Loses circuit context |
| **Hybrid** | Per-page + unified graph | Best of both | More complex schema |

**Recommendation**: Hybrid - extract per-page first, then build unified graph

---

### Q3: What should Gemini extract per page?

**Option A: Comprehensive dump**
Ask Gemini to extract EVERYTHING on each page:
- All components with IDs, types, ratings
- All wire numbers and paths
- All cross-references
- All text labels

**Option B: Targeted extraction**
Pre-identify components from JSON text, then ask Gemini to:
- Verify component identification
- Trace connections between them
- Identify control logic (what enables what)

**Option C: Circuit-focused queries**
For each page, ask specific questions:
- "List all solenoid valves and their control circuits"
- "List all relays and what activates each one"
- "List all cross-page references"

**Your input**: Which approach matches how you've been prompting?

---

### Q4: How to handle Gemini's natural language output?

Your current approach returns natural language descriptions. For database storage, we need structured data.

**Option A: Two-pass extraction**
1. First pass: Natural language trace (like you're doing now)
2. Second pass: "Convert this to JSON with schema: {component, wire_from, wire_to, ...}"

**Option B: Structured prompt from start**
```
Extract all components and connections from this schematic page.
Return as JSON:
{
  "components": [{"id": "...", "type": "...", "rating": "..."}],
  "connections": [{"from": "...", "to": "...", "wire": "..."}],
  "cross_refs": [{"direction": "to/from", "page": N, "line": N}]
}
```

**Option C: Hybrid natural + structured**
Get natural language explanation PLUS structured data - keeps the reasoning visible for validation

---

## Proposed Database Schema

### Core Entity: COMPONENT (from Schematic)

```
COMPONENT (Master Table - populated from schematic)
├── component_id (SOL1B, CR200, MCB10) ← PRIMARY KEY for all cross-refs
├── type (SOLENOID_VALVE, RELAY, CIRCUIT_BREAKER)
├── subtype (from legend)
├── schematic_page
├── schematic_line
├── grid_position (C-5)
├── name_en
├── name_jp
│
├── [FROM PARTS LIST]
│   ├── manufacturer
│   ├── part_number
│   ├── voltage_rating
│   ├── current_rating
│   └── specifications{}
│
├── [FROM GENERAL ARRANGEMENT]
│   ├── physical_location
│   ├── mounting_detail
│   └── coordinates_on_machine
│
├── [FROM TERMINAL BOX]
│   ├── terminal_box_id
│   ├── terminal_numbers[]
│   └── field_wiring{}
│
├── [FROM PARAM LISTS]
│   └── settings{}

WIRE
├── wire_number (R101, 3042)
├── from_component_id → COMPONENT
├── from_terminal
├── to_component_id → COMPONENT
├── to_terminal
├── schematic_page
├── cable_id (from cable list)
├── cable_length
├── routing_path

CIRCUIT
├── circuit_id
├── name (ACC_CHARGE, SHOT_FORWARD)
├── function_description
├── component_ids[] → COMPONENT
├── sequence_order (for control logic)

ERROR_CODE
├── error_code
├── description
├── related_components[] → COMPONENT
├── troubleshooting_steps
```

---

## Extraction Strategy: Phased Approach

### Phase 1: SCHEMATIC (Master Index) ← WE ARE HERE
**Goal**: Extract all component IDs, wire numbers, connections, cross-references
**Method**: Gemini vision + structured prompts
**Output**: Component table + Wire table + Cross-reference resolution

### Phase 2: PARTS LIST (Doc 04)
**Goal**: Enrich components with specs, part numbers, manufacturers
**Method**: Table extraction (structured PDF)
**Link**: Match on component_id

### Phase 3: TERMINAL BOX WIRING (Doc 02(4))
**Goal**: Field wiring details, terminal assignments
**Method**: Vision extraction (diagram)
**Link**: Match on component_id + wire_number

### Phase 4: GENERAL ARRANGEMENT (Doc 02(6))
**Goal**: Physical locations on machine
**Method**: Vision extraction (layout drawing)
**Link**: Match on component_id

### Phase 5: PANEL OUTLINE (Doc 03)
**Goal**: Cabinet layouts, panel assignments
**Method**: Vision extraction (layout drawing)
**Link**: Match on panel references (PP, etc.)

### Phase 6: PARAMETER LISTS (Docs 09(1-6))
**Goal**: Configuration settings for servos, sensors, inverters
**Method**: Table extraction
**Link**: Match on device references

### Phase 7: ERROR LIST (Doc 08)
**Goal**: Fault codes linked to components
**Method**: Table extraction
**Link**: Match on component_id or circuit references

---

## Prompt Engineering Strategy

Based on your successful queries, a good extraction prompt might be:

```
You are analyzing page {N} of an electrical schematic for a UBE die casting machine.

Reference: The legend (attached) shows symbol definitions.
Reference: Reading instructions (attached) show how to interpret the diagram.

For this page, extract:

1. COMPONENTS - List every component with:
   - ID (e.g., MCB10, CR200)
   - Type (from legend)
   - Rating/specs if shown
   - Grid position (column letter, row number)

2. CONNECTIONS - For each wire/conductor:
   - Wire number
   - From component and terminal
   - To component and terminal

3. CROSS-REFERENCES - Any references to other pages:
   - Direction (to/from)
   - Target page and line number
   - Wire number

4. CIRCUIT DESCRIPTION - Brief description of what this page controls

Return as structured JSON.
```

---

## Questions to Resolve Together

1. **Schematic extraction format**: 
   - Full page dump vs. circuit-focused queries?
   - Natural language + JSON hybrid?

2. **Gemini workflow details**:
   - Web interface or API?
   - Batch size you've been using?
   - Any pages that gave trouble?

3. **Cross-page circuit assembly**:
   - How should we store a circuit that spans pages 7, 12, and 45?
   - Unified graph vs. page-linked records?

4. **Supporting doc priority**:
   - After schematic, which doc next? (Parts List is probably most valuable)

5. **Validation criteria**:
   - What does "100% accuracy" mean for your apps?
   - Acceptable error rate?

6. **Database technology**:
   - Relational (PostgreSQL)?
   - Graph (Neo4j)?
   - Document (MongoDB)?
   - All of the above with different views?

---

## Legend Reference (from page 3)

| Mark | Type | English | Japanese |
|------|------|---------|----------|
| MCB | Circuit Breaker | Molded Case Circuit Breaker | サーキットブレーカ |
| ELB | Circuit Breaker | Earth Leakage Breaker | 漏電ブレーカ |
| MC | Contactor | Magnetic Contactor | 電磁開閉器 |
| CR | Relay | Auxiliary Relay | 補助リレー |
| TR | Timer | Timer Relay | タイマー |
| TH | Protection | Thermal Overload Relay | サーマルリレー |
| SOL | Valve | Solenoid Valve | ソレノイドバルブ |
| LS | Switch | Limit Switch | リミットスイッチ |
| PS | Switch | Pressure Switch | 圧力スイッチ |
| PL | Indicator | Pilot Lamp | 表示灯 |
| PB | Switch | Push Button | 押釦スイッチ |
| F | Protection | Fuse | ヒューズ |
| T | Power | Transformer | トランス |
| M | Motor | Induction Motor | 誘動電動機 |
| SS | Switch | Selector Switch | セレクトスイッチ |
| CS | Switch | Control Switch | コントロールスイッチ |
| FL | Switch | Flow Switch | フロースイッチ |
| SP | Switch | Plug Switch | プラグスイッチ |
| KS | Switch | Key Switch | キースイッチ |
| ESPB | Safety | Emergency Stop Push Button | 非常停止押釦 |

---

## Next Steps

### Immediate (Phase 1 - Schematic)
1. **Finalize extraction prompt** for Gemini
2. **Generate all page images** at optimal resolution
3. **Build extraction pipeline** (API or semi-automated)
4. **Store structured results** per page
5. **Assemble cross-page graph**
6. **Validate sample pages**

### Short-term (Phase 2-3)
7. **Process Parts List** → enrich component records
8. **Process Terminal Box Wiring** → add field wiring data

### Medium-term (Phase 4-7)
9. **Process remaining docs** → complete data model
10. **Build query API** for maintenance apps

---

## Open Discussion Points

- What's your current Gemini prompt structure?
- Any circuits you've already traced that we can use as validation?
- Timeline expectations?
- How many machines/lines will eventually be in the database?

---

## Gemini API Research: Key Capabilities for This Project

### Context Caching (CRITICAL for our use case)

**What it does**: Upload documents once, cache them, and query multiple times at reduced cost.

**Two types**:
1. **Implicit caching** (Gemini 2.5+): Automatic - if you send similar prefixes repeatedly, Google passes on savings automatically
2. **Explicit caching**: You control it - upload files, set TTL (time-to-live), reference cached content in subsequent queries

**Perfect for our use case**:
- Cache the entire 129-page schematic + legend + reading instructions
- Query it repeatedly ("trace SOL1B circuit", "trace CR200 circuit", etc.)
- Pay ~4x less per query after initial cache

**Code pattern**:
```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload schematic PDF
schematic = client.files.upload(file='schematic.pdf')

# Create cache with legend + reading instructions as system context
cache = client.caches.create(
    model='models/gemini-2.5-pro-001',
    config=types.CreateCachedContentConfig(
        display_name='UBE 1650 Schematic',
        system_instruction='''You are an expert electrical schematic analyzer 
        for UBE die casting machines. Use the legend and reading instructions 
        to interpret the schematic diagrams.''',
        contents=[legend_file, reading_instructions_file, schematic_file],
        ttl="3600s",  # 1 hour cache
    )
)

# Now query multiple times at reduced cost
response = client.models.generate_content(
    model='models/gemini-2.5-pro-001',
    contents='Trace the circuit for SOL1B. Return as JSON with components, wires, and cross-page references.',
    config=types.GenerateContentConfig(cached_content=cache.name)
)
```

**Cache limits**:
- Minimum tokens: 1,024 (Flash) / 4,096 (Pro)
- TTL: Configurable, billed by duration
- Files persist 48 hours via Files API

---

### Structured Outputs (JSON Schema Enforcement)

**What it does**: Guarantee the model returns valid JSON matching your schema.

**For our circuit extraction**:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Component(BaseModel):
    id: str = Field(description="Component ID (e.g., SOL1B, CR200)")
    type: str = Field(description="Component type from legend")
    page: int
    line: int
    grid_position: Optional[str]

class Wire(BaseModel):
    wire_number: str
    from_component: str
    from_terminal: Optional[str]
    to_component: str
    to_terminal: Optional[str]

class CircuitTrace(BaseModel):
    target_component: str
    description: str
    components: List[Component]
    wires: List[Wire]
    cross_page_refs: List[dict]

# Request with guaranteed JSON structure
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Trace the circuit for SOL1B from power source to solenoid",
    config={
        "response_mime_type": "application/json",
        "response_json_schema": CircuitTrace.model_json_schema(),
    },
)
```

---

### Document Processing Capabilities

**Native PDF vision** (not just text extraction):
- Understands diagrams, charts, tables, layouts
- Up to 1000 pages per document
- Each page = 258 tokens
- Can process multiple PDFs in single request

**For our 129-page schematic**:
- ~33,000 tokens for the whole document (129 × 258)
- Well within 1M token context window
- Can include legend + reading instructions + schematic in single context

---

### Long Context (1M+ tokens)

**Gemini 2.5 Pro context window**: 1,048,576 tokens

**What this means for us**:
- Entire schematic (129 pages × 258 tokens) = ~33K tokens
- All supporting docs can fit in single context
- No need for RAG or chunking strategies
- Model can trace circuits across all pages natively

**Best practice**: Put the query at the END of the prompt (after all document context)

---

### Object Detection & Bounding Boxes (Gemini 2.0+)

**What it does**: Returns [ymin, xmin, ymax, xmax] coordinates for detected objects

**Could be useful for**:
- Locating specific symbols on schematic pages
- Extracting component positions for spatial mapping
- Building visual overlays for maintenance apps

---

## Recommended Extraction Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SETUP PHASE (Once)                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Upload all docs to Gemini Files API                      │
│    - Schematic PDF (129 pages)                              │
│    - Legend PNG                                             │
│    - Reading instructions PNG                               │
│                                                             │
│ 2. Create cached context with system instructions           │
│    - TTL: 1-2 hours (or longer for batch processing)        │
│    - Include interpretation rules from legend               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 EXTRACTION PHASE (Per-page)                 │
├─────────────────────────────────────────────────────────────┤
│ For each schematic page (6-129):                            │
│                                                             │
│ Query: "For page {N}, extract all components and            │
│         connections. Return as JSON with schema:            │
│         {components: [...], wires: [...], cross_refs: [...]}│
│                                                             │
│ → Store structured JSON per page                            │
│ → Accumulate into master component list                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               GRAPH ASSEMBLY PHASE (Automated)              │
├─────────────────────────────────────────────────────────────┤
│ 1. Merge all page extractions                               │
│ 2. Resolve cross-page references                            │
│ 3. Build component → wire → component graph                 │
│ 4. Validate consistency (no orphan references)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│             ENRICHMENT PHASE (From other docs)              │
├─────────────────────────────────────────────────────────────┤
│ For each component in master list:                          │
│ - Query Parts List for specs                                │
│ - Query Terminal Box docs for field wiring                  │
│ - Query General Arrangement for physical location           │
│ - Query Parameter Lists for settings                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Cost Estimate (Gemini 2.5 Pro)

| Phase | Tokens | Cost (approx) |
|-------|--------|---------------|
| Upload schematic (129 pages) | ~33K input | ~$0.04 |
| Cache storage (1 hour) | 33K × 1hr | ~$0.01 |
| Per-page extraction (124 queries) | ~8K output total | ~$0.06 |
| **Total schematic extraction** | | **~$0.15** |

With context caching, repeated queries against the same schematic are ~4x cheaper.

---

## Next Action Items

1. **Set up Gemini API access** - get API key, install google-genai SDK
2. **Create extraction schema** - Pydantic models for components, wires, circuits
3. **Test on 3-5 pages** - validate extraction quality
4. **Build extraction pipeline** - batch process all pages
5. **Assemble graph** - resolve cross-references
6. **Validate** - spot-check against your known circuit traces
