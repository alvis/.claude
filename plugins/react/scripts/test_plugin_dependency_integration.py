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
        invocation = [command, *args] if args else ["/bin/bash", "-c", command]
        return subprocess.run(
            invocation,
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
            self.assertTrue(
                (essential_root / "shared/scripts/subagent-start.sh").is_file()
            )
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


class EssentialHookExecutable(unittest.TestCase):
    def test_session_start_runs_for_consumer_plugin(self):
        with tempfile.TemporaryDirectory() as temporary:
            plugin_root = Path(temporary)
            (plugin_root / "scripts").mkdir()
            (plugin_root / "scripts/context.sh").write_text(
                "get_plugin_context() { echo -n consumer-context; }\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    str(ROOT / "plugins/essential/bin/session-start"),
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

    def test_essential_session_start_includes_consolidated_main_agent_instructions(self):
        completed = subprocess.run(
            [
                str(ROOT / "plugins/essential/bin/session-start"),
                "--plugin-dir",
                str(ROOT / "plugins/essential"),
                "--constitution-paths",
                str(ROOT / "plugins/essential"),
            ],
            input='{"source":"startup","session_id":"test"}',
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        output = json.loads(completed.stdout)["hookSpecificOutput"]
        self.assertEqual("SessionStart", output["hookEventName"])
        context = output["additionalContext"]
        self.assertIn("You are running as the main session", context)
        self.assertIn("greet the user a good day", context)

    def test_essential_subagent_hook_loads_consolidated_instructions(self):
        manifest = json.loads(
            (ROOT / "plugins/essential/.claude-plugin/plugin.json").read_text()
        )
        self.assertIn("SubagentStart", manifest["hooks"])

        completed = subprocess.run(
            [
                str(ROOT / "plugins/essential/bin/subagent-start"),
                "--plugin-dir",
                str(ROOT / "plugins/essential"),
                "--constitution-paths",
                str(ROOT / "plugins/essential"),
            ],
            input='{"session_id":"test"}',
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        output = json.loads(completed.stdout)["hookSpecificOutput"]
        self.assertEqual("SubagentStart", output["hookEventName"])
        context = output["additionalContext"]
        self.assertIn("You are running as a subagent or teammate", context)
        workflow_reference = str(
            (ROOT / "plugins/essential/references/workflow-tool.md").resolve()
        )
        self.assertIn(workflow_reference, context)


if __name__ == "__main__":
    unittest.main()
