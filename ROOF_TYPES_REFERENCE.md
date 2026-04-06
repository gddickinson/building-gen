# Roof Types Reference: Building Type, Style and Period Mapping

Comprehensive reference for selecting the correct roof type based on building type,
architectural style, and historical period. Intended for procedural building generation.

See also: `ROOF_CONSTRUCTION_DETAIL.md` for cut timber geometry and jointing details.

---

## 1. ROOF TYPE CATALOGUE

### 1.1 Gable Roof

**Description:** Two sloping planes meeting at a central ridge, with vertical triangular
walls (gables) at each end. The most common and simplest pitched roof form.

**Pitch angle range:** 25-45 degrees typical; 30-35 degrees is the residential default.
Tudor/medieval gables can be 45-60 degrees. Modern low-pitch gables can be 20-25 degrees.

**Key structural elements:**
- Common rafters (47x150mm at 400-600mm centres)
- Ridge board (25x175mm) at apex -- non-structural nailing board
- Ceiling joists / tie beams spanning wall-to-wall
- Purlins at mid-span for wider buildings (47x175mm)
- Wall plates on top of walls (100x50mm)
- Collar ties at upper third for additional rigidity
- Gable walls carry no roof thrust (rafters bear on side walls)

**Construction method:**
Pairs of common rafters are cut with birdsmouth joints to sit on wall plates,
and meet at the ridge board. Rafters are spaced at 400mm or 600mm centres.
For spans over ~3.4m, a purlin at mid-rafter supported by struts from internal
walls halves the effective span. Ceiling joists tie the rafter feet together,
preventing spread. No hip or valley rafters needed -- simplest framing.

**Building types:** Residential (houses, cottages, barns), religious (simple churches,
chapels), agricultural, light industrial, schools.

**Historical periods:**
- Medieval (steep pitch 45-60 deg, often with cruck frames)
- Tudor (steep pitch 45-60 deg, half-timbered gable ends, decorative bargeboards)
- Georgian (used on provincial/rural houses, less common in London townhouses)
- Victorian (cross-gables very common, decorated bargeboards, 35-45 deg pitch)
- Edwardian (front-facing gable with half-timbered infill)
- Modern (30-35 deg standard, trussed rafters)

**Advantages:**
- Simplest and cheapest to build
- Good attic ventilation through gable vents
- Easy to add dormers
- Good water and snow shedding
- Maximum attic space

**Disadvantages:**
- Gable walls vulnerable to wind (no bracing from roof on that face)
- Less wind-resistant than hip roofs
- Aesthetically plain without decoration

---

### 1.2 Hip Roof

**Description:** Four sloping planes -- two trapezoids on the long sides and two
triangles on the short sides -- all meeting at a central ridge. No vertical gable walls
are exposed. The ridge is shorter than the building length.

**Pitch angle range:** 25-35 degrees typical for Georgian; 30-40 degrees general.
All four slopes typically at the same pitch.

**Key structural elements:**
- Common rafters on all four sides
- Hip rafters (47x200mm C24) -- run diagonally from each corner to the ridge ends
- Jack rafters -- shortened common rafters running from wall plate to hip rafter
- Ridge board (shorter than building length)
- Ceiling joists / tie beams
- Purlins as needed
- Wall plates on all four walls

**Construction method:**
The hip rafter runs at 45 degrees in plan from each corner of the building up to
the end of the ridge. It has a shallower actual pitch than common rafters (for a
35-degree common pitch, the hip is approximately 27 degrees). Jack rafters are
progressively shorter, nailed to the hip rafter with compound angle cuts. The
ridge board runs only between the two hip rafter connections, making it shorter
than the building length by the building width.

**Building types:** Residential (townhouses, detached houses), civic buildings,
institutional (hospitals, schools), some churches.

**Historical periods:**
- Georgian (1714-1830) -- THE defining Georgian roof, especially for townhouses
- Regency (1811-1820) -- continuation of Georgian hip
- Colonial American (hip common on grander houses)
- Modern -- still widely used

**Advantages:**
- Excellent wind resistance (all faces sloped, no flat gable wall)
- Self-bracing structure (four-way triangulation)
- Consistent eave line on all sides -- suits classical/symmetrical facades
- Concealed behind parapet in Georgian London townhouses

**Disadvantages:**
- More complex framing than gable (hip and jack rafters need compound cuts)
- Reduced attic space (hipped ends eat into volume)
- More expensive in materials and labour
- Shorter ridge means less ventilation area

---

### 1.3 Half-Hip / Jerkinhead / Clipped Gable

**Description:** A gable roof where the top portion of each gable is "clipped" back
to a small hip. The gable wall rises most of the way up but stops short; a small
triangular hip slope fills the top. Alternatively described as: a hip roof where
the hip extends only partway down.

**Pitch angle range:** 30-45 degrees (same as gable, with hip section matching pitch).

**Key structural elements:**
- Common rafters as for gable
- Short hip rafters at each end (from gable wall top to ridge end)
- Short jack rafters filling the clipped triangle
- Ridge board extends nearly to gable wall but stops short
- Gable wall built to ~2/3 to 3/4 of full height

**Construction method:**
Frame as a gable roof but stop the gable wall short of the ridge. Install short
hip rafters from the top of the truncated gable wall to the ridge end. Fill with
jack rafters. The result is mostly gable with a small hip at the apex.

**Building types:** Residential, some civic buildings.

**Historical periods:**
- Medieval / Tudor (common in vernacular English architecture)
- Arts & Crafts (late Victorian / Edwardian revival)
- 1920s-1950s suburban houses
- Some Scandinavian and Central European traditions

**Advantages:**
- Better wind resistance than pure gable (no sharp apex to catch wind)
- Retains most of the attic space of a gable
- Distinctive appearance, avoids plainness of simple gable

**Disadvantages:**
- Slightly more complex than pure gable
- Less common, may look unfamiliar

---

### 1.4 Mansard Roof

**Description:** A four-sided double-pitched roof. Each face has two slopes: a very
steep lower slope (nearly vertical, 70-80 degrees) and a shallow upper slope
(~30 degrees). Named after Francois Mansart (17th century). Dormer windows are
typically set into the steep lower slope.

**Pitch angle range:**
- Lower slope: 70-80 degrees (classified as wall cladding above 75 degrees in BS 5534)
- Upper slope: 25-35 degrees

**Key structural elements:**
- Curb beam -- heavy horizontal timber at the junction between lower and upper slopes
- Lower slope rafters (steep, acting almost as wall studs)
- Upper slope rafters (conventional pitch)
- Ridge board or flat top (some mansards have a flat deck at the top)
- Dormer window frames set into lower slope
- Strong floor structure at curb level (this is a habitable storey)
- Tie beams / floor joists at eaves level

**Construction method:**
The lower steep slope is framed like a stud wall with closely spaced rafters/studs
from the eaves up to the curb. The curb is a heavy timber or steel beam at the
break point. From the curb, conventional upper rafters rise to a ridge or flat deck.
The space within the lower slope is a full usable storey (garret/attic rooms).
Dormer windows are framed into the steep face.

**Building types:** Residential (townhouses, apartments), commercial (hotels, shops
with upper-floor accommodation), civic.

**Historical periods:**
- 17th century French origin
- Georgian and Regency (some grand townhouses, especially London)
- Second Empire style (1850s-1880s, very popular in Paris, also North America)
- Victorian (revival)
- Modern (loft conversions often create pseudo-mansard)

**Advantages:**
- Maximises habitable space under the roof (full extra storey)
- In Paris, historically allowed extra floors without counting as full storeys (tax avoidance)
- Elegant appearance
- Dormers provide light and ventilation

**Disadvantages:**
- Complex and expensive to build
- Steep lower slope requires special cladding (slate, zinc, tiles hung vertically)
- Higher maintenance (many junctions, dormers, valleys)
- Not suitable for very wide buildings without intermediate support

---

### 1.5 Gambrel Roof

**Description:** A gable roof with two pitches on each side: steep lower slope and
shallower upper slope. Like a mansard but with gable ends instead of hipped ends.
Strongly associated with barns and Dutch Colonial architecture.

**Pitch angle range:**
- Lower slope: 50-60 degrees (typically ~14/12 pitch, or ~49 degrees)
- Upper slope: 20-30 degrees (typically ~7/12 pitch, or ~30 degrees)
- Rule of thumb: upper pitch should be at least half the lower pitch

**Key structural elements:**
- Lower rafters (steep section, from wall plate to curb)
- Upper rafters (from curb to ridge)
- Curb / purlin plate at the break point
- Ridge board at apex
- Gable wall framing at each end (full height to ridge)
- Collar ties or cross-ties at curb level
- Knee braces at the curb junction

**Construction method:**
Often built as a truss combining both pitches. The curb point can be a heavy
purlin supported by posts from the floor below. Lower rafters are steep; upper
rafters are shallow. Gable end walls are framed to follow the double-pitch profile.
For barns, the gambrel maximises hay loft volume.

**Building types:** Agricultural (barns -- the classic "barn roof"), residential
(Dutch Colonial houses), storage buildings.

**Historical periods:**
- 17th-18th century Dutch Colonial (North America)
- 18th-19th century agricultural buildings
- Traditional barns (ongoing)
- Some modern houses referencing barn aesthetic

**Advantages:**
- Maximum interior volume for a given footprint
- Lower wall height needed (saves on wall material)
- Distinctive, attractive silhouette
- Sheds water well on steep lower section

**Disadvantages:**
- Curb junction is a weathering weak point
- Not highly wind-resistant (flat upper section and broad gable)
- More complex framing than simple gable
- Less suitable for heavy snow loads on upper section

---

### 1.6 Flat Roof

**Description:** A roof with minimal pitch (0.5-5 degrees), appearing horizontal.
Used extensively on modern commercial, industrial, and some residential buildings.
Always has some fall for drainage.

**Pitch angle range:** 0.5-5 degrees (1:40 to ~1:11 fall). Minimum 1:80 fall to
internal outlets; 1:40 fall recommended.

**Key structural elements:**
- Flat roof joists (timber, steel, or concrete)
- Firring strips to create falls (tapered timber strips on top of level joists)
- Decking (plywood, OSB, or concrete)
- Waterproof membrane (felt, EPDM, GRP, single-ply)
- Parapet walls with copings
- Internal drainage outlets or scuppers through parapets
- Upstands at abutments

**Construction method:**
Joists span between walls, either level with firring strips on top to create falls,
or set at a slight slope. Decking is fixed to joists, then waterproof membrane
applied. Parapets are built up from the walls, with scuppers or internal drains.
For larger spans: steel beams, concrete slabs, or composite deck.

**Building types:** Commercial (offices, shops), industrial (factories, warehouses),
residential (modern houses, extensions), civic (brutalist era).

**Historical periods:**
- Ancient (Middle Eastern flat roofs for hot climates)
- Georgian (hidden behind parapets on London townhouses -- actually shallow pitch)
- Modernist (1920s onwards, International Style)
- Brutalist (1950s-1970s)
- Contemporary (green roofs, roof terraces)

**Advantages:**
- Maximises internal volume (no wasted roof space)
- Can be used as terrace, green roof, or plant room
- Easy to install services (HVAC, solar panels)
- Simple, low-cost structure
- Modern aesthetic

**Disadvantages:**
- Drainage problems if falls are inadequate (ponding)
- Shorter waterproof membrane lifespan than pitched coverings
- Requires regular maintenance and inspection
- Poor insulation performance historically (though modern solutions exist)
- Not suitable for heavy snow regions without engineering

---

### 1.7 Lean-To / Mono-Pitch / Skillion

**Description:** A single sloping plane, higher on one side than the other. One edge
typically abuts an existing higher wall. The simplest possible pitched roof.

**Pitch angle range:** 5-25 degrees typical. Minimum depends on covering material:
- Metal sheets: 4 degrees minimum
- Tiles: 15-20 degrees minimum
- Slate: 20-25 degrees minimum

**Key structural elements:**
- Rafters spanning from lower wall plate to upper wall plate (or ledger board)
- Ledger board (bolted to existing wall for extensions)
- Wall plates on lower wall
- Purlins for wider spans
- No ridge board needed

**Construction method:**
Rafters run from the lower wall plate up to a ledger board bolted to the higher
wall or to a higher wall plate on a taller wall. For extensions, the ledger is
lag-bolted into the masonry of the existing building. Simpler than any other
pitched roof as there is only one slope and no ridge, hip, or valley complexity.

**Building types:** Extensions, lean-to conservatories, outbuildings, porches,
garages, sheds, verandahs, some modern houses.

**Historical periods:**
- All periods (vernacular addition/extension form)
- Medieval (simple lean-to shelters, pentice roofs)
- Industrial (factory roofs, saw-tooth with clerestory glazing)
- Modern (skillion roofs on contemporary houses)

**Advantages:**
- Simplest and cheapest roof to build
- Good for extensions against existing walls
- Allows clerestory windows at the high wall
- Effective drainage (single direction)

**Disadvantages:**
- Limited span (no triangulation for rigidity)
- Aesthetically basic
- Height differential between walls
- Not self-supporting (needs existing wall or taller wall)

---

### 1.8 Butterfly Roof (Inverted / V-Shaped)

**Description:** Two roof planes sloping inward to meet at a central valley, forming
a V-shape. The opposite of a gable -- walls are highest at the edges, lowest in
the middle. Popularised by mid-century modern architects, especially William Krisel
in 1950s California.

**Pitch angle range:** 10-25 degrees (shallow pitches typical).

**Key structural elements:**
- Rafters sloping inward from high perimeter walls to central valley beam
- Central valley beam (heavy timber or steel -- critical structural element)
- Valley gutter / channel (must handle all water from both slopes)
- Perimeter wall framing (taller than conventional)
- Strong posts/columns supporting valley beam

**Construction method:**
The valley beam is the primary structural element, spanning the building length
at the lowest point. Rafters slope down from the high perimeter walls to this beam.
The valley must incorporate a large gutter or drainage channel, as ALL rainwater
is directed to the centre. Typically steel or glulam for the valley beam.

**Building types:** Residential (modern/contemporary houses), some commercial
(mid-century modern commercial buildings).

**Historical periods:**
- Mid-century modern (1950s-1960s, the classic period)
- Contemporary / avant-garde (2000s onwards revival)

**Advantages:**
- Dramatic modern aesthetic
- High perimeter walls allow large windows
- Rainwater collection at central valley
- Good for solar panel placement (outward-facing slopes)

**Disadvantages:**
- Drainage is critical -- central valley must never block or overflow
- No attic space
- Structural complexity (central beam carries entire roof load)
- Snow accumulation in valley is dangerous
- Not suitable for wet/snowy climates without robust drainage engineering
- Expensive to build and maintain

---

### 1.9 Pavilion / Pyramid Roof

**Description:** Four equal triangular slopes meeting at a single apex point (no
ridge). Used on square or regular polygonal plan buildings. A special case of
the hip roof where the building is square and the ridge reduces to zero length.

**Pitch angle range:** 25-45 degrees.

**Key structural elements:**
- Four hip rafters meeting at the apex (no ridge board)
- Jack rafters on all four sides
- Wall plates on all four walls
- Central post or structural connection at apex
- Ceiling joists / ties

**Construction method:**
Four hip rafters rise from the four corners to meet at a central point. All
intermediate rafters are jack rafters diminishing in length toward each corner.
There is no ridge board; instead, the four hips meet at a single point, often
with a metal connector plate or a short post. For larger spans, a king post
from the apex down to a tie beam provides support.

**Building types:** Pavilions, gazebos, bandstands, small square towers, entrance
porches, garden buildings, some church towers.

**Historical periods:**
- All periods (used wherever square plan buildings occur)
- Classical (temple-inspired small structures)
- Georgian (small ancillary buildings, garden temples)
- Modern (entrance canopies, small buildings)

**Advantages:**
- Excellent wind resistance (symmetrical, no flat faces)
- Elegant on square plans
- Self-bracing

**Disadvantages:**
- Only works on square or regular polygon plans
- Complex apex junction
- Limited attic space
- Cannot be extended without becoming a hip roof

---

### 1.10 Cross-Gable / Cross-Hip

**Description:** Two or more gable (or hip) roofs intersecting at right angles,
forming L-shaped, T-shaped, or more complex plan buildings. The intersection
creates valleys where the two roof planes meet.

**Pitch angle range:** Same as base roof type (25-45 degrees). Both intersecting
roofs should ideally have the same pitch for clean valley lines.

**Key structural elements:**
- All elements of the base roof type (gable or hip)
- Valley rafters where roofs intersect (similar to hip rafters but in a concave angle)
- Valley jack rafters
- Valley boards / lead-lined valley gutters
- Headers and trimmers where rafters are interrupted

**Construction method:**
Each wing of the building has its own roof structure. Where two roofs intersect,
a valley rafter runs from the junction point at the eaves up to the ridge (or
to a point on the other roof's slope). Valley jack rafters fill between the
valley rafter and the ridge of the subsidiary roof. Valley junctions require
careful flashing/lead work to prevent leaks.

**Building types:** Larger residential (L-plan, T-plan houses), churches (nave +
transepts = cross plan), institutional, Victorian villas.

**Historical periods:**
- Medieval (church cruciform plans)
- Tudor (complex plan manor houses)
- Victorian (very common -- cross-gable villas, bay windows creating sub-roofs)
- Edwardian (L-plan houses)
- Modern (any complex plan building)

**Advantages:**
- Allows complex floor plans with good roof coverage
- Creates architectural interest and varied roofline
- Each wing can have different ridge heights for hierarchy

**Disadvantages:**
- Valleys are leak-prone junctions requiring careful detailing
- More complex framing
- Higher cost
- Valley gutters need regular maintenance

---

### 1.11 Dutch Gable (Gablet)

**Description:** A hip roof with a small vertical gable (gablet) at the top of the
hip end. The hip rises from the eaves but stops partway up; a small triangular
gable wall fills the space between the top of the hip and the ridge. The inverse
of a jerkinhead: hip below, gable above (jerkinhead = gable below, hip above).

**Pitch angle range:** 30-45 degrees.

**Key structural elements:**
- Hip rafters (truncated, stopping at the gablet)
- Jack rafters below the gablet
- Small gable wall framing above the hip termination
- Common rafters in the gablet section
- Ridge board extending to the gable wall

**Construction method:**
Frame as a hip roof but terminate the hip partway up. Build a small gable wall
from the top of the hip to the ridge. The gablet can contain a window or vent.
The ridge board extends to the small gable wall instead of stopping at the hip
rafter junction.

**Building types:** Residential, some commercial.

**Historical periods:**
- Dutch / Flemish origin (16th-17th century)
- Cape Dutch (South African colonial)
- Arts & Crafts (late 19th / early 20th century)
- Queen Anne style Victorian
- Some modern suburban houses

**Advantages:**
- Combines wind resistance of hip with ventilation of gable
- Gablet can house a vent or decorative window
- Distinctive and attractive appearance
- Better attic ventilation than pure hip

**Disadvantages:**
- More complex junction between hip and gable
- Additional weathering risk at the hip-to-gable transition
- Slightly more expensive than either pure hip or pure gable

---

### 1.12 Crown Roof

**Description:** A roof with sloping sides rising to a flat top (like a truncated
pyramid or a frustum). Combines elements of a hip roof with a flat deck.
Sometimes called a "deck roof" or "platform roof."

**Pitch angle range:** Sides: 30-60 degrees. Flat top: 0.5-2 degrees for drainage.

**Key structural elements:**
- Sloping rafters from eaves to the edge of the flat deck
- Flat deck joists spanning the top opening
- Parapet or curb at the transition from slope to flat
- Waterproof membrane on the flat section
- Drainage to the flat deck (internal outlets)
- Similar to mansard without the double pitch

**Construction method:**
Frame the sloping sides as for a hip roof, but instead of rising to a ridge or
apex, the rafters terminate at a horizontal curb/beam defining the flat deck.
The flat deck is then framed with joists and decked as a flat roof. Drainage
is critical for the flat section.

**Building types:** Residential (some Georgian, some modern), commercial,
civic buildings.

**Historical periods:**
- Georgian (some larger houses)
- Italianate style (mid-Victorian)
- Modern (contemporary houses)

**Advantages:**
- Flat top can be used as a roof terrace
- From street level, the building appears to have a flat roof (classically proportioned)
- Sloping sides shed water away from the flat deck
- Good for installing HVAC or solar equipment on flat section

**Disadvantages:**
- Flat deck still has all flat roof drainage issues
- Complex junction between slope and flat
- Expensive compared to simple hip or gable

---

### 1.13 Barrel Vault

**Description:** A continuous curved/arched roof forming a semi-cylindrical shape.
The cross-section is an arc (semicircle, segmental arc, or pointed arc). Used
for churches (naves), industrial buildings, and some modern architecture.

**Pitch angle range:** Not expressed as a simple pitch. The rise-to-span ratio
typically ranges from 1:4 (shallow segmental) to 1:2 (full semicircle).

**Key structural elements:**
- Curved ribs / arched rafters (timber, steel, or laminated)
- Purlins running longitudinally between ribs
- Tie rods or tie beams at the base to resist outward thrust
- Buttresses or thick walls to absorb lateral thrust
- Curved decking or sheet cladding

**Construction method:**
Arched ribs are erected at regular intervals, spanning from wall to wall. These
can be solid timber arches (laminated/glulam), steel trusses bent to a curve, or
built-up from segments. Longitudinal purlins connect the ribs. The curved surface
is clad with flexible sheet materials (lead, copper, zinc) or small overlapping
units (tiles, slates on curved battens). Lateral thrust is the critical structural
challenge -- either absorbed by massive walls/buttresses or resisted by tie rods
at the springing points.

**Building types:** Churches (Romanesque naves), cathedrals, train stations,
industrial buildings (factories, warehouses), aircraft hangars, Nissen/Quonset huts.

**Historical periods:**
- Roman (concrete barrel vaults)
- Romanesque / Norman (11th-12th century stone vaults)
- Gothic (pointed barrel vaults, though groin vaults more common)
- Industrial Revolution (iron/steel framed, railway stations)
- 20th century (Nissen huts, industrial sheds, glulam arches)

**Advantages:**
- Can span very wide spaces without intermediate columns
- Structurally efficient in compression
- Dramatic interior volume
- Good acoustics for churches/concert halls

**Disadvantages:**
- Significant lateral thrust must be resolved
- Curved construction is more expensive than straight
- Difficult to add windows (requires dormers or clerestory)
- Limited to rectangular plans (curved in one direction only)

---

### 1.14 Dome

**Description:** A hemispherical or semi-elliptical roof over a circular or polygonal
plan. The ultimate expression of vaulted construction. Can be a full hemisphere,
a shallow saucer dome, a pointed dome, or an onion dome.

**Pitch angle range:** Not applicable as a simple pitch. Profile defined by
curvature. Rise-to-span ratio from 1:5 (saucer) to 1:1 (hemisphere) to >1:1 (onion).

**Key structural elements:**
- Meridional ribs (rising from base to apex like lines of longitude)
- Ring beams (horizontal rings at intervals, like lines of latitude)
- Lantern or oculus at the apex (optional)
- Drum wall (cylindrical wall below the dome)
- Pendentives or squinches (transition from square plan to circular dome base)
- Tension ring at the base to resist outward thrust

**Construction method:**
For timber domes: curved ribs rise from a circular or polygonal base ring beam to
meet at the apex. Horizontal ring members provide lateral bracing. Cladding is
applied over purlins/battens. For masonry: courses of brick/stone are laid in
gradually diminishing rings. For modern: steel, concrete, or geodesic frameworks.
Pendentives (curved triangular surfaces) or squinches (small arches across corners)
transition from a square building plan to the circular dome base.

**Building types:** Churches (crossing domes), mosques, civic buildings (capitol
buildings, courthouses), mausolea, planetariums, sports arenas.

**Historical periods:**
- Roman (Pantheon, concrete dome)
- Byzantine (pendentive domes, Hagia Sophia)
- Renaissance (Brunelleschi's dome, St Peter's)
- Baroque (elaborately decorated domes)
- 18th-19th century civic buildings
- Modern (geodesic domes, tensile membrane domes)

**Advantages:**
- Spans the largest possible area without columns
- Structurally very efficient (double curvature)
- Iconic, monumental appearance
- Excellent acoustics

**Disadvantages:**
- Very complex to construct
- Expensive
- Only suits circular or regular polygon plans (unless on pendentives)
- Lateral thrust issues at base
- Difficult to waterproof (many joints on curved surface)

---

## 2. PERIOD-BY-PERIOD ROOF GUIDE

### 2.1 Medieval (1066-1485)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Church nave | Barrel vault / open timber | 45-60 deg | Hammerbeam, crown post, or scissor-braced |
| Church tower | Pyramid / spire | 60-75 deg | Stone or timber spire |
| Manor house / hall | Steep gable | 45-60 deg | Open hall with arch-braced or hammerbeam roof |
| Cottage | Steep gable | 50-60 deg | Cruck frame, thatched |
| Castle | Various | -- | Flat behind battlements, steep within towers |
| Barn | Steep gable | 45-55 deg | Aisled barn with arcade posts |

**Key construction:** Cruck frames, crown posts, tie beams, collar-and-rafter,
scissor braces, hammerbeam trusses. No purlins in earliest period (sans-purlin
roof with rafters braced only by battens). Crown post roofs from ~1350 (SE England).
Butt purlins and clasped purlins from late 15th century.

### 2.2 Tudor (1485-1603)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Manor house | Steep cross-gable | 45-60 deg | Multiple gables, decorated bargeboards |
| Townhouse | Steep gable | 45-55 deg | Jettied upper floors, gable to street |
| Church | Gable / barrel vault | 45-55 deg | Hammerbeam or arch-braced |
| Cottage | Steep gable | 50-60 deg | Half-timbered, thatch then tile |
| Barn | Gable | 45-55 deg | Large aisled barns |

**Key construction:** Half-timbered gable ends. Thatch being replaced by clay tiles
(mid-16th century onwards). Steep pitches required for thatch (min 45 deg) retained
even when tiles used. Decorative bargeboards on gable ends. Wind-braced purlins.

### 2.3 Georgian (1714-1830)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| London townhouse | Hip (hidden behind parapet) | 25-35 deg | Parapet required by 1707 Building Act |
| Provincial townhouse | Hip or gable | 30-35 deg | Hip preferred, gable acceptable |
| Terraced house | Hip or M-profile | 25-35 deg | Party walls extend as parapets; butterfly/M between pairs |
| Detached villa | Hip | 30-35 deg | Symmetrical, often with dormers |
| Country house | Hip, sometimes with pediment | 25-35 deg | Palladian influence, hidden roof |
| Church | Gable (behind pediment) | 30-40 deg | Classical temple front |
| Public building | Hip / crown / dome | varies | Classical proportions |

**Key construction:** Cut timber roof with purlins and common rafters. Lower pitches
than medieval/Tudor (slate replacing thatch and plain tiles, allowing lower pitch).
Welsh slate widely available from mid-18th century. Parapet walls (mandatory in
London from 1707) hide the roof from street view. Lead flats and valleys.

### 2.4 Regency (1811-1837)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Townhouse | Hip behind parapet | 25-30 deg | Continuation of Georgian |
| Villa | Hip, low pitch | 20-30 deg | Italianate influence, wider eaves |
| Terrace | Hip/flat behind parapet | 25-30 deg | Stucco facades |

### 2.5 Victorian (1837-1901)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Terraced house | Gable (side) | 30-40 deg | Welsh slate, party wall parapets |
| Semi-detached | Cross-gable / gable | 35-45 deg | Front-facing gable common |
| Detached villa | Cross-gable / hip | 35-45 deg | Complex rooflines, multiple gables |
| Church | Steep gable | 50-60 deg | Gothic Revival, steep pitch |
| Public building | Mansard / hip | 30-45 deg | Second Empire or classical |
| Industrial | Lean-to / saw-tooth | 5-30 deg | North-light saw-tooth roofs |
| Railway station | Barrel vault | varies | Iron/steel arched roofs |
| Barn | Gable / gambrel | 35-45 deg | Agricultural |
| Gothic Revival | Steep gable / cross-gable | 50-65 deg | Polychrome, decorated ridges |

**Key construction:** Machine-cut timber becoming standard. Welsh slate dominant
roofing material. Elaborate ridge tiles, finials, decorative bargeboards on gables.
Cast iron rainwater goods. Cross-gable plans very common for larger houses.
Queen Anne Revival uses Dutch gables. Second Empire style uses mansard.

### 2.6 Edwardian (1901-1914)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Semi-detached | Cross-gable with half-timber | 35-40 deg | Mock-Tudor gable infill |
| Terraced | Gable | 30-35 deg | Simpler than Victorian |
| Detached | Hip or half-hip | 30-40 deg | Arts & Crafts influence |
| Bungalow | Low gable / hip | 25-35 deg | Broad, sweeping roofs |

### 2.7 Inter-War (1918-1939)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Semi-detached | Hip or half-hip | 30-40 deg | Bay-windowed semis, plain tile |
| Bungalow | Hip | 25-35 deg | Broad eaves |
| Art Deco | Flat (behind parapet) | 0.5-5 deg | Streamlined appearance |
| Council housing | Gable or hip | 30-35 deg | Standardised designs |

### 2.8 Modern / Contemporary (1945-present)

| Building Type | Primary Roof | Pitch | Notes |
|---------------|-------------|-------|-------|
| Detached house | Gable / hip | 30-40 deg | Trussed rafters, concrete tile |
| Apartment block | Flat | 0.5-3 deg | Concrete/steel frame |
| Office building | Flat | 0.5-3 deg | Steel frame, membrane roofing |
| Industrial | Flat / shallow pitch | 3-6 deg | Portal frame, metal cladding |
| Contemporary house | Butterfly / flat / mono | varies | Architect-designed |
| Extension | Flat / lean-to | 0.5-15 deg | EPDM or GRP membrane |

---

## 3. GEORGIAN TOWNHOUSE ROOF: DETAILED GUIDANCE

### 3.1 The Default: Hip Roof Behind Parapet

The Georgian townhouse roof is almost always a **hip roof**, hidden behind a
**brick parapet wall**. This is both a legal requirement and an aesthetic choice.

**Legal basis:** The 1707 Building Act (London) required roofs to be hidden behind
an 18-inch brick parapet, banning projecting wooden eaves as a fire risk (response
to the 1666 Great Fire legacy). The 1774 Building Act further standardised this.

**Aesthetic basis:** Georgians admired classical proportions. The parapet gives the
building a rectangular silhouette reminiscent of classical temples, hiding the
pitched roof from street view.

### 3.2 Variation by Location

| Location | Typical Roof | Parapet | Notes |
|----------|-------------|---------|-------|
| London (central) | Hip, hidden behind parapet | Mandatory (1707 Act) | Slate or lead. Virtually always hipped. |
| London (suburbs) | Hip, sometimes visible | Usually present | Slightly relaxed beyond city limits |
| Bath | Hip behind parapet | Yes (classical terraces) | Crescent and terrace designs |
| Edinburgh New Town | Hip behind parapet | Yes | Scottish Georgian follows London norms |
| Provincial towns | Hip or gable | Often present | More variation; gable acceptable on side elevations |
| Rural / country | Hip, sometimes gable | Less common | Detached houses may show gable on secondary elevations |

### 3.3 Variation by Building Form

| Form | Roof Type | Notes |
|------|-----------|-------|
| Terraced (mid-terrace) | Hip or shallow pitch between parapets | Party walls act as parapets on two sides. Roof slopes front-to-back (lean-to), or M-profile between party walls. Front and rear parapets hide the roof. |
| Terraced (end-of-terrace) | Hip on exposed end, parapet on party wall side | The exposed end gets a hip slope; the terrace side is defined by the party wall. |
| Semi-detached | Hip on three sides, party wall parapet on shared side | Uncommon in Georgian period (terraces dominant). |
| Detached | Full hip (four sides) | The classic Georgian hip with dormers. Ridge parallel to the street. |
| Corner plot | Hip with returns | Hipped on all exposed elevations. |

### 3.4 Typical Georgian Roof Section

```
    Parapet (front)            Parapet (rear)
    _____|_____                _____|_____
   |           |              |           |
   |  Gutter   |   Hip Roof   |  Gutter   |
   |  (lead)   |  ___/\___    |  (lead)   |
   |           | /   ||   \   |           |
   |___________||    ||    |  |___________|
                |    ||    |
      Front     | Rafters  |     Rear
      Wall      |          |     Wall
                |__________|

   - Roof pitch: ~27-30 degrees
   - Slate covering (Welsh blue/grey)
   - Lead-lined valley gutters behind parapets
   - Lead flashings at parapet abutments
   - Dormers (if present) on rear slope
```

### 3.5 Key Rules for Georgian Roof Generation

1. **Always use hip roof** unless the building is a simple rural cottage.
2. **Hide the roof behind a parapet** for any London or major city townhouse.
3. **Pitch angle: 27-33 degrees** -- lower than Victorian, reflecting classical restraint.
4. **Covering: Welsh slate** (blue-grey) or, for grander buildings, lead sheet.
5. **Dormers:** If present, on the rear slope (not visible from the front).
6. **Chimneys:** Symmetrical pairs at each party wall (terraces) or at each gable end (detached).
7. **No visible bargeboards or decorative elements** -- the roof should be invisible from the street.
8. **Ridge line parallel to the street** for terraces and most detached houses.

---

## 4. MAPPING RULES: building_type + style + period -> roof_type

### 4.1 Decision Rules (pseudocode)

```
function select_roof_type(building_type, style, period, plan_shape, location):

    # --- Religious buildings ---
    if building_type == "church":
        if period in ["medieval", "tudor"]:
            if has_crossing:
                return "cross-gable"  # nave + transepts
            return "gable"  # steep pitch, 45-60 deg
        if period == "victorian" and style == "gothic_revival":
            return "gable"  # steep, 50-65 deg
        if period == "georgian":
            return "gable"  # behind classical pediment
        if has_dome:
            return "dome"
        return "gable"

    # --- Industrial ---
    if building_type == "industrial":
        if period in ["victorian", "edwardian"]:
            if has_north_lights:
                return "saw_tooth"  # lean-to repeated
            return "gable"  # simple industrial shed
        if period == "modern":
            return "flat"  # or shallow mono-pitch
        return "barrel_vault"  # train sheds, large spans

    # --- Agricultural ---
    if building_type == "barn":
        if style == "dutch_colonial":
            return "gambrel"
        return "gable"  # steep, 40-50 deg

    # --- Residential ---
    if building_type == "house":

        # Georgian period
        if period == "georgian":
            if location == "london":
                return "hip"  # always, hidden behind parapet
            if form == "terraced":
                return "hip"  # or lean-to/M-profile between party walls
            if form == "detached":
                return "hip"  # the Georgian default
            return "hip"

        # Victorian period
        if period == "victorian":
            if form == "terraced":
                return "gable"  # side gable, party wall parapets
            if form == "semi_detached":
                return "cross_gable"  # front-facing gable feature
            if form == "detached":
                if style == "gothic_revival":
                    return "cross_gable"  # steep, decorated
                if style == "italianate":
                    return "hip"  # or crown roof with tower
                if style == "second_empire":
                    return "mansard"
                if style == "queen_anne":
                    return "cross_gable"  # or dutch_gable
                return "cross_gable"
            return "gable"

        # Tudor period
        if period == "tudor":
            return "gable"  # steep, 45-60 deg, half-timbered gable ends

        # Medieval period
        if period == "medieval":
            return "gable"  # steep, cruck or tie-beam

        # Edwardian period
        if period == "edwardian":
            if style == "arts_and_crafts":
                return "half_hip"  # or cross-gable with half-timbered gable
            return "cross_gable"  # front gable with mock-Tudor infill

        # Inter-war period
        if period == "inter_war":
            if style == "art_deco":
                return "flat"
            return "hip"  # or half-hip, typical 1930s semi

        # Modern period
        if period == "modern":
            if style == "contemporary":
                return random_choice("flat", "butterfly", "mono_pitch")
            if form == "apartment":
                return "flat"
            return "gable"  # or hip, standard modern house

    # --- Commercial ---
    if building_type == "commercial":
        if period == "georgian":
            return "hip"  # behind parapet
        if period == "victorian":
            if style == "second_empire":
                return "mansard"
            return "gable"  # or hip behind parapet
        if period == "modern":
            return "flat"
        return "flat"

    # --- Civic / Public ---
    if building_type == "civic":
        if has_dome:
            return "dome"
        if period == "georgian":
            return "hip"  # classical, behind pediment or parapet
        if period == "victorian":
            return "hip"  # or mansard
        return "flat"  # modern civic

    # --- Extensions / Outbuildings ---
    if building_type in ["extension", "outbuilding", "porch"]:
        return "lean_to"

    # --- Square plan buildings ---
    if plan_shape == "square" and building_type in ["tower", "pavilion", "gazebo"]:
        return "pavilion"  # pyramid roof

    # --- Default ---
    return "gable"
```

### 4.2 Pitch Angle Selection

```
function select_pitch(roof_type, period, covering_material):

    base_pitches = {
        "gable":       {default: 35, range: [25, 60]},
        "hip":         {default: 30, range: [25, 40]},
        "half_hip":    {default: 35, range: [30, 45]},
        "mansard_lower": {default: 75, range: [70, 80]},
        "mansard_upper": {default: 30, range: [25, 35]},
        "gambrel_lower": {default: 55, range: [50, 60]},
        "gambrel_upper": {default: 27, range: [20, 30]},
        "flat":        {default: 1.5, range: [0.5, 5]},
        "lean_to":     {default: 15, range: [5, 25]},
        "butterfly":   {default: 15, range: [10, 25]},
        "pavilion":    {default: 35, range: [25, 45]},
        "cross_gable": {default: 38, range: [30, 55]},
        "dutch_gable": {default: 35, range: [30, 45]},
        "crown_side":  {default: 45, range: [30, 60]},
        "crown_top":   {default: 1.5, range: [0.5, 2]},
    }

    # Period adjustments
    if period in ["medieval", "tudor"]:
        pitch += 15  # steeper for thatch/early tile
    if period == "georgian":
        pitch -= 3   # lower pitch, slate
    if period == "victorian" and style == "gothic_revival":
        pitch += 10  # steep Gothic pitch

    # Material constraints
    if covering == "thatch":
        pitch = max(pitch, 45)  # thatch needs min 45 deg
    if covering == "slate":
        pitch = max(pitch, 20)  # slate needs min 20-25 deg
    if covering == "plain_tile":
        pitch = max(pitch, 35)  # plain tiles need min 35 deg
    if covering == "concrete_tile":
        pitch = max(pitch, 17.5)
    if covering == "metal_sheet":
        pitch = max(pitch, 4)

    return clamp(pitch, range.min, range.max)
```

---

## 5. QUICK REFERENCE TABLE

| Roof Type | Pitch (deg) | Complexity | Wind Resist. | Attic Space | Best For |
|-----------|-------------|------------|-------------|-------------|----------|
| Gable | 25-60 | Low | Medium | Excellent | Most residential, all periods |
| Hip | 25-40 | Medium | Excellent | Good | Georgian, formal houses |
| Half-hip | 30-45 | Medium | Good | Very good | Arts & Crafts, transitional |
| Mansard | 70-80/25-35 | High | Good | Excellent (extra storey) | French style, loft space |
| Gambrel | 50-60/20-30 | Medium | Low | Excellent | Barns, Dutch Colonial |
| Flat | 0.5-5 | Low | Good | None | Modern, commercial |
| Lean-to | 5-25 | Very low | Medium | None | Extensions, outbuildings |
| Butterfly | 10-25 | High | Low | None | Mid-century modern |
| Pavilion | 25-45 | Medium | Excellent | Limited | Square plan buildings |
| Cross-gable | 30-55 | High | Medium | Good | L/T plan, Victorian |
| Dutch gable | 30-45 | Medium-High | Good | Good | Dutch/Flemish influence |
| Crown | 30-60/flat | High | Good | Limited | Italianate, formal |
| Barrel vault | n/a | Very high | Good | Volume | Churches, industrial |
| Dome | n/a | Very high | Excellent | Volume | Churches, civic |

---

## 6. COVERING MATERIAL BY PERIOD

| Period | Primary Covering | Minimum Pitch | Notes |
|--------|-----------------|---------------|-------|
| Medieval | Thatch | 45 deg | Straw or reed bundles |
| Medieval | Stone slate | 30 deg | Heavy, needs strong framing |
| Tudor | Thatch then clay tile | 45/35 deg | Transition to tile mid-16th C |
| Georgian | Welsh slate | 20-25 deg | Blue-grey, thin, light |
| Georgian | Lead sheet | 1 deg | Flats, valleys, gutters |
| Victorian | Welsh slate | 20-25 deg | Dominant material |
| Victorian | Plain clay tile | 35 deg | South-east England especially |
| Edwardian | Slate or plain tile | 20-35 deg | Both common |
| Inter-war | Concrete tile | 17.5 deg | Machine-made, cheaper |
| Modern | Concrete tile | 17.5 deg | Dominant residential |
| Modern | Membrane (EPDM/GRP) | 0.5 deg | Flat roofs |
| Modern | Metal standing seam | 3-5 deg | Commercial, contemporary |

---

## 7. STRUCTURAL MEMBER SUMMARY BY ROOF TYPE

| Roof Type | Ridge Board | Hip Rafter | Valley Rafter | Jack Rafter | Common Rafter | Purlin | Tie Beam | Collar |
|-----------|------------|------------|---------------|-------------|---------------|--------|----------|--------|
| Gable | Yes | No | No | No | Yes | If needed | Yes | Optional |
| Hip | Yes (short) | Yes (4) | No | Yes | Yes | If needed | Yes | Optional |
| Half-hip | Yes | Yes (2, short) | No | Yes (few) | Yes | If needed | Yes | Optional |
| Mansard | Optional | Optional | No | Optional | Yes (2 sets) | Curb beam | Yes | No |
| Gambrel | Yes | No | No | No | Yes (2 sets) | Curb beam | Yes | No |
| Flat | No | No | No | No | No | No | Joists only | No |
| Lean-to | No | No | No | No | Yes | If needed | No | No |
| Butterfly | No | No | Valley beam | No | Yes | If needed | No | No |
| Pavilion | No | Yes (4) | No | Yes (all) | No | If needed | Yes | No |
| Cross-gable | Yes (2+) | No | Yes | No | Yes | If needed | Yes | Optional |
| Cross-hip | Yes (2+) | Yes (4+) | Yes | Yes | Yes | If needed | Yes | Optional |
| Dutch gable | Yes | Yes (truncated) | No | Yes | Yes | If needed | Yes | Optional |
| Crown | No | Optional | No | Optional | Yes | Curb beam | Yes | No |
| Barrel vault | No | No | No | No | Curved ribs | Yes (longitudinal) | Tie rods | No |
| Dome | No | No | No | No | Ribs | Ring beams | Tension ring | No |

---

*This reference should be used in conjunction with `ROOF_CONSTRUCTION_DETAIL.md`
which provides detailed geometry, joint details, and timber dimensions for
cut timber roof construction.*
