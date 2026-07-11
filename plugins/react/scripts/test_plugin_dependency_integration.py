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

    def test_react_install_and_disable_dependency_behavior(self):
        with tempfile.TemporaryDirectory() as config:
            added = self.run_claude(config, "marketplace", "add", str(ROOT))
            self.assertEqual(0, added.returncode, added.stderr)
            installed = self.run_claude(config, "install", "react@alvis")
            self.assertEqual(0, installed.returncode, installed.stderr)
            listed = self.run_claude(config, "list", "--json")
            plugins = {item["id"]: item["enabled"] for item in json.loads(listed.stdout)}
            self.assertEqual({"coding@alvis": True, "react@alvis": True}, plugins)
            blocked = self.run_claude(config, "disable", "coding@alvis")
            self.assertNotEqual(0, blocked.returncode)
            self.assertIn("still required by react", blocked.stderr + blocked.stdout)
            self.assertEqual(0, self.run_claude(config, "disable", "react@alvis").returncode)
            self.assertEqual(0, self.run_claude(config, "disable", "coding@alvis").returncode)
            listed = self.run_claude(config, "list", "--json")
            plugins = {item["id"]: item["enabled"] for item in json.loads(listed.stdout)}
            self.assertEqual({"coding@alvis": False, "react@alvis": False}, plugins)


if __name__ == "__main__":
    unittest.main()
