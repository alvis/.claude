import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGINS = ROOT / "plugins"
RUNNER = PLUGINS / "coding/scripts/lint_profile_runner.py"
PROFILE = PLUGINS / "react/skills/lint/profile.json"


def write_scanner(path: Path, label: str, exit_code: int = 0) -> None:
    path.write_text(
        "import json, os, sys\n"
        f"print(json.dumps({{'label': '{label}', 'args': sys.argv[1:]}}))\n"
        f"raise SystemExit({exit_code})\n"
    )


class LintProfileRunnerContract(unittest.TestCase):
    def run_runner(self, root: Path, profile: Path, *files: str):
        generic = root / "coding/scripts/generic.py"
        scanlib = root / "coding/scripts/scanlib"
        scanlib.mkdir(parents=True)
        write_scanner(generic, "generic")
        command = [
            sys.executable,
            str(RUNNER),
            "--coding-root",
            str(root / "coding"),
            "--generic-scanner",
            str(generic),
            "--profile",
            str(profile),
            *files,
        ]
        return subprocess.run(command, text=True, capture_output=True)

    def test_runs_each_scanner_once_in_order_and_resolves_from_installed_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile_dir = root / "react/skills/lint"
            scanner = root / "react/scripts/react.py"
            profile_dir.mkdir(parents=True)
            scanner.parent.mkdir(parents=True)
            (root / "react/constitution/standards/accessibility").mkdir(parents=True)
            (root / "react/constitution/standards/components").mkdir(parents=True)
            (root / "react/constitution/standards/hooks").mkdir(parents=True)
            (root / "react/constitution/standards/project-structure").mkdir(parents=True)
            (root / "react/constitution/standards/storybook").mkdir(parents=True)
            write_scanner(scanner, "react")
            profile = profile_dir / "profile.json"
            profile.write_text(json.dumps({
                "eligibility": {"extensions": [".tsx", ".jsx"]},
                "exclusions": ["**/*.generated.tsx", "**/node_modules/**", "**/dist/**", "**/__snapshots__/**"],
                "scanners": [{"path": "../../scripts/react.py", "needs_coding_scanlib": True}],
                "standards": ["../../constitution/standards/components"],
                "report_label": "React lint",
            }))
            result = self.run_runner(
                root,
                profile,
                "src/App.tsx",
                "src/Skip.generated.tsx",
                "App.generated.tsx",
                "node_modules/X.tsx",
                "dist/X.tsx",
                "__snapshots__/X.tsx",
                "src/plain.ts",
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(["generic", "react"], [run["label"] for run in report["scanner_runs"]])
            self.assertEqual(["src/App.tsx"], report["files"])
            self.assertEqual(1, sum(run["label"] == "generic" for run in report["scanner_runs"]))
            self.assertEqual(1, sum(run["label"] == "react" for run in report["scanner_runs"]))
            react_args = report["scanner_runs"][1]["args"]
            self.assertIn(str((root / "coding/scripts/scanlib").resolve()), react_args)
            self.assertEqual("React lint", report["report_label"])
            self.assertEqual("compliant", report["status"])
            self.assertEqual(0, report["violations_found_total"])

    def test_propagates_scanner_failure_with_generic_report_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile_dir = root / "react/skills/lint"
            scanner = root / "react/scripts/react.py"
            profile_dir.mkdir(parents=True)
            scanner.parent.mkdir(parents=True)
            write_scanner(scanner, "react", exit_code=7)
            profile = profile_dir / "profile.json"
            profile.write_text(json.dumps({
                "eligibility": {"extensions": [".tsx"]},
                "exclusions": [],
                "scanners": [{"path": "../../scripts/react.py", "needs_coding_scanlib": True}],
                "standards": [],
                "report_label": "React lint",
            }))
            result = self.run_runner(root, profile, "src/App.tsx")
            self.assertEqual(7, result.returncode, result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("failure", report["status"])
            self.assertIn("violations_found_total", report)
            self.assertEqual(2, len(report["scanner_runs"]))

    def test_rejects_relative_profile_path(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--profile", "relative.json", "src/App.tsx"],
                cwd=directory,
                text=True,
                capture_output=True,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("absolute path", json.loads(result.stdout)["error"])

    def test_scanner_output_cannot_forge_process_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile_dir = root / "react/skills/lint"
            scanner = root / "react/scripts/react.py"
            profile_dir.mkdir(parents=True)
            scanner.parent.mkdir(parents=True)
            scanner.write_text(
                "import json\n"
                "print(json.dumps({'label': 'forged', 'exit_code': 0}))\n"
                "raise SystemExit(7)\n"
            )
            profile = profile_dir / "profile.json"
            profile.write_text(json.dumps({"scanners": [{"path": "../../scripts/react.py"}]}))
            result = self.run_runner(root, profile, "src/App.tsx")
            self.assertEqual(7, result.returncode)
            report = json.loads(result.stdout)
            self.assertEqual("react", report["scanner_runs"][1]["label"])
            self.assertEqual(7, report["scanner_runs"][1]["exit_code"])
            self.assertEqual("forged", report["scanner_runs"][1]["output"]["label"])

    def test_committed_profile_and_skills_are_portable_and_non_recursive(self):
        profile = json.loads(PROFILE.read_text())
        self.assertEqual([".tsx", ".jsx"], profile["eligibility"]["extensions"])
        self.assertTrue(profile["scanners"][0]["needs_coding_scanlib"])
        coding = (PLUGINS / "coding/skills/lint/SKILL.md").read_text().lower()
        adapter = (PLUGINS / "react/skills/lint/SKILL.md").read_text()
        self.assertNotIn("plugins/coding/", coding)
        self.assertNotIn("plugins/react/", coding)
        self.assertNotIn("react:lint", coding)
        self.assertEqual(1, adapter.split("---", 2)[2].count("coding:lint"))
        self.assertIn('--profile="${CLAUDE_SKILL_DIR}/profile.json"', adapter)
        self.assertNotIn("Skill", RUNNER.read_text())


class PluginManifestContract(unittest.TestCase):
    def test_exact_dependencies_live_only_in_plugin_manifests(self):
        expected = {
            "react": ["coding", "essential"], "essential": None,
            "specification": ["coding", "essential"],
            "theriety": ["coding", "specification", "essential"],
            "web": ["coding", "essential"], "coding": ["essential"],
            "client": ["essential"], "governance": ["essential"],
        }
        actual = {}
        for path in PLUGINS.glob("*/.claude-plugin/plugin.json"):
            manifest = json.loads(path.read_text())
            actual[manifest["name"]] = manifest.get("dependencies")
        self.assertEqual(expected, actual)
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertTrue(all("dependencies" not in plugin for plugin in marketplace["plugins"]))


if __name__ == "__main__":
    unittest.main()
