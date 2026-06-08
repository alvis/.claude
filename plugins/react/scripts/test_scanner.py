#!/usr/bin/env python3
"""Fixture-driven and loader smoke tests for the React Props scanner.

Run directly: `python3.13 plugins/react/scripts/test_scanner.py`.

The shared `scanlib` engine lives in the coding plugin; this test adds that
directory to `sys.path` exactly as the production shim does. Each
`fixtures/<dir>/` carrying an `expected.txt` is a fixture: it is scanned with
`--category <id>`, where `<id>` is read from an optional `category.txt` file
(for scenario fixtures whose directory name is not a rule id) or defaults to
the directory name. Scenario fixtures with zero matches act as true-negatives.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
CODING_SCRIPTS = SCRIPTS_DIR.parent.parent / "coding" / "scripts"
sys.path.insert(0, str(CODING_SCRIPTS))
sys.path.insert(0, str(SCRIPTS_DIR))

from scanlib.core import run
from scanlib.loader import load_rules

FIXTURES_DIR = SCRIPTS_DIR / "fixtures"


def _capture(argv: list[str], /) -> str:
    """Run the scanner with ``argv`` and return its captured stdout."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(argv)
    return buffer.getvalue()


def _capture_from(directory: Path, extra: list[str], /) -> str:
    """Run the scanner with ``directory`` as cwd, scanning `.` — relative paths."""
    original = Path.cwd()
    os.chdir(directory)
    try:
        return _capture(["."] + extra)
    finally:
        os.chdir(original)


def _fixture_category(fixture: Path, /) -> str:
    """Return the --category for a fixture: `category.txt` if present, else dir name."""
    override = fixture / "category.txt"
    if override.is_file():
        return override.read_text(encoding="utf-8").strip()
    return fixture.name


class FixtureScanTests(unittest.TestCase):
    """Every `fixtures/<dir>/` golden file matches a fresh scan."""

    def test_fixtures_match_expected(self) -> None:
        # a fixture is any `fixtures/<dir>/` carrying an `expected.txt` golden;
        # the scanned category comes from `category.txt` or the directory name.
        fixture_dirs = sorted(
            p for p in FIXTURES_DIR.iterdir()
            if p.is_dir() and (p / "expected.txt").is_file()
        )
        self.assertTrue(fixture_dirs, "no rule fixture directories discovered")
        for fixture in fixture_dirs:
            category = _fixture_category(fixture)
            expected_path = fixture / "expected.txt"
            with self.subTest(fixture=fixture.name, category=category):
                expected = expected_path.read_text(encoding="utf-8")
                actual = _capture_from(fixture, ["--category", category])
                self.assertEqual(actual, expected, f"fixture drift for {fixture.name}")


class LoaderSmokeTests(unittest.TestCase):
    """The auto-loader discovers a complete, well-formed React rule set."""

    EXPECTED_IDS = {
        "props-interface",
        "props-children-inline",
        "props-element-handrolled",
        "barrel-missing-props-reexport",
    }

    def setUp(self) -> None:
        self.rules = load_rules()

    def test_discovers_all_four_rules(self) -> None:
        self.assertEqual(len(self.rules), 4)

    def test_rule_ids_are_unique(self) -> None:
        ids = [rule.id for rule in self.rules]
        self.assertEqual(len(ids), len(set(ids)))

    def test_rule_ids_match_expected_set(self) -> None:
        self.assertEqual({rule.id for rule in self.rules}, self.EXPECTED_IDS)

    def test_rules_sorted_by_order_then_id(self) -> None:
        keys = [(rule.order, rule.id) for rule in self.rules]
        self.assertEqual(keys, sorted(keys))

    def test_blocks_helper_is_skipped(self) -> None:
        # `_blocks.py` exports no Rule and must not surface as a rule
        self.assertTrue(all(not rule.id.startswith("_") for rule in self.rules))

    def test_every_rule_is_a_category_choice(self) -> None:
        for rule in self.rules:
            with self.subTest(rule=rule.id):
                output = _capture([str(FIXTURES_DIR), "--category", rule.id])
                self.assertIn(f"  {rule.id}:", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
