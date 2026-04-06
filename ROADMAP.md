# Procedural Building Generator — Development Roadmap

## Philosophy

Start with one building type (Georgian townhouse), get the full pipeline working end-to-end, then expand horizontally (more types) and vertically (more detail). Each phase produces working, testable output. No phase depends on incomplete work from a prior phase.

---

## Phase 1: Foundation & Single Building Type

**Goal:** Generate a simple Georgian townhouse with rooms, walls, windows, doors, and a roof. Full pipeline working end-to-end.

### 1.1 Project Setup
- [ ] Create `pyproject.toml` with dependencies (shapely, trimesh, networkx, numpy, pyyaml)
- [ ] Create package structure: `src/buildgen/` with all sub-packages
- [ ] Create `__init__.py` interface files for every package
- [ ] Set up pytest with a basic smoke test
- [ ] Verify `pip install -e .` works

### 1.2 Data Models
- [ ] Define `RoomSpec` — room type, min/max area, min/max aspect ratio, required features (window, exterior wall, etc.)
- [ ] Define `AdjacencyRequirement` — which rooms must/should/must-not be adjacent
- [ ] Define `BuildingProgram` — complete specification: list of rooms per floor, adjacency graph, building footprint constraints
- [ ] Define `FloorPlan` — collection of `RoomPolygon` objects with wall segments, door positions, window positions
- [ ] Define `StyleParams` — wall thickness, floor height, window proportions, roof pitch, material references
- [ ] Define `Building3D` — the final 3D output: mesh + metadata

### 1.3 Building Program Generator (Stage 1)
- [ ] Create YAML template format for building types
- [ ] Write Georgian townhouse template:
  - Ground floor: entrance hall, front parlour, rear parlour/dining, kitchen, scullery, WC
  - First floor: master bedroom, dressing room, 2 secondary bedrooms, bathroom
  - Second floor (optional): servants' quarters, nursery, storage
  - Adjacency rules: hall connects to all ground-floor rooms, kitchen adjacent to dining, stairs connect floors
- [ ] Implement `ProgramGenerator` — loads template, applies randomized variation (room count, sizes), outputs `BuildingProgram`
- [ ] Test: generate 100 programs, validate all satisfy constraints

### 1.4 Floor Plan Layout Engine (Stage 2)
- [ ] Implement rectangular footprint generation (width x depth from program constraints)
- [ ] Implement BSP subdivision — recursively split rectangle into rooms matching target areas
- [ ] Implement adjacency optimization — swap/adjust rooms to satisfy adjacency graph using simulated annealing
- [ ] Implement wall segment extraction — derive wall lines from room polygons
- [ ] Implement door placement — doors on shared walls between adjacent rooms per program
- [ ] Implement window placement — windows on exterior walls, spaced by style rhythm, respecting structural bays
- [ ] Implement stairwell reservation — reserve a rectangular region that aligns across all floors
- [ ] Implement multi-floor coherence — stairwells align, exterior walls align, structural walls carry through
- [ ] Test: generate floor plans, export as SVG for visual inspection
- [ ] Test: validate all rooms reachable via doors from entrance

### 1.5 3D Geometry Generator (Stage 3)
- [ ] Implement wall extrusion — 2D wall segments to 3D wall meshes with thickness
- [ ] Implement floor/ceiling slab generation
- [ ] Implement window openings — boolean-subtract window holes from walls, insert window frame geometry
- [ ] Implement door openings — boolean-subtract door holes, insert door frame geometry
- [ ] Implement simple staircase — straight-run stairs between floors
- [ ] Implement roof generation — gable or hip roof from footprint using straight skeleton or simplified algorithm
- [ ] Implement glTF export — full building as `.glb` file with material assignments
- [ ] Test: export buildings, open in Blender/three.js viewer to verify

### 1.6 Style System (Stage 4)
- [ ] Define YAML style format — proportions, materials, roof type, window style, ornament level
- [ ] Write Georgian style definition:
  - Symmetrical facade, sash windows (6-over-6), regular bay spacing
  - Brick exterior, stone quoins, dentil cornice
  - Floor heights: ~3m ground, ~2.8m upper
  - Roof: low-pitch hip or parapet
  - Panelled front door with fanlight
- [ ] Implement `StyleLibrary` — loads style YAML, applies params to geometry generator
- [ ] Test: same floor plan rendered with different wall heights and window sizes

### 1.7 End-to-End Pipeline
- [ ] Implement `Pipeline` class — chains all 4 stages
- [ ] CLI entry point: `python -m buildgen --type townhouse --style georgian --seed N --output file.glb`
- [ ] Generate 10 varied townhouses, visually inspect
- [ ] Write integration test: pipeline runs without error for 50 random seeds

**Phase 1 Deliverable:** A CLI that generates varied Georgian townhouses as glTF files. Each has a plausible floor plan, properly placed windows/doors, stairs between floors, and a roof.

---

## Phase 2: Residential Expansion

**Goal:** Expand to multiple residential building types and a second architectural style.

### 2.1 Additional Residential Types
- [ ] Cottage template — 1-2 rooms down, 1-2 up, simple rectangular plan
- [ ] Manor house template — central hall, wings, service quarters, larger scale
- [ ] Terraced house template — narrow deep plan, shared party walls, rear extension
- [ ] Farmhouse template — linear plan, kitchen as main room, attached utility spaces

### 2.2 Second Style: Medieval English
- [ ] Style definition: timber frame, steep pitched roofs, small casement windows, irregular spacing
- [ ] Thicker walls, lower ceilings, larger fireplaces
- [ ] Asymmetric facades (contrast with Georgian regularity)
- [ ] Jettied upper floors (overhanging) — geometry modification

### 2.3 Layout Engine Improvements
- [ ] L-shaped and T-shaped footprints (for manor houses, farmhouses)
- [ ] Rear extensions and outbuildings
- [ ] Hallway/corridor generation (not just room-to-room doors)
- [ ] Fireplace/chimney placement (structural element that spans floors)

### 2.4 Geometry Improvements
- [ ] Multiple stair types: L-shaped, U-shaped, spiral
- [ ] Chimney geometry (exterior element rising through roof)
- [ ] Dormer windows (penetrate roof surface)
- [ ] Ground-floor bay windows (bump-out geometry)

### 2.5 Validation & Testing
- [ ] Generate 100 buildings per type/style combination
- [ ] Automated checks: no overlapping rooms, all rooms reachable, windows don't overlap doors
- [ ] Visual inspection gallery: render all variants to PNG grid

**Phase 2 Deliverable:** 4 residential types x 2 styles = 8 building categories, each with significant variation.

---

## Phase 3: Commercial & Civic Buildings

**Goal:** Non-residential building types with fundamentally different spatial programs.

### 3.1 Commercial Building Types
- [ ] Shop/corner shop — ground-floor shopfront (large glazing), residential above
- [ ] Tavern/inn — public bar, private rooms, kitchen, lodging above, cellar below
- [ ] Bakery/boulangerie — shop front, baking room (oven), proving room, flour storage
- [ ] Workshop/printer shop — large work floor, storage, small office
- [ ] Warehouse — large open volumes, loading doors, minimal internal subdivision
- [ ] Department store — multi-floor open retail, grand staircase, service areas

### 3.2 Civic Building Types
- [ ] Post office — public counter hall, sorting room, storage, offices
- [ ] Fire station — apparatus bay (tall, wide doors), watch room, dormitory, kitchen, training tower
- [ ] Police station — front desk, offices, interview rooms, cells, parade room
- [ ] Church/chapel — nave, chancel, vestry, tower/bell tower (tall single volume)

### 3.3 New Spatial Features
- [ ] Double-height spaces (apparatus bays, naves, warehouses)
- [ ] Large shopfront windows (different from residential windows)
- [ ] Cellars/basements
- [ ] Service entrances vs public entrances
- [ ] Counter/service areas within rooms
- [ ] Loading bays and wide industrial doors

### 3.4 Third Style: Victorian Commercial
- [ ] Ornate facades, large plate-glass shopfronts, decorative cornices
- [ ] Cast iron columns (allow wider shopfront openings)
- [ ] Higher ornament density than Georgian

### 3.5 Fourth Style: Half-Timbered (Tudor)
- [ ] Exposed timber framing on facade
- [ ] Wattle-and-daub infill panels
- [ ] Irregular, organic proportions

**Phase 3 Deliverable:** 10+ commercial/civic types, 4 styles. Buildings with fundamentally different spatial programs (tall bays, open floors, public counters).

---

## Phase 4: Industrial, Military & Specialized

**Goal:** Buildings with unusual structural systems and very large or very small scales.

### 4.1 Industrial Types
- [ ] Factory — large open floor, clerestory windows, structural frame
- [ ] Smithy/forge — open work area, forge hearth, tool storage, quench tank
- [ ] Mill — multi-story with heavy floor loads, drive shaft routes, grain storage
- [ ] Garage/workshop — vehicle bay doors, pit/lift, parts storage, office

### 4.2 Military & Fortified
- [ ] Castle keep — thick walls, small windows, spiral stairs, great hall, chapel, dungeon
- [ ] Gatehouse — passage through, guard rooms, portcullis, murder holes
- [ ] Barracks — long dormitory rooms, mess hall, armoury, parade ground
- [ ] Watchtower — circular or square, multiple levels, observation platform

### 4.3 Agricultural & Utility
- [ ] Barn — large open volume, hayloft above, wide doors
- [ ] Garden shed — single room, simple structure
- [ ] Stable — stalls, tack room, hayloft
- [ ] Greenhouse — glass structure, different geometry rules

### 4.4 Large Scale
- [ ] Mansion — many rooms, multiple wings, grand entrance hall, ballroom
- [ ] Skyscraper — repeating floor plates, elevator core, curtain wall facade
- [ ] Aircraft hangar — enormous single volume, massive doors

### 4.5 Structural Systems
- [ ] Load-bearing masonry (default for most historic)
- [ ] Timber frame (medieval, Tudor)
- [ ] Steel frame (industrial, modern commercial, skyscrapers)
- [ ] Stone vaulting (castles, churches)
- [ ] Each system has different wall thickness, span limits, and opening sizes

### 4.6 Defensive/Fortification Geometry
- [ ] Thick walls with wall walks
- [ ] Crenellations and arrow loops
- [ ] Round and square towers
- [ ] Curtain walls and courtyards

**Phase 4 Deliverable:** 15+ additional building types covering industrial, military, agricultural, utility, and large-scale buildings. Structural system affects geometry.

---

## Phase 5: Exterior Spaces & Context

**Goal:** Buildings don't exist in isolation. Add courtyards, gardens, outbuildings, and site context.

### 5.1 Courtyards
- [ ] Courtyard generation — enclosed by building wings or walls
- [ ] Cloister-style covered walkways
- [ ] Inn yard (for taverns)
- [ ] Castle bailey / castle courtyard

### 5.2 Gardens & Grounds
- [ ] Formal garden layout — geometric paths, beds, lawn areas
- [ ] Kitchen garden — rectangular beds, greenhouse
- [ ] Walled garden — enclosure walls with gates
- [ ] Churchyard/graveyard

### 5.3 Outbuildings & Compound Layout
- [ ] Outbuilding placement — sheds, stables, workshops relative to main building
- [ ] Walls, fences, gates between buildings
- [ ] Farmyard layout — house + barn + stable + storage arranged around a yard
- [ ] Castle compound — keep + curtain wall + towers + gatehouse + buildings within walls

### 5.4 Site Integration
- [ ] Terrain response — buildings on slopes get stepped foundations or raised entries
- [ ] Street frontage — buildings aligned to a street edge, setback rules
- [ ] Party walls — terraced/attached buildings sharing walls
- [ ] Plot boundaries — building fits within a defined lot

**Phase 5 Deliverable:** Buildings with exterior spaces, outbuildings, and site context. Compound building types (farms, castles) generated as coherent assemblies.

---

## Phase 6: Style Expansion & Historical Depth

**Goal:** Broad coverage of architectural styles across periods and regions.

### 6.1 European Historical Styles
- [ ] Romanesque (11th-12th C) — round arches, thick walls, small windows
- [ ] Gothic (12th-16th C) — pointed arches, flying buttresses, large windows, tracery
- [ ] Renaissance (15th-17th C) — classical orders, symmetry, pediments
- [ ] Baroque (17th-18th C) — curved forms, ornate decoration
- [ ] Georgian (18th C) — already implemented in Phase 1
- [ ] Regency (early 19th C) — stucco, bow windows, iron balconies
- [ ] Victorian (19th C) — ornate, eclectic, polychrome brick
- [ ] Edwardian (early 20th C) — lighter, wider windows
- [ ] Art Deco (1920s-30s) — geometric ornament, stepped forms
- [ ] Modernist (mid 20th C) — flat roofs, glass curtain walls, pilotis
- [ ] Brutalist (1950s-70s) — raw concrete, massive forms

### 6.2 Regional Styles
- [ ] Mediterranean — white walls, terracotta roofs, inner courtyards
- [ ] Northern European timber (Scandinavian, Alpine) — log or stave construction
- [ ] Japanese traditional — post-and-beam, sliding screens, tatami module
- [ ] Chinese traditional — courtyard houses (siheyuan), curved roofs
- [ ] Middle Eastern — courtyard houses, mashrabiya screens, wind towers
- [ ] Colonial American — clapboard, central chimney, saltbox
- [ ] Adobe/Pueblo — thick earth walls, flat roofs, vigas

### 6.3 Style Blending & Evolution
- [ ] Transitional styles — buildings that mix elements from two periods
- [ ] Regional variants — "Gothic" looks different in England, France, Italy, Germany
- [ ] Vernacular vs high-style — same period, different levels of formality

**Phase 6 Deliverable:** 20+ architectural styles spanning 1000 years and multiple continents. Style parameters drive all geometry decisions.

---

## Phase 7: Advanced Generation Methods

**Goal:** Move beyond templates to AI-assisted and evolutionary generation.

### 7.1 Evolutionary Optimization
- [ ] Genetic algorithm for floor plan optimization
- [ ] Fitness functions: natural light, circulation efficiency, structural rationality, style adherence
- [ ] Population of building variants that evolve toward better solutions
- [ ] Interactive evolution — user selects preferred variants

### 7.2 AI-Assisted Program Generation
- [ ] LLM integration for generating room programs for unusual building types
- [ ] "Describe a 16th-century Venetian printing house" -> room list + adjacency
- [ ] Validation layer ensures LLM output meets structural constraints
- [ ] Fallback to templates if LLM output fails validation

### 7.3 Reference Plan Learning
- [ ] Ingest real architectural plans (RPLAN dataset, historical plans)
- [ ] Extract room adjacency patterns and proportions
- [ ] Use learned distributions to improve procedural generation
- [ ] Style transfer — apply proportions from real plans to generated ones

### 7.4 Wave Function Collapse for Detail
- [ ] WFC for interior furniture/fixture layout within rooms
- [ ] WFC for facade ornament pattern generation
- [ ] WFC for garden/landscape detail within plots

### 7.5 Simulation-Based Validation
- [ ] Pathfinding: verify all rooms reachable
- [ ] Lighting simulation: verify habitable rooms get natural light
- [ ] Structural check: verify walls align vertically, loads transfer to ground
- [ ] Functional simulation: agents perform building's function (cook in kitchen, serve in bar) to test layout

**Phase 7 Deliverable:** AI and evolutionary methods augment the template system. Buildings are validated by simulation. The system can generate building types it has never seen a template for.

---

## Phase 8: Scale, Polish & Integration

**Goal:** Production quality. Generate thousands of buildings for world simulation.

### 8.1 Batch Generation
- [ ] Batch CLI: generate N buildings of specified type/style distribution
- [ ] Parallel generation using multiprocessing
- [ ] Output catalog with metadata (type, style, room count, floor area, seed)
- [ ] Deduplication — ensure sufficient variety in large batches

### 8.2 LOD (Level of Detail)
- [ ] LOD0: detailed interior + exterior (close-up)
- [ ] LOD1: exterior only, simplified roof
- [ ] LOD2: extruded footprint block
- [ ] LOD3: bounding box
- [ ] Automatic LOD generation from full model

### 8.3 Material & Texture System
- [ ] PBR material definitions per style (albedo, roughness, normal)
- [ ] Texture atlas generation for efficient rendering
- [ ] Weathering and age variation (new vs. old buildings)
- [ ] Material variety within style (different brick colors, stone types)

### 8.4 World Integration API
- [ ] Python API for requesting buildings by constraint
- [ ] "Give me a medieval tavern that fits on a 10x15m lot" -> Building3D
- [ ] Integration hooks for world simulation (place building on terrain, connect to roads)
- [ ] Serialization for building state (save/load generated buildings)

### 8.5 Documentation & Gallery
- [ ] API documentation
- [ ] Style guide with visual examples of each style
- [ ] Building type catalog with example renders
- [ ] Tutorial: "Adding a new building type" and "Adding a new style"

**Phase 8 Deliverable:** Production-ready system. Batch-generate thousands of buildings. Full API for world simulation integration. Documentation and visual catalog.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Building types | 50+ |
| Architectural styles | 20+ |
| Historical periods covered | 1000+ years |
| Generation speed | < 2 seconds per building |
| Variety | 1000 unique buildings per type with no obvious repeats |
| Structural plausibility | No floating floors, aligned stairs, load paths to ground |
| Functional plausibility | All rooms reachable, habitable rooms have windows |
| Output format | glTF 2.0, optionally USD |

---

## Current Progress

**Phase 1: Foundation & Single Building Type** — COMPLETE
- [x] Create CLAUDE.md and ROADMAP.md
- [x] Project setup (pyproject.toml, package structure, pip install)
- [x] Data models (RoomSpec, BuildingProgram, FloorPlan, StyleParams, Building3D)
- [x] Building program generator (YAML templates, random variation)
- [x] Floor plan layout engine (BSP + grid-based reference layouts)
- [x] 3D geometry generator (walls, floors, roofs, stairs, window/door openings)
- [x] Style system (Georgian style with parameters)
- [x] End-to-end pipeline (CLI + Python API)
- [x] Visualization (floor plan renderer, building sheets, 3D export)

**Phase 1 extras completed:**
- [x] Interior fixture placement (kitchen, bathroom, bedroom, fireplace)
- [x] Architectural floor plan conventions (wall thickness, door swings, window marks, stair arrows)
- [x] Component library (80+ standard elements: doors, windows, walls, fireplaces, furniture)
- [x] Validation system (windows on exterior only, door placement, wall alignment, room sizes)
- [x] Multiple staircase types (straight, L-shape, U-shape, spiral)
- [x] Floor slab openings for stairwells
- [x] Front + rear door placement
- [x] 29 building types researched with detailed rules (94KB YAML)
- [x] Architectural standards from UK/US building codes encoded

**Phase 2: Building Type Expansion** — IN PROGRESS
- [x] Victorian terrace template (grid-based)
- [x] English cottage template (grid-based)
- [x] Medieval tavern template (grid-based)
- [x] Georgian townhouse reference template (from real floor plans)
- [ ] More building types from reference plans
- [ ] Medieval style definition
- [ ] Victorian style definition
- [ ] L-shaped and T-shaped footprints
- [ ] Curved geometry (arches, towers, cupolas)

**Phase 2.5: Engineering & Granular Detail** — IN PROGRESS
- [x] Structural engineering from first principles (loads, spans, foundations)
- [x] Material science database (20 materials with real engineering properties)
- [x] Individual brick-level wall construction (Flemish, English, stretcher bond)
- [x] Cavity wall construction (inner/outer leaves, wall ties, DPC)
- [x] Stone masonry walls (ashlar, rubble, coursed)
- [x] Detailed floor construction (joists, floorboards, ceiling laths, 3-coat plaster, skirting)
- [x] Detailed roof construction (rafters at correct pitch angle, purlins, battens, ridge board)
- [x] Individual slate/tile placement on roof
- [x] Sash window construction (box frame, sashes, glazing bars, glass panes, sash weights)
- [x] Panel door construction (frame, stiles, rails, panels, hinges, fanlight)
- [x] Multiple stair types with treads, risers, stringers, newels, balusters, handrails
- [x] Chimney stacks with fireplaces, flues, mantels, hearths on each floor
- [x] Plumbing system (soil stack, waste pipes, traps, supply pipes, hot water cylinder)
- [x] Heating system (boiler, radiators, flow/return pipes, cisterns)
- [x] Basement/cellar with light wells, air bricks, flagstone floor
- [x] Guttering (cast iron gutters, downpipes, hopper heads, fascia, soffit)
- [x] Interior partition walls (timber stud with lath and plaster)
- [x] Door steps (limestone) at front and rear
- [x] Structural validation (zero failures across 82,000+ elements)
- [x] Interactive 3D viewer (HTML/three.js with 22 toggleable element groups)
- [x] Diagnostic views (6 types: elevations, sections, cutaways, exploded, systems)
- [x] Properly angled rafter meshes (rotated 3D geometry, not axis-aligned boxes)
- [ ] Birdsmouth cuts at rafter/wall-plate junction
- [ ] Roof ventilation (ridge vents, soffit vents)
- [ ] Roof insulation (between rafters or at ceiling level)
- [ ] Roof decking/underlayment
- [ ] Electrical system (consumer unit, ring mains, lighting circuits)
- [ ] More detailed chimney flue construction
- [ ] Dormer window construction
- [ ] Bay window construction
- [ ] Period-correct construction for each building type

**Current Statistics:**
- 82,470 individual building elements per townhouse
- 302.5 tonnes total building weight
- Zero structural failures
- 22 toggleable groups in 3D viewer
- 47 Python source files, ~12,000 lines of code
- 5 reference documents (engineering, historical, architectural standards, roof detail)
- 4 building types with grid templates
