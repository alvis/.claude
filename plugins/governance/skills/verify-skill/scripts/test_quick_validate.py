from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("quick_validate.py")
SPEC = importlib.util.spec_from_file_location("quick_validate", MODULE_PATH)
assert SPEC and SPEC.loader
quick_validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quick_validate)


class QuickValidateTests(unittest.TestCase):
    def write_skill(self, root: Path, name: str, description: str, body: str) -> Path:
        path = root / "skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            f'---\nname: {name}\ndescription: "{description}"\n---\n\n{body}\n',
            encoding="utf-8",
        )
        return path

    def test_discovers_skills_from_plugins_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.write_skill(
                root / "plugins" / "one",
                "first",
                "Use when creating a focused reusable capability for a known workflow.",
                "# First\n\n## Workflow\n\nDo the work.",
            )
            second = self.write_skill(
                root / "plugins" / "two",
                "second",
                "Use when maintaining a focused reusable capability for an existing workflow.",
                "# Second\n\n## Workflow\n\nDo the work.",
            )

            self.assertEqual(
                quick_validate.discover_skills(root / "plugins"),
                [first.resolve(), second.resolve()],
            )

    def test_accepts_minimal_skill_without_ceremony(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(
                Path(directory),
                "minimal",
                "Use when a concise reusable workflow needs clear boundaries and verification.",
                "# Minimal\n\n## Boundaries\n\nStay scoped.\n\n"
                "## Inputs\n\nA target.\n\n## Workflow\n\nPerform it.\n\n"
                "## Verification\n\nCheck the result.\n\n## Completion\n\nReport it.",
            )

            report = quick_validate.validate_policy(skill)

            self.assertEqual(report["errors"], [])
            messages = "\n".join(issue["message"] for issue in report["warnings"])
            self.assertNotIn("diagram", messages.lower())
            self.assertNotIn("subagent", messages.lower())
            self.assertNotIn("coherence mandate", messages.lower())

    def test_reports_placeholders_long_body_and_missing_local_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(
                Path(directory),
                "broken",
                "Use when checking a deliberately invalid repository policy fixture.",
                "# Broken\n\nSee [missing](references/missing.md).\n\n[TODO]\n"
                + "\n".join("line" for _ in range(501)),
            )

            report = quick_validate.validate_policy(skill)
            messages = "\n".join(issue["message"] for issue in report["errors"])

            self.assertIn("Unresolved local reference", messages)
            self.assertIn("Placeholder", messages)
            self.assertIn("500 lines", messages)

    def test_marketplace_validation_includes_manifest_and_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marketplace = root / ".claude-plugin" / "marketplace.json"
            marketplace.parent.mkdir()
            marketplace.write_text("{}", encoding="utf-8")
            for name in ("one", "two"):
                manifest = root / "plugins" / name / ".claude-plugin" / "plugin.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text("{}", encoding="utf-8")

            self.assertEqual(
                quick_validate.claude_targets(root),
                [
                    root.resolve(),
                    (root / "plugins" / "one").resolve(),
                    (root / "plugins" / "two").resolve(),
                ],
            )

    def test_cli_runs_official_validator_for_every_target_and_propagates_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marketplace = root / ".claude-plugin" / "marketplace.json"
            marketplace.parent.mkdir()
            marketplace.write_text("{}", encoding="utf-8")
            for name in ("one", "two"):
                plugin = root / "plugins" / name
                manifest = plugin / ".claude-plugin" / "plugin.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text("{}", encoding="utf-8")
                self.write_skill(
                    plugin,
                    name,
                    "Use when testing official validation execution for every discovered plugin target.",
                    f"# {name.title()}\n\n## Workflow\n\nValidate it.",
                )

            results = [
                quick_validate.subprocess.CompletedProcess([], 0, "marketplace ok", ""),
                quick_validate.subprocess.CompletedProcess([], 1, "", "plugin failed"),
                quick_validate.subprocess.CompletedProcess([], 0, "plugin ok", ""),
            ]
            with patch.object(quick_validate.subprocess, "run", side_effect=results) as mocked:
                exit_status = quick_validate.run([str(root)])

            self.assertEqual(exit_status, 1)
            self.assertEqual(
                [call.args[0] for call in mocked.call_args_list],
                [
                    ["claude", "plugin", "validate", "--strict", str(root.resolve())],
                    [
                        "claude",
                        "plugin",
                        "validate",
                        "--strict",
                        str((root / "plugins" / "one").resolve()),
                    ],
                    [
                        "claude",
                        "plugin",
                        "validate",
                        "--strict",
                        str((root / "plugins" / "two").resolve()),
                    ],
                ],
            )


if __name__ == "__main__":
    unittest.main()
