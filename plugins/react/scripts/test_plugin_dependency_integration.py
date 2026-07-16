import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def require_executable(name: str, /) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(f"{name} is required for plugin dependency integration tests")
    return executable


CLAUDE = require_executable("claude")


class PluginDependencyIntegration(unittest.TestCase):
    def run_claude(
        self, config: str, *args: str
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ | {"CLAUDE_CONFIG_DIR": config}
        return subprocess.run(
            [CLAUDE, "plugin", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )

    def run_installed_hooks(
        self,
        config: str,
        *,
        plugin_root: Path,
        event: str,
        input_json: str,
    ) -> tuple[subprocess.CompletedProcess[str], ...]:
        manifest = json.loads((plugin_root / ".claude-plugin/plugin.json").read_text())
        substitutions = {
            "${CLAUDE_PLUGIN_ROOT}": str(plugin_root),
            "${HOME}": os.environ["HOME"],
        }
        completed = []
        for matcher in manifest["hooks"][event]:
            for hook in matcher["hooks"]:
                command = hook["command"]
                args = hook.get("args", [])
                for key, value in substitutions.items():
                    command = command.replace(key, value)
                    args = [argument.replace(key, value) for argument in args]
                invocation = [command, *args] if args else ["/bin/bash", "-c", command]
                completed.append(
                    subprocess.run(
                        invocation,
                        cwd="/tmp",
                        env=os.environ | {"CLAUDE_CONFIG_DIR": config},
                        input=input_json,
                        text=True,
                        capture_output=True,
                    )
                )
        return tuple(completed)

    def test_react_install_and_disable_dependency_behavior(self) -> None:
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
            hooks = self.run_installed_hooks(
                config,
                plugin_root=essential_root,
                event="SessionStart",
                input_json='{"source":"startup","session_id":"integration"}',
            )
            payloads = []
            for hook in hooks:
                self.assertEqual(0, hook.returncode, hook.stderr)
                payloads.append(json.loads(hook.stdout)["hookSpecificOutput"])
            self.assertTrue(payloads)
            self.assertTrue(
                all(
                    payload["hookEventName"] == "SessionStart"
                    and payload["additionalContext"]
                    for payload in payloads
                )
            )
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
    def test_essential_session_start_emits_environment_context(self) -> None:
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
        self.assertEqual(
            {
                "hookEventName": output["hookEventName"],
                "has_context": bool(output["additionalContext"]),
            },
            {"hookEventName": "SessionStart", "has_context": True},
        )

    def test_essential_subagent_hook_emits_environment_context(self) -> None:
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
        self.assertEqual(
            {
                "hookEventName": output["hookEventName"],
                "has_context": bool(output["additionalContext"]),
            },
            {"hookEventName": "SubagentStart", "has_context": True},
        )


if __name__ == "__main__":
    unittest.main()
