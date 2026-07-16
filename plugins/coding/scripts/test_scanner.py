#!/usr/bin/env python3
"""Fixture-driven and loader smoke tests for the coding standard scanner.

Run directly: `python3.13 plugins/coding/scripts/test_scanner.py`.

Each `fixtures/<rule-id>/` directory holds an `input.*` tree plus an
`expected.txt` golden file. The fixture test scans the directory with
`--category <rule-id>` and asserts byte-identical stdout. Further suites cover
loader discovery, the auto-loader's broken-module isolation, prefix derivation,
and the byte-identical CLI-variant output contract.
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from scanlib.core import run
from scanlib.loader import load_rules
from scanlib.prefixes import FALLBACK_PREFIXES, derive_rule_id_prefixes

FIXTURES_DIR = SCRIPTS_DIR / "fixtures"
RULES = tuple(load_rules())

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


class FixtureScanTests(unittest.TestCase):
    """Every `fixtures/<rule-id>/` golden file matches a fresh scan."""

    def test_fixtures_match_expected(self) -> None:
        # a rule fixture is any `fixtures/<dir>/` carrying an `expected.txt`
        # golden — other directories (legacy ad-hoc fixtures) are ignored.
        fixture_dirs = sorted(
            p for p in FIXTURES_DIR.iterdir()
            if p.is_dir() and (p / "expected.txt").is_file()
        )
        self.assertTrue(fixture_dirs, "no rule fixture directories discovered")
        for fixture in fixture_dirs:
            rule_id = fixture.name
            expected_path = fixture / "expected.txt"
            with self.subTest(rule=rule_id):
                expected = expected_path.read_text(encoding="utf-8")
                # the golden file is generated from inside the fixture dir with `.`
                actual = _capture_from(fixture, ["--category", rule_id])
                self.assertEqual(actual, expected, f"fixture drift for {rule_id}")


class LoaderSmokeTests(unittest.TestCase):
    """The auto-loader discovers a complete, well-formed rule set."""

    def test_rule_ids_are_unique(self) -> None:
        ids = [rule.id for rule in RULES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_rules_sorted_by_order_then_id(self) -> None:
        keys = [(rule.order, rule.id) for rule in RULES]
        self.assertEqual(keys, sorted(keys))

    def test_underscore_modules_are_skipped(self) -> None:
        # no rule should carry an id starting with an underscore
        self.assertTrue(all(not rule.id.startswith("_") for rule in RULES))

    def test_every_rule_is_a_category_choice(self) -> None:
        # running with each id as --category must not raise SystemExit(2)
        for rule in RULES:
            with self.subTest(rule=rule.id):
                output = _capture([str(FIXTURES_DIR), "--category", rule.id])
                self.assertIn(f"  {rule.id}:", output)


class LoaderIsolationTests(unittest.TestCase):
    """A malformed dropped-in rule module must not crash the advisory loader."""

    def test_broken_module_is_isolated(self) -> None:
        # build a throwaway package: one module raises at import time, one is
        # a valid rule. load_rules() must skip the broken one and keep the good
        # one — no exception may propagate to the caller.
        with tempfile.TemporaryDirectory() as tmp:
            pkg_root = Path(tmp)
            pkg_dir = pkg_root / "broken_pkg"
            pkg_dir.mkdir()
            (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
            (pkg_dir / "boom.py").write_text(
                'raise RuntimeError("intentional import-time failure")\n',
                encoding="utf-8",
            )
            (pkg_dir / "good.py").write_text(
                "from pathlib import Path\n"
                "from scanlib.core import Match\n"
                "from scanlib.rule import Rule\n"
                "def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:\n"
                "    return None\n"
                'RULE = Rule(id="ok-rule", label="OK", scan=scan, order=0)\n',
                encoding="utf-8",
            )
            sys.path.insert(0, str(pkg_root))
            stderr = io.StringIO()
            try:
                with redirect_stderr(stderr):
                    rules = load_rules(package="broken_pkg")
            finally:
                sys.path.remove(str(pkg_root))
                for name in ("broken_pkg", "broken_pkg.boom", "broken_pkg.good"):
                    sys.modules.pop(name, None)
        self.assertEqual([r.id for r in rules], ["ok-rule"])
        self.assertIn("failed to load rule module boom", stderr.getvalue())


class PrefixDerivationTests(unittest.TestCase):
    """Step 7 — rule-ID prefix whitelist is derived, not hardcoded."""

    def test_derives_live_constitution_prefixes(self) -> None:
        prefixes = derive_rule_id_prefixes()
        self.assertTrue(prefixes)
        self.assertTrue(
            all(
                prefix.isupper() and prefix.replace("_", "").isalnum()
                for prefix in prefixes
            )
        )

    def test_empty_glob_falls_back(self) -> None:
        # point the deriver at an empty directory: the glob yields nothing,
        # so it must return the hardcoded FALLBACK_PREFIXES. this is the
        # branch that runs when the scanner executes outside the .claude repo.
        with tempfile.TemporaryDirectory() as tmp:
            from scanlib import prefixes

            original = prefixes._plugins_root
            prefixes._plugins_root = lambda: Path(tmp)
            try:
                derived = prefixes.derive_rule_id_prefixes()
            finally:
                prefixes._plugins_root = original
        self.assertEqual(derived, FALLBACK_PREFIXES)

    def test_fallback_matches_live_constitution(self) -> None:
        # the hardcoded fallback must agree with the live constitution so an
        # off-repo run produces the same answer as an in-repo run.
        self.assertEqual(FALLBACK_PREFIXES, derive_rule_id_prefixes())


class OutputContractTests(unittest.TestCase):
    """Lock the byte-identical CLI-variant output contract via the corpus fixture."""

    CORPUS = FIXTURES_DIR / "_corpus"

    def test_category_all_lists_every_rule_in_order(self) -> None:
        output = _capture_from(self.CORPUS, ["--category", "all"])
        positions = [output.index(f"  {rule.id}:") for rule in RULES]
        self.assertEqual(positions, sorted(positions), "summary order drifted")

    def test_no_tests_drops_spec_let_matches(self) -> None:
        # honor_no_tests path: `let` in a spec file is counted by default but
        # skipped under --no-tests; non-spec `let` matches are unaffected.
        with_tests = _capture_from(self.CORPUS, ["--category", "let"])
        without_tests = _capture_from(self.CORPUS, ["--category", "let", "--no-tests"])
        self.assertIn("feature.spec.ts", with_tests)
        self.assertNotIn("feature.spec.ts", without_tests)
        self.assertIn("source.ts", without_tests)

    def test_empty_match_renders_no_matches(self) -> None:
        # a category with zero hits must render the literal "(no matches)" block.
        output = _capture_from(self.CORPUS / "clean", ["--category", "let"])
        self.assertIn("(no matches)", output)

    def test_spec_only_rules_skip_non_spec_files(self) -> None:
        # test-hooks / test-mock-stub gate on is_spec_file: a non-spec source
        # file carrying hook-shaped text must NOT be flagged.
        hooks = _capture_from(self.CORPUS, ["--category", "test-hooks"])
        self.assertNotIn("not-a-spec.ts", hooks)
        self.assertIn("feature.spec.ts", hooks)


if __name__ == "__main__":
    unittest.main(verbosity=2)
