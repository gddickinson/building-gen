# Engineering Reference Data for Procedural Building Generation

Comprehensive structural engineering values from British/European standards for
generating physically correct buildings at the individual-component level.

Every value includes its source standard, clause, or table number where possible.
Values are in SI units unless otherwise noted.

---

## 1. BRICK MASONRY (BS EN 1996 / Eurocode 6)

### 1.1 Standard UK Brick Dimensions

| Dimension | Metric (mm) | Imperial (in) | Source |
|-----------|-------------|---------------|--------|
| Length | 215 | 8.5 | BS 3921 |
| Width | 102.5 | 4.0 | BS 3921 |
| Height | 65 | 2.5 | BS 3921 |
| Standard mortar joint | 10 | 3/8 | BS EN 1996 |
| **Coordinating size** (with mortar) | 225 x 112.5 x 75 | -- | BS 3921 |

The coordinating size (brick + mortar joint) is what matters for coursing:
- **Course height** = 65 + 10 = **75 mm** (13.33 courses per metre height)
- **Stretcher length** = 215 + 10 = **225 mm** (4.44 stretchers per metre length)

Source: BS 3921:1985, now superseded by BS EN 771-1. Metric brick introduced January 1970.
Imperial equivalent defined by Parliament in 18th century as 8.5 x 4 x 2.5 inches.

### 1.2 Bricks Per Square Metre

| Bond Type | Bricks/m2 (half-brick wall) | Bricks/m2 (one-brick wall) | When Used |
|-----------|----------------------------|---------------------------|-----------|
| **Stretcher bond** | **60** | 120 | Modern cavity walls, partitions |
| **Flemish bond** | -- | **120** | Georgian facades, decorative |
| **English bond** | -- | **120** | Victorian, structural, below DPC |
| **Header bond** | -- | **120** | Curved walls, decorative |

Notes: Flemish bond alternates headers and stretchers in each course. English bond
alternates full courses of headers and stretchers. Stretcher bond shows only
stretchers (half-brick thick wall, 102.5mm).

Source: BS 3921, manufacturer data (Imperial Bricks, Traditional Brick & Stone).

### 1.3 Brick Strength Classes (BS EN 771-1)

| Class | Compressive Strength (MPa / N/mm2) | Typical Use |
|-------|-------------------------------------|-------------|
| 5 | 5 | Internal partitions |
| 7 | 7 | General purpose (sheltered) |
| 10 | 10 | General purpose |
| 15 | 15 | General purpose / facing |
| 20 | 20 | Common brick (typical) |
| 30 | 30 | Facing brick (typical) |
| 40 | 40 | Engineering Class B |
| 50 | 50 | Engineering Class B (high) |
| 70 | 70 | Engineering Class A |
| 100 | 100 | Engineering Class A (high) |

Source: BS EN 771-1, Table NA.1 (normalised compressive strength of unit, fb).

### 1.4 Mortar Types and Strengths

| Designation | Compressive Strength (MPa) | Cement : Lime : Sand | Cement : Sand (no lime) | Typical Use |
|-------------|---------------------------|---------------------|------------------------|-------------|
| **M12** | 12 | 1 : 0-0.25 : 3 | 1 : 3 | Engineering, below DPC |
| **M6** | 6 | 1 : 0.5 : 4-4.5 | 1 : 3-4 | General purpose external |
| **M4** | 4 | 1 : 1 : 5-6 | 1 : 5-6 | General purpose |
| **M2** | 2 | 1 : 2 : 8-9 | 1 : 7-8 | Internal, sheltered, conservation |

**Historical mortars:**
- **Pre-1900 (Georgian/early Victorian):** Pure lime mortar (no Portland cement), ~1-2 MPa
- **1860-1920:** Lime + early Portland cement blends, ~2-4 MPa
- **Post-1920:** Portland cement dominant, 4-12 MPa

Source: BS EN 998-2, UK NA Table NA.2 to BS EN 1996-1-1, Lignacite Design Guidance Section 7.
Portland cement first manufactured 1824, widespread use from ~1860s.

### 1.5 Characteristic Compressive Strength of Masonry (fk)

Calculated per BS EN 1996-1-1, Clause 3.6.1.2:

**fk = K x fb^0.7 x fm^0.3** (MPa)

Where:
- fb = normalised compressive strength of masonry unit (MPa)
- fm = compressive strength of mortar (MPa), capped at min(20, 2*fb)
- K = constant from UK NA Table NA.4

**K values (UK National Annex Table NA.4):**

| Unit Type | Group 1 (solid/perforated) | Group 2 |
|-----------|---------------------------|---------|
| Clay brick | **0.50** | 0.40 |
| Calcium silicate | 0.50 | -- |
| Aggregate concrete | 0.55 | 0.45 |
| AAC | 0.55 | 0.45 |
| Natural stone (dressed) | 0.45 | -- |

**Example fk values (Clay brick Group 1, K=0.50):**

| Brick fb (MPa) | Mortar M2 (fm=2) | Mortar M4 (fm=4) | Mortar M6 (fm=6) | Mortar M12 (fm=12) |
|----------------|-------------------|-------------------|-------------------|--------------------|
| 10 | 2.4 | 3.0 | 3.4 | 4.2 |
| 20 | 3.9 | 4.9 | 5.5 | 6.8 |
| 30 | 5.2 | 6.4 | 7.3 | 9.0 |
| 40 | 6.3 | 7.8 | 8.9 | 10.9 |
| 50 | 7.3 | 9.0 | 10.3 | 12.7 |
| 70 | 9.1 | 11.2 | 12.7 | 15.7 |
| 100 | 11.5 | 14.2 | 16.2 | 20.0 |

Source: BS EN 1996-1-1:2005, Equation 3.1, UK NA Table NA.4.
Calculated values: fk = 0.50 x fb^0.7 x fm^0.3.

### 1.6 Partial Safety Factor for Masonry (gamma_M)

From UK National Annex Table NA.1 to BS EN 1996-1-1:

| Condition | Category I units, designed mortar | Category I units, prescribed mortar | Category II units |
|-----------|----------------------------------|-------------------------------------|-------------------|
| **ULS compression/flexural compression** | **2.7** | **3.0** | **3.5** |
| **ULS flexural tension** | **2.7** | **3.0** | **3.5** |
| **ULS shear** | **2.5** | **2.5** | **2.5** |

**For our generator, use gamma_M = 3.0 as the default** (prescribed mortar, Category I units).

Note: Category I = units with a declared compressive strength with a probability of
failure not exceeding 5%. Category II = all other units. Designed mortar = tested to
achieve specified strength. Prescribed mortar = mixed to specified proportions.

Source: UK NA to BS EN 1996-1-1:2005, Table NA.1.

### 1.7 Slenderness Ratio

| Parameter | Value | Source |
|-----------|-------|--------|
| Maximum slenderness ratio (load-bearing walls) | **27** | UK NA Clause NA.2.15 |
| Maximum slenderness ratio (non-load-bearing) | **30** | UK NA |
| Slenderness ratio = hef / tef | -- | BS EN 1996-1-1, Cl. 5.5.1.3 |

**Effective height (hef):**
- Both edges restrained: 0.75 x h
- One edge restrained (top): 1.0 x h
- One vertical edge restrained: 1.5 x h
- Cantilever / free-standing: 2.0 x h

**Effective thickness (tef):**
- Single-leaf wall: actual thickness
- Cavity wall: ((t1^3 + t2^3) / (t1 + t2))^(1/3) approximately, but typically taken as the greater of the two leaf thicknesses

Source: BS EN 1996-1-1:2005, Clause 5.5.1.2 and 5.5.1.3.

### 1.8 Mortar Joint Thickness

| Joint Type | Standard Thickness | Source |
|------------|-------------------|--------|
| Bed joint (horizontal) | **10 mm** | BS EN 1996 |
| Perpend joint (vertical) | **10 mm** | BS EN 1996 |
| Thin-layer mortar | 1-3 mm | BS EN 1996 |
| Historical lime mortar joints | 10-15 mm | Conservation practice |
| Rubble stone joints | 15-25 mm | Conservation practice |

---

## 2. TIMBER STRUCTURAL DESIGN (BS EN 1995 / Eurocode 5)

### 2.1 Strength Classes (BS EN 338:2016, Table 1)

**Softwood (Coniferous) Classes:**

| Property | Unit | C14 | C16 | C18 | C20 | C22 | C24 | C27 | C30 | TR26 |
|----------|------|-----|-----|-----|-----|-----|-----|-----|-----|------|
| Bending fm,k | MPa | 14 | **16** | 18 | 20 | 22 | **24** | 27 | 30 | 26 |
| Tension parallel ft,0,k | MPa | 7.2 | 8.5 | 10 | 11.5 | 13 | **14.5** | 16.5 | 19 | 15.5 |
| Tension perp ft,90,k | MPa | 0.4 | 0.4 | 0.4 | 0.4 | 0.4 | **0.4** | 0.4 | 0.4 | 0.4 |
| Compression parallel fc,0,k | MPa | 16 | **17** | 18 | 19 | 20 | **21** | 22 | 24 | 22 |
| Compression perp fc,90,k | MPa | 2.0 | 2.2 | 2.2 | 2.3 | 2.4 | **2.5** | 2.5 | 2.7 | 2.5 |
| Shear fv,k | MPa | 3.0 | **3.2** | 3.4 | 3.6 | 3.8 | **4.0** | 4.0 | 4.0 | 4.0 |
| E mean E0,mean | GPa | 7.0 | **8.0** | 9.0 | 9.5 | 10.0 | **11.0** | 11.5 | 12.0 | 11.0 |
| E 5% E0,05 | GPa | 4.7 | 5.4 | 6.0 | 6.4 | 6.7 | **7.4** | 7.7 | 8.0 | 7.4 |
| G mean | GPa | 0.44 | 0.50 | 0.56 | 0.59 | 0.63 | **0.69** | 0.72 | 0.75 | 0.69 |
| Density rho,k | kg/m3 | 290 | **310** | 320 | 330 | 340 | **350** | 360 | 380 | 370 |
| Density rho,mean | kg/m3 | 350 | **370** | 380 | 390 | 410 | **420** | 430 | 460 | 450 |

**Notes on TR26:** TR26 is a UK trade grade for trussed rafters. Not formally in
EN 338 but specified in BS 5268. Properties between C24 and C27. Bending 26 MPa.

Source: BS EN 338:2016, Table 1. TR26 from TDUK/BSI specifications.

**CORRECTIONS TO EXISTING CODE:** The current `properties.py` has:
- C16 density 370 (should be **rho_mean=370** or **rho_k=310**)
- C16 tensile_strength 10.0 (should be **8.5** per EN 338:2016 or 10.0 per older standard)
- C16 shear_strength 1.8 (should be **3.2**)
- C24 density 420 (correct for rho_mean)
- C24 tensile_strength 14.0 (should be **14.5**)
- C24 shear_strength 2.5 (should be **4.0**)
- C24 elastic_modulus 11.0 (correct)

### 2.2 Standard Timber Section Sizes (UK)

Regularised (finished) structural softwood section sizes commonly available:

| Width (mm) | Available Depths (mm) |
|------------|----------------------|
| **38** | 89 (CLS), 140, 184, 235, 285 |
| **47** | 50, 75, 100, 125, 150, 175, 200, 225, 250 |
| **75** | 100, 150, 175, 200, 225, 250 |
| **100** | 100, 150, 200, 250, 300 |

Standard lengths: 2.4m, 2.7m, 3.0m, 3.6m, 4.2m, 4.8m, 5.4m, 6.0m

Source: Timber Development UK, BS EN 336:2013.

### 2.3 Floor Joist Span Tables

**Domestic floor joists, C24, imposed load 1.5 kN/m2, dead load <= 0.5 kN/m2**
**(BS 5268-7.1)**

| Joist Size (mm) | 400mm centres | 450mm centres | 600mm centres |
|-----------------|---------------|---------------|---------------|
| 47 x 100 | 1.72 m | 1.64 m | 1.44 m |
| 47 x 125 | 2.26 m | 2.17 m | 1.95 m |
| 47 x 150 | 2.96 m | 2.83 m | 2.49 m |
| 47 x 175 | 3.47 m | 3.33 m | 2.92 m |
| 47 x 200 | 3.98 m | 3.82 m | 3.36 m |
| 47 x 225 | 4.49 m | 4.32 m | 3.80 m |
| 47 x 250 | 4.97 m | 4.78 m | 4.21 m |
| 75 x 200 | 4.50 m | 4.40 m | 4.08 m |
| 75 x 225 | 5.07 m | 4.94 m | 4.50 m |

**Domestic floor joists, C16, imposed load 1.5 kN/m2, dead load <= 0.5 kN/m2**
**(BS 5268-7.1)**

| Joist Size (mm) | 400mm centres | 450mm centres | 600mm centres |
|-----------------|---------------|---------------|---------------|
| 47 x 100 | 1.49 m | 1.42 m | 1.24 m |
| 47 x 125 | 1.97 m | 1.88 m | 1.67 m |
| 47 x 150 | 2.53 m | 2.42 m | 2.13 m |
| 47 x 175 | 2.96 m | 2.83 m | 2.49 m |
| 47 x 200 | 3.39 m | 3.25 m | 2.86 m |
| 47 x 225 | 3.82 m | 3.67 m | 3.23 m |
| 47 x 250 | 4.23 m | 4.06 m | 3.57 m |

Source: BS 5268-7.1:1990, Timber Beam Calculator (timberbeamcalculator.co.uk),
BSW Timber Span Tables 2025, TRADA span tables.

### 2.4 Modification Factors (BS EN 1995-1-1)

**kmod (duration of load and service class):**

| Load Duration | Service Class 1 (dry interior) | Service Class 2 (sheltered) | Service Class 3 (exposed) |
|---------------|-------------------------------|-----------------------------|-----------------------------|
| Permanent (>10 yr) | 0.60 | 0.60 | 0.50 |
| Long-term (6mo-10yr) | 0.70 | 0.70 | 0.55 |
| Medium-term (1wk-6mo) | 0.80 | 0.80 | 0.65 |
| Short-term (<1wk) | 0.90 | 0.90 | 0.70 |
| Instantaneous | 1.10 | 1.10 | 0.90 |

Source: BS EN 1995-1-1:2004, Table 3.1.

**Partial factor for timber (gamma_M):**
- Solid timber: **1.3**
- Glulam: 1.25
- LVL, plywood, OSB: 1.2
- Connections: 1.3
- Accidental combinations: 1.0

Source: BS EN 1995-1-1:2004, Table 2.3.

### 2.5 Deflection Limits

| Element | Limit | Source |
|---------|-------|--------|
| Floor joists (total deflection) | **span / 250** | BS EN 1995-1-1, Table 7.2 |
| Floor joists (live load only) | span / 300 | BS EN 1995-1-1, Table 7.2 |
| Roof rafters (total) | **span / 150** | BS EN 1995-1-1, Table 7.2 |
| Roof rafters (live only) | span / 200 | BS EN 1995-1-1, Table 7.2 |
| Cantilevers | span / 125 | Common practice |

### 2.6 Joist Notching and Drilling Rules (UK Building Regulations)

**Notches (top of joist only):**
- Position: between 0.07 and 0.25 of span from support
- Maximum depth: 0.125 x joist depth
- Absolute maximum depth: 35 mm
- Must be in the top edge only

**Holes (on neutral axis / centreline only):**
- Position: between 0.25 and 0.4 of span from support
- Maximum diameter: 0.25 x joist depth
- Minimum 3 diameters between adjacent holes
- Minimum 100 mm from any notch
- Must be drilled on the centreline (neutral axis)

Source: NHBC Standards 6.4.18, Approved Document A Section 2E,
Hertsmere Building Control TN No. 22. Applies to solid timber joists up to 250mm depth.

---

## 3. ROOF CONSTRUCTION

### 3.1 Traditional Cut Roof Components

| Component | Typical Size (mm) | Material | Notes |
|-----------|-------------------|----------|-------|
| Common rafter | 47 x 100 to 47 x 150 | C24 softwood | Size depends on span, pitch, loading |
| Ridge board | 38 x 175 to 38 x 200 | C16/C24 softwood | Depth >= cut depth of rafter |
| Purlin | 75 x 150 to 75 x 225 | C24 softwood | Span depends on loading |
| Ceiling joist | 47 x 100 to 47 x 150 | C16/C24 | Acts as tie at eaves level |
| Hip rafter | 47 x 175 to 47 x 225 | C24 | Deeper than common rafters |
| Valley rafter | 47 x 175 to 47 x 225 | C24 | Same as hip |
| Wall plate | 100 x 75 | C16/C24 | Bedded on mortar on wall top |
| Collar tie | 47 x 100 to 47 x 150 | C16 | Prevents rafter spread |
| Hangers | 47 x 100 | C16 | Supports ceiling joists from purlins |
| Binder | 47 x 100 | C16 | Runs along length, supports ceiling joists |

Source: TRADA, BM TRADA Technology, Timber Frame construction guides.

### 3.2 Rafter Span Tables (C24, pitched roof, dead load <= 1.0 kN/m2)

**Roof slope 30-45 degrees (BS 5268-7.5):**

| Rafter Size (mm) | 400mm centres | 600mm centres |
|-------------------|---------------|---------------|
| 47 x 100 | 2.35 m | 2.07 m |
| 47 x 125 | 2.93 m | 2.59 m |
| 47 x 150 | 3.52 m | 3.10 m |

**Roof slope 22.5-30 degrees:**

| Rafter Size (mm) | 400mm centres | 600mm centres |
|-------------------|---------------|---------------|
| 47 x 100 | 2.21 m | 1.94 m |
| 47 x 125 | 2.76 m | 2.43 m |
| 47 x 150 | 3.31 m | 2.92 m |

Source: BS 5268-7.5:1990, Timber Beam Calculator.

### 3.3 Purlin Spacing and Sizing

| Rafter span | Purlin required | Purlin spacing |
|-------------|----------------|----------------|
| Up to 2.5 m | No purlin needed | -- |
| 2.5 - 4.5 m | One purlin per slope | ~1.5-1.8 m from wall plate |
| 4.5 - 6.0 m | Two purlins per slope | ~1.2-1.5 m apart |

Purlin sizing rule of thumb: depth (mm) = span (mm) / 20 for softwood purlins.
Typical purlin spans between supports (truss or load-bearing wall): 2.0 - 3.0 m.

Source: TRADA, common practice guidance.

### 3.4 Roof Covering Weights

| Covering | Weight (kg/m2 on slope) | Dead Load (kN/m2 on slope) | Tiles/slates per m2 |
|----------|------------------------|----------------------------|---------------------|
| Plain clay tile (265x165mm, 100mm gauge) | 64 | **0.63** | 60 |
| Plain clay tile (265x165mm, 115mm gauge) | 56 | **0.55** | -- |
| Plain concrete tile (100mm gauge) | 74 | **0.73** | 60 |
| Concrete interlocking tile | 44-50 | **0.43-0.49** | ~10 |
| Natural slate 500x250mm | 37 | **0.36** | -- |
| Natural slate 600x300mm | 35-40 | **0.35-0.39** | -- |
| Welsh slate (thicker) | 40-50 | **0.39-0.49** | -- |
| Thatch (reed) | 30-35 | **0.29-0.34** | -- |
| Lead sheet (Code 5) | 25.4 | **0.25** | -- |

Source: Maguire Brothers weight loading tables, Wienerberger product data,
Cupa Pizarras, BS EN 12588 (lead).

### 3.5 Roof Dead Loads (complete, kN/m2 on slope)

| Component | Covering + battens | Felt/membrane | Rafters | Total dead load |
|-----------|-------------------|---------------|---------|-----------------|
| Slate on timber | 0.40 | 0.02 | 0.10-0.15 | **0.52-0.57** |
| Clay plain tile on timber | 0.65 | 0.02 | 0.10-0.15 | **0.77-0.82** |
| Concrete interlocking | 0.50 | 0.02 | 0.10-0.15 | **0.62-0.67** |
| Thatch | 0.35 | -- | 0.10-0.15 | **0.45-0.50** |
| Lead on boarding | 0.25 | -- | 0.20 (boards) | **0.45-0.50** |

**CORRECTIONS TO EXISTING CODE:** `loads.py` has:
- "slate_on_timber": 0.8 -- should be approximately **0.55 on slope** (0.8 is on plan for ~35deg pitch, which is correct if using plan area)
- "clay_tile_on_timber": 0.7 -- should be approximately **0.80 on slope** or 0.7 is reasonable on plan
- Values are roughly correct if interpreted as on-plan rather than on-slope

### 3.6 Batten Sizes and Spacing

| Covering Type | Batten Size (mm) | Gauge (spacing) | Source |
|---------------|-----------------|-----------------|--------|
| Plain clay tile | 38 x 25 | **100 mm** (max for double lap) | BS 5534 |
| Concrete interlocking tile | 38 x 25 or 50 x 25 | 340-345 mm (varies by tile) | BS 5534 |
| Natural slate (500x250mm, 75mm lap) | 50 x 25 | **(500-75)/2 = 212 mm** | BS 5534, BS 8000 Pt 6 |
| Natural slate (600x300mm, 75mm lap) | 50 x 25 | **(600-75)/2 = 262 mm** | BS 5534, BS 8000 Pt 6 |
| Natural slate (400x200mm, 75mm lap) | 50 x 25 | **(400-75)/2 = 162 mm** | BS 5534 |

Batten gauge formula for slates: **(slate length - headlap) / 2**
Standard headlap: 75 mm minimum, 80-110 mm typical.

Source: BS 5534:2014, SIGA Natural Slate Knowledge Base, BS 8000-6:2013.

### 3.7 Natural Slate Sizes (UK Standard)

| Size Name | Dimensions (mm) | Weight each (approx) | Common Region |
|-----------|-----------------|---------------------|---------------|
| Countess | **500 x 250** | 1.9 kg | Southern England (most common) |
| Duchess | **600 x 300** | 2.7 kg | Grand buildings |
| Ladies | **400 x 200** | 1.1 kg | Scotland, Northern England |
| Small Ladies | **350 x 175** | 0.8 kg | Cottages |
| Queens | **450 x 225** | 1.5 kg | General |
| Viscountess | **500 x 300** | 2.3 kg | Large buildings |

Standard thickness: **4-7 mm** (sorted by thickness, thickest at eaves).

Source: Welsh Slate, Cupa Pizarras, BS 680.

### 3.8 Lead Flashing

| Code | Thickness (mm) | Weight (kg/m2) | Typical Use |
|------|----------------|----------------|-------------|
| Code 3 | 1.32 | 14.97 | Soakers, small flashings |
| Code 4 | 1.80 | 20.41 | Chimney flashings (most common) |
| Code 5 | 2.24 | 25.40 | Valleys, aprons, bay roofs |
| Code 6 | 2.65 | 30.05 | Flat roofs, parapets |
| Code 7 | 3.15 | 35.72 | Heavy-duty flat roofs |
| Code 8 | 3.55 | 40.26 | Specialist applications |

Source: BS EN 12588:2006, Lead Sheet Association, Ashbrook Roofing.

---

## 4. FLOOR CONSTRUCTION

### 4.1 Joist Bearing Requirements

| Requirement | Value | Source |
|-------------|-------|--------|
| Minimum bearing on masonry wall | **90 mm** | BS EN 1995, NHBC 6.4 |
| Minimum bearing on steel beam | **50 mm** | NHBC 6.4 |
| Minimum bearing on timber beam | **50 mm** | NHBC 6.4 |
| Joist spacing (standard centres) | **400, 450, 600 mm** | BS 5268-7.1 |

### 4.2 Strutting / Bridging Between Joists

| Span | Requirement | Source |
|------|-------------|--------|
| Up to 2.5 m | No strutting required | NHBC 6.4 |
| 2.5 - 4.5 m | **One row of strutting at mid-span** | NHBC 6.4.13 |
| Over 4.5 m | **Two rows of strutting at 1/3 points** | NHBC 6.4.13 |

Strutting types:
- **Herringbone strutting:** 38 x 38 mm or 50 x 50 mm timber, or galvanised steel
- **Solid strutting:** Same depth as joists, minimum 38 mm thick
- **Proprietary metal:** Galvanised steel herringbone struts

Source: NHBC Standards Chapter 6.4, Building Regulations Approved Document A.

### 4.3 Floorboard Sizes

| Type | Nominal Size (mm) | Finished Size (mm) | Notes |
|------|-------------------|---------------------|-------|
| Softwood T&G | 25 x 150 | 20-21 x 144-145 | Traditional, Victorian/Georgian |
| Softwood T&G | 25 x 125 | 20-21 x 119-120 | Common for older buildings |
| Softwood T&G | 22 x 125 | 18-19 x 119 | Modern |
| T&G chipboard (P5) | 22 x 2400 x 600 | 22 x 2400 x 600 | Moisture resistant |
| T&G chipboard (P5) | 18 x 2400 x 600 | 18 x 2400 x 600 | Light domestic |

Source: Timber merchants (Jewson, Wickes, Howarth), BS EN 312 (chipboard).

### 4.4 Ceiling Construction

**Lath and plaster (Georgian / Victorian):**
- Lath size: 25 mm wide x 6 mm thick x 1200 mm long
- Gap between laths: ~6 mm (1/4 inch)
- Plaster thickness: ~25 mm (3 coats: scratch, float, finish)
- Plaster composition: lime + sand + horsehair (reinforcement)
- Dead load: **~0.50 kN/m2**

**Plasterboard (modern):**
- Standard thickness: 9.5 mm or 12.5 mm
- Sheet size: 2400 x 1200 mm
- Skim coat: 3-5 mm finish plaster
- Dead load: **~0.15-0.20 kN/m2**

Source: LABC guidance, Adaptavate lath and plaster guide, Wikipedia.

### 4.5 Floor Dead Loads

| Construction | Dead Load (kN/m2) | Source |
|--------------|-------------------|--------|
| Timber joists + softwood boards | **0.30-0.40** | Calculated from section weights |
| Timber joists + boards + lath/plaster ceiling | **0.70-0.90** | Standard reference |
| Timber joists + chipboard + plasterboard | **0.40-0.50** | Modern construction |
| 150mm RC slab | **3.60** | 24 kN/m3 x 0.15 |
| 200mm RC slab | **4.80** | 24 kN/m3 x 0.20 |
| Stone flag floor on joists | **1.00-1.20** | Historical construction |

Source: BS EN 1991-1-1, IStructE Manual.

### 4.6 Sound Insulation (Between Floors)

Approved Document E requirements:
- Airborne sound insulation: minimum **43 dB** (DnT,w) between dwellings
- Impact sound insulation: maximum **64 dB** (L'nT,w) between dwellings
- For conversions: 43 dB airborne, 64 dB impact

Source: Building Regulations Approved Document E (2015).

---

## 5. FOUNDATION DESIGN

### 5.1 Minimum Foundation Depths

| Condition | Minimum Depth | Source |
|-----------|---------------|--------|
| General (non-clay soils) | **0.45 m** (to avoid frost) | Approved Document A, 2E4 |
| Clay - low shrinkage | **0.75 m** | Approved Document A, NHBC 4.2 |
| Clay - medium shrinkage | **0.90 m** | Approved Document A, NHBC 4.2 |
| Clay - high shrinkage | **1.00 m** | Approved Document A, NHBC 4.2 |
| Near trees (shrinkable clay) | **Up to 3.0+ m** | NHBC Chapter 4.2 |
| Rock | On surface (if adequate bearing) | Approved Document A |

Source: Building Regulations Approved Document A (2004, amended 2013), Section 2E,
NHBC Standards Chapter 4.2.

### 5.2 Strip Foundation Widths (Approved Document A, Table 10)

Minimum width of strip foundations for various total wall loads and soil conditions:

| Soil Type / Condition | Bearing Capacity (kN/m2) | 20 kN/m | 30 kN/m | 40 kN/m | 50 kN/m | 60 kN/m | 70 kN/m |
|----------------------|--------------------------|---------|---------|---------|---------|---------|---------|
| I - Rock | -- | 300 | 300 | 300 | 300 | 300 | 300 |
| II - Gravel, sand (compact) | >=300 | 250 | 300 | 400 | 500 | 600 | 650 |
| III - Clay, sandy clay (stiff) | 150-300 | 250 | 350 | 450 | 600 | 750 | 850 |
| IV - Clay, sandy clay (firm) | 75-150 | 300 | 450 | 600 | 750 | 850 | * |
| V - Sand, silty sand (loose) | <75 | 400 | 600 | * | * | * | * |
| VI - Soft silt, clay, sandy clay | <75 | 450 | 650 | * | * | * | * |

Widths in mm. * = requires engineer design.

Source: Approved Document A, Table 10 (2E12).

### 5.3 Soil Bearing Capacities

| Soil Type | Presumed Bearing Capacity (kN/m2) | Source |
|-----------|-----------------------------------|--------|
| Strong igneous rock | 10,000+ | BS 8004:1986 |
| Strong limestone/sandstone | 2,000-4,000 | BS 8004:1986 |
| Weak sandstone | 450-900 | BS 8004:1986 |
| Chalk (weathered) | 200-600 | BS 8004:1986 |
| Dense gravel / dense sand | **300-600** | BS 8004:1986 |
| Medium dense gravel/sand | **100-300** | BS 8004:1986 |
| Loose gravel/sand | **<100** | BS 8004:1986 |
| Stiff clay | **150-300** | BS 8004:1986 |
| Firm clay | **75-150** | BS 8004:1986 |
| Soft clay | **<75** | BS 8004:1986 |
| Very soft clay / silt | **<50** | BS 8004:1986 |
| Peat / organic | Not suitable | -- |

Source: BS 8004:1986 Table 1, now BS EN 1997 (Eurocode 7).

### 5.4 Concrete Foundation Mix

| Application | Mix Designation | Cement (kg/m3) | Strength Class | Source |
|-------------|-----------------|----------------|----------------|--------|
| Strip foundations (general) | GEN 1 | ~220 | C12/15 | BS 8500-2 |
| Strip foundations (sulfate conditions) | FND 2 / FND 3 | 280-340 | C25/30 | BS 8500-2 |
| Trench fill | GEN 1 to GEN 3 | 220-300 | C12/15 to C20/25 | BS 8500-2 |
| Minimum for foundations | GEN 1 | -- | Not less than C12/15 | Approved Doc A |

Source: BS 8500-2:2015, Building Regulations Approved Document A.

### 5.5 DPC (Damp Proof Course)

| Requirement | Value | Source |
|-------------|-------|--------|
| Minimum height above ground level | **150 mm** | Approved Document C, Cl. 5.5 |
| DPC width | Full wall width | Approved Document C |
| Cavity tray | Required at all interruptions | Approved Document C |

**Historical DPC Materials:**
- Pre-1875: None (no DPC requirement) or slate/lead
- 1875-1920: Slate DPC common (2 courses of slate in mortar)
- 1920-1970: Bitumen felt / bitumen-coated hessian
- Post-1970: Polyethylene sheet (most common modern material)

Source: Building Regulations Approved Document C (2004), NHBC Standards 5.1.19.

---

## 6. WINDOW AND DOOR CONSTRUCTION

### 6.1 Georgian Sash Window Components

**Box frame (outer frame) dimensions:**

| Component | Width/Depth (mm) | Notes |
|-----------|-----------------|-------|
| Box frame depth (front to back) | **130-165** | Contains weights and pulleys |
| Pulley stile (inner lining) | 25-30 thick | Vertical member, pulley mortised into top |
| Outer lining | 22-25 thick | Outer face of box frame |
| Parting bead | **8 x 20** (approx) | Separates inner/outer sash channels |
| Staff bead | **12 x 20** (approx) | Holds lower sash in place, pinned to frame |
| Parting slip | 8 x 25 | Separates weights in box |

**Sash dimensions:**

| Component | Size (mm) | Notes |
|-----------|----------|-------|
| Sash stile width | **44-50** | Vertical side members of each sash |
| Top rail | 44-50 | Horizontal top member |
| Bottom rail | 60-75 | Wider for strength, houses fastener |
| Meeting rails | 38-44 each | Where upper and lower sash meet |
| Sash thickness | **35-44** | Overall sash depth |

**Glazing bars:**

| Period | Width (mm) | Section Depth (mm) | Notes |
|--------|-----------|-------------------|-------|
| Early Georgian (1720-1770) | **25-32** | 44 | Thick, bold profile |
| Late Georgian (1770-1840) | **18-22** | 44 | Thinner, more refined |
| Victorian (post-1840) | **15-20** | 44 | Thinnest, plate glass era |
| Applied (non-structural, modern) | 22 | -- | Stuck onto glass surface |

Source: Georgian Group (Brooking article on sash windows), Sash Window Specialist,
Timber Sash Co specifications, Chiltern Timber profiles.

### 6.2 Glass Thickness by Period

| Period | Glass Type | Thickness (mm) | Max Pane Size | Notes |
|--------|-----------|----------------|---------------|-------|
| Pre-1700 | Crown glass | **1.0-2.0** | ~250 x 200 mm | Spun disc, uneven thickness |
| 1700-1845 | Crown glass (refined) | **1.0-1.5** | ~300 x 250 mm | Bull's eye at centre |
| 1830-1900 | Cylinder glass | **1.5-2.5** | ~500 x 400 mm | Blown cylinder, flattened |
| 1840-1950 | Plate glass (polished) | **4-6** (1/4 inch) | Large sheets | Ground and polished, expensive |
| Post-1959 | Float glass | **3-6** | Very large | Pilkington process, optically perfect |

For our generator:
- Georgian 6-over-6 windows: **1.5 mm** crown glass panes (~230 x 180 mm each)
- Victorian 2-over-2 windows: **3-4 mm** cylinder/plate glass (~400 x 500 mm each)
- Modern: **4 mm** float glass standard

Source: Histoglass, Building Conservation (Ben Sinclair), Sash Window Specialist,
Wikipedia (Crown glass).

### 6.3 Sash Weights and Counterbalance

Each sash is counterbalanced by cast iron or lead weights connected by sash cord
(later sash chain) running over a brass pulley.

Weight of each sash weight = weight of the sash it counterbalances.
Typical sash weight: **3-8 kg** per weight (2 per sash, 4 per window).

### 6.4 Door Construction

**Georgian 6-panel door (external):**

| Component | Width (mm) | Height/Length (mm) | Thickness (mm) | Material |
|-----------|-----------|-------------------|----------------|----------|
| Stile (2 vertical sides) | **110-120** | Full door height | 44-50 | Hardwood or softwood |
| Top rail | **110-120** | Door width | 44-50 | Same |
| Bottom rail | **180-220** | Door width | 44-50 | Wider for strength |
| Lock rail (middle) | **200-220** | Door width | 44-50 | Houses lock mortise |
| Frieze rail | **110-120** | Door width | 44-50 | Between upper panels |
| Muntin (vertical divider) | **90-110** | Between rails | 44-50 | Divides panels |
| Panels | -- | -- | 12-18 | Raised and fielded |

**Standard door sizes:**

| Door Type | Width (mm) | Height (mm) | Thickness (mm) |
|-----------|-----------|-------------|----------------|
| Georgian front door (6-panel) | **910-1070** | **2130-2440** | 44-50 |
| Victorian front door (4-panel) | **840-910** | **2030-2130** | 44 |
| Internal door (modern standard) | **762** | **1981** | 35 |
| Internal door (wider) | **838** | **1981** | 35 |
| Service/back door | **762** | **1981** | 44 |

**Fanlight:**
- Semi-circular or semi-elliptical glazed panel above Georgian front door
- Width: matches door width (910-1070 mm)
- Height: typically 400-600 mm (radius of ~450-550 mm)
- Glazing bars: radial pattern, 15-20 mm wide

Source: Cotswood Doors, Georgian Group, Brent Hull millwork.

### 6.5 Lintel Requirements

| Lintel Type | Max Span | Depth | Material | Period |
|-------------|----------|-------|----------|--------|
| Timber lintel | **1.2-2.0 m** | 100-150 mm | Oak (Georgian), softwood | Pre-1850 |
| Stone lintel | **1.0-2.0 m** | 150-225 mm | Limestone, sandstone | All periods |
| Brick flat arch (soldier course) | **0.9-1.2 m** | 65-215 mm | Hard brick | Georgian, Victorian |
| Brick segmental arch | **1.5-3.0 m** | 215-325 mm | Brick | Georgian, Victorian |
| Brick gauged arch | **1.0-1.8 m** | 215 mm | Rubbed/gauged brick | Georgian |
| Cast iron lintel | **2.0-3.5 m** | 75-150 mm | Cast iron | Victorian (post-1840) |
| Steel lintel | **1.0-4.5 m** | 100-225 mm | Galvanised steel | Post-1970 |
| Precast concrete | **1.0-3.0 m** | 100-225 mm | Reinforced concrete | Post-1920 |

Minimum bearing each side: **150 mm** on masonry.

Source: Historical construction guides, NHBC Standards Chapter 6.1.

---

## 7. CAVITY WALL CONSTRUCTION

### 7.1 Historical Introduction

| Period | Wall Type | Notes |
|--------|----------|-------|
| Medieval - 1920s | **Solid walls** | One-brick (215mm) to two-brick (450mm) thick |
| 1920s - 1940s | **Early cavity walls** | 50mm cavity, two half-brick (102.5mm) leaves |
| 1940s - 1980s | **Standard cavity** | 50-75mm cavity, wire butterfly ties |
| 1980s - present | **Insulated cavity** | 75-150mm cavity, filled with insulation |

Source: Action Wall Ties, London Damp Company, Designing Buildings Wiki.

### 7.2 Standard Cavity Wall Construction

| Component | Dimension (mm) | Notes |
|-----------|----------------|-------|
| Outer leaf | **102.5** (half brick) | Facing brick or render |
| Inner leaf | **100** (blockwork) or **102.5** (brick) | Load-bearing |
| **Cavity width (standard)** | **50** (early), **75** (standard), **100-150** (modern insulated) | |
| **Total wall thickness** | **255-350** (typical), up to 400+ (modern) | |
| DPC | Full width of each leaf + cavity tray | 150mm above ground |

### 7.3 Wall Tie Spacing

| Requirement | Value | Source |
|-------------|-------|--------|
| Horizontal spacing | **900 mm** max | BS EN 1996-2, PD 6697 |
| Vertical spacing | **450 mm** max | BS EN 1996-2, PD 6697 |
| Pattern | **Staggered** (not aligned) | BS EN 1996-2 |
| Density | Minimum **2.5 ties/m2** | BS EN 1996-2 |
| Around openings | **300 mm** from edge, **225 mm** vertical spacing | PD 6697 |
| At unbonded edges | **300 mm** max vertical spacing | PD 6697 |

**Wall tie types:**
- **Butterfly wire ties** (pre-1981): Galvanised mild steel wire, prone to corrosion
- **Double triangle ties** (pre-1981): Galvanised mild steel wire
- **Vertical twist ties** (post-1981): Stainless steel, most common modern
- **Helical ties** (remedial): Stainless steel, drilled into masonry

Source: BS EN 845-1:2013, PD 6697:2010, NHBC Standards Chapter 6.1,
Target Fixings wall tie history.

### 7.4 Weep Holes

- Spacing: **900 mm** centres (every 4th perpend on stretcher bond)
- Position: immediately above cavity trays, DPC, lintels
- Open perpend joints (no mortar in vertical joint)
- Purpose: drain moisture from cavity

Source: BS EN 1996-2, PD 6697:2010.

---

## 8. LOADS AND FORCES

### 8.1 Imposed Loads (BS EN 1991-1-1 + UK National Annex)

| Category | Description | qk (kN/m2) | Qk (kN point load) | Source |
|----------|-------------|------------|---------------------|--------|
| **A1** | Residential - floors | **1.5** | 2.0 | UK NA Table NA.3 |
| **A2** | Residential - stairs | **2.0** | 2.0 | UK NA Table NA.3 |
| **A3** | Residential - balconies | **2.5** | 2.0 | UK NA Table NA.3 |
| **B1** | Office - general | **2.5** | 2.7 | UK NA Table NA.3 |
| **B2** | Office - at or below ground | **3.0** | 2.7 | UK NA Table NA.3 |
| **C1** | Assembly - tables (restaurants, cafes) | **2.0** | 3.0 | UK NA Table NA.3 |
| **C2** | Assembly - fixed seats (churches, theatres) | **4.0** | 3.6 | UK NA Table NA.3 |
| **C3** | Assembly - no obstacles (museums, exhibition) | **4.0** | 4.5 | UK NA Table NA.3 |
| **C4** | Assembly - physical activities (dance halls) | **5.0** | 3.6 | UK NA Table NA.3 |
| **C5** | Assembly - crowds (concert halls, terraces) | **5.0** | 4.5 | UK NA Table NA.3 |
| **D1** | Shopping - retail | **4.0** | 3.6 | UK NA Table NA.3 |
| **D2** | Shopping - department stores | **4.0** | 3.6 | UK NA Table NA.3 |
| **E1** | Storage / industrial | **7.5** | 7.0 | UK NA Table NA.3 |
| **F** | Traffic - vehicles <=30kN | **2.5** | 20.0 | UK NA Table NA.3 |
| **H** | Roofs - not accessible (maintenance only) | **0.6** | 0.9 | UK NA Table NA.6 |
| -- | Roofs - no access | **0.4** | -- | Practice |

**CORRECTIONS TO EXISTING CODE:** `loads.py` IMPOSED_LOADS needs these updates:
- "residential": 1.5 -- correct
- "residential_stairs": 2.0 -- correct
- "office": 2.5 -- correct
- "congregation": 4.0 -- correct (C2/C3)
- "shopping": 4.0 -- correct
- "storage": 7.5 -- correct
- "roof_access": 0.6 -- correct
- "roof_no_access": 0.4 -- acceptable simplification
- "balcony": 2.5 -- correct
- "garage": 2.5 -- correct

Source: BS EN 1991-1-1:2002, UK National Annex Tables NA.2-NA.7.

### 8.2 Load Combination Factors (ULS and SLS)

**Ultimate Limit State (ULS) - STR/GEO:**

| Combination | Expression |
|-------------|-----------|
| **Primary** (Exp. 6.10) | **1.35 Gk + 1.5 Qk,1 + 1.5 * sum(psi_0,i * Qk,i)** |
| **Alternative a** (Exp. 6.10a) | 1.35 Gk + 1.5 * psi_0,1 * Qk,1 |
| **Alternative b** (Exp. 6.10b) | 1.25 Gk + 1.5 Qk,1 |
| **Favourable permanent** | 1.0 Gk (when permanent load is beneficial) |

**Combination factors (psi):**

| Action | psi_0 | psi_1 | psi_2 |
|--------|-------|-------|-------|
| Residential (Cat A) | **0.7** | 0.5 | 0.3 |
| Office (Cat B) | **0.7** | 0.5 | 0.3 |
| Congregation (Cat C) | **0.7** | 0.7 | 0.6 |
| Shopping (Cat D) | **0.7** | 0.7 | 0.6 |
| Storage (Cat E) | **1.0** | 0.9 | 0.8 |
| Wind | **0.5** | 0.2 | 0.0 |
| Snow (altitude <= 1000m) | **0.5** | 0.2 | 0.0 |

**Serviceability Limit State (SLS):**

| Combination | Expression |
|-------------|-----------|
| Characteristic | Gk + Qk,1 + sum(psi_0,i * Qk,i) |
| Frequent | Gk + psi_1,1 * Qk,1 + sum(psi_2,i * Qk,i) |
| Quasi-permanent | Gk + sum(psi_2,i * Qk,i) |

Source: BS EN 1990:2002, UK National Annex, Tables NA.A1.1 and NA.A1.2(B).

### 8.3 Partial Safety Factors for Actions

| Factor | Permanent (G) unfavourable | Permanent (G) favourable | Variable (Q) unfavourable | Variable (Q) favourable |
|--------|---------------------------|--------------------------|--------------------------|------------------------|
| **gamma** | **1.35** | **1.0** | **1.5** | **0.0** |

Source: BS EN 1990:2002, Table A1.2(A).

### 8.4 Wind Loading (Simplified, BS EN 1991-1-4)

Simplified procedure for low-rise buildings:

**Basic wind velocity:** vb = cdir x cseason x vb,0

UK fundamental basic wind velocity (vb,0) from map: **21-30 m/s** depending on location.
- London area: ~22 m/s
- Scottish Highlands: ~28-30 m/s
- West coast: ~25-27 m/s

**Peak velocity pressure (simplified):** qp(z) depends on height, terrain, orography.
Typical values for low-rise residential (z < 10m):
- Sheltered suburban: **0.4-0.6 kN/m2**
- Open country: **0.6-0.9 kN/m2**
- Exposed coastal: **0.9-1.3 kN/m2**

Source: BS EN 1991-1-4:2005 + UK NA, Figure NA.1 (wind speed map).

### 8.5 Snow Loading (BS EN 1991-1-3)

**UK characteristic ground snow loads (sk):**

| Location | sk (kN/m2) | Notes |
|----------|-----------|-------|
| South England (below 100m altitude) | **0.40-0.50** | London, Bristol |
| Midlands | **0.50-0.60** | Birmingham |
| North England | **0.50-0.70** | Manchester, Leeds |
| Scotland (lowlands) | **0.55-0.70** | Edinburgh, Glasgow |
| Scotland (highlands, >300m) | **0.70-1.50+** | Altitude dependent |

**Snow load on roof:** s = mu_i x Ce x Ct x sk

Where:
- mu_i = shape coefficient (0.8 for pitched roof 0-30 deg, reduces for steeper)
- Ce = exposure coefficient = 1.0 (UK)
- Ct = thermal coefficient = 1.0 (UK)

For a typical 35-degree pitched roof in London: s = 0.8 x 1.0 x 1.0 x 0.5 = **0.40 kN/m2**

Source: BS EN 1991-1-3:2003, UK NA Figure NA.1 (snow map), Equation NA.1.

---

## 9. HISTORICAL CONSTRUCTION DIFFERENCES

### 9.1 Construction Methods by Period

| Feature | Medieval (pre-1600) | Georgian (1714-1837) | Victorian (1837-1901) | Edwardian/Modern |
|---------|--------------------|--------------------|--------------------|--------------------|
| **Wall material** | Rubble stone, timber frame | Handmade brick, ashlar stone | Machine-made brick | Cavity wall, brick+block |
| **Wall thickness** | 450-900 mm (solid) | 225-350 mm (solid, 1-1.5 brick) | 225-350 mm (solid) | 255-350 mm (cavity) |
| **Mortar** | Lime putty, earth | **Lime mortar** (1-2 MPa) | Lime + **Portland cement** (2-6 MPa) | Portland cement (4-12 MPa) |
| **DPC** | None | None (or slate from ~1800) | Slate, bitumen (from ~1875) | Polyethylene sheet |
| **Glass** | Leaded lights, horn | **Crown glass** (1-1.5mm) | **Plate/cylinder glass** (3-6mm) | Float glass (4mm+) |
| **Lintels** | Timber, stone | **Timber** (oak), stone, brick arch | **Stone**, cast iron, brick arch | Steel, precast concrete |
| **Floor joists** | Oak, irregular | **Oak or softwood**, irregular | **Softwood**, regular | C16/C24 regularised |
| **Roof covering** | Thatch, stone slabs | **Welsh slate**, clay tile | **Welsh slate**, clay tile | Concrete tile, slate |
| **Windows** | Casement (leaded) | **6-over-6 sash** (box frame) | **2-over-2 sash**, bay windows | Casement, PVCu |
| **Nails** | Hand-forged iron | **Cut nails** (machine from ~1790) | **Wire nails** (from ~1860) | Wire nails |
| **Ceiling** | Open timber, or plaster | **Lath and plaster** (lime) | **Lath and plaster** (lime+gypsum) | Plasterboard |

### 9.2 Key Dates for Material Availability

| Material / Technology | First Available | Widespread Use |
|----------------------|----------------|----------------|
| Crown glass | ~1620 in England | 1700-1845 |
| Cylinder (broad) glass | ~1830 | 1845-1900 |
| Plate glass (polished) | ~1773 (cast plate) | 1840-1959 |
| Float glass | 1959 (Pilkington) | 1960-present |
| Portland cement | 1824 (patented) | **~1860 onwards** |
| Machine-made bricks | ~1850 | **~1870 onwards** |
| Cast iron structural | ~1780 | 1790-1900 |
| Wrought iron structural | ~1820 | 1840-1900 |
| Structural steel | ~1880 (Bessemer) | 1890-present |
| Wire nails | ~1860 | 1880-present |
| DPC (slate) | ~1800 | 1830-1920 |
| DPC (bitumen felt) | ~1900 | 1920-1970 |
| DPC (polyethylene) | ~1960 | 1970-present |
| Plasterboard | ~1894 (invented) | 1940s-present |
| Cavity wall construction | ~1900 (experiments) | **1920s onwards** |
| Roof felt / sarking | ~1920 | 1940s-present |

Source: Building Conservation articles, Historic England, Wikipedia,
The Yorkshire Lime Company, Mortar (masonry) Wikipedia article.

### 9.3 Brick Sizes by Period

| Period | Approximate Size (mm) | Notes |
|--------|----------------------|-------|
| Tudor (1500-1600) | 230 x 115 x 50 | Thin, wide |
| Stuart (1600-1714) | 225 x 108 x 60 | Variable |
| Georgian (1714-1837) | 225 x 108 x 65 | Parliamentary standard (1776) |
| Victorian (1837-1901) | 225 x 108 x 75 | Slightly taller (some regions) |
| Modern metric (1970+) | **215 x 102.5 x 65** | BS 3921 standard |

Source: Scottish Brick History, Imperial Bricks guidance, BS 3921:1985.

---

## 10. PLUMBING AND SERVICES (STRUCTURAL IMPACT)

### 10.1 Chimney Construction

**Chimney breast dimensions (internal, standard UK):**

| Feature | Dimension (mm) | Notes |
|---------|----------------|-------|
| Chimney breast width (external wall) | **900-1200** | Single flue |
| Chimney breast width (party wall, back-to-back) | **1050-1500** | Two flues |
| Chimney breast depth (projection into room) | **300-450** | One brick + flue |
| Fireplace opening (builder's opening) | **400 x 550** (W x H) | Standard 16"x22" |
| Fireplace opening (large Georgian) | **900 x 900** (W x H) | 36"x36" |
| Flue internal size (clay liner) | **185 x 185** or **225 x 225** | Square clay liner |
| Flue internal size (round liner) | **175 dia** (7") or **200 dia** (8") | Clay pipe |
| Chimney stack above roof | Min **1.0 m** above roof penetration | Building Regs |
| Stack free-standing height limit | **4.5 x narrowest dimension** | Approved Document J |

**Chimney construction rules:**
- Minimum height: 4.5 m from top of appliance to chimney top
- Within 600mm of ridge: min 600mm above ridge
- Further than 600mm from ridge: top must be within 2300mm horizontal of ridge
  and above a line drawn at 2.5 degrees below horizontal from ridge
- Maximum 4 bends, maximum angle from vertical: 45 degrees

Source: Approved Document J, NHBC Standards 6.8.23, BFCMA guidance.

### 10.2 Soil Pipe / Waste Pipe Routing

| Pipe | External Diameter (mm) | Notes |
|------|----------------------|-------|
| Soil pipe (WC) | **110** | Must be internal or external, not within floor voids |
| Waste pipe (basin/bath) | 40 | Can run in floor void |
| Waste pipe (kitchen sink) | 40-50 | Can run in floor void |
| Vent pipe | 110 (or 75 if separate) | Must terminate above roof |

**Structural impact:**
- 110mm soil pipes require 130mm+ holes through joists (if passing through)
- This exceeds the 0.25 x depth limit for standard joists
- Solution: box out around soil pipe with trimmer joists, or route externally
- Soil pipe stacks should be positioned on external walls or within purpose-built ducts

### 10.3 Joist Notching Summary (for pipe routing)

For a 200mm deep joist:
- Max notch depth: 0.125 x 200 = **25 mm** (but absolute max is 35mm)
- Max hole diameter: 0.25 x 200 = **50 mm**
- Notch zone: 0.07-0.25 of span from support
- Hole zone: 0.25-0.4 of span from support

A 22mm copper pipe needs a 25mm hole -- OK in zone.
A 40mm waste pipe needs a 45mm hole -- OK in 200mm joist.
A 110mm soil pipe needs a 115mm hole -- NOT OK, requires trimmer framing.

---

## 11. MATERIAL DENSITIES (for self-weight calculations)

| Material | Density (kg/m3) | Unit Weight (kN/m3) | Source |
|----------|----------------|--------------------| --------|
| Brickwork (common) | 1900 | **18.6** | BS EN 1991-1-1 |
| Brickwork (engineering) | 2200 | **21.6** | BS EN 1991-1-1 |
| Blockwork (dense concrete) | 2000 | **19.6** | BS EN 1991-1-1 |
| Blockwork (lightweight) | 600-1400 | **5.9-13.7** | BS EN 1991-1-1 |
| Natural stone (limestone) | 2300 | **22.6** | BS EN 1991-1-1 |
| Natural stone (sandstone) | 2200 | **21.6** | BS EN 1991-1-1 |
| Natural stone (granite) | 2650 | **26.0** | BS EN 1991-1-1 |
| Rubble masonry | 2000-2200 | **19.6-21.6** | BS EN 1991-1-1 |
| Softwood timber | 350-450 | **3.4-4.4** | BS EN 338 |
| Hardwood (oak) | 600-750 | **5.9-7.4** | BS EN 338 |
| Reinforced concrete | 2400-2500 | **23.5-24.5** | BS EN 1991-1-1 |
| Steel | 7850 | **77.0** | BS EN 1993 |
| Cast iron | 7200 | **70.6** | Reference data |
| Wrought iron | 7700 | **75.5** | Reference data |
| Lead sheet | 11340 | **111.2** | BS EN 12588 |
| Slate (roofing) | 2700-2900 | **26.5-28.4** | BS EN 1991-1-1 |
| Clay tile | 1900-2000 | **18.6-19.6** | BS EN 1991-1-1 |
| Float glass | 2500 | **24.5** | BS EN 572 |
| Lime plaster | 1600 | **15.7** | Reference data |
| Gypsum plaster | 1200 | **11.8** | Reference data |
| Lime mortar | 1800 | **17.7** | Reference data |
| Cement mortar | 2000 | **19.6** | Reference data |

**CORRECTIONS TO EXISTING CODE:** `loads.py` DENSITIES needs these updates:
- "brick": 19.0 -- should be **18.6** (or 19.0 is acceptable rounding for brickwork including mortar)
- "timber": 5.0 -- should be **3.5-4.4** (350-450 kg/m3 range for softwood)
- "slate": 28.0 -- correct range
- "clay_tile": 20.0 -- approximately correct

---

## 12. CODE CORRECTIONS SUMMARY

Based on this research, the following values in the existing codebase need correction:

### materials/properties.py

| Material | Property | Current Value | Correct Value | Source |
|----------|----------|--------------|---------------|--------|
| softwood_c16 | tensile_strength (ft,0,k) | 10.0 | **8.5** | EN 338:2016 |
| softwood_c16 | shear_strength (fv,k) | 1.8 | **3.2** | EN 338:2016 |
| softwood_c16 | density (rho_k) | 370 (ambiguous) | **310** (char) / **370** (mean) | EN 338:2016 |
| softwood_c24 | tensile_strength | 14.0 | **14.5** | EN 338:2016 |
| softwood_c24 | shear_strength | 2.5 | **4.0** | EN 338:2016 |
| softwood_c24 | density | 420 | Correct (rho_mean) | EN 338:2016 |
| common_brick | gamma_m | 3.5 | **3.0** (typical) or 2.7-3.5 (range) | UK NA to EC6 |

### loads.py

| Constant | Current Value | Correct Value | Notes |
|----------|--------------|---------------|-------|
| DENSITIES["timber"] | 5.0 | **3.5-4.4** | 350-450 kg/m3 for softwood |
| FLOOR_DEAD_LOADS["timber_joists"] | 0.5 | **0.35** | Joists + boards only |
| FLOOR_DEAD_LOADS["timber_with_plaster"] | 0.8 | **0.75-0.85** | Range acceptable; 0.8 is fine |

### granular_builder.py

| Constant | Current Value | Correct Value | Notes |
|----------|--------------|---------------|-------|
| BOARD_WIDTH | 0.150 | **0.145** | 25x150 nominal = 20x145 finished |
| BOARD_THICKNESS | 0.022 | **0.020-0.021** | 25mm nominal = 20-21mm finished |
| SASH_FRAME_W | 0.070 | **0.044-0.050** | Sash stile/rail width |
| GLAZING_BAR_W | 0.020 | **0.020-0.025** | Correct for late Georgian |
| GLASS_T | 0.003 | **0.0015** (Georgian) or **0.004** (modern) | Period-dependent |
| RAFTER_SPACING | 0.400 | Correct | 400mm standard centres |

---

## Sources

### Standards (numbered references)
- BS EN 1990:2002 - Eurocode: Basis of structural design
- BS EN 1991-1-1:2002 - Actions on structures: Densities, self-weight, imposed loads
- BS EN 1991-1-3:2003 - Actions on structures: Snow loads
- BS EN 1991-1-4:2005 - Actions on structures: Wind actions
- BS EN 1992-1-1:2004 - Design of concrete structures
- BS EN 1993-1-1:2005 - Design of steel structures
- BS EN 1995-1-1:2004 - Design of timber structures (Eurocode 5)
- BS EN 1996-1-1:2005 - Design of masonry structures (Eurocode 6)
- BS EN 338:2016 - Structural timber: Strength classes
- BS EN 771-1 - Specification for masonry units: Clay masonry units
- BS EN 998-2 - Specification for mortar for masonry: Masonry mortar
- BS EN 12588:2006 - Lead and lead alloys: Rolled lead sheet
- BS 3921:1985 - Clay bricks: Specification
- BS 5268-7.1:1990 - Structural use of timber: Domestic floor joists
- BS 5268-7.5:1990 - Structural use of timber: Rafters
- BS 5534:2014 - Code of practice for slating and tiling
- BS 8004:1986 - Foundations (now superseded by EC7)
- BS 8000-6:2013 - Workmanship: Code of practice for slating and tiling
- BS 8500-2:2015 - Concrete: Complementary British Standard to BS EN 206
- Building Regulations Approved Document A (Structure)
- Building Regulations Approved Document C (Site preparation and resistance to moisture)
- Building Regulations Approved Document E (Resistance to sound)
- Building Regulations Approved Document J (Combustion appliances and fuel storage)

### Web Sources
- [RoyMech - Masonry Design](https://roymech.org/Related/Construction/Masonry_design.html)
- [Structville - Design of Masonry Walls EN 1996-1](https://structville.com/design-of-masonry-walls-en-1996)
- [Timber Beam Calculator - Span Tables](https://www.timberbeamcalculator.co.uk/en-gb/span-tables/)
- [Timber Development UK](https://timberdevelopment.uk/)
- [BSW Span Tables](https://www.bsw.co.uk/wp-content/uploads/2022/10/Span_Table_2022.pdf)
- [Taylor Maxwell - C24 Span Tables](https://www.taylormaxwell.co.uk/uploads/files/D.100.02-01_C24-Span-Tables_Design_Span-Tables.pdf)
- [Maguire Brothers - Weight Loading](https://www.maguirebrothers.co.uk/articles/technical-articles/weight-loading-on-a-roof/)
- [SIGA Slate - Batten Gauge Tables](https://www.sigaslate.co.uk/knowledgebase/installation-advice/batten-and-holing-gauges-for-natural-slate/)
- [Ashbrook Roofing - Lead Codes](https://ashbrookroofing.co.uk/blogs/lead-flashing-buying-guides/lead-codes-explained)
- [Georgian Group - Sash Windows (Brooking)](https://georgiangroup.org.uk/wp-content/uploads/2024/07/GGM_Brooking_02_Sash_windows.pdf)
- [Sash Window Specialist - History of Glass](https://sashwindowspecialist.com/blog/history-of-window-glass/)
- [Histoglass - Cylinder Glass](https://histoglass.co.uk/period-glass/authentic-cylinder-glass/)
- [Building Conservation - Plain Glazing](https://www.buildingconservation.com/articles/glazing/glazing.htm)
- [Lisa.blue - Eurocode Imposed Loads](https://lisa.blue/help/eurocode_imposed_loads/en_GB)
- [Eurocodes JRC - Actions on Structures](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/EN1991_2_Malakatas.pdf)
- [Action Wall Ties - Cavity Wall History](https://actionwallties.co.uk/customer-stories/cavity-wall-construction-history)
- [Imperial Bricks - Standard Brick Size UK](https://www.imperialbricks.co.uk/guidance/standard-brick-size-in-the-uk/)
- [Lignacite - Mortar Design Guidance](https://lignacite.co.uk/wp-content/uploads/2023/01/Design-Guidance-Mortar.pdf)
- [Brick Development Association - Eurocode 6 Guidance](https://www.brick.org.uk/uploads/downloads/d-eurocode-6-masonry-introduction.pdf)
- [NHBC Standards 2025](https://nhbc-standards.co.uk/)
- [Designing Buildings Wiki](https://www.designingbuildings.co.uk/)
- [Cotswood Doors - Four Panelled Doors](https://www.cotswood-doors.co.uk/bespoke-doors/four-panelled-doors-through-the-ages/)
- [Yorkshire Lime Company - History of Cement & Lime Mortars](https://www.theyorkshirelime.company/a-basic-history-of-cement-and-lime-mortars-and-their-use-in-construction/)
- [LABC - Lath and Plaster Ceilings](https://www.labc.co.uk/news/my-dad-told-me-about-them-lath-and-plaster-ceilings)
- [Pavingexpert - DPC](https://www.pavingexpert.com/dpc01)
