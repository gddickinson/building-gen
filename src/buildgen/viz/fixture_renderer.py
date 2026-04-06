"""Fixture symbol rendering for floor plans."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from ..layout.fixtures import Fixture, FixtureType


# Fixture drawing symbols
FIXTURE_SYMBOLS: dict[str, str] = {
    "toilet": "WC",
    "bath": "BATH",
    "shower": "SHW",
    "basin": "BS",
    "sink": "SK",
    "cooker": "CK",
    "fridge": "FR",
    "worktop": "WT",
    "fireplace": "FP",
    "bed_single": "BED",
    "bed_double": "BED",
    "wardrobe": "WR",
    "sofa": "SOFA",
    "dining_table": "TABLE",
    "desk": "DESK",
    "washing_machine": "WM",
    "boiler": "BLR",
}


def draw_room_fixtures(ax: plt.Axes, room) -> None:
    """Draw fixture symbols inside a room."""
    if not hasattr(room, '_fixtures') or not room._fixtures:
        return

    for fixture in room._fixtures:
        draw_single_fixture(ax, fixture)


def draw_single_fixture(ax: plt.Axes, fixture: Fixture) -> None:
    """Draw a single fixture symbol."""
    x, y = fixture.x, fixture.y
    fw, fd = fixture.width, fixture.depth
    ft = fixture.fixture_type

    if ft == FixtureType.TOILET:
        cistern = patches.Rectangle(
            (x - fw / 2, y + fd / 4), fw, fd / 4,
            facecolor="white", edgecolor="#666", linewidth=0.8, zorder=6,
        )
        bowl = patches.Ellipse(
            (x, y), fw * 0.8, fd * 0.6,
            facecolor="white", edgecolor="#666", linewidth=0.8, zorder=6,
        )
        ax.add_patch(cistern)
        ax.add_patch(bowl)

    elif ft == FixtureType.BATH:
        rect = patches.FancyBboxPatch(
            (x - fw / 2, y - fd / 2), fw, fd,
            boxstyle="round,pad=0.05",
            facecolor="#E8F4F8", edgecolor="#666", linewidth=0.8, zorder=6,
        )
        ax.add_patch(rect)
        ax.text(x, y, "BATH", ha="center", va="center",
                fontsize=5, color="#666", zorder=7)

    elif ft == FixtureType.SHOWER:
        rect = patches.Rectangle(
            (x - fw / 2, y - fd / 2), fw, fd,
            facecolor="#E0F0F8", edgecolor="#666",
            linewidth=0.8, linestyle="--", zorder=6,
        )
        ax.add_patch(rect)
        ax.text(x, y, "SHW", ha="center", va="center",
                fontsize=5, color="#666", zorder=7)

    elif ft == FixtureType.BASIN:
        basin = patches.Ellipse(
            (x, y), fw * 0.8, fd * 0.8,
            facecolor="white", edgecolor="#666", linewidth=0.8, zorder=6,
        )
        ax.add_patch(basin)

    elif ft in (FixtureType.SINK, FixtureType.COOKER, FixtureType.FRIDGE,
                FixtureType.WORKTOP, FixtureType.WASHING_MACHINE):
        rect = patches.Rectangle(
            (x - fw / 2, y - fd / 2), fw, fd,
            facecolor="#F5F5F0", edgecolor="#888", linewidth=0.6, zorder=6,
        )
        ax.add_patch(rect)
        label = FIXTURE_SYMBOLS.get(ft.value, "")
        ax.text(x, y, label, ha="center", va="center",
                fontsize=4.5, color="#666", zorder=7)

    elif ft == FixtureType.FIREPLACE:
        rect = patches.Rectangle(
            (x - fw / 2, y - fd / 2), fw, fd,
            facecolor="#DDD0C0", edgecolor="#555", linewidth=1.0, zorder=6,
        )
        ax.add_patch(rect)
        opening = patches.Rectangle(
            (x - fw / 4, y - fd / 2), fw / 2, fd * 0.6,
            facecolor="#444", edgecolor="#333", linewidth=0.5, zorder=7,
        )
        ax.add_patch(opening)

    elif ft in (FixtureType.BED_SINGLE, FixtureType.BED_DOUBLE):
        rect = patches.Rectangle(
            (x - fw / 2, y - fd / 2), fw, fd,
            facecolor="#F0E8F0", edgecolor="#999", linewidth=0.6, zorder=6,
        )
        ax.add_patch(rect)
        pw = fw * 0.8
        pillow = patches.Rectangle(
            (x - pw / 2, y + fd / 2 - 0.25), pw, 0.2,
            facecolor="#E8E0E8", edgecolor="#999", linewidth=0.4, zorder=7,
        )
        ax.add_patch(pillow)
        ax.text(x, y, "BED", ha="center", va="center",
                fontsize=4.5, color="#888", zorder=7)

    else:
        rect = patches.Rectangle(
            (x - fw / 2, y - fd / 2), fw, fd,
            facecolor="#F0F0F0", edgecolor="#999",
            linewidth=0.5, zorder=6,
        )
        ax.add_patch(rect)
        label = FIXTURE_SYMBOLS.get(ft.value, ft.value[:3].upper())
        ax.text(x, y, label, ha="center", va="center",
                fontsize=4.5, color="#666", zorder=7)
