"""Command-line interface for buildgen."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="buildgen",
        description="Procedural 3D building generator",
    )
    parser.add_argument(
        "--type", "-t",
        default="townhouse",
        help="Building type template name (default: townhouse)",
    )
    parser.add_argument(
        "--style", "-s",
        default="georgian",
        help="Architectural style (default: georgian)",
    )
    parser.add_argument(
        "--seed", "-S",
        type=int, default=42,
        help="Random seed for reproducible generation (default: 42)",
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--count", "-n",
        type=int, default=1,
        help="Number of buildings to generate (default: 1)",
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List available building types",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available styles",
    )

    args = parser.parse_args(argv)

    from .pipeline import Pipeline
    pipe = Pipeline()

    if args.list_types:
        print("Available building types:")
        for t in pipe.program_gen.available_types():
            print(f"  {t}")
        return

    if args.list_styles:
        print("Available styles:")
        for s in pipe.style_library.available_styles():
            print(f"  {s}")
        return

    output_dir = Path(args.output)

    for i in range(args.count):
        seed = args.seed + i
        print(f"Generating {args.type} ({args.style}) seed={seed}...")

        result = pipe.generate_and_save(
            building_type=args.type,
            style=args.style,
            seed=seed,
            output_dir=output_dir,
        )

        b = result.building
        print(f"  Floors: {b.num_floors}")
        print(f"  Footprint: {b.footprint_area:.1f}m²")
        print(f"  Total area: {b.total_floor_area:.1f}m²")
        print(f"  Rooms: {sum(len(fp.rooms) for fp in result.floor_plans)}")
        print(f"  Output: {output_dir}/")

    print("Done.")


if __name__ == "__main__":
    main()
