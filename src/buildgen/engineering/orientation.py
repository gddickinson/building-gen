"""Element orientation utilities.

Elements are axis-aligned boxes positioned at (x, y, z) with
dimensions (length, width, height). In the 3D scene:
  - length is along X
  - height is along Y (vertical)
  - width is along Z

When an element runs along the Z axis instead of X (e.g. a wall plate
on the east wall, a floorboard running north-south), we need to swap
length and width so the box is correctly oriented WITHOUT relying on
rotation transforms in the exporter.

For pitched elements (rafters), we use a special approach: the rafter
is stored as a box at its midpoint position, with its length being
the horizontal projection and height being the vertical extent.
"""

from __future__ import annotations

import math


def dims_for_direction(
    element_length: float,
    section_w: float,
    section_h: float,
    direction: str,
) -> tuple[float, float, float]:
    """Return (length, width, height) for an element running in a given direction.

    Args:
        element_length: The actual length of the element
        section_w: Cross-section width
        section_h: Cross-section height (or depth)
        direction: "x" (runs along X), "z" (runs along Z), "y" (vertical)

    Returns:
        (length_x, width_z, height_y) — the box dimensions in world axes
    """
    if direction == "x":
        return element_length, section_w, section_h
    elif direction == "z":
        # Swap length and width — element runs along Z
        return section_w, element_length, section_h
    elif direction == "y":
        # Vertical element — length becomes height
        return section_w, section_h, element_length
    else:
        return element_length, section_w, section_h


def rafter_box(
    eaves_x: float, eaves_y: float, eaves_z: float,
    ridge_x: float, ridge_y: float,
    section_w: float, section_h: float,
) -> tuple[float, float, float, float, float, float]:
    """Calculate box position and dimensions for a pitched rafter.

    A rafter runs from eaves to ridge at an angle. We represent it
    as an axis-aligned box covering its bounding box. This isn't
    perfectly accurate but prevents protrusion.

    Returns: (cx, cy, cz, length_x, width_z, height_y)
    """
    dx = ridge_x - eaves_x
    dy = ridge_y - eaves_y
    actual_length = math.hypot(dx, dy)

    # Centre position
    cx = (eaves_x + ridge_x) / 2
    cy = (eaves_y + ridge_y) / 2
    cz = eaves_z

    # Box dimensions: horizontal extent x, vertical extent y
    box_x = abs(dx) + section_h * abs(dy) / actual_length  # Width at angle
    box_y = abs(dy) + section_h * abs(dx) / actual_length  # Height at angle

    return cx, cy, cz, box_x, section_w, box_y
