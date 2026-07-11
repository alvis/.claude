import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


@unittest.skipUnless(shutil.which("claude"), "Claude CLI is unavailable")
class PluginDependencyIntegration(unittest.TestCase):
    def run_claude(self, config: str, *args: str):
        env = os.environ | {"CLAUDE_CONFIG_DIR": config}
        return subprocess.run(["claude", "plugin", *args], cwd=ROOT, env=env, text=True, capture_output=True)

    def run_installed_hook(self, config: str, plugin_root: Path, event: str, input_json: str):
        manifest = json.loads((plugin_root / ".claude-plugin/plugin.json").read_text())
        hook = manifest["hooks"][event][0]["hooks"][0]
        substitutions = {
            "${CLAUDE_PLUGIN_ROOT}": str(plugin_root),
            "${HOME}": os.environ["HOME"],
        }
        command = hook["command"]
        args = hook.get("args", [])
        for key, value in substitutions.items():
            command = command.replace(key, value)
            args = [argument.replace(key, value) for argument in args]
        return subprocess.run(
            [command, *args],
            cwd="/tmp",
            env=os.environ | {"CLAUDE_CONFIG_DIR": config},
            input=input_json,
            text=True,
            capture_output=True,
        )

    def test_react_install_and_disable_dependency_behavior(self):
        with tempfile.TemporaryDirectory() as config:
            added = self.run_claude(config, "marketplace", "add", str(ROOT))
            self.assertEqual(0, added.returncode, added.stderr)
            installed = self.run_claude(config, "install", "react@alvis")
            self.assertEqual(0, installed.returncode, installed.stderr)
            listed = self.run_claude(config, "list", "--json")
            records = {item["id"]: item for item in json.loads(listed.stdout)}
            plugins = {name: item["enabled"] for name, item in records.items()}
            self.assertEqual(
                {"coding@alvis": True, "essential@alvis": True, "react@alvis": True},
                plugins,
            )
            essential_root = Path(records["essential@alvis"]["installPath"])
            session_hook = essential_root / "bin/session-start"
            self.assertTrue(session_hook.is_file())
            self.assertTrue(os.access(session_hook, os.X_OK))
            self.assertFalse(any((essential_root / "shared").glob("**/*")))
            consumer_root = Path(records["react@alvis"]["installPath"])
            hook = self.run_installed_hook(
                config,
                consumer_root,
                "SessionStart",
                '{"source":"startup","session_id":"integration"}',
            )
            self.assertEqual(0, hook.returncode, hook.stderr)
            self.assertIn('"hookEventName": "SessionStart"', hook.stdout)
            blocked = self.run_claude(config, "disable", "essential@alvis")
            self.assertNotEqual(0, blocked.returncode)
            dependency_error = blocked.stderr + blocked.stdout
            self.assertIn("still required by", dependency_error)
            self.assertIn("coding", dependency_error)
            blocked = self.run_claude(config, "disable", "coding@alvis")
            self.assertNotEqual(0, blocked.returncode)
            self.assertIn("still required by react", blocked.stderr + blocked.stdout)
            self.assertEqual(0, self.run_claude(config, "disable", "react@alvis").returncode)
            self.assertEqual(0, self.run_claude(config, "disable", "coding@alvis").returncode)
            self.assertEqual(0, self.run_claude(config, "disable", "essential@alvis").returncode)
            listed = self.run_claude(config, "list", "--json")
            plugins = {item["id"]: item["enabled"] for item in json.loads(listed.stdout)}
            self.assertEqual(
                {"coding@alvis": False, "essential@alvis": False, "react@alvis": False},
                plugins,
            )


if __name__ == "__main__":
    unittest.main()
