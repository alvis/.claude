"""Run the Discover presentation validator as part of the repository suite.

The validator is a CLI module named ``test_html_templates.py`` that pytest
cannot collect (it holds no test functions and shadows the naming convention),
so ``pytest.ini`` ignores it and this wrapper imports it by path instead. Until
this file existed, the repository's own rule — every mechanical gate is a pytest
test — was false for the largest generator in the tree.

``run("complete")`` compiles a board through ``build_artifact.build``, which
downloads the Tailwind runtime unless the gitignored vendor cache holds it. CI
has a network, so the gate runs there. An offline developer gets a skip rather
than a failure that says nothing about their change.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

VALIDATOR = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "discover"
    / "scripts"
    / "test_html_templates.py"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("discover_validator", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True  # keep scripts/__pycache__ out of the tree
    spec.loader.exec_module(module)
    return module


def test_discover_presentation_contract_holds() -> None:
    assert VALIDATOR.is_file(), f"{VALIDATOR}: Discover validator is missing"
    validator = _load_validator()

    builder = validator._load_builder()
    try:
        builder.get_tailwind_runtime()
    except builder.BuildError as error:
        # An unreachable CDN with no cache is an offline developer, not a
        # contract failure; every other BuildError is a real finding.
        if "could not fetch" not in str(error):
            raise
        pytest.skip(f"Tailwind runtime unavailable offline: {error}")

    result = validator.run("complete")
    assert result["errors"] == []
    assert result["status"] == "pass"
    assert (
        result["presentation_patterns_covered"]
        == result["presentation_patterns_required"]
    )
