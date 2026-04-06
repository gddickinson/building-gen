# Roof Construction Detail: Traditional Cut Timber Roof

Comprehensive reference for 3D modeling of a traditional UK cut timber roof,
component by component, with exact geometry for creating rotated meshes.

---

## 1. COMPONENT INVENTORY AND DIMENSIONS

### 1.1 Standard UK Timber Sections (BS EN 336 / regularised)

| Component         | Nominal (mm)  | Actual/Finished (mm) | Typical Length  | Grade |
|-------------------|---------------|----------------------|-----------------|-------|
| Common rafter     | 47 x 150      | 45 x 145             | 4.2m - 5.4m     | C16/C24 |
| Hip rafter        | 47 x 200      | 45 x 195             | 5.0m - 7.0m     | C24 |
| Jack rafter       | 47 x 150      | 45 x 145             | varies           | C16/C24 |
| Ridge board       | 25 x 175      | 22 x 170             | up to 4.8m      | C16 |
| Purlin            | 47 x 175      | 45 x 170             | up to 4.8m      | C16/C24 |
| Ceiling joist     | 47 x 100      | 45 x 95              | up to 4.8m      | C16 |
| Wall plate        | 100 x 50      | 97 x 47              | up to 4.8m      | C16 |
| Tile batten       | 25 x 50       | 25 x 50              | up to 4.8m      | BS 5534 graded |
| Counter batten    | 25 x 38       | 25 x 38              | varies           | -- |
| Fascia board      | 25 x 150      | 22 x 145             | up to 4.8m      | treated softwood |
| Soffit board      | 9mm plywood or 12mm UPVC | -- | varies        | -- |
| Collar tie        | 47 x 100      | 45 x 95              | varies           | C16 |

Source: BS EN 336, UK regularised carcassing timber. Nominal 47mm finished to 45mm,
nominal 150mm finished to 145mm. Suppliers: Travis Perkins, Chiltern Timber.

### 1.2 Span Tables Summary (BS 5268-7.5 / Eurocode 5)

For **C16 grade, 47x150mm rafters** at standard spacings:

| Rafter spacing (mm) | Max span @ 22.5-30 deg | Max span @ 30-45 deg |
|---------------------|------------------------|----------------------|
| 400                 | ~3.4m                  | ~3.8m                |
| 450                 | ~3.2m                  | ~3.6m                |
| 600                 | ~2.8m                  | ~3.1m                |

For C24 grade: add approximately 10-15% to these spans.

Where span exceeds table limits, a **purlin** at mid-span halves the rafter span.

---

## 2. BIRDSMOUTH CUT: RAFTER TO WALL PLATE CONNECTION

### 2.1 Geometry

The birdsmouth is a notch cut in the underside of the rafter where it sits on the
wall plate. It consists of two cuts:

```
                    Rafter (going up at pitch angle)
                   /
                  /
                 /
    ____________/
    |          |  <-- Heel cut (vertical, = pitch angle from rafter edge)
    |__________|  <-- Seat cut (horizontal, sits flat on wall plate)

    [== WALL PLATE ==]
```

**Seat cut**: Horizontal cut that sits flat on top of the wall plate.
- Length = width of the wall plate = 100mm (typically)
- Must provide at least 40mm bearing on the wall plate

**Heel cut**: Vertical cut perpendicular to the seat cut.
- The plumb line at the birdsmouth location

### 2.2 Critical Rule: Maximum Depth

**Never cut more than 1/3 of the rafter depth.** For a 150mm rafter:
- Maximum birdsmouth depth = 50mm
- Recommended depth = 38-50mm
- Remaining timber at the notch = at least 100mm (2/3 of 150mm)

### 2.3 Angles at the Birdsmouth (for 35-degree pitch)

```
Pitch angle = 35 degrees

Seat cut angle from the rafter's bottom edge:
  = 90 - pitch = 90 - 35 = 55 degrees (from the long axis of the rafter)

Heel cut angle from the rafter's bottom edge:
  = pitch = 35 degrees (from the long axis of the rafter)
```

### 2.4 Fixing

The rafter is nailed through into the wall plate with:
- 2x 100mm galvanised nails skew-nailed through rafter into wall plate
- Alternatively: framing anchors (galvanised steel straps)

### 2.5 3D Modeling Notes

For a simplified 3D model, the birdsmouth can be ignored -- just place the rafter
so its bottom edge at the eaves touches the top of the wall plate. The centre of
the rafter at the wall plate position should be at:

```
y_rafter_centre = wall_plate_top + (rafter_depth / 2) * cos(pitch)
```

---

## 3. RAFTER TO RIDGE BOARD CONNECTION

### 3.1 Geometry

The rafter receives a **plumb cut** (vertical cut) at its top end where it butts
against the ridge board. The opposing rafter does the same on the other side.

```
        Ridge board (vertical, 25x175mm)
             |     |
            /|     |\
           / |     | \
     Rafter  |     |  Rafter
         /   |     |   \
        /    |     |    \
```

The plumb cut angle = the pitch angle (35 degrees from vertical, or 55 degrees
from horizontal). The rafter's top end is cut so its end face is vertical.

### 3.2 How They Meet

- The ridge board stands vertically
- Its depth (175mm) must be >= the plumb cut depth of the rafter
- Rafters from opposing sides butt against the ridge board, one on each face
- The ridge board is NOT a structural beam -- it is a locating/nailing board
  (the triangulated structure of rafter pairs + ceiling joist carries the load)

### 3.3 Fixing

- Each rafter is nailed through the ridge board into the opposing rafter's end
- 2x 100mm nails through ridge into rafter end on each side
- Additionally, a nail through each rafter face into the ridge board

### 3.4 Ridge Height Calculation

```
Ridge height above wall plate top:
  h_ridge = span/2 * tan(pitch)

For 8m span at 35 degrees:
  h_ridge = 4.0 * tan(35) = 4.0 * 0.7002 = 2.801m

Ridge board centre Y position:
  y_ridge = wall_plate_top + h_ridge
```

### 3.5 3D Modeling Notes

The ridge board is an axis-aligned vertical plank running the length of the
building. Place it as a simple box:
- Length = building length (along the ridge)
- Height = 175mm (the board depth, oriented vertically)
- Width = 25mm
- Position: centred on building width, at ridge height

---

## 4. RAFTER GEOMETRY: THE KEY 3D PROBLEM

### 4.1 The Problem

A rafter is a rectangular-cross-section timber beam (47mm x 150mm) that runs from
the wall plate to the ridge at the roof pitch angle (e.g. 35 degrees). An
axis-aligned bounding box cannot represent this -- you need a **rotated mesh**.

### 4.2 Rafter Dimensions

For a building with:
- Span (wall plate to wall plate) = 8.0m
- Pitch = 35 degrees
- Eaves overhang = 0.3m

```
Rafter length (wall plate to ridge):
  L_main = (span/2) / cos(pitch) = 4.0 / cos(35) = 4.0 / 0.8192 = 4.883m

Rafter length (with overhang):
  L_total = L_main + overhang / cos(pitch) = 4.883 + 0.366 = 5.249m

Cross-section: 47mm wide x 150mm deep (47mm is the "thickness" you see from
the side; 150mm is the depth measured perpendicular to the roof slope)
```

### 4.3 HOW TO CREATE A ROTATED BOX MESH (Trimesh)

This is the critical geometry for your 3D model. A rafter is a box that must be
rotated around its base point (at the wall plate) by the pitch angle.

#### Method: Rotation Matrix Applied to Box Vertices

```python
import numpy as np
import trimesh

def create_rafter_mesh(
    length: float,       # Total rafter length (metres), e.g. 5.249
    width: float,        # Cross-section width (metres), e.g. 0.047
    depth: float,        # Cross-section depth (metres), e.g. 0.150
    pitch_deg: float,    # Roof pitch in degrees, e.g. 35.0
    base_x: float,       # X position of rafter foot (along building length)
    base_y: float,       # Y position of rafter foot (height, top of wall plate)
    base_z: float,       # Z position of rafter foot (across building width)
    side: int = 1,       # 1 = left-to-right slope, -1 = right-to-left slope
) -> trimesh.Trimesh:
    """Create a rafter mesh rotated to the correct pitch angle.

    The rafter is created as a box, then rotated around its base point
    so it rises from the wall plate to the ridge at the given pitch.

    Coordinate system:
      X = along building length (parallel to ridge)
      Y = vertical (up)
      Z = across building width (perpendicular to ridge)

    The rafter runs in the Y-Z plane (across the building, rising to ridge).
    The rotation is around the X axis.
    """
    pitch_rad = np.radians(pitch_deg)

    # Step 1: Create box centred at origin
    mesh = trimesh.creation.box(extents=[width, depth, length])

    # Step 2: Translate so the "base" end of the box is at origin.
    # The box is centred at (0,0,0), extends from -length/2 to +length/2 on Z.
    # We want the base (foot) end at Z=0, so shift +Z by length/2.
    # We also want the bottom face of the rafter at Y=0.
    mesh.apply_translation([0, depth / 2, length / 2])
    # Now: box spans X: [-width/2, +width/2]
    #                Y: [0, depth]              (bottom face at Y=0)
    #                Z: [0, length]             (foot at Z=0, tip at Z=length)

    # Step 3: Rotate around the X axis by the pitch angle.
    # This tilts the rafter upward: Z becomes slope direction, Y becomes height.
    # Rotation matrix around X axis:
    #   [1,    0,         0    ]
    #   [0,  cos(a),  -sin(a)  ]
    #   [0,  sin(a),   cos(a)  ]

    cos_p = np.cos(pitch_rad)
    sin_p = np.sin(pitch_rad)

    rotation_matrix = np.array([
        [1,  0,      0,     0],
        [0,  cos_p, -sin_p, 0],
        [0,  sin_p,  cos_p, 0],
        [0,  0,      0,     1],
    ])

    mesh.apply_transform(rotation_matrix)

    # Step 4: Flip for the other side of the roof if needed
    if side == -1:
        # Mirror in Z: the rafter slopes the other way
        mirror = np.eye(4)
        mirror[2, 2] = -1
        mesh.apply_transform(mirror)

    # Step 5: Translate to the actual world position
    mesh.apply_translation([base_x, base_y, base_z])

    return mesh
```

#### Verification: Key Vertex Positions After Rotation

For a rafter of length L at pitch P, foot at origin:
```
Foot (bottom-outside corner):  (0, 0, 0)
Tip  (top-outside corner):     (0, L*sin(P), L*cos(P))

For L=5.249m, P=35deg:
  Tip Y = 5.249 * sin(35) = 5.249 * 0.5736 = 3.011m  (height gained)
  Tip Z = 5.249 * cos(35) = 5.249 * 0.8192 = 4.300m  (horizontal run)
```

### 4.4 Alternative: Direct Vertex Construction

If you want to avoid rotation matrices, you can build the 8 vertices directly:

```python
def rafter_vertices(
    length: float, width: float, depth: float,
    pitch_deg: float,
    base_x: float, base_y: float, base_z: float,
    side: int = 1,
) -> np.ndarray:
    """Return 8 vertices of a rafter box at the given pitch.

    Returns array of shape (8, 3) suitable for trimesh.
    """
    p = np.radians(pitch_deg)

    # Unit vectors along and perpendicular to the rafter
    # "along" = direction rafter runs (up the slope)
    along = np.array([0, np.sin(p), side * np.cos(p)])
    # "up" = perpendicular to rafter surface (normal to roof plane)
    up = np.array([0, np.cos(p), -side * np.sin(p)])
    # "across" = along the ridge (X axis)
    across = np.array([1, 0, 0])

    hw = width / 2   # half-width

    # 8 corners: 4 at foot end (t=0), 4 at tip end (t=length)
    # At each end: bottom-left, bottom-right, top-left, top-right
    vertices = np.array([
        # Foot end (t=0)
        -hw * across + 0 * up,              # 0: foot, bottom-left
        +hw * across + 0 * up,              # 1: foot, bottom-right
        +hw * across + depth * up,          # 2: foot, top-right
        -hw * across + depth * up,          # 3: foot, top-left
        # Tip end (t=length)
        -hw * across + length * along + 0 * up,         # 4: tip, bottom-left
        +hw * across + length * along + 0 * up,         # 5: tip, bottom-right
        +hw * across + length * along + depth * up,     # 6: tip, top-right
        -hw * across + length * along + depth * up,     # 7: tip, top-left
    ])

    # Offset to world position
    offset = np.array([base_x, base_y, base_z])
    vertices += offset

    return vertices

# Standard box faces (for trimesh)
RAFTER_FACES = np.array([
    [0, 1, 2], [0, 2, 3],  # foot end
    [4, 6, 5], [4, 7, 6],  # tip end
    [0, 4, 5], [0, 5, 1],  # bottom face
    [2, 6, 7], [2, 7, 3],  # top face
    [0, 3, 7], [0, 7, 4],  # left side
    [1, 5, 6], [1, 6, 2],  # right side
])
```

### 4.5 Integration with Current Element System

The current `_element_to_mesh()` in `element_renderer.py` creates axis-aligned
boxes and only translates them. To support pitched roof elements, extend it:

```python
def _element_to_mesh(element: Element) -> trimesh.Trimesh | None:
    if element.length <= 0 or element.width <= 0 or element.height <= 0:
        return None

    mesh = trimesh.creation.box(
        extents=[element.length, element.height, element.width],
    )

    # Apply pitch rotation for roof elements
    if element.pitch != 0:
        pitch_rad = math.radians(element.pitch)
        cos_p = math.cos(pitch_rad)
        sin_p = math.sin(pitch_rad)
        # Rotate around X axis (rafter runs in Y-Z plane)
        R = np.array([
            [1,  0,      0,     0],
            [0,  cos_p, -sin_p, 0],
            [0,  sin_p,  cos_p, 0],
            [0,  0,      0,     1],
        ])
        mesh.apply_transform(R)

    # Apply Y-axis rotation (existing field)
    if element.rotation != 0:
        rot_rad = math.radians(element.rotation)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        R = np.array([
            [ cos_r, 0, sin_r, 0],
            [ 0,     1, 0,     0],
            [-sin_r, 0, cos_r, 0],
            [ 0,     0, 0,     1],
        ])
        mesh.apply_transform(R)

    mesh.apply_translation([element.x, element.y, element.z])

    color = _MAT_COLORS.get(element.material_name, [180, 180, 180, 255])
    mesh.visual.face_colors = color
    return mesh
```

This requires adding a `pitch` field to the Element dataclass:
```python
pitch: float = 0.0  # degrees, rotation around X axis (for rafters etc.)
```

---

## 5. PURLIN SUPPORT AT MID-SPAN

### 5.1 What Is a Purlin?

A purlin is a horizontal timber beam that runs parallel to the ridge and wall
plate, at approximately mid-span of the rafters. It reduces the effective span
of each rafter by providing intermediate support.

### 5.2 Dimensions and Position

```
Typical purlin: 47 x 175mm (or 63 x 175mm for longer spans)
Minimum: 125 x 44mm C16

Position: roughly halfway between wall plate and ridge, measured along the slope.
  - At height: h_ridge / 2 = (span/2 * tan(pitch)) / 2
  - At horizontal offset: span/4 from wall plate
```

### 5.3 How Rafters Sit on Purlins

The purlin runs horizontally (parallel to the ridge). Rafters cross over it at
the pitch angle. The rafter is notched (birdsmouthed or simply rests) on top of
the purlin. In traditional construction, rafters are notched to sit over the
purlin with a small housing joint.

### 5.4 Purlin Support

Purlins are supported by:
- **Struts**: Diagonal timbers from purlin down to a load-bearing internal wall
- **Hangers**: From the ridge or a beam above
- **Built into gable walls**: Purlin ends housed into the masonry

### 5.5 3D Modeling

The purlin is an **axis-aligned horizontal box** (no rotation needed):
```
Position:
  x = centred along building length
  y = wall_plate_top + purlin_height_on_slope
    = wall_plate_top + (rafter_length/2) * sin(pitch)
  z = wall_plate_z + (rafter_length/2) * cos(pitch)

Dimensions:
  length = building length (along X)
  height = 175mm (vertical depth of purlin)
  width = 47mm (horizontal thickness)
```

---

## 6. CEILING JOISTS / TIE BEAMS

### 6.1 Function

Ceiling joists span from wall plate to wall plate horizontally. They serve two
critical functions:
1. **Tie the rafter feet together** -- preventing the rafters from pushing the
   walls outward (thrust). This is the "tie" function.
2. **Support the ceiling** -- plasterboard or lath-and-plaster is fixed to their
   underside.

### 6.2 Dimensions

```
Typical: 47 x 100mm (up to ~3.6m span) or 47 x 150mm (up to ~4.8m span)
Spacing: Same as rafters -- 400mm or 600mm centres
Grade: C16
```

### 6.3 Connection to Rafter Feet

The ceiling joist sits on top of the wall plate, alongside the rafter foot. They
are nailed together at the wall plate:

```
Side view at eaves:
                  /  Rafter
                 /
                /
    ___________/___________
    |  Ceiling joist      |   <-- horizontal, on top of wall plate
    |_____________________|
    [===== WALL PLATE ====]
    ========================  <-- top of wall
```

- The ceiling joist and rafter are nailed together with 3x 75mm or 100mm nails
- Both sit on the wall plate
- The ceiling joist provides the critical horizontal tie force

### 6.4 3D Modeling

Ceiling joists are **axis-aligned horizontal boxes** running across the building:
```
Position:
  x = same x-position as the corresponding rafter pair
  y = wall_plate_top + joist_height/2  (sits on top of wall plate)
  z = centred between the two wall plates

Dimensions:
  length = 47mm (along X, same as rafter width -- they pair up)
  height = 100mm (vertical depth)
  width = span between wall plates (along Z)
```

---

## 7. TILE BATTENS

### 7.1 What They Are

Battens are thin horizontal timbers nailed across the tops of the rafters,
perpendicular to the rafter slope. They provide the fixing points for slates
or tiles.

### 7.2 Dimensions and Spacing

```
Cross-section: 25mm x 50mm (BS 5534 graded)
Spacing (gauge): depends on tile/slate size and headlap:
  - Plain clay tiles: 100mm gauge (265mm tile, 65mm headlap)
  - Concrete interlocking tiles: 330-345mm gauge
  - Natural slate (500x250mm): ~210mm gauge with 75mm headlap
  - Fibre cement slate: varies, typically 140-170mm gauge
```

### 7.3 How Battens Are Fixed

- Nailed through into each rafter with 65mm x 3.35mm galvanised round wire nails
- Each batten is nailed at every rafter crossing
- Battens run horizontally when viewed from the front, but they follow the roof
  plane (they are on top of the rafters which are at the pitch angle)

### 7.4 Counter Battens (for ventilation)

In modern construction, counter battens (25 x 38mm) run vertically UP the slope
(parallel to rafters), on top of the breathable membrane. Tile battens then cross
over them. This creates a ventilation gap.

### 7.5 3D Modeling

Battens are the trickiest element because they lie in the roof plane but run
horizontally across it. Each batten is a thin box that must be rotated to lie
in the roof plane:

```python
def create_batten_mesh(
    batten_length: float,   # Across the roof (along X axis)
    pitch_deg: float,
    position_along_slope: float,  # Distance from eaves up the slope
    base_y: float,          # Y of wall plate top
    base_z: float,          # Z of wall plate
    side: int = 1,
) -> trimesh.Trimesh:
    """A batten lies in the roof plane, running along the X axis."""
    width = 0.050   # 50mm
    height = 0.025  # 25mm

    pitch_rad = np.radians(pitch_deg)

    # Batten position on the roof surface
    y = base_y + position_along_slope * np.sin(pitch_rad) + height/2 * np.cos(pitch_rad)
    z = base_z + side * position_along_slope * np.cos(pitch_rad) - side * height/2 * np.sin(pitch_rad)

    mesh = trimesh.creation.box(extents=[batten_length, height, width])

    # Rotate to lie in roof plane (tilt around X axis)
    cos_p = np.cos(pitch_rad)
    sin_p = np.sin(pitch_rad)
    R = np.array([
        [1, 0, 0, 0],
        [0, cos_p, -sin_p, 0],
        [0, sin_p,  cos_p, 0],
        [0, 0, 0, 1],
    ])
    mesh.apply_transform(R)
    mesh.apply_translation([0, y, z])

    return mesh
```

---

## 8. SLATES AND TILES

### 8.1 How They Work

Slates and tiles hang from battens by means of a **nib** (tiles) or **nail holes**
(slates). They overlap each other by a defined "headlap" so water runs down
without penetrating.

### 8.2 Slate Dimensions (Welsh slate, typical)

```
Standard sizes:
  500 x 250mm ("Countess") -- most common
  600 x 300mm ("Duchess")
  400 x 200mm ("Lady")

Thickness: 4-6mm (natural slate), 4mm (fibre cement)
Weight: ~50 kg/m2 for natural slate, ~20 kg/m2 for fibre cement
```

### 8.3 Headlap and Gauge

```
Headlap: the amount by which each slate overlaps the slate two courses below.
  - Minimum 75mm at pitches >= 30 degrees
  - Minimum 100mm at pitches 25-30 degrees
  - Minimum 110mm at pitches 22.5-25 degrees

Gauge = (Slate length - Headlap) / 2
  For 500mm slate, 75mm headlap: gauge = (500 - 75) / 2 = 212.5mm

Margin (exposed part): = gauge = 212.5mm
```

### 8.4 Fixing

- Each slate is fixed with 2 copper or aluminium nails (30-40mm)
- Nails go through pre-punched holes near the head of the slate
- The slate hangs from the batten by these nails
- Modern practice: every slate nailed (BS 5534 requirement)

### 8.5 3D Modeling

Each slate is a thin flat box lying in the roof plane. Like battens, they need
pitch rotation:

```python
def create_slate_mesh(
    slate_width: float,     # 0.250m
    slate_height: float,    # 0.500m (along slope)
    slate_thickness: float, # 0.005m
    pitch_deg: float,
    position_x: float,      # Along building length
    position_along_slope: float,  # Distance from eaves
    base_y: float,
    base_z: float,
    side: int = 1,
) -> trimesh.Trimesh:
    """A slate is a thin flat plate lying in the roof plane."""
    mesh = trimesh.creation.box(
        extents=[slate_width, slate_thickness, slate_height]
    )

    pitch_rad = np.radians(pitch_deg)

    # Position on roof surface (on top of battens)
    y = base_y + position_along_slope * np.sin(pitch_rad)
    z = base_z + side * position_along_slope * np.cos(pitch_rad)

    # Rotate into roof plane
    cos_p = np.cos(pitch_rad)
    sin_p = np.sin(pitch_rad)
    R = np.array([
        [1, 0, 0, 0],
        [0, cos_p, -sin_p, 0],
        [0, sin_p,  cos_p, 0],
        [0, 0, 0, 1],
    ])
    mesh.apply_transform(R)
    mesh.apply_translation([position_x, y, z])

    return mesh
```

---

## 9. FASCIA BOARD

### 9.1 Function

The fascia board is a flat board fixed vertically to the ends of the rafter tails
(the overhanging part beyond the wall). It:
- Provides a neat finish at the eaves
- Supports the gutter
- Closes off the rafter ends from weather

### 9.2 Dimensions

```
Typical: 25mm x 150mm (or 25mm x 175mm, or 25mm x 200mm)
Material: Treated softwood, or UPVC
Length: Full length of the building eaves
```

### 9.3 Connection

```
Side view:
              /  Rafter
             /
            /
    _______/
    |      |  <-- Rafter tail (overhang)
    |  F   |  <-- Fascia board nailed to rafter end
    |  A   |
    |  S   |
    |  C   |
    |  I   |
    |  A   |
    |______|
       |
     Gutter

The rafter tail is typically cut with a plumb cut (vertical face)
at its very end. The fascia is nailed to this vertical face.
```

### 9.4 3D Modeling

The fascia is a simple **axis-aligned vertical board** running the full length
of the eaves:

```
Position:
  x = centred along building length
  y = at rafter tail end height
    = wall_plate_top - overhang * tan(pitch) + fascia_height/2
  z = wall_plate_z + overhang (outside the wall)

Dimensions:
  length = building_length (along X)
  height = 150mm (vertical)
  width = 25mm (thin board)
```

Actually, since the rafter tail is cut with a plumb cut, the fascia
centre Y depends on how the rafter tail is cut. Typically:
```
fascia_top_y = wall_plate_top  (approximately level with wall plate top)
fascia_bottom_y = fascia_top_y - 0.150
fascia_centre_y = fascia_top_y - 0.075
```

---

## 10. HIP ROOF CONSTRUCTION

### 10.1 Hip Rafter

A hip rafter runs diagonally from the corner of the building (at the wall plate)
up to the end of the ridge board. It is the diagonal "spine" of the hip.

```
Plan view:
    _________________________
    |           |           |
    |    /      |      \    |
    |  /   Common rafters \  |
    |/     (parallel)      \|
    |\                     /|
    |  \        |        /  |
    |    \      |      /    |
    |      \ Hip rafter/    |
    |        \  |  /        |
    |__________\|/__________|
                Corner
```

### 10.2 Hip Rafter Angle

The hip rafter's plan angle is 45 degrees (for a rectangular building with
equal pitch on all sides). But its actual slope is less than the common rafters:

```
Common rafter pitch = P (e.g. 35 degrees)
Common rafter rise = span/2 * tan(P)

Hip rafter plan run = (span/2) * sqrt(2)  [diagonal of the corner triangle]
Hip rafter rise = same as common rafter = span/2 * tan(P)

Hip rafter pitch = arctan(rise / plan_run)
                 = arctan(tan(P) / sqrt(2))

For P = 35 degrees:
  Hip pitch = arctan(tan(35) / sqrt(2))
            = arctan(0.7002 / 1.4142)
            = arctan(0.4951)
            = 26.34 degrees
```

### 10.3 Hip Rafter Length

```
Hip rafter length = rise / sin(hip_pitch)
                  = (span/2 * tan(P)) / sin(hip_pitch)

Or equivalently:
  Hip rafter length = (span/2) * sqrt(2) / cos(hip_pitch)

For span=8m, P=35:
  Rise = 4.0 * 0.7002 = 2.801m
  Hip length = 2.801 / sin(26.34) = 2.801 / 0.4437 = 6.314m
```

### 10.4 Hip Rafter Cross-Section

```
Typical: 47 x 200mm (needs to be deeper than common rafters because jack
rafters connect to it and it carries more load)

The hip rafter also has a "backing cut" -- the top edges are beveled so the
roof plane (sheathing/battens) lies flat across it.

Backing angle = arctan(sin(common_pitch) * tan(45))
              = arctan(sin(35) * 1.0)
              = arctan(0.5736)
              = 29.8 degrees
```

### 10.5 Jack Rafters

Jack rafters are shorter rafters that run from the wall plate to the hip rafter
(instead of to the ridge). They are parallel to the common rafters but
progressively shorter.

```
Plan view showing jack rafters:
                Hip rafter
               /
              /
    ________/________
    |  |  |/  |  |  |
    |  | /|   |  |  |  <-- Jack rafters (parallel to common rafters)
    |  /  |   |  |  |
    |/ |  |   |  |  |

Each successive jack rafter is shorter by a fixed amount:
  Jack rafter length reduction per spacing =
    rafter_spacing / cos(common_pitch) * 1/cos(45)

For 400mm spacing, 35-degree pitch:
  Reduction = 0.400 / cos(35) / cos(45) = 0.400 / 0.8192 / 0.7071 = 0.691m

So if the longest jack rafter (nearest the ridge end) is 4.5m,
the next is 3.81m, then 3.12m, then 2.43m, etc.
```

### 10.6 Jack Rafter Compound Cut

Where the jack rafter meets the hip rafter, it needs a **compound cut** -- a
combination of:
1. A plumb cut (like at the ridge)
2. A side bevel (because the hip runs at 45 degrees in plan)

```
Side cut angle = arctan(tan(common_pitch) / sqrt(2))  [this gives the cheek cut]
For 35 degrees: arctan(0.7002 / 1.4142) = arctan(0.4951) = 26.3 degrees
```

### 10.7 3D Modeling of Hip Rafter

The hip rafter needs **two rotations**: one for pitch (around a horizontal axis)
and one for the 45-degree plan angle (around the Y axis):

```python
def create_hip_rafter_mesh(
    length: float,
    width: float,        # 0.047m
    depth: float,        # 0.200m
    common_pitch_deg: float,
    base_x: float,       # Corner X
    base_y: float,       # Wall plate top
    base_z: float,       # Corner Z
    corner: str = "SW",  # Which corner: SW, SE, NW, NE
) -> trimesh.Trimesh:
    """Create a hip rafter running diagonally from corner to ridge end."""

    hip_pitch_rad = np.arctan(np.tan(np.radians(common_pitch_deg)) / np.sqrt(2))

    # Create box with length along Z
    mesh = trimesh.creation.box(extents=[width, depth, length])
    mesh.apply_translation([0, depth / 2, length / 2])

    # Step 1: Rotate for pitch (around X axis)
    cos_p = np.cos(hip_pitch_rad)
    sin_p = np.sin(hip_pitch_rad)
    Rx = np.array([
        [1, 0, 0, 0],
        [0, cos_p, -sin_p, 0],
        [0, sin_p,  cos_p, 0],
        [0, 0, 0, 1],
    ])
    mesh.apply_transform(Rx)

    # Step 2: Rotate 45 degrees in plan (around Y axis)
    # Direction depends on which corner
    plan_angles = {"SW": 45, "SE": 135, "NW": -45, "NE": -135}
    plan_rad = np.radians(plan_angles.get(corner, 45))
    cos_y = np.cos(plan_rad)
    sin_y = np.sin(plan_rad)
    Ry = np.array([
        [cos_y,  0, sin_y, 0],
        [0,      1, 0,     0],
        [-sin_y, 0, cos_y, 0],
        [0,      0, 0,     1],
    ])
    mesh.apply_transform(Ry)

    # Step 3: Translate to corner position
    mesh.apply_translation([base_x, base_y, base_z])

    return mesh
```

---

## 11. COMPLETE ROOF ASSEMBLY SEQUENCE

This is the order in which a traditional cut roof is built, and a sensible order
for generating the 3D model:

### Step 1: Wall Plates
Axis-aligned horizontal boxes on top of the walls.
```
Size: 100 x 50mm
Position: centred on top of each external wall
Orientation: runs along the wall length (horizontal, axis-aligned)
```

### Step 2: Ceiling Joists
Axis-aligned horizontal boxes spanning between wall plates.
```
Size: 47 x 100mm (or 47 x 150mm)
Spacing: 400mm or 600mm centres
Orientation: perpendicular to wall plates, horizontal
```

### Step 3: Ridge Board
Axis-aligned vertical plank at the apex.
```
Size: 25 x 175mm (vertical)
Position: centred on building width, at ridge height
Orientation: runs along building length (horizontal, axis-aligned)
```

### Step 4: Common Rafters (ROTATED)
Rotated boxes from wall plate to ridge, in pairs.
```
Size: 47 x 150mm
Spacing: 400mm or 600mm centres, matching ceiling joists
Rotation: pitch angle around X axis
Position: one each side, mirrored
```

### Step 5: Hip Rafters (ROTATED, two axes)
Rotated boxes from corners to ridge ends.
```
Size: 47 x 200mm
Rotation: hip pitch around local axis, then 45 degrees in plan
```

### Step 6: Jack Rafters (ROTATED)
Same as common rafters but shorter, meeting hip rafter.
```
Size: 47 x 150mm
Rotation: same pitch as common rafters
Length: progressively shorter toward corner
```

### Step 7: Purlins (if span requires)
Axis-aligned horizontal boxes at mid-span.
```
Size: 47 x 175mm
Position: at half-height on the roof slope
```

### Step 8: Fascia Boards
Axis-aligned vertical boards at eaves.
```
Size: 25 x 150mm
Position: at rafter tail ends
```

### Step 9: Tile Battens (ROTATED)
Thin horizontal strips rotated to lie in roof plane.
```
Size: 25 x 50mm
Spacing: depends on tile/slate gauge
Rotation: pitch angle (lying in roof plane)
```

### Step 10: Slates/Tiles (ROTATED)
Thin flat elements lying in roof plane, overlapping.
```
Size: 500 x 250 x 5mm (slate) or similar
Spacing: gauge = (length - headlap) / 2
Rotation: pitch angle
```

---

## 12. SUMMARY: ROTATION APPROACHES

### Elements That Need Rotation

| Element       | Pitch rotation (around X) | Plan rotation (around Y) |
|---------------|--------------------------|--------------------------|
| Common rafter | YES (pitch angle)         | NO (runs perpendicular to ridge) |
| Hip rafter    | YES (hip pitch angle)     | YES (45 degrees)         |
| Jack rafter   | YES (pitch angle)         | NO (parallel to common rafters) |
| Tile batten   | YES (pitch angle)         | NO (lies in roof plane)  |
| Slate/tile    | YES (pitch angle)         | NO (lies in roof plane)  |
| Ridge board   | NO                        | NO (axis-aligned)        |
| Wall plate    | NO                        | NO (axis-aligned)        |
| Ceiling joist | NO                        | NO (axis-aligned)        |
| Purlin        | NO                        | NO (axis-aligned)        |
| Fascia        | NO                        | NO (axis-aligned)        |

### The Universal Rotation Pattern

For any element that lies in the roof plane or runs along the roof slope,
the rotation is always around the X axis (assuming the ridge runs along X):

```python
pitch_rad = math.radians(pitch_degrees)
rotation_matrix_4x4 = [
    [1,  0,              0,             0],
    [0,  cos(pitch_rad), -sin(pitch_rad), 0],
    [0,  sin(pitch_rad),  cos(pitch_rad), 0],
    [0,  0,              0,             1],
]
```

For elements on the opposite side of the roof, negate the pitch angle (or
equivalently, mirror in Z after rotation).

---

## 13. QUICK REFERENCE FORMULAE

```
Given:
  S = full span (wall plate to wall plate), metres
  P = pitch angle, degrees
  O = eaves overhang, metres
  R = rafter spacing, metres (0.4 or 0.6)

Derived:
  Ridge height above wall plate:     H = (S/2) * tan(P)
  Common rafter length (no overhang): L = (S/2) / cos(P)
  Common rafter length (with overhang): L = (S/2 + O) / cos(P)
  Hip rafter pitch:                   Hp = arctan(tan(P) / sqrt(2))
  Hip rafter length:                  Lh = H / sin(Hp)
  Number of rafter pairs:             N = floor(building_length / R) + 1
  Jack rafter length decrement:       dJ = R / (cos(P) * cos(45))
  Batten gauge (plain tile, 265mm):   G = (265 - 65) / 2 = 100mm
  Batten gauge (500mm slate, 75mm lap): G = (500 - 75) / 2 = 212.5mm
  Slates per m2 (500x250, 75mm lap):  ~18.8 slates/m2
  Roof surface area (one side):       A = (S/2 + O) / cos(P) * building_length
```

---

## Sources

- [DIY Doctor - Birdsmouth Joint](https://www.diydoctor.org.uk/projects/birdsmouth.htm)
- [Omnicalculator - Birdsmouth Cut Calculator](https://www.omnicalculator.com/construction/birdsmouth-cut)
- [Woodspec Ireland - Cut Roof Detailed Drawings (PDF)](https://www.woodspec.ie/docs/Woodspec%20Final%20-%20Section%20B.pdf)
- [TAFE NSW - Conventional Pitched Roof (PDF)](https://qbis.com.au/wp-content/uploads/2015/08/Convention-Pitched-Roof-tafe-NSW1.pdf-Complete1.pdf)
- [Fine Homebuilding - Hip Roof Framing](https://www.finehomebuilding.com/project-guides/framing/hip-roof-framing-made-easier)
- [Carpentry Compendium - Hip Jack Rafters](https://www.carpentrycompendium.com/hip-jack-rafters)
- [CNC Building Control - Rafter/Joist Timber Sizes](https://cncbuildingcontrol.gov.uk/faqs/size-timbers-need-rafters-joists/)
- [Timber Beam Calculator - UK Rafter Span Tables](https://www.timberbeamcalculator.co.uk/en-gb/span-tables/rafters)
- [Travis Perkins - 47x150mm C24 Timber](https://www.travisperkins.co.uk/treated-timber/47mm-x-150mm-x-4-2m-regularised-treated-sawn-timber-c24/p/206902)
- [LABC Warranty - Roofs Technical Manual](https://info.labcwarranty.co.uk/hubfs/Technical%20Manual%20v10%20Files%20and%20Images/Manual%20Sections/Section%2011%20Roofs.pdf)
- [First In Architecture - Pitched Roof Details](https://www.firstinarchitecture.co.uk/detail-post-pitched-roof-details/)
- [Marley - BS 5534 Code of Practice](https://www.marley.co.uk/britishstandards/bs5534)
- [InterNACHI - Collar Ties vs Rafter Ties](https://www.nachi.org/collar-rafter-ties.htm)
- [UpCodes - Ceiling Joist and Rafter Connections](https://up.codes/s/ceiling-joist-and-rafter-connections)
- [MyBuilder - Birdsmouth Dimensions](https://www.mybuilder.com/questions/v/22715/birdsmouth-dimensions)
- [Right Survey - Rafter Span Tables](https://www.rightsurvey.co.uk/roof-rafters-span-tables-for-surveyors-roof-construction/)
