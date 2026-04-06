"""Visualization and screenshot tools for buildgen.

Provides 2D floor plan rendering and 3D building screenshots
for inspecting generated buildings during development.

Public API:
    - render_floor_plan: draw a FloorPlan to PNG
    - render_all_floors: draw all floor plans side-by-side
    - screenshot_3d: render a 3D building to PNG
    - render_building_sheet: full building overview (plans + 3D views)
"""

from .floor_plan_renderer import render_floor_plan, render_all_floors
from .building_renderer import screenshot_3d, render_building_sheet

__all__ = [
    "render_floor_plan",
    "render_all_floors",
    "screenshot_3d",
    "render_building_sheet",
]
