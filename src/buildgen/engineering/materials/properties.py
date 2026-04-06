"""Material engineering properties from standards and test data.

All values in SI units:
    Stress/strength: MPa (N/mm² = MN/m²)
    Density: kg/m³
    Elastic modulus: GPa (kN/mm²)
    Thermal conductivity: W/(m·K)

Sources:
    BS EN 1996 (masonry), BS EN 1995 (timber), BS EN 1993 (steel),
    BS EN 1992 (concrete), Illston & Domone "Construction Materials",
    IStructE guides, BRE publications.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Material:
    """Complete material specification for structural analysis."""
    name: str
    category: str  # masonry, timber, metal, earth, glass, composite

    # Density
    density: float              # kg/m³

    # Strength (characteristic values, not design values)
    compressive_strength: float  # MPa — crushing resistance
    tensile_strength: float      # MPa — pulling apart resistance
    flexural_strength: float     # MPa — bending resistance
    shear_strength: float        # MPa — sliding resistance

    # Stiffness
    elastic_modulus: float       # GPa — Young's modulus (stiffness)

    # Safety factors (partial factors for design)
    gamma_m: float = 2.5        # Material partial safety factor

    # Thermal
    thermal_conductivity: float = 1.0   # W/(m·K)
    specific_heat: float = 1000.0       # J/(kg·K)
    thermal_expansion: float = 10e-6    # per °C

    # Physical
    porosity: float = 0.0       # 0-1 fraction
    moisture_absorption: float = 0.0  # % by weight
    fire_resistance_mins: int = 0     # minutes of fire resistance

    # Standard dimensions (if applicable)
    standard_sizes: list[tuple[float, float, float]] = field(
        default_factory=list
    )  # (length, width, height) in mm

    # Appearance
    color_rgb: tuple[int, int, int] = (128, 128, 128)
    texture: str = ""

    @property
    def design_compressive(self) -> float:
        """Design compressive strength (f_k / gamma_m)."""
        return self.compressive_strength / self.gamma_m

    @property
    def design_tensile(self) -> float:
        """Design tensile strength."""
        return self.tensile_strength / self.gamma_m

    @property
    def design_flexural(self) -> float:
        """Design flexural strength."""
        return self.flexural_strength / self.gamma_m

    @property
    def weight_per_m3(self) -> float:
        """Weight in kN/m³ (density * g / 1000)."""
        return self.density * 9.81 / 1000


# ── MASONRY MATERIALS ─────────────────────────────────────────────

_COMMON_BRICK = Material(
    name="common_brick",
    category="masonry",
    density=1900,
    compressive_strength=20.0,   # N/mm², typical Class B engineering
    tensile_strength=0.4,        # Very weak in tension
    flexural_strength=0.8,       # Bending across the brick
    shear_strength=0.35,
    elastic_modulus=8.0,         # GPa
    gamma_m=3.5,                # BS EN 1996 masonry safety factor
    thermal_conductivity=0.77,
    fire_resistance_mins=120,
    standard_sizes=[
        (215, 102.5, 65),        # UK standard metric brick (mm)
    ],
    color_rgb=(180, 100, 70),
    texture="brick_common",
)

_FACING_BRICK = Material(
    name="facing_brick",
    category="masonry",
    density=2000,
    compressive_strength=30.0,
    tensile_strength=0.5,
    flexural_strength=1.0,
    shear_strength=0.4,
    elastic_modulus=10.0,
    gamma_m=3.5,
    thermal_conductivity=0.96,
    fire_resistance_mins=120,
    standard_sizes=[(215, 102.5, 65)],
    color_rgb=(190, 120, 80),
    texture="brick_facing",
)

_ENGINEERING_BRICK = Material(
    name="engineering_brick",
    category="masonry",
    density=2200,
    compressive_strength=70.0,   # Class A engineering brick
    tensile_strength=0.8,
    flexural_strength=1.5,
    shear_strength=0.6,
    elastic_modulus=15.0,
    gamma_m=3.5,
    thermal_conductivity=1.15,
    fire_resistance_mins=240,
    standard_sizes=[(215, 102.5, 65)],
    color_rgb=(100, 60, 50),
    texture="brick_engineering",
)

_MORTAR_LIME = Material(
    name="mortar_lime",
    category="masonry",
    density=1800,
    compressive_strength=2.0,    # Lime mortar is weak
    tensile_strength=0.1,
    flexural_strength=0.3,
    shear_strength=0.15,
    elastic_modulus=2.0,
    gamma_m=3.5,
    standard_sizes=[(0, 0, 10)],  # 10mm joint thickness
    color_rgb=(220, 215, 200),
)

_MORTAR_CEMENT = Material(
    name="mortar_cement",
    category="masonry",
    density=2000,
    compressive_strength=10.0,
    tensile_strength=0.3,
    flexural_strength=0.5,
    shear_strength=0.25,
    elastic_modulus=5.0,
    gamma_m=3.5,
    standard_sizes=[(0, 0, 10)],
    color_rgb=(200, 200, 195),
)

_LIMESTONE = Material(
    name="limestone",
    category="masonry",
    density=2300,
    compressive_strength=30.0,   # Bath stone ~20-40 MPa
    tensile_strength=3.0,
    flexural_strength=5.0,
    shear_strength=4.0,
    elastic_modulus=25.0,
    gamma_m=3.0,
    thermal_conductivity=1.5,
    fire_resistance_mins=120,
    color_rgb=(220, 210, 180),
    texture="stone_limestone",
)

_SANDSTONE = Material(
    name="sandstone",
    category="masonry",
    density=2200,
    compressive_strength=40.0,
    tensile_strength=4.0,
    flexural_strength=6.0,
    shear_strength=5.0,
    elastic_modulus=20.0,
    gamma_m=3.0,
    thermal_conductivity=1.8,
    fire_resistance_mins=120,
    color_rgb=(200, 180, 140),
    texture="stone_sandstone",
)

_GRANITE = Material(
    name="granite",
    category="masonry",
    density=2650,
    compressive_strength=130.0,  # Very strong in compression
    tensile_strength=10.0,
    flexural_strength=15.0,
    shear_strength=12.0,
    elastic_modulus=50.0,
    gamma_m=3.0,
    color_rgb=(160, 160, 165),
    texture="stone_granite",
)

# ── TIMBER ────────────────────────────────────────────────────────

_SOFTWOOD_C16 = Material(
    name="softwood_c16",
    category="timber",
    density=370,
    compressive_strength=17.0,   # Parallel to grain (EN 338 Table 1)
    tensile_strength=8.5,        # Parallel to grain (EN 338: ft,0,k=8.5)
    flexural_strength=16.0,      # BS EN 338 strength class C16 (fm,k=16)
    shear_strength=3.2,          # EN 338: fv,k=3.2 MPa
    elastic_modulus=8.0,
    gamma_m=1.3,                # Timber partial factor
    thermal_conductivity=0.13,
    fire_resistance_mins=30,     # Charring rate ~0.65mm/min
    standard_sizes=[
        (4800, 47, 100), (4800, 47, 150), (4800, 47, 175),
        (4800, 47, 200), (4800, 47, 225), (4800, 47, 250),
    ],
    color_rgb=(200, 170, 120),
    texture="timber_softwood",
)

_SOFTWOOD_C24 = Material(
    name="softwood_c24",
    category="timber",
    density=420,
    compressive_strength=21.0,    # EN 338: fc,0,k=21 MPa
    tensile_strength=14.5,        # EN 338: ft,0,k=14.5 MPa
    flexural_strength=24.0,       # EN 338: fm,k=24 MPa
    shear_strength=4.0,           # EN 338: fv,k=4.0 MPa
    elastic_modulus=11.0,
    gamma_m=1.3,
    thermal_conductivity=0.13,
    fire_resistance_mins=30,
    standard_sizes=[
        (4800, 47, 150), (4800, 47, 200), (4800, 47, 250),
    ],
    color_rgb=(190, 160, 110),
    texture="timber_softwood",
)

_OAK = Material(
    name="oak",
    category="timber",
    density=690,
    compressive_strength=26.0,
    tensile_strength=18.0,
    flexural_strength=30.0,
    shear_strength=4.0,
    elastic_modulus=12.0,
    gamma_m=1.3,
    thermal_conductivity=0.17,
    fire_resistance_mins=40,
    color_rgb=(160, 120, 70),
    texture="timber_oak",
)

# ── METALS ────────────────────────────────────────────────────────

_MILD_STEEL = Material(
    name="mild_steel",
    category="metal",
    density=7850,
    compressive_strength=275.0,  # S275 grade yield
    tensile_strength=275.0,      # Yield strength
    flexural_strength=275.0,
    shear_strength=160.0,        # ~0.58 * fy
    elastic_modulus=210.0,
    gamma_m=1.0,                # Already factored in design strength
    thermal_conductivity=50.0,
    fire_resistance_mins=15,     # Unprotected
    color_rgb=(180, 180, 185),
)

_CAST_IRON = Material(
    name="cast_iron",
    category="metal",
    density=7200,
    compressive_strength=600.0,  # Very strong in compression
    tensile_strength=100.0,      # Weak in tension (brittle)
    flexural_strength=200.0,
    shear_strength=170.0,
    elastic_modulus=100.0,
    gamma_m=3.0,                # High safety factor (brittle)
    color_rgb=(80, 80, 85),
)

_WROUGHT_IRON = Material(
    name="wrought_iron",
    category="metal",
    density=7700,
    compressive_strength=200.0,
    tensile_strength=250.0,
    flexural_strength=250.0,
    shear_strength=150.0,
    elastic_modulus=190.0,
    gamma_m=1.5,
    color_rgb=(100, 100, 105),
)

# ── GLASS ─────────────────────────────────────────────────────────

_GLASS_FLOAT = Material(
    name="float_glass",
    category="glass",
    density=2500,
    compressive_strength=1000.0,
    tensile_strength=45.0,
    flexural_strength=45.0,
    shear_strength=30.0,
    elastic_modulus=70.0,
    gamma_m=2.5,
    thermal_conductivity=1.0,
    color_rgb=(200, 220, 240),
    texture="glass",
)

# ── EARTH / COB ───────────────────────────────────────────────────

_COB = Material(
    name="cob",
    category="earth",
    density=1700,
    compressive_strength=1.0,    # Very low
    tensile_strength=0.05,
    flexural_strength=0.1,
    shear_strength=0.1,
    elastic_modulus=0.5,
    gamma_m=4.0,                # High safety factor
    thermal_conductivity=0.5,
    fire_resistance_mins=120,    # Good fire resistance
    color_rgb=(180, 160, 130),
    texture="cob",
)

# ── PLASTER / RENDER ──────────────────────────────────────────────

_LIME_PLASTER = Material(
    name="lime_plaster",
    category="finish",
    density=1600,
    compressive_strength=2.0,
    tensile_strength=0.2,
    flexural_strength=0.3,
    shear_strength=0.15,
    elastic_modulus=3.0,
    gamma_m=3.0,
    standard_sizes=[(0, 0, 15)],  # 15mm typical thickness
    color_rgb=(240, 235, 225),
)

# ── ROOFING ───────────────────────────────────────────────────────

_SLATE = Material(
    name="roofing_slate",
    category="masonry",
    density=2800,
    compressive_strength=100.0,
    tensile_strength=30.0,
    flexural_strength=40.0,
    shear_strength=20.0,
    elastic_modulus=30.0,
    gamma_m=2.5,
    standard_sizes=[
        (600, 300, 5),   # 600x300mm, 5mm thick
        (500, 250, 5),
    ],
    color_rgb=(80, 85, 90),
    texture="slate",
)

_CLAY_TILE = Material(
    name="clay_roof_tile",
    category="masonry",
    density=1900,
    compressive_strength=15.0,
    tensile_strength=2.0,
    flexural_strength=3.0,
    shear_strength=1.5,
    elastic_modulus=5.0,
    gamma_m=3.0,
    standard_sizes=[
        (265, 165, 12),  # Plain tile
        (420, 330, 15),  # Pantile
    ],
    color_rgb=(170, 90, 60),
    texture="clay_tile",
)


# ── MATERIALS DATABASE ────────────────────────────────────────────

MATERIALS_DB: dict[str, Material] = {
    # Masonry
    "common_brick": _COMMON_BRICK,
    "facing_brick": _FACING_BRICK,
    "engineering_brick": _ENGINEERING_BRICK,
    "mortar_lime": _MORTAR_LIME,
    "mortar_cement": _MORTAR_CEMENT,
    "limestone": _LIMESTONE,
    "sandstone": _SANDSTONE,
    "granite": _GRANITE,
    # Timber
    "softwood_c16": _SOFTWOOD_C16,
    "softwood_c24": _SOFTWOOD_C24,
    "oak": _OAK,
    # Metals
    "mild_steel": _MILD_STEEL,
    "cast_iron": _CAST_IRON,
    "wrought_iron": _WROUGHT_IRON,
    # Glass
    "float_glass": _GLASS_FLOAT,
    # Earth
    "cob": _COB,
    # Finishes
    "lime_plaster": _LIME_PLASTER,
    # Roofing
    "roofing_slate": _SLATE,
    "clay_roof_tile": _CLAY_TILE,
}


def get_material(name: str) -> Material:
    """Look up a material by name."""
    if name in MATERIALS_DB:
        return MATERIALS_DB[name]
    raise ValueError(f"Unknown material '{name}'. Available: {list(MATERIALS_DB.keys())}")


def check_compressive_stress(
    load_kn: float,
    area_m2: float,
    material: Material,
) -> tuple[bool, float, float]:
    """Check if compressive stress is within limits.

    Returns (is_ok, actual_stress_mpa, allowable_stress_mpa).
    """
    actual = (load_kn * 1000) / (area_m2 * 1e6)  # Convert to MPa
    allowable = material.design_compressive
    return actual <= allowable, actual, allowable


def check_tensile_stress(
    load_kn: float,
    area_m2: float,
    material: Material,
) -> tuple[bool, float, float]:
    """Check if tensile stress is within limits."""
    actual = (load_kn * 1000) / (area_m2 * 1e6)
    allowable = material.design_tensile
    return actual <= allowable, actual, allowable


def check_bending_stress(
    moment_knm: float,
    section_modulus_m3: float,
    material: Material,
) -> tuple[bool, float, float]:
    """Check if bending stress is within limits.

    Section modulus Z = I/y = bh²/6 for rectangular section.
    """
    actual = (moment_knm * 1000) / (section_modulus_m3 * 1e9)
    allowable = material.design_flexural
    return actual <= allowable, actual, allowable


def check_shear_stress(
    shear_kn: float,
    area_m2: float,
    material: Material,
) -> tuple[bool, float, float]:
    """Check if shear stress is within limits."""
    actual = (shear_kn * 1000) / (area_m2 * 1e6)
    allowable = material.shear_strength / material.gamma_m
    return actual <= allowable, actual, allowable
