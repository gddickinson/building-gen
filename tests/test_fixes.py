"""Regression tests for bugs fixed while adding the web interface (2026-11-11).

Each test failed before its fix; see SESSION_LOG.md for what changed.
"""
import pytest

from buildgen.pipeline import Pipeline
from buildgen.program import ProgramGenerator


def test_rules_file_is_not_listed_as_a_building_type():
    # building_type_rules.yaml is a design-rules reference, not a template: --list-types offered it and
    # generating it built an empty default box.
    types = ProgramGenerator().available_types()
    assert "building_type_rules" not in types
    assert {"townhouse", "cottage", "tavern", "victorian_terrace",
            "townhouse_reference", "grosvenor_townhouse"} <= set(types)


def test_generating_a_non_template_raises():
    with pytest.raises(ValueError):
        Pipeline().generate("building_type_rules", "georgian", 1)
