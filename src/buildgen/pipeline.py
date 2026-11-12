"""End-to-end building generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .program import ProgramGenerator, BuildingProgram
from .layout import LayoutEngine, FloorPlan
from .layout.grid_layout import generate_from_grid, load_grid_template
from .geometry import GeometryBuilder, Building3D
from .style import StyleLibrary, StyleParams


TEMPLATE_DIR = Path(__file__).parent / "program" / "templates"


@dataclass
class PipelineResult:
    """Result of a complete pipeline run."""
    program: BuildingProgram | None
    floor_plans: list[FloorPlan]
    building: Building3D
    style: StyleParams


class Pipeline:
    """End-to-end building generation pipeline.

    Supports two modes:
    1. Template mode (default): BSP subdivision from YAML room templates
    2. Grid mode: reference-based grid layout from *_reference.yaml files

    Usage:
        pipe = Pipeline()
        result = pipe.generate("townhouse", style="georgian", seed=42)
        result = pipe.generate("townhouse_reference", style="georgian", seed=42)
    """

    def __init__(self):
        self.program_gen = ProgramGenerator()
        self.layout_engine = LayoutEngine()
        self.geometry_builder = GeometryBuilder()
        self.style_library = StyleLibrary()

    def generate(
        self,
        building_type: str,
        style: str = "georgian",
        seed: int = 0,
    ) -> PipelineResult:
        """Run the full generation pipeline."""
        style_params = self.style_library.get(style)

        # Check for grid-based reference template
        grid_path = TEMPLATE_DIR / f"{building_type}.yaml"
        if grid_path.exists():
            import yaml
            with open(grid_path) as f:
                tmpl = yaml.safe_load(f)

            if tmpl.get("layout_type") == "grid":
                return self._generate_grid(
                    tmpl, building_type, style, style_params, seed
                )

        # Standard BSP pipeline
        program = self.program_gen.generate(building_type, style, seed)
        floor_plans = self.layout_engine.generate(program)

        building = self.geometry_builder.build(floor_plans, style_params)
        building.building_type = building_type
        building.style = style
        building.seed = seed

        return PipelineResult(
            program=program,
            floor_plans=floor_plans,
            building=building,
            style=style_params,
        )

    def _generate_grid(
        self,
        template: dict,
        building_type: str,
        style: str,
        style_params: StyleParams,
        seed: int,
    ) -> PipelineResult:
        """Generate from a grid-based reference template."""
        floor_plans, width, depth = generate_from_grid(template, seed, style)

        building = self.geometry_builder.build(floor_plans, style_params)
        building.building_type = building_type
        building.style = style
        building.seed = seed

        return PipelineResult(
            program=None,
            floor_plans=floor_plans,
            building=building,
            style=style_params,
        )

    def generate_and_save(
        self,
        building_type: str,
        style: str = "georgian",
        seed: int = 0,
        output_dir: str | Path = "output",
        export_3d: bool = True,
        export_plans: bool = True,
        export_sheet: bool = True,
    ) -> PipelineResult:
        """Generate a building and save all outputs."""
        result = self.generate(building_type, style, seed)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = f"{building_type}_{style}_s{seed}"

        if export_plans:
            from .viz import render_all_floors
            render_all_floors(
                result.floor_plans,
                output_dir / f"{prefix}_plans.png",
                building_title=f"{style.title()} {building_type.replace('_', ' ').title()} (seed={seed})",
            )

        if export_sheet:
            from .viz import render_building_sheet
            render_building_sheet(
                result.building,
                result.floor_plans,
                output_dir / f"{prefix}_sheet.png",
                building_title=f"{style.title()} {building_type.replace('_', ' ').title()} (seed={seed})",
            )

        if export_3d:
            result.building.export(output_dir / f"{prefix}.glb")

        from .viz import screenshot_3d
        screenshot_3d(
            result.building,
            output_dir / f"{prefix}_3d",
            angles=["perspective"],
        )

        return result
