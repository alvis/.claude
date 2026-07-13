import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from install_agents import discover_agent_templates, install_agents
from stitch_agent import AgentTemplateError, stitch_agent_definition


def write_template(plugin_root: Path, name: str, frontmatter: dict, body: str = "# Body\n") -> Path:
    template = plugin_root / "templates/agents" / name
    (template / "frontmatter").mkdir(parents=True)
    (template / "frontmatter/claude.json").write_text(
        json.dumps(frontmatter), encoding="utf-8"
    )
    (template / "base.md").write_text(body, encoding="utf-8")
    return template


class StitchAgentDefinitionTest(unittest.TestCase):
    def test_stitches_nested_json_lists_and_multiline_strings_deterministically(self):
        with tempfile.TemporaryDirectory() as temporary:
            template = write_template(
                Path(temporary),
                "test-agent",
                {
                    "name": "test-agent",
                    "description": "first line\nsecond line",
                    "tools": ["Read", "Bash"],
                    "emptyObject": {},
                    "emptyList": [],
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {"type": "prompt", "prompt": "review: yes\nthen stop"}
                                ]
                            }
                        ]
                    },
                },
                "\n\n# Test agent\n",
            )

            stitched = stitch_agent_definition(template)

            frontmatter_text = stitched.split("---\n", 2)[1]
            self.assertEqual(
                json.loads((template / "frontmatter/claude.json").read_text()),
                json.loads(frontmatter_text),
            )
            self.assertTrue(stitched.endswith("---\n\n# Test agent\n"))
            self.assertEqual(stitched, stitch_agent_definition(template))

    def test_rejects_missing_base_invalid_json_and_directory_name_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing = root / "templates/agents/missing"
            (missing / "frontmatter").mkdir(parents=True)
            (missing / "frontmatter/claude.json").write_text(
                '{"name":"missing"}', encoding="utf-8"
            )
            with self.assertRaisesRegex(AgentTemplateError, "base.md"):
                stitch_agent_definition(missing)

            invalid = root / "templates/agents/invalid"
            (invalid / "frontmatter").mkdir(parents=True)
            (invalid / "frontmatter/claude.json").write_text("{", encoding="utf-8")
            (invalid / "base.md").write_text("body", encoding="utf-8")
            with self.assertRaisesRegex(AgentTemplateError, "invalid JSON"):
                stitch_agent_definition(invalid)

            mismatch = write_template(root, "directory-name", {"name": "other-name"})
            with self.assertRaisesRegex(AgentTemplateError, "does not match"):
                stitch_agent_definition(mismatch)

            nonstandard_number = write_template(
                root, "nonstandard-number", {"name": "nonstandard-number"}
            )
            (nonstandard_number / "frontmatter/claude.json").write_text(
                '{"name":"nonstandard-number","maxTurns":NaN}', encoding="utf-8"
            )
            with self.assertRaisesRegex(AgentTemplateError, "invalid JSON"):
                stitch_agent_definition(nonstandard_number)


class AgentDiscoveryTest(unittest.TestCase):
    def test_installed_mode_reports_plugin_list_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            essential = Path(temporary) / "cache/alvis/essential/1"
            essential.mkdir(parents=True)
            cases = (
                (OSError("missing"), "cannot list installed plugins"),
                (
                    subprocess.CompletedProcess([], 1, stdout="", stderr="failed"),
                    "cannot list installed plugins: failed",
                ),
                (
                    subprocess.CompletedProcess([], 0, stdout="{", stderr=""),
                    "invalid JSON from claude plugin list",
                ),
                (
                    subprocess.CompletedProcess([], 0, stdout="{}", stderr=""),
                    "did not return a list",
                ),
            )
            for result, message in cases:
                with self.subTest(message=message), patch(
                    "install_agents.subprocess.run",
                    side_effect=result if isinstance(result, OSError) else None,
                    return_value=None if isinstance(result, OSError) else result,
                ):
                    with self.assertRaisesRegex(AgentTemplateError, message):
                        discover_agent_templates(essential)

    def test_source_checkout_discovers_the_distributed_twenty_agent_roster(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")
        owners = {}
        for template in templates:
            owners.setdefault(template.owner, set()).add(template.name)

        self.assertEqual(20, len(templates))
        self.assertEqual(
            {
                "essential": 2,
                "coding": 8,
                "governance": 2,
                "web": 3,
                "backend": 4,
                "specification": 1,
            },
            {owner: len(names) for owner, names in owners.items()},
        )

    def test_each_distributed_agent_has_an_owner_routing_row(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")
        instructions = {
            owner: (ROOT / "plugins" / owner / "CLAUDE.md").read_text(encoding="utf-8")
            for owner in {template.owner for template in templates}
        }

        for template in templates:
            self.assertIn(f"`{template.name}` |", instructions[template.owner])

    def test_installed_mode_uses_only_enabled_plugins_from_essential_marketplace(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            essential = root / "cache/alvis/essential/1"
            web = root / "cache/alvis/web/1"
            disabled = root / "cache/alvis/backend/1"
            other = root / "cache/other/coding/1"
            for path in (essential, web, disabled, other):
                path.mkdir(parents=True)
            write_template(essential, "essential-agent", {"name": "essential-agent"})
            write_template(web, "web-agent", {"name": "web-agent"})
            write_template(disabled, "disabled-agent", {"name": "disabled-agent"})
            write_template(other, "other-agent", {"name": "other-agent"})
            records = [
                {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
                {"id": "web@alvis", "enabled": True, "installPath": str(web)},
                {"id": "backend@alvis", "enabled": False, "installPath": str(disabled)},
                {"id": "coding@other", "enabled": True, "installPath": str(other)},
            ]

            templates = discover_agent_templates(essential, records)

            self.assertEqual(
                {"essential:essential-agent", "web:web-agent"},
                {f"{template.owner}:{template.name}" for template in templates},
            )

    def test_installed_mode_rejects_wrong_or_ambiguous_essential_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            essential = Path(temporary) / "cache/alvis/essential/1"
            essential.mkdir(parents=True)
            wrong_identity = [
                {"id": "other@alvis", "enabled": True, "installPath": str(essential)}
            ]
            with self.assertRaisesRegex(AgentTemplateError, "essential plugin"):
                discover_agent_templates(essential, wrong_identity)

            duplicate_identity = [
                {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
                {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
            ]
            with self.assertRaisesRegex(AgentTemplateError, "multiple essential"):
                discover_agent_templates(essential, duplicate_identity)


class InstallAgentsTest(unittest.TestCase):
    def test_template_symlink_cannot_escape_its_plugin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            essential = root / "repo/plugins/essential"
            templates = essential / "templates/agents"
            templates.mkdir(parents=True)
            external = write_template(
                root / "external", "escaped-agent", {"name": "escaped-agent"}
            )
            (templates / "escaped-agent").symlink_to(external, target_is_directory=True)

            with self.assertRaisesRegex(AgentTemplateError, "symlink"):
                install_agents(essential, root / "destination")

    def test_existing_destination_symlink_is_replaced_not_followed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            essential = root / "repo/plugins/essential"
            destination = root / "destination"
            destination.mkdir()
            external = root / "external.md"
            external.write_text("do not overwrite", encoding="utf-8")
            target = destination / "current-agent.md"
            target.symlink_to(external)
            write_template(
                essential, "current-agent", {"name": "current-agent"}, "# Current\n"
            )

            install_agents(essential, destination)

            self.assertFalse(target.is_symlink())
            self.assertIn("# Current", target.read_text(encoding="utf-8"))
            self.assertEqual("do not overwrite", external.read_text(encoding="utf-8"))

    def test_shell_entrypoint_resolves_essential_plugin_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "agents"
            completed = subprocess.run(
                [str(SCRIPTS / "install-agents.sh"), "--destination", str(destination)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual(20, len(list(destination.glob("*.md"))))

    def test_source_checkout_installs_all_twenty_agents(self):
        with tempfile.TemporaryDirectory() as temporary, redirect_stdout(StringIO()):
            destination = Path(temporary) / "agents"

            count = install_agents(ROOT / "plugins/essential", destination)

            self.assertEqual(20, count)
            self.assertEqual(20, len(list(destination.glob("*.md"))))
            self.assertTrue((destination / "priya-sharma-frontend-implementer.md").is_file())

    def test_duplicate_names_fail_before_any_destination_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            essential = root / "repo/plugins/essential"
            web = root / "repo/plugins/web"
            destination = root / "home/.claude/agents"
            destination.mkdir(parents=True)
            existing = destination / "duplicate.md"
            existing.write_text("original", encoding="utf-8")
            write_template(essential, "duplicate", {"name": "duplicate"}, "essential")
            write_template(web, "duplicate", {"name": "duplicate"}, "web")

            with self.assertRaisesRegex(AgentTemplateError, "duplicate"):
                install_agents(essential, destination)

            self.assertEqual("original", existing.read_text(encoding="utf-8"))
            self.assertEqual([existing], list(destination.iterdir()))

    def test_rerun_overwrites_discovered_agents_without_pruning_other_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            essential = root / "repo/plugins/essential"
            destination = root / "home/.claude/agents"
            destination.mkdir(parents=True)
            unrelated = destination / "personal-agent.md"
            stale = destination / "formerly-managed.md"
            unrelated.write_text("personal", encoding="utf-8")
            stale.write_text("stale", encoding="utf-8")
            template = write_template(
                essential, "current-agent", {"name": "current-agent"}, "# Version one\n"
            )

            self.assertEqual(1, install_agents(essential, destination))
            (template / "base.md").write_text("# Version two\n", encoding="utf-8")
            self.assertEqual(1, install_agents(essential, destination))

            self.assertIn(
                "# Version two", (destination / "current-agent.md").read_text(encoding="utf-8")
            )
            self.assertEqual("personal", unrelated.read_text(encoding="utf-8"))
            self.assertEqual("stale", stale.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
