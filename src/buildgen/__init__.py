"""buildgen — Procedural 3D building generator.

Generates realistic buildings with full architectural detail across
a wide range of types, styles, and historical periods.

Pipeline stages:
    1. ProgramGenerator  — building type + constraints -> room adjacency graph
    2. LayoutEngine       — room graph + footprint -> 2D floor plans
    3. GeometryBuilder    — floor plans + style -> 3D mesh
    4. StyleLibrary       — style parameter management

Public API:
    - Pipeline: end-to-end generation
    - BuildingProgram, RoomSpec, FloorPlan, Building3D: core data types
    - ProgramGenerator, LayoutEngine, GeometryBuilder: pipeline stages
    - StyleLibrary, StyleParams: style management
"""

__version__ = "0.1.0"
