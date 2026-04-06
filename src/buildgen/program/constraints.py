"""Architectural constraints and design rules.

Encodes knowledge about how buildings actually work — minimum clearances,
material impacts, functional requirements, stair/landing relationships,
and fixture space requirements.

Sources: UK Building Regulations (Approved Documents K, M), US IRC,
UK NDSS (Nationally Described Space Standard), NKBA Guidelines,
Neufert Architects' Data. See ARCHITECTURAL_STANDARDS.md for full
references and derivations.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ── Minimum room dimensions for function ──────────────────────────
# Each room type has minimum width, depth, and clearance requirements.
# These ensure rooms can actually contain their required fixtures
# with space for people to move.
#
# Values derived from:
#   - UK NDSS: single bedroom 7.5m² (2.15m wide), double 11.5m² (2.75m)
#   - US IRC: habitable room min 6.5m² (2.13m wide), one room min 11.15m²
#   - UK Building Regs: WC min 0.7m x 1.3m
#   - NKBA: kitchen work aisle min 1.07m (1 cook), 1.22m (2 cooks)
#   - Neufert: corridor min 1.5-1.8m, habitable ceiling min 2.4m

@dataclass
class RoomConstraints:
    """Minimum dimensions and requirements for a room type."""
    min_width: float       # metres — narrowest acceptable dimension
    min_depth: float       # metres — other dimension
    min_area: float        # m² — minimum usable area
    min_clearance: float   # metres — clear floor space for movement
    needs_plumbing: bool = False    # Needs water/waste connection
    needs_exterior: bool = True     # Needs exterior wall / window
    needs_ventilation: bool = True
    max_depth_ratio: float = 3.0    # max depth/width ratio
    min_window_ratio: float = 0.08  # min glazing area / floor area (IRC 8%)

ROOM_CONSTRAINTS: dict[str, RoomConstraints] = {
    # ── Residential ──
    # Entrance/circulation
    "entrance_hall": RoomConstraints(1.2, 2.0, 3.0, 1.0, needs_exterior=True),
    "hallway": RoomConstraints(0.914, 2.0, 2.5, 0.914,  # IRC: 36in min
                               needs_exterior=False, min_window_ratio=0.0),
    "landing": RoomConstraints(1.2, 1.5, 2.0, 0.914,    # IRC: 36in min
                               needs_exterior=False, min_window_ratio=0.0),
    # Reception rooms
    "parlour": RoomConstraints(3.0, 3.5, 12.0, 1.5),
    "drawing_room": RoomConstraints(3.5, 4.0, 16.0, 1.5),
    "dining_room": RoomConstraints(3.0, 3.5, 12.0, 1.07),  # NKBA: 42in aisle
    # Kitchen/service (NKBA work triangle: legs 1.2-2.7m, total <7.9m)
    "kitchen": RoomConstraints(2.4, 3.0, 8.0, 1.07,     # 42in work aisle
                               needs_plumbing=True),
    "scullery": RoomConstraints(1.8, 2.0, 4.0, 0.9, needs_plumbing=True),
    "pantry": RoomConstraints(1.2, 1.5, 2.0, 0.8,
                              needs_exterior=False, min_window_ratio=0.0),
    # Wet rooms (UK Regs: WC min 0.7x1.3m, bathroom min 1.8x2.2m)
    "wc": RoomConstraints(0.7, 1.3, 0.91, 0.6,          # UK Regs minimum
                          needs_plumbing=True, needs_exterior=False,
                          min_window_ratio=0.0),
    "bathroom": RoomConstraints(1.8, 2.2, 4.0, 0.7,     # UK standard bath
                                needs_plumbing=True, needs_exterior=False,
                                min_window_ratio=0.0),
    # Bedrooms (NDSS: single 7.5m²/2.15m, double 11.5m²/2.75m)
    "master_bedroom": RoomConstraints(2.75, 4.0, 11.5, 0.76),  # NDSS double
    "bedroom": RoomConstraints(2.15, 3.0, 7.5, 0.61),          # NDSS single
    "dressing_room": RoomConstraints(1.5, 2.0, 3.5, 0.76,      # wardrobe open
                                     needs_exterior=False,
                                     min_window_ratio=0.0),
    "nursery": RoomConstraints(2.15, 3.0, 7.5, 1.0),           # NDSS single
    "servants_quarters": RoomConstraints(2.13, 2.8, 6.51, 0.61),  # HMO 1-adult
    # Study/work
    "study": RoomConstraints(2.4, 3.0, 8.0, 1.0),
    "library": RoomConstraints(3.0, 3.5, 12.0, 1.2),
    "storage": RoomConstraints(1.2, 1.5, 2.0, 0.6,
                               needs_exterior=False,
                               needs_ventilation=False,
                               min_window_ratio=0.0),
    # Circulation
    "stairwell": RoomConstraints(1.8, 2.5, 4.0, 0.85,   # UK typical 850mm
                                 needs_exterior=False,
                                 min_window_ratio=0.0),
    # Commercial
    "shop_floor": RoomConstraints(4.0, 5.0, 25.0, 2.0),
    "workshop": RoomConstraints(4.0, 5.0, 25.0, 2.0),
    "office": RoomConstraints(2.5, 3.0, 9.0, 1.2),
}


# ── Ceiling heights by standard ──────────────────────────────────

CEILING_HEIGHTS: dict[str, float] = {
    "uk_building_regs_min": 2.0,     # Approved Document absolute minimum
    "uk_ndss_min": 2.3,              # NDSS: min for 75% of GIA
    "london_plan_min": 2.5,          # London Plan minimum
    "london_plan_ground_best": 3.5,  # London Plan ground-floor best practice
    "us_irc_habitable": 2.134,       # 7 ft
    "us_irc_bathroom": 2.032,        # 6 ft 8 in
    "us_irc_basement": 2.032,        # 6 ft 8 in
    "us_irc_under_beam": 1.981,      # 6 ft 6 in (beams >3ft apart)
    "us_irc_sloped_min": 1.524,      # 5 ft (minimum anywhere in room)
    "neufert_residential": 2.5,      # Neufert recommended
    "georgian_principal": 3.2,       # Georgian ground/first floor
    "georgian_upper": 2.8,           # Georgian second floor
    "georgian_attic": 2.3,           # Georgian servants' attic
    "georgian_basement": 2.5,        # Georgian basement/kitchen level
}


# ── Natural light / daylight rules ───────────────────────────────

@dataclass
class DaylightRules:
    """Rules for natural light provision in habitable rooms.

    Sources: IRC R303 (8% rule), NYC Building Code (30ft depth limit),
    WBDG daylighting guidelines (1.5-2.0x head height rule).
    """
    min_glazing_ratio: float = 0.08   # min window area / floor area
    max_room_depth_factor: float = 2.0  # max depth = factor * window head height
    max_room_depth_two_sides: float = 4.0  # factor when windows on 2 walls
    absolute_max_depth: float = 9.14  # metres (30 ft, NYC code)


DAYLIGHT_RULES = DaylightRules()


# ── Room connectivity rules ──────────────────────────────────────

# Which rooms must NOT open directly onto each other (UK Building Regs)
WC_EXCLUSION_ROOMS = {"kitchen", "dining_room"}

# Rooms that must connect to hallway/landing (not through another room)
MUST_CONNECT_VIA_CIRCULATION = {
    "bedroom", "master_bedroom", "nursery", "servants_quarters",
    "study", "library", "bathroom",  # except en-suite
}

# Rooms that can connect directly to each other (no hallway needed)
DIRECT_CONNECTION_PAIRS = {
    ("parlour", "dining_room"),       # folding doors
    ("drawing_room", "dining_room"),  # folding doors
    ("kitchen", "scullery"),
    ("kitchen", "pantry"),
    ("master_bedroom", "dressing_room"),
    ("master_bedroom", "bathroom"),   # en-suite
    ("entrance_hall", "parlour"),
    ("entrance_hall", "drawing_room"),
}


# ── Plumbing stacking preferences ───────────────────────────────

PLUMBING_ROOMS = {"kitchen", "scullery", "bathroom", "wc"}

# Max horizontal distance from plumbing stack for wet rooms (metres)
MAX_PLUMBING_OFFSET = 2.0


# ── Furniture dimensions for room sizing ─────────────────────────

BED_SIZES: dict[str, tuple[float, float]] = {
    # (width, length) in metres
    "single": (0.99, 1.90),
    "double": (1.37, 1.90),
    "queen": (1.52, 2.03),
    "king": (1.93, 2.03),
}

# Clearance around beds (metres)
BED_CLEARANCE_SIDE = 0.76       # 30 in, each side
BED_CLEARANCE_SIDE_MIN = 0.61   # 24 in, minimum one side
BED_CLEARANCE_FOOT = 0.91       # 36 in, for dresser/wardrobe

# Dining table clearances (metres)
DINING_CLEARANCE_NO_PASSAGE = 0.91   # 36 in, table to wall
DINING_CLEARANCE_WITH_PASSAGE = 1.17  # 46 in, passage behind chairs
DINING_WIDTH_PER_PERSON = 0.61        # 24 in per place setting


# ── Material impact on structure ──────────────────────────────────
# Different building materials have fundamentally different properties
# that affect wall thickness, maximum span, and window sizes.

@dataclass
class MaterialProperties:
    """How a building material affects structural design."""
    name: str
    wall_thickness_exterior: float   # metres
    wall_thickness_interior: float   # metres
    max_span: float                  # metres — max unsupported span
    max_opening_width: float         # metres — max window/door width
    min_pier_width: float            # metres — min wall between openings
    weight_class: str                # "light", "medium", "heavy"
    fire_resistance: str             # "low", "medium", "high"
    typical_floor_height: float      # metres
    description: str = ""

MATERIALS: dict[str, MaterialProperties] = {
    "brick": MaterialProperties(
        "brick", 0.35, 0.12, 5.0, 2.5, 0.45, "heavy", "high", 3.0,
        "Load-bearing brick. Standard for Georgian/Victorian.",
    ),
    "stone": MaterialProperties(
        "stone", 0.60, 0.45, 4.0, 2.0, 0.6, "heavy", "high", 3.2,
        "Dressed or rubble stone. Thick walls, small openings.",
    ),
    "timber_frame": MaterialProperties(
        "timber_frame", 0.20, 0.10, 6.0, 3.0, 0.15, "light", "low", 2.8,
        "Timber frame with infill. Medieval to modern.",
    ),
    "stucco_over_brick": MaterialProperties(
        "stucco_over_brick", 0.38, 0.12, 5.0, 2.5, 0.45, "heavy", "high",
        3.0, "Brick with stucco render. Regency/Georgian.",
    ),
    "cob": MaterialProperties(
        "cob", 0.50, 0.30, 3.5, 1.5, 0.6, "heavy", "medium", 2.5,
        "Earth/cob walls. Cottage construction. Very thick walls.",
    ),
    "concrete": MaterialProperties(
        "concrete", 0.25, 0.15, 8.0, 6.0, 0.3, "heavy", "high", 3.0,
        "Reinforced concrete. Modern construction.",
    ),
    "steel_frame": MaterialProperties(
        "steel_frame", 0.15, 0.10, 12.0, 10.0, 0.15, "medium", "medium",
        3.6, "Steel frame with curtain wall. Commercial/industrial.",
    ),
    "wattle_and_daub": MaterialProperties(
        "wattle_and_daub", 0.18, 0.12, 4.0, 1.8, 0.3, "light", "low",
        2.4, "Wattle and daub infill in timber frame.",
    ),
    "log": MaterialProperties(
        "log", 0.30, 0.20, 5.0, 2.0, 0.4, "medium", "medium", 2.6,
        "Log construction. Scandinavian/frontier.",
    ),
}


# ── Staircase types and their requirements ────────────────────────

@dataclass
class StairType:
    """Requirements for different staircase configurations."""
    name: str
    min_width: float           # metres — clear width of treads
    min_stairwell_width: float # metres — total width including walls
    min_stairwell_depth: float # metres — total depth
    landing_width: float       # metres — landing at top/bottom
    landing_depth: float       # metres
    typical_riser: float       # metres
    typical_tread: float       # metres
    turns: int                 # 0=straight, 1=L-shape, 2=U-shape
    suits_buildings: list[str] = field(default_factory=list)
    description: str = ""

STAIR_TYPES: dict[str, StairType] = {
    "straight": StairType(
        "straight", 0.85, 2.0, 4.5, 2.0, 1.0, 0.19, 0.25, 0,
        ["townhouse", "cottage", "terrace"],
        "Simple straight run. Needs long stairwell.",
    ),
    "l_shape": StairType(
        "l_shape", 0.85, 2.5, 3.5, 2.5, 1.2, 0.19, 0.25, 1,
        ["townhouse", "manor", "villa"],
        "Quarter-turn with landing. Compact.",
    ),
    "u_shape": StairType(
        "u_shape", 0.85, 2.0, 3.0, 2.0, 2.0, 0.19, 0.25, 2,
        ["townhouse", "mansion", "hotel"],
        "Half-turn with intermediate landing. Very compact footprint.",
    ),
    "spiral": StairType(
        "spiral", 0.7, 1.8, 1.8, 1.0, 1.0, 0.22, 0.20, 0,
        ["castle", "tower", "lighthouse"],
        "Circular spiral. Small footprint but steep and narrow.",
    ),
    "grand": StairType(
        "grand", 1.5, 4.0, 5.0, 4.0, 2.0, 0.16, 0.30, 1,
        ["mansion", "palace", "hotel", "department_store"],
        "Wide ceremonial staircase. Impressive but space-hungry.",
    ),
    "ladder": StairType(
        "ladder", 0.6, 0.8, 2.0, 0.8, 0.6, 0.25, 0.20, 0,
        ["loft", "attic", "shed", "tower"],
        "Steep ship's ladder / loft ladder. Minimal space.",
    ),
}


# ── Site and environment factors ──────────────────────────────────

@dataclass
class SiteConstraints:
    """How site conditions affect building design."""
    slope_degrees: float = 0.0    # Ground slope
    orientation: float = 0.0      # Degrees from north (0=north-facing)
    climate: str = "temperate"    # temperate, hot_dry, hot_humid, cold
    urban_density: str = "medium" # rural, suburban, medium, dense
    street_side: str = "south"    # Which side faces the street
    plot_width: float = 0.0       # 0 = unconstrained
    plot_depth: float = 0.0
    party_wall_left: bool = False  # Attached to neighbour
    party_wall_right: bool = False
    rear_access: bool = True       # Has back lane/alley

CLIMATE_IMPACTS: dict[str, dict] = {
    "temperate": {
        "wall_thickness_factor": 1.0,
        "window_size_factor": 1.0,
        "roof_pitch_factor": 1.0,
        "needs_heating": True,
        "needs_cooling": False,
        "porch_depth": 1.2,
    },
    "hot_dry": {
        "wall_thickness_factor": 1.3,  # Thick walls for thermal mass
        "window_size_factor": 0.6,     # Small windows to reduce heat
        "roof_pitch_factor": 0.3,      # Flat roofs common
        "needs_heating": False,
        "needs_cooling": True,
        "porch_depth": 2.0,            # Deep shade porches
    },
    "hot_humid": {
        "wall_thickness_factor": 0.8,
        "window_size_factor": 1.4,     # Large windows for ventilation
        "roof_pitch_factor": 1.5,      # Steep roofs for rain
        "needs_heating": False,
        "needs_cooling": True,
        "porch_depth": 2.5,            # Wide verandahs
    },
    "cold": {
        "wall_thickness_factor": 1.4,  # Thick for insulation
        "window_size_factor": 0.8,     # Smaller to reduce heat loss
        "roof_pitch_factor": 1.3,      # Steep for snow
        "needs_heating": True,
        "needs_cooling": False,
        "porch_depth": 1.5,            # Enclosed porches
    },
}
