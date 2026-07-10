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
        path.parent.mkdir(parents=True, exist_ok=True)
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

    def test_local_link_policy_skips_examples_and_checks_real_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            references = root / "skills" / "links" / "references"
            references.mkdir(parents=True)
            (references / "present.md").write_text("present", encoding="utf-8")
            skill = self.write_skill(
                root,
                "links",
                "Use when validating conservative local Markdown destination handling in skill policy checks.",
                "# Links\n\n"
                "Examples: [label](url), [label](…), and [section](#anchor).\n\n"
                "Read [present](references/present.md) and "
                "[missing](references/missing.md).",
            )

            report = quick_validate.validate_policy(skill)
            messages = [item["message"] for item in report["errors"]]

            self.assertEqual(messages, ["Unresolved local reference: references/missing.md"])

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

    def test_unavailable_claude_is_structured_and_other_targets_continue(self) -> None:
        targets = [Path("/plugin/one"), Path("/plugin/two")]
        completed = quick_validate.subprocess.CompletedProcess([], 0, "ok", "")
        with patch.object(
            quick_validate.subprocess,
            "run",
            side_effect=[FileNotFoundError("claude not found"), completed],
        ) as mocked:
            status, results = quick_validate.run_claude_validation(targets)

        self.assertEqual(status, 1)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(results[0]["status"], "fail")
        self.assertIn("Unable to launch Claude validator", results[0]["output"])
        self.assertEqual(results[1]["status"], "pass")

    def test_timed_out_claude_is_structured_and_other_targets_continue(self) -> None:
        targets = [Path("/plugin/one"), Path("/plugin/two")]
        timed_out = quick_validate.subprocess.TimeoutExpired(["claude"], 30)
        completed = quick_validate.subprocess.CompletedProcess([], 0, "ok", "")
        with patch.object(
            quick_validate.subprocess,
            "run",
            side_effect=[timed_out, completed],
        ) as mocked:
            status, results = quick_validate.run_claude_validation(targets)

        self.assertEqual(status, 1)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(results[0]["status"], "fail")
        self.assertIn("timed out", results[0]["output"])
        self.assertEqual(results[1]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
