"""Guttering, downpipes, and rainwater goods.

Collects rainwater from the roof and channels it to ground drains.

Components:
- Eaves gutter: half-round or ogee profile, along eaves
- Gutter brackets: fixed to fascia or rafter feet
- Downpipes: vertical pipes from gutter to drain
- Hopper heads: collect water from multiple sources
- Shoes: bottom fitting directing water into drain
- Fascia board: timber board at rafter ends (gutter fixes to this)
- Soffit: boards closing the gap under the eaves

Georgian/Victorian materials: cast iron
Modern: uPVC or aluminium

Sizing (BS EN 12056-3):
- 100mm half-round gutter: up to 37m² roof area
- 125mm half-round: up to 58m²
- 150mm half-round: up to 86m²
- 68mm round downpipe per 40m² effective roof area
"""

from __future__ import annotations

import math

from .elements import Element, ElementType


# Gutter dimensions (cast iron half-round)
GUTTER_W = 0.125             # 125mm (5") half-round
GUTTER_H = 0.065             # 65mm depth
GUTTER_T = 0.005             # 5mm wall thickness
BRACKET_SPACING = 0.900      # 900mm bracket centres

# Downpipe
DOWNPIPE_DIA = 0.075         # 75mm (3") round downpipe
DOWNPIPE_OFFSET = 0.040      # 40mm from wall face

# Fascia and soffit
FASCIA_H = 0.150             # 150mm fascia board height
FASCIA_T = 0.025             # 25mm thickness
SOFFIT_W = 0.200             # 200mm soffit width (eaves overhang)
SOFFIT_T = 0.012             # 12mm soffit thickness

# Hopper head
HOPPER_W = 0.200
HOPPER_H = 0.250
HOPPER_D = 0.150

# Shoe (bottom of downpipe)
SHOE_L = 0.200
SHOE_DIA = DOWNPIPE_DIA


def build_guttering(
    width: float,
    depth: float,
    eaves_y: float,
    roof_overhang: float = 0.300,
    material: str = "cast_iron",
    parent: str = "guttering",
) -> list[Element]:
    """Build complete rainwater goods.

    Creates:
    - Fascia boards at rafter feet (all 4 sides)
    - Soffit boards closing the eaves
    - Eaves gutters on front and back
    - Gutter brackets
    - Downpipes at corners
    - Hopper heads and shoes
    """
    elements = []

    ovh = roof_overhang

    # ── FASCIA BOARDS (timber, at rafter ends) ──
    # South/north run along X, east/west run along Z (swap L/W)
    for name, fx, fz, fl_x, fl_z in [
        ("south", width / 2, -ovh, width + ovh * 2, FASCIA_T),
        ("north", width / 2, depth + ovh, width + ovh * 2, FASCIA_T),
        ("east", width + ovh, depth / 2, FASCIA_T, depth + ovh * 2),
        ("west", -ovh, depth / 2, FASCIA_T, depth + ovh * 2),
    ]:
        elements.append(Element(
            element_type=ElementType.FLOORBOARD,
            material_name="softwood_c16",
            x=fx, y=eaves_y - FASCIA_H / 2, z=fz,
            length=fl_x, width=fl_z, height=FASCIA_H,
            parent=f"{parent}_fascia_{name}",
        ))

    # ── SOFFIT BOARDS (closing underside of eaves) ──
    for name, sx, sz, sl_x, sl_z in [
        ("south", width / 2, -ovh / 2, width + ovh * 2, SOFFIT_W),
        ("north", width / 2, depth + ovh / 2, width + ovh * 2, SOFFIT_W),
        ("east", width + ovh / 2, depth / 2, SOFFIT_W, depth + ovh * 2),
        ("west", -ovh / 2, depth / 2, SOFFIT_W, depth + ovh * 2),
    ]:
        elements.append(Element(
            element_type=ElementType.FLOORBOARD,
            material_name="softwood_c16",
            x=sx, y=eaves_y - FASCIA_H, z=sz,
            length=sl_x, width=sl_z, height=SOFFIT_T,
            parent=f"{parent}_soffit_{name}",
        ))

    # ── EAVES GUTTERS (front and back) ──
    for name, gx, gz, gl in [
        ("south", width / 2, -ovh, width + ovh * 2),
        ("north", width / 2, depth + ovh, width + ovh * 2),
    ]:
        elements.append(Element(
            element_type=ElementType.BEAM,
            material_name=material,
            x=gx, y=eaves_y - FASCIA_H - GUTTER_H / 2, z=gz,
            length=gl, width=GUTTER_W, height=GUTTER_H,
            parent=f"{parent}_gutter_{name}",
        ))

        # Gutter brackets
        num_brackets = int(gl / BRACKET_SPACING) + 1
        for bi in range(num_brackets):
            bx = (bi + 0.5) * gl / num_brackets - gl / 2 + gx
            elements.append(Element(
                element_type=ElementType.HINGE,  # Bracket
                material_name=material,
                x=bx,
                y=eaves_y - FASCIA_H - GUTTER_H / 2,
                z=gz,
                length=0.030, width=GUTTER_W, height=0.100,
                parent=f"{parent}_bracket_{name}",
            ))

    # ── DOWNPIPES (at corners, 4 total) ──
    pipe_height = eaves_y - 0.300  # From gutter to near ground
    corners = [
        ("sw", DOWNPIPE_OFFSET, -ovh - DOWNPIPE_OFFSET),
        ("se", width - DOWNPIPE_OFFSET, -ovh - DOWNPIPE_OFFSET),
        ("nw", DOWNPIPE_OFFSET, depth + ovh + DOWNPIPE_OFFSET),
        ("ne", width - DOWNPIPE_OFFSET, depth + ovh + DOWNPIPE_OFFSET),
    ]

    for name, dx, dz in corners:
        # Downpipe (vertical)
        elements.append(Element(
            element_type=ElementType.COLUMN,
            material_name=material,
            x=dx, y=pipe_height / 2, z=dz,
            length=DOWNPIPE_DIA, width=DOWNPIPE_DIA, height=pipe_height,
            parent=f"{parent}_downpipe_{name}",
        ))

        # Hopper head (at top, collects gutter water)
        elements.append(Element(
            element_type=ElementType.BEAM,
            material_name=material,
            x=dx, y=eaves_y - FASCIA_H - GUTTER_H - HOPPER_H / 2, z=dz,
            length=HOPPER_W, width=HOPPER_D, height=HOPPER_H,
            parent=f"{parent}_hopper_{name}",
        ))

        # Shoe (at bottom, directs water to drain)
        elements.append(Element(
            element_type=ElementType.BEAM,
            material_name=material,
            x=dx, y=0.100, z=dz,
            length=SHOE_DIA, width=SHOE_L, height=SHOE_DIA,
            parent=f"{parent}_shoe_{name}",
        ))

    return elements
