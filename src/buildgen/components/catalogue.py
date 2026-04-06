"""Building component catalogue.

Standard building elements with dimensions, variants, and period tags.
Each component specifies which architectural styles it belongs to,
so the system can select appropriate components for each building.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Component:
    """A building component with dimensions and metadata."""
    name: str
    category: str
    width: float          # metres
    height: float         # metres
    depth: float          # metres (thickness for doors/windows)
    styles: list[str] = field(default_factory=list)  # Which styles use this
    periods: list[str] = field(default_factory=list)  # Time periods
    description: str = ""
    variants: list[str] = field(default_factory=list)


# ── DOORS ─────────────────────────────────────────────────────────

DOORS: dict[str, Component] = {
    # External doors
    "panel_6": Component(
        "Six-Panel Door", "door", 0.91, 2.1, 0.045,
        ["georgian", "regency", "federal"],
        ["18th_century", "early_19th_century"],
        "Classic Georgian 6-panel door with raised panels.",
        ["with_fanlight", "with_sidelights", "painted"],
    ),
    "panel_4": Component(
        "Four-Panel Door", "door", 0.84, 2.0, 0.044,
        ["victorian", "edwardian"],
        ["19th_century", "early_20th_century"],
        "Victorian 4-panel door, often with glazed upper panels.",
        ["half_glazed", "solid", "with_letterbox"],
    ),
    "plank": Component(
        "Plank Door", "door", 0.80, 1.90, 0.050,
        ["medieval", "tudor", "vernacular", "cottage"],
        ["medieval", "16th_century", "17th_century"],
        "Vertical plank door with iron strap hinges.",
        ["arched_top", "square_top", "studded"],
    ),
    "stable": Component(
        "Stable Door", "door", 0.84, 2.0, 0.045,
        ["farmhouse", "cottage", "rural"],
        ["17th_century", "18th_century", "19th_century"],
        "Horizontally-split door (top opens independently).",
    ),
    "french": Component(
        "French Doors", "door", 1.50, 2.1, 0.050,
        ["georgian", "regency", "victorian", "edwardian"],
        ["18th_century", "19th_century"],
        "Pair of glazed doors opening to garden/terrace.",
    ),
    "arched": Component(
        "Arched Door", "door", 0.90, 2.4, 0.060,
        ["romanesque", "gothic", "church", "castle"],
        ["medieval", "12th_century", "13th_century"],
        "Door with semicircular or pointed arch head.",
        ["round_arch", "pointed_arch", "ogee_arch"],
    ),
    "double_front": Component(
        "Double Front Door", "door", 1.50, 2.5, 0.055,
        ["georgian", "victorian", "mansion"],
        ["18th_century", "19th_century"],
        "Grand double entrance doors.",
        ["with_fanlight", "with_portico", "with_columns"],
    ),
    "industrial": Component(
        "Industrial Door", "door", 3.0, 3.5, 0.060,
        ["industrial", "warehouse", "factory"],
        ["19th_century", "20th_century"],
        "Large sliding or hinged industrial door.",
        ["sliding", "roller", "hinged"],
    ),
    "garage": Component(
        "Garage Door", "door", 2.5, 2.2, 0.050,
        ["modern", "suburban"],
        ["20th_century"],
        "Vehicle-width garage door.",
        ["up_and_over", "roller", "side_hinged"],
    ),

    # Internal doors
    "internal_panel": Component(
        "Internal Panel Door", "door", 0.76, 2.0, 0.035,
        ["all"],
        ["18th_century", "19th_century", "20th_century"],
        "Standard internal panel door.",
        ["2_panel", "4_panel", "6_panel"],
    ),
    "ledged_braced": Component(
        "Ledged & Braced Door", "door", 0.76, 1.95, 0.040,
        ["cottage", "farmhouse", "barn", "medieval"],
        ["medieval", "17th_century", "18th_century"],
        "Simple construction: vertical boards with horizontal ledges and diagonal brace.",
    ),
}


# ── WINDOWS ───────────────────────────────────────────────────────

WINDOWS: dict[str, Component] = {
    "sash_6over6": Component(
        "Six-over-Six Sash", "window", 1.05, 1.65, 0.12,
        ["georgian", "federal", "colonial"],
        ["18th_century"],
        "Classic Georgian sash window. Two sliding sashes, each with 6 panes.",
        ["recessed", "flush", "with_horns"],
    ),
    "sash_2over2": Component(
        "Two-over-Two Sash", "window", 1.05, 1.65, 0.12,
        ["victorian", "edwardian"],
        ["late_19th_century", "early_20th_century"],
        "Later sash with larger panes (plate glass era).",
    ),
    "casement": Component(
        "Casement Window", "window", 0.90, 1.20, 0.10,
        ["medieval", "tudor", "cottage", "vernacular"],
        ["medieval", "16th_century", "17th_century"],
        "Side-hinged window opening outward. Small panes in lead cames.",
        ["2_light", "3_light", "with_transom"],
    ),
    "oriel": Component(
        "Oriel Window", "window", 1.50, 1.50, 0.80,
        ["medieval", "tudor", "gothic"],
        ["medieval", "15th_century", "16th_century"],
        "Projecting bay window supported on corbels.",
    ),
    "lancet": Component(
        "Lancet Window", "window", 0.60, 2.00, 0.15,
        ["gothic", "church", "castle"],
        ["13th_century", "14th_century"],
        "Tall narrow window with pointed arch top.",
    ),
    "rose": Component(
        "Rose Window", "window", 3.00, 3.00, 0.20,
        ["gothic", "church", "cathedral"],
        ["13th_century", "14th_century"],
        "Large circular window with radiating tracery.",
    ),
    "bay": Component(
        "Bay Window", "window", 2.40, 1.65, 1.00,
        ["victorian", "edwardian", "georgian"],
        ["19th_century", "early_20th_century"],
        "Projecting bay window (canted or square).",
        ["canted_3_sided", "square", "full_height"],
    ),
    "dormer": Component(
        "Dormer Window", "window", 1.20, 1.20, 1.00,
        ["georgian", "victorian", "cottage", "mansard"],
        ["18th_century", "19th_century"],
        "Window projecting from a sloped roof.",
        ["gable_dormer", "hip_dormer", "shed_dormer", "eyebrow"],
    ),
    "skylight": Component(
        "Skylight/Rooflight", "window", 0.80, 1.20, 0.10,
        ["modern", "industrial", "victorian"],
        ["19th_century", "20th_century"],
        "Window set into the plane of the roof.",
    ),
    "arrow_loop": Component(
        "Arrow Loop", "window", 0.10, 1.00, 0.80,
        ["castle", "fortified"],
        ["12th_century", "13th_century", "14th_century"],
        "Narrow defensive slit in castle wall.",
        ["cross_loop", "keyhole", "plain_slit"],
    ),
    "shopfront": Component(
        "Shopfront Window", "window", 3.00, 2.50, 0.10,
        ["victorian", "edwardian", "commercial"],
        ["19th_century", "early_20th_century"],
        "Large plate-glass shop display window.",
    ),
}


# ── WALL TYPES ────────────────────────────────────────────────────

WALLS: dict[str, Component] = {
    "brick_flemish": Component(
        "Flemish Bond Brick", "wall", 0.0, 0.0, 0.35,
        ["georgian", "victorian"],
        ["18th_century", "19th_century"],
        "Alternating headers and stretchers. Classic Georgian finish.",
    ),
    "brick_english": Component(
        "English Bond Brick", "wall", 0.0, 0.0, 0.35,
        ["victorian", "industrial"],
        ["19th_century"],
        "Alternating courses of headers and stretchers. Strong.",
    ),
    "stone_ashlar": Component(
        "Ashlar Stone", "wall", 0.0, 0.0, 0.60,
        ["georgian", "gothic", "classical"],
        ["medieval", "18th_century"],
        "Dressed stone blocks with thin joints. Formal.",
    ),
    "stone_rubble": Component(
        "Rubble Stone", "wall", 0.0, 0.0, 0.55,
        ["medieval", "cottage", "vernacular"],
        ["medieval", "17th_century", "18th_century"],
        "Irregular stones with thick mortar joints.",
    ),
    "timber_frame": Component(
        "Timber Frame", "wall", 0.0, 0.0, 0.20,
        ["medieval", "tudor", "half_timbered"],
        ["medieval", "15th_century", "16th_century"],
        "Oak frame with wattle-and-daub or brick infill.",
    ),
    "cob": Component(
        "Cob/Earth", "wall", 0.0, 0.0, 0.50,
        ["vernacular", "cottage"],
        ["medieval", "17th_century", "18th_century"],
        "Unbaked earth mixed with straw. Devon/Somerset tradition.",
    ),
    "stucco": Component(
        "Stucco/Render", "wall", 0.0, 0.0, 0.38,
        ["regency", "georgian", "neoclassical"],
        ["late_18th_century", "early_19th_century"],
        "Brick with stucco render scored to look like ashlar.",
    ),
}


# ── FIREPLACES ────────────────────────────────────────────────────

FIREPLACES: dict[str, Component] = {
    "inglenook": Component(
        "Inglenook Fireplace", "fireplace", 1.80, 1.50, 0.80,
        ["medieval", "tudor", "cottage"],
        ["medieval", "16th_century", "17th_century"],
        "Large walk-in fireplace with seats inside. Bread oven to one side.",
        ["with_bread_oven", "with_settle", "stone_lintel"],
    ),
    "georgian_marble": Component(
        "Georgian Marble Chimneypiece", "fireplace", 1.40, 1.20, 0.35,
        ["georgian", "regency"],
        ["18th_century", "early_19th_century"],
        "Elegant marble surround with mantelshelf. Adam-style decoration.",
        ["plain", "carved", "with_hob_grate"],
    ),
    "victorian_cast_iron": Component(
        "Victorian Cast Iron Fireplace", "fireplace", 1.10, 1.00, 0.30,
        ["victorian"],
        ["19th_century"],
        "Decorative cast iron surround with tiled cheeks.",
        ["arched", "rectangular", "with_overmantel"],
    ),
    "kitchen_range": Component(
        "Kitchen Range", "fireplace", 1.50, 0.90, 0.60,
        ["victorian", "edwardian", "farmhouse"],
        ["19th_century", "early_20th_century"],
        "Cast iron cooking range with oven, hob, and hot water boiler.",
    ),
    "open_hearth": Component(
        "Open Hearth", "fireplace", 2.00, 0.00, 1.00,
        ["medieval", "great_hall"],
        ["medieval"],
        "Central open fire on a stone hearth. Smoke rises to louvre in roof.",
    ),
}


# ── FURNITURE ─────────────────────────────────────────────────────

FURNITURE: dict[str, Component] = {
    "bed_single": Component("Single Bed", "furniture", 0.99, 0.55, 1.90),
    "bed_double": Component("Double Bed", "furniture", 1.37, 0.55, 1.90),
    "bed_king": Component("King Bed", "furniture", 1.93, 0.55, 2.03),
    "bed_four_poster": Component(
        "Four-Poster Bed", "furniture", 1.60, 2.20, 2.10,
        ["georgian", "victorian", "medieval", "tudor"],
        description="Canopied bed with corner posts.",
    ),
    "wardrobe": Component("Wardrobe", "furniture", 1.20, 2.00, 0.60),
    "chest_of_drawers": Component("Chest of Drawers", "furniture", 0.80, 0.90, 0.45),
    "dressing_table": Component("Dressing Table", "furniture", 1.00, 0.75, 0.50),
    "dining_table_4": Component("Dining Table (4)", "furniture", 1.20, 0.75, 0.90),
    "dining_table_6": Component("Dining Table (6)", "furniture", 1.60, 0.75, 0.90),
    "dining_table_8": Component("Dining Table (8)", "furniture", 2.20, 0.75, 1.00),
    "dining_chair": Component("Dining Chair", "furniture", 0.45, 0.90, 0.45),
    "armchair": Component("Armchair", "furniture", 0.80, 0.90, 0.80),
    "sofa_2seat": Component("Two-Seat Sofa", "furniture", 1.50, 0.85, 0.85),
    "sofa_3seat": Component("Three-Seat Sofa", "furniture", 2.10, 0.85, 0.85),
    "bookcase": Component("Bookcase", "furniture", 1.00, 1.80, 0.30),
    "desk": Component("Writing Desk", "furniture", 1.20, 0.75, 0.60),
    "sideboard": Component("Sideboard", "furniture", 1.50, 0.90, 0.50),
    "settle": Component(
        "Settle (Bench)", "furniture", 1.50, 1.20, 0.50,
        ["medieval", "cottage", "tavern"],
        description="High-backed wooden bench, often near fireplace.",
    ),
    "trestle_table": Component(
        "Trestle Table", "furniture", 2.00, 0.75, 0.80,
        ["medieval", "tavern"],
        description="Long table on trestle supports.",
    ),
}


# ── APPLIANCES ────────────────────────────────────────────────────

APPLIANCES: dict[str, Component] = {
    "toilet": Component("Toilet", "appliance", 0.40, 0.40, 0.70),
    "bath_standard": Component("Standard Bath", "appliance", 0.70, 0.55, 1.70),
    "bath_freestanding": Component(
        "Freestanding Bath", "appliance", 0.75, 0.60, 1.70,
        ["victorian", "edwardian", "georgian"],
        description="Roll-top or claw-foot freestanding bath.",
    ),
    "shower_enclosure": Component("Shower Enclosure", "appliance", 0.90, 2.00, 0.90),
    "basin": Component("Wash Basin", "appliance", 0.55, 0.85, 0.45),
    "kitchen_sink": Component("Kitchen Sink", "appliance", 0.60, 0.90, 0.50),
    "belfast_sink": Component(
        "Belfast Sink", "appliance", 0.60, 0.25, 0.46,
        ["victorian", "farmhouse", "cottage"],
        description="Deep ceramic butler/Belfast sink.",
    ),
    "range_cooker": Component("Range Cooker", "appliance", 0.90, 0.90, 0.60),
    "fridge": Component("Refrigerator", "appliance", 0.60, 1.70, 0.65),
    "washing_machine": Component("Washing Machine", "appliance", 0.60, 0.85, 0.60),
    "dishwasher": Component("Dishwasher", "appliance", 0.60, 0.85, 0.58),
    "boiler": Component("Boiler", "appliance", 0.50, 0.80, 0.40),
}


# ── ROOF FEATURES ─────────────────────────────────────────────────

ROOF_FEATURES: dict[str, Component] = {
    "chimney_brick": Component(
        "Brick Chimney Stack", "roof_feature", 0.80, 2.00, 0.60,
        ["georgian", "victorian", "edwardian"],
        description="Brick chimney stack with multiple flues and clay pots.",
    ),
    "chimney_stone": Component(
        "Stone Chimney Stack", "roof_feature", 0.90, 1.80, 0.70,
        ["medieval", "cottage", "vernacular"],
    ),
    "dormer_gable": Component(
        "Gable Dormer", "roof_feature", 1.20, 1.80, 1.50,
        ["georgian", "victorian"],
    ),
    "dormer_hip": Component(
        "Hipped Dormer", "roof_feature", 1.20, 1.50, 1.50,
        ["georgian", "regency"],
    ),
    "cupola": Component(
        "Cupola", "roof_feature", 2.00, 3.00, 2.00,
        ["classical", "georgian", "baroque"],
        description="Small domed structure on roof for ventilation or decoration.",
    ),
    "bellcote": Component(
        "Bellcote", "roof_feature", 0.80, 1.50, 0.40,
        ["church", "chapel", "medieval"],
        description="Small bell housing on the ridge of a church roof.",
    ),
    "finial": Component(
        "Roof Finial", "roof_feature", 0.15, 0.50, 0.15,
        ["victorian", "gothic", "tudor"],
    ),
    "weathervane": Component(
        "Weathervane", "roof_feature", 0.60, 1.00, 0.05,
        ["all"],
    ),
}


# ── ARCHITECTURAL DETAILS ─────────────────────────────────────────

ARCHITECTURAL_DETAILS: dict[str, Component] = {
    "cornice_dentil": Component(
        "Dentil Cornice", "detail", 0.0, 0.20, 0.30,
        ["georgian", "classical", "neoclassical"],
        description="Projecting cornice with tooth-like blocks.",
    ),
    "quoins": Component(
        "Quoins", "detail", 0.30, 0.0, 0.35,
        ["georgian", "classical"],
        description="Dressed stone blocks at building corners.",
    ),
    "pilaster": Component(
        "Pilaster", "detail", 0.30, 0.0, 0.10,
        ["georgian", "classical", "neoclassical"],
        description="Flat column projecting from wall face.",
    ),
    "column_doric": Component(
        "Doric Column", "detail", 0.35, 3.00, 0.35,
        ["classical", "georgian", "greek_revival"],
    ),
    "column_ionic": Component(
        "Ionic Column", "detail", 0.30, 3.20, 0.30,
        ["classical", "georgian", "neoclassical"],
    ),
    "column_corinthian": Component(
        "Corinthian Column", "detail", 0.30, 3.50, 0.30,
        ["classical", "baroque", "neoclassical"],
    ),
    "arch_round": Component(
        "Round Arch", "detail", 0.0, 0.0, 0.35,
        ["romanesque", "classical", "georgian"],
        description="Semicircular arch.",
    ),
    "arch_pointed": Component(
        "Pointed Arch", "detail", 0.0, 0.0, 0.35,
        ["gothic", "church", "medieval"],
        description="Gothic pointed arch (lancet, equilateral, or ogee).",
        variants=["lancet", "equilateral", "ogee", "tudor_4_centred"],
    ),
    "buttress": Component(
        "Buttress", "detail", 0.60, 0.0, 1.00,
        ["gothic", "church", "medieval"],
        description="Masonry support projecting from wall.",
        variants=["clasping", "diagonal", "flying"],
    ),
    "crenellation": Component(
        "Crenellation/Battlement", "detail", 0.60, 0.90, 0.45,
        ["castle", "fortified", "gothic"],
        description="Alternating merlons and embrasures atop a wall.",
    ),
    "balustrade": Component(
        "Balustrade", "detail", 0.0, 0.90, 0.15,
        ["georgian", "regency", "classical"],
        description="Row of balusters supporting a handrail.",
    ),
    "fanlight": Component(
        "Fanlight", "detail", 0.90, 0.50, 0.05,
        ["georgian", "regency"],
        description="Semi-circular glazed panel above a door.",
    ),
    "portico": Component(
        "Portico", "detail", 3.00, 3.50, 1.50,
        ["georgian", "classical", "neoclassical"],
        description="Roofed entrance porch supported by columns.",
    ),
    "porch_tudor": Component(
        "Tudor Porch", "detail", 2.00, 2.50, 1.50,
        ["tudor", "medieval"],
        description="Timber-framed porch with gabled roof.",
    ),
}


def get_components_for_style(style: str) -> dict[str, list[Component]]:
    """Get all components applicable to a given architectural style.

    Returns dict keyed by category with lists of matching components.
    """
    result: dict[str, list[Component]] = {}

    all_catalogues = {
        "doors": DOORS,
        "windows": WINDOWS,
        "walls": WALLS,
        "fireplaces": FIREPLACES,
        "furniture": FURNITURE,
        "appliances": APPLIANCES,
        "roof_features": ROOF_FEATURES,
        "architectural_details": ARCHITECTURAL_DETAILS,
    }

    for cat_name, catalogue in all_catalogues.items():
        matches = []
        for key, comp in catalogue.items():
            if not comp.styles or "all" in comp.styles or style in comp.styles:
                matches.append(comp)
        if matches:
            result[cat_name] = matches

    return result
