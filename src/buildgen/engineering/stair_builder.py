"""Detailed staircase construction at component level.

Every individual element of a staircase:
- Treads: the horizontal boards you step on
- Risers: the vertical boards between treads
- Stringers: the diagonal beams supporting treads and risers
- Newel posts: the vertical posts at turns and ends
- Balusters: the vertical spindles of the balustrade
- Handrail: the continuous rail at hand height
- Nosing: the projecting front edge of each tread
- Wedges/glue blocks: fixing tread/riser to stringer
- Carriage: central support beam under wide stairs
- Landing: platform at top, bottom, or turns

Dimensions from BS 5395-1 (stairs), Building Regulations Part K.
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# ── Stair dimensions (BS 5395-1 / Part K) ────────────────────────

# Rise and going (private stair)
MAX_RISE = 0.220       # 220mm max riser height
MIN_GOING = 0.220      # 220mm min tread going
TYPICAL_RISE = 0.190   # 190mm typical
TYPICAL_GOING = 0.250  # 250mm typical

# 2R + G should be 550-700mm
# Pitch should not exceed 42 degrees

# Component dimensions
TREAD_T = 0.032        # 32mm tread thickness
TREAD_NOSING = 0.025   # 25mm nosing projection
RISER_T = 0.018        # 18mm riser board thickness
STRINGER_W = 0.038     # 38mm stringer width
STRINGER_H = 0.225     # 225mm stringer depth
HANDRAIL_W = 0.065     # 65mm handrail width
HANDRAIL_H = 0.075     # 75mm handrail height
HANDRAIL_HEIGHT = 0.900  # 900mm above pitch line
NEWEL_W = 0.090        # 90mm newel post square section
NEWEL_H_ABOVE = 1.000  # 1000mm above landing
BALUSTER_W = 0.032     # 32mm square baluster
BALUSTER_SPACING = 0.100  # 100mm max gap (Part K: 100mm sphere test)
LANDING_T = 0.038      # 38mm landing boards

# Minimum widths
MIN_WIDTH = 0.800      # 800mm min clear width (Part K)
TYPICAL_WIDTH = 0.860  # 860mm typical


def build_detailed_staircase(
    x: float, z: float,
    base_y: float,
    total_rise: float,
    stair_width: float = TYPICAL_WIDTH,
    stair_depth: float = 3.0,
    direction: str = "z",
    stair_type: str = "straight",
    parent: str = "",
    floor_idx: int = 0,
) -> list[Element]:
    """Build a complete staircase with every component.

    Args:
        x, z: Bottom-left corner of stairwell in plan
        base_y: Height of bottom landing
        total_rise: Total height to climb
        stair_width: Clear width between stringers
        stair_depth: Available depth for the stair run
        direction: "z" (run along depth) or "x" (run along width)
        stair_type: "straight", "quarter_turn", "half_turn"

    Returns:
        List of Element objects for every component
    """
    elements = []

    # Calculate number of steps
    num_steps = max(3, round(total_rise / TYPICAL_RISE))
    rise = total_rise / num_steps
    going = min(stair_depth / num_steps, 0.300)

    # Check 2R+G rule
    two_r_plus_g = 2 * rise + going
    if two_r_plus_g < 0.550 or two_r_plus_g > 0.700:
        # Adjust going to satisfy the rule
        going = max(0.550 - 2 * rise, min(0.700 - 2 * rise, going))
        going = max(MIN_GOING, going)

    if stair_type == "straight":
        elements = _build_straight_stair_detailed(
            x, z, base_y, num_steps, rise, going,
            stair_width, direction, parent, floor_idx,
        )
    elif stair_type == "quarter_turn":
        elements = _build_quarter_turn_detailed(
            x, z, base_y, num_steps, rise, going,
            stair_width, direction, parent, floor_idx,
        )
    elif stair_type == "half_turn":
        elements = _build_half_turn_detailed(
            x, z, base_y, num_steps, rise, going,
            stair_width, direction, parent, floor_idx,
        )

    return elements


def _build_straight_stair_detailed(
    x, z, base_y, num_steps, rise, going,
    width, direction, parent, floor_idx,
):
    """Build a straight-run stair with every component."""
    elements = []

    # ── STRINGERS (2 diagonal beams, one each side) ──
    total_run = num_steps * going
    stair_angle = math.atan2(num_steps * rise, total_run)
    stringer_length = math.hypot(total_run, num_steps * rise)

    for side, offset in [("left", 0), ("right", width + STRINGER_W)]:
        if direction == "z":
            sx = x + offset
            sz = z + total_run / 2
            sy = base_y + num_steps * rise / 2
        else:
            sx = x + total_run / 2
            sz = z + offset
            sy = base_y + num_steps * rise / 2

        elements.append(Element(
            element_type=ElementType.BEAM,
            material_name="softwood_c24",
            x=sx, y=sy, z=sz,
            length=stringer_length, width=STRINGER_W, height=STRINGER_H,
            rotation=math.degrees(stair_angle) if direction == "z" else 0,
            parent=parent + f"_stringer_{side}",
            floor_index=floor_idx,
        ))

    # ── TREADS + RISERS + NOSING ──
    for step in range(num_steps):
        step_y = base_y + (step + 1) * rise
        step_run = step * going

        if direction == "z":
            tx = x + STRINGER_W + width / 2
            tz = z + step_run + going / 2
        else:
            tx = x + step_run + going / 2
            tz = z + STRINGER_W + width / 2

        # Tread (horizontal board)
        elements.append(Element(
            element_type=ElementType.FLOORBOARD,  # Using floorboard type
            material_name="softwood_c24",
            x=tx, y=step_y - TREAD_T / 2, z=tz,
            length=width if direction == "z" else going + TREAD_NOSING,
            width=going + TREAD_NOSING if direction == "z" else width,
            height=TREAD_T,
            parent=parent + f"_tread_{step}",
            floor_index=floor_idx,
        ))

        # Riser (vertical board)
        if direction == "z":
            rz = z + step_run
        else:
            rz = tz

        elements.append(Element(
            element_type=ElementType.FLOORBOARD,
            material_name="softwood_c16",
            x=tx, y=step_y - rise / 2, z=rz if direction == "z" else tz,
            length=width if direction == "z" else RISER_T,
            width=RISER_T if direction == "z" else width,
            height=rise,
            parent=parent + f"_riser_{step}",
            floor_index=floor_idx,
        ))

    # ── NEWEL POSTS (bottom and top) ──
    for pos_name, step_offset in [("bottom", 0), ("top", num_steps)]:
        ny = base_y + step_offset * rise
        if direction == "z":
            nz = z + step_offset * going
            for side_x in [x, x + width + STRINGER_W]:
                elements.append(Element(
                    element_type=ElementType.COLUMN,
                    material_name="oak",
                    x=side_x, y=ny + NEWEL_H_ABOVE / 2, z=nz,
                    length=NEWEL_W, width=NEWEL_W,
                    height=NEWEL_H_ABOVE,
                    parent=parent + f"_newel_{pos_name}",
                    floor_index=floor_idx,
                ))
        else:
            nx = x + step_offset * going
            for side_z in [z, z + width + STRINGER_W]:
                elements.append(Element(
                    element_type=ElementType.COLUMN,
                    material_name="oak",
                    x=nx, y=ny + NEWEL_H_ABOVE / 2, z=side_z,
                    length=NEWEL_W, width=NEWEL_W,
                    height=NEWEL_H_ABOVE,
                    parent=parent + f"_newel_{pos_name}",
                    floor_index=floor_idx,
                ))

    # ── HANDRAIL (continuous rail along both sides) ──
    for side, offset in [("left", 0), ("right", width + STRINGER_W)]:
        if direction == "z":
            hx = x + offset
            hz = z + total_run / 2
        else:
            hx = x + total_run / 2
            hz = z + offset

        hy = base_y + num_steps * rise / 2 + HANDRAIL_HEIGHT

        elements.append(Element(
            element_type=ElementType.BEAM,
            material_name="oak",
            x=hx, y=hy, z=hz,
            length=stringer_length, width=HANDRAIL_W, height=HANDRAIL_H,
            parent=parent + f"_handrail_{side}",
            floor_index=floor_idx,
        ))

    # ── BALUSTERS (vertical spindles between handrail and stringer) ──
    num_balusters_per_step = max(1, int(going / BALUSTER_SPACING))
    for step in range(num_steps):
        for bi in range(num_balusters_per_step):
            step_y = base_y + (step + 0.5) * rise
            bal_t = (bi + 0.5) / num_balusters_per_step

            if direction == "z":
                bz = z + step * going + bal_t * going
                for side_x in [x + STRINGER_W / 2,
                               x + width + STRINGER_W / 2]:
                    elements.append(Element(
                        element_type=ElementType.STUD,
                        material_name="softwood_c16",
                        x=side_x,
                        y=step_y + HANDRAIL_HEIGHT / 2,
                        z=bz,
                        length=BALUSTER_W, width=BALUSTER_W,
                        height=HANDRAIL_HEIGHT,
                        parent=parent + f"_baluster",
                        floor_index=floor_idx,
                    ))

    # ── LANDING at top ──
    landing_y = base_y + num_steps * rise
    if direction == "z":
        lz = z + total_run
        elements.append(Element(
            element_type=ElementType.FLOORBOARD,
            material_name="softwood_c24",
            x=x + (width + STRINGER_W * 2) / 2,
            y=landing_y - LANDING_T / 2,
            z=lz + 0.5,
            length=width + STRINGER_W * 2,
            width=1.0,
            height=LANDING_T,
            parent=parent + "_landing",
            floor_index=floor_idx,
        ))

    return elements


def _build_quarter_turn_detailed(
    x, z, base_y, num_steps, rise, going,
    width, direction, parent, floor_idx,
):
    """Quarter-turn stair — first flight + 90° landing + second flight."""
    elements = []

    steps_1 = num_steps * 3 // 5
    steps_2 = num_steps - steps_1

    # First flight (straight)
    elems1 = _build_straight_stair_detailed(
        x, z, base_y, steps_1, rise, going,
        width, "z", parent + "_flight1", floor_idx,
    )
    elements.extend(elems1)

    # Quarter landing
    landing_y = base_y + steps_1 * rise
    landing_z = z + steps_1 * going
    elements.append(Element(
        element_type=ElementType.FLOORBOARD,
        material_name="softwood_c24",
        x=x + width / 2, y=landing_y - LANDING_T / 2, z=landing_z + width / 2,
        length=width + STRINGER_W * 2, width=width + STRINGER_W * 2,
        height=LANDING_T,
        parent=parent + "_quarter_landing",
        floor_index=floor_idx,
    ))

    # Second flight (turned 90°)
    elems2 = _build_straight_stair_detailed(
        x + width, landing_z, landing_y, steps_2, rise, going,
        width, "x", parent + "_flight2", floor_idx,
    )
    elements.extend(elems2)

    return elements


def _build_half_turn_detailed(
    x, z, base_y, num_steps, rise, going,
    width, direction, parent, floor_idx,
):
    """Half-turn (dog-leg) stair — two parallel flights + 180° landing."""
    elements = []

    steps_per_flight = num_steps // 2
    steps_2 = num_steps - steps_per_flight

    flight_width = (width - 0.050) / 2  # Two flights side by side

    # First flight going forward
    elems1 = _build_straight_stair_detailed(
        x, z, base_y, steps_per_flight, rise, going,
        flight_width, "z", parent + "_flight1", floor_idx,
    )
    elements.extend(elems1)

    # Half landing
    landing_y = base_y + steps_per_flight * rise
    landing_z = z + steps_per_flight * going
    elements.append(Element(
        element_type=ElementType.FLOORBOARD,
        material_name="softwood_c24",
        x=x + width / 2, y=landing_y - LANDING_T / 2, z=landing_z + 0.5,
        length=width + STRINGER_W * 2, width=1.0,
        height=LANDING_T,
        parent=parent + "_half_landing",
        floor_index=floor_idx,
    ))

    # Second flight going back (reversed direction)
    x2 = x + flight_width + 0.050
    elems2 = _build_straight_stair_detailed(
        x2, landing_z, landing_y, steps_2, rise, going,
        flight_width, "z", parent + "_flight2", floor_idx,
    )
    elements.extend(elems2)

    return elements
