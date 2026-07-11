#!/usr/bin/env python3
"""Regression tests for the resolved PR review contracts."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGINS = ROOT / "plugins"
SHARED_SCRIPT_NAMES = {
    "constitution.sh",
    "context.sh",
    "reminder.sh",
    "session-start.sh",
    "user-prompt-submit.sh",
}


class PrReviewContractTest(unittest.TestCase):
    def manifests(self) -> dict[str, tuple[Path, dict[str, object]]]:
        manifests: dict[str, tuple[Path, dict[str, object]]] = {}
        for path in sorted(PLUGINS.glob("*/.claude-plugin/plugin.json")):
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifests[str(manifest["name"])] = (path, manifest)
        self.assertEqual(8, len(manifests))
        return manifests

    def test_skills_do_not_select_general_purpose_agent(self) -> None:
        offenders = [
            str(path.relative_to(ROOT))
            for path in PLUGINS.glob("*/skills/*/SKILL.md")
            if "agent: general-purpose" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual([], offenders)

    def test_manifests_keep_author_for_strict_claude_validation(self) -> None:
        missing = [
            str(path.relative_to(ROOT))
            for path, manifest in self.manifests().values()
            if "author" not in manifest
        ]
        self.assertEqual([], missing)

    def test_hook_consumers_depend_on_essential_without_cycle(self) -> None:
        manifests = self.manifests()
        for name, (_, manifest) in manifests.items():
            dependencies = manifest.get("dependencies", [])
            self.assertNotIn(name, dependencies, f"{name} must not depend on itself")
            if name != "essential" and manifest.get("hooks"):
                self.assertIn("essential", dependencies, f"{name} uses Essential hooks")
        self.assertNotIn("coding", manifests["essential"][1].get("dependencies", []))

    def test_essential_coding_routes_are_availability_checked(self) -> None:
        for path in (PLUGINS / "essential/skills").rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8")
            if "coding:" not in text:
                continue
            self.assertIn(
                "coding integration is optional",
                text.lower(),
                f"{path.relative_to(ROOT)} must not assume Coding is installed",
            )

    def test_shared_hook_scripts_are_owned_only_by_essential(self) -> None:
        essential_scripts = PLUGINS / "essential/hooks/lib"
        self.assertTrue(
            SHARED_SCRIPT_NAMES.issubset({path.name for path in essential_scripts.iterdir()})
        )
        root_scripts = {path.name for path in (ROOT / "scripts").iterdir() if path.is_file()}
        self.assertTrue(SHARED_SCRIPT_NAMES.isdisjoint(root_scripts))
        unsupported = [
            str(path.relative_to(ROOT))
            for path in PLUGINS.glob("*/shared/scripts")
            if path.exists() or path.is_symlink()
        ]
        self.assertEqual([], unsupported)

    def test_manifests_call_essential_owned_hook_executables(self) -> None:
        for name, (_, manifest) in self.manifests().items():
            hooks = manifest.get("hooks", {})
            commands = [
                hook["command"]
                for registrations in hooks.values()
                for registration in registrations
                for hook in registration.get("hooks", [])
                if hook.get("type") == "command"
            ]
            serialized_hooks = json.dumps(hooks)
            self.assertIn("alvis-session-start", serialized_hooks)
            self.assertIn("alvis-user-prompt-submit", serialized_hooks)
            if name != "essential":
                self.assertIn("claude plugin list --json", serialized_hooks)
                self.assertIn("essential@alvis", serialized_hooks)
            self.assertFalse(any("shared/scripts" in command for command in commands))

    def test_essential_hook_executables_run_for_consumer_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugin_root = Path(temporary)
            (plugin_root / "scripts").mkdir()
            (plugin_root / "scripts/context.sh").write_text(
                "get_plugin_context() { echo -n consumer-context; }\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    str(PLUGINS / "essential/bin/alvis-session-start"),
                    "--plugin-dir",
                    str(plugin_root),
                    "--constitution-paths",
                    str(plugin_root),
                ],
                input='{"source":"startup","session_id":"test"}',
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("consumer-context", completed.stdout)


if __name__ == "__main__":
    unittest.main()
