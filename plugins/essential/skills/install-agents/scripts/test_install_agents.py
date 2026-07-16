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
from stitch_agent import (
    AgentTemplateError,
    stitch_agent_definition,
    validate_agent_contract,
)


def write_template(plugin_root: Path, name: str, frontmatter: dict, body: str = "# Body\n") -> Path:
    template = plugin_root / "templates/agents" / name
    (template / "frontmatter").mkdir(parents=True)
    tools = frontmatter.get("tools")
    if isinstance(tools, list) and "SendMessage" not in tools:
        tools.append("SendMessage")
    elif isinstance(tools, str) and "SendMessage" not in tools.split(", "):
        frontmatter["tools"] = f"{tools}, SendMessage"
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

    def test_rejects_haiku_effort_fixed_routing_and_tool_mismatches(self):
        cases = (
            (
                {"name": "test-agent", "model": "haiku", "effort": "medium"},
                "A role-specific body.",
                "haiku agents must omit effort",
            ),
            (
                {"name": "test-agent", "tools": ["Read"]},
                "I hand results over SendMessage.",
                "mentions SendMessage but its tools omit it",
            ),
            (
                {"name": "test-agent", "tools": ["Read", "Agent"]},
                "A role-specific body.",
                "explicit tools must include SendMessage",
            ),
            (
                {"name": "test-agent"},
                "I only spawn fixed-reviewer.",
                "fixed routing language conflicts with runtime discovery",
            ),
            (
                {
                    "name": "test-agent",
                    "description": "Always route reviews to fixed-reviewer",
                    "initialPrompt": "Only spawn fixed-reviewer for review",
                },
                "A role-specific body.",
                "fixed routing language conflicts with runtime discovery",
            ),
        )

        for frontmatter, body, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(
                AgentTemplateError, message
            ):
                validate_agent_contract(frontmatter, body)

    def test_rejects_shared_delegation_policy_in_agent_body(self):
        for phrase in (
            "current `Agent` roster",
            "When I need a Dynamic Workflow",
            "For changed code, I inspect",
            "REVIEWED: source=",
            "I hold the `Agent` tool",
            "I hold `Agent`",
            "spawn target",
            "spawned by",
        ):
            with self.subTest(phrase=phrase), self.assertRaisesRegex(
                AgentTemplateError, "repeats shared delegation policy"
            ):
                validate_agent_contract({"name": "test-agent"}, phrase)

    def test_review_hook_requires_concrete_defaults_and_review_action(self):
        def frontmatter(prompt):
            return {
                "name": "test-agent",
                "hooks": {"Stop": [{"hooks": [{"prompt": prompt}]}]},
            }

        with self.assertRaisesRegex(AgentTemplateError, "concrete reviewer defaults"):
            validate_agent_contract(
                frontmatter("You are the review-routing gate. Use named defaults."),
                "A role-specific body.",
            )

        with self.assertRaisesRegex(AgentTemplateError, "independent review action"):
            validate_agent_contract(
                frontmatter(
                    "You are the review-routing gate. Use Marcus Williams "
                    "(Code Quality Critic; reviews changed code) as proven defaults, "
                    "but choose a better runtime specialist when available."
                ),
                "A role-specific body.",
            )


class AgentDiscoveryTest(unittest.TestCase):
    def test_frontend_routing_uses_requested_deliverable_not_shared_nouns(self):
        web = ROOT / "plugins/web"
        routing = (web / "references/ROUTING.md").read_text(encoding="utf-8")
        instructions = (web / "CLAUDE.md").read_text(encoding="utf-8")
        coco = json.loads(
            (
                web
                / "templates/agents/coco-laurent-frontend-designer/frontmatter/claude.json"
            ).read_text(encoding="utf-8")
        )
        priya = json.loads(
            (
                web
                / "templates/agents/priya-sharma-frontend-implementer/frontmatter/claude.json"
            ).read_text(encoding="utf-8")
        )

        self.assertIn("classify the requested deliverable", instructions)
        self.assertIn("Do not route an implementation request to a designer", instructions)
        self.assertIn("with or without a prior design handoff", routing)
        self.assertIn("Never use Coco to create or edit production React/TypeScript", coco["description"])
        self.assertIn("whether or not an approved design exists", priya["description"])
        self.assertIn("If none exists, proceed", priya["initialPrompt"])

    def test_essential_runtime_context_uses_measured_dynamic_delegation(self):
        essential = ROOT / "plugins/essential"
        shared_context = "\n".join(
            (essential / name).read_text(encoding="utf-8")
            for name in ("CLAUDE.md", "MAINAGENT.md", "SUBAGENT.md")
        )

        self.assertIn("current `Agent` roster", shared_context)
        self.assertIn("REVIEWED: source=<specialist|general|external|none>", shared_context)
        self.assertNotIn("75%", shared_context)
        self.assertNotIn("~200k", shared_context)

    def test_session_start_actually_injects_essential_runtime_context(self):
        essential = ROOT / "plugins/essential"
        completed = subprocess.run(
            [
                str(essential / "bin/session-start"),
                "--plugin-dir",
                str(essential),
                "--constitution-paths",
                str(essential),
            ],
            input='{"source":"startup"}',
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        context = json.loads(completed.stdout)["hookSpecificOutput"][
            "additionalContext"
        ]
        self.assertIn("Discover before dispatching", context)
        self.assertIn("REVIEWED: source=<specialist|general|external|none>", context)
        self.assertNotIn("75%", context)

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

    def test_source_checkout_discovers_the_distributed_twenty_three_agent_roster(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")
        owners = {}
        for template in templates:
            owners.setdefault(template.owner, set()).add(template.name)

        self.assertEqual(23, len(templates))
        self.assertEqual(
            {
                "essential": 1,
                "coding": 9,
                "governance": 2,
                "web": 6,
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

    def test_distributed_agents_satisfy_the_delegation_contract(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")

        for template in templates:
            with self.subTest(agent=template.name):
                stitch_agent_definition(template.path)

    def test_distributed_collaboration_sections_are_point_form_only(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")

        for template in templates:
            body = (template.path / "base.md").read_text(encoding="utf-8")
            collaboration = body.split("\n## Collaboration\n", 1)[1]
            lines = [line for line in collaboration.splitlines() if line.strip()]
            with self.subTest(agent=template.name):
                self.assertTrue(lines)
                self.assertTrue(all(line.startswith("- ") for line in lines), lines)

    def test_only_true_leaf_roles_omit_agent_and_every_role_can_handoff(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")
        expected_leaves = {
            "ada-bishop-initializer",
            "ava-thompson-testing-evangelist",
            "kai-raven-adversarial-redteam",
            "penelope-sterling-aesthetic-evaluator",
            "sam-taylor-specification",
            "tess-park-test-runner",
        }
        actual_leaves = set()

        for template in templates:
            frontmatter = json.loads(
                (template.path / "frontmatter/claude.json").read_text(encoding="utf-8")
            )
            tools = frontmatter.get("tools")
            if tools is not None:
                self.assertIn("SendMessage", tools, template.name)
                if "Agent" not in tools:
                    actual_leaves.add(template.name)

        self.assertEqual(expected_leaves, actual_leaves)

    def test_changed_code_gates_use_runtime_review_routing(self):
        templates = discover_agent_templates(ROOT / "plugins/essential")
        gated_agents = set()
        expected_defaults = {
            "ethan-kumar-data-architect": (
                "Zara Ahmad (ML Engineer; data analysis and ML/AI features)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "james-mitchell-service-implementation": (
                "Marcus Williams (Code Quality Critic; reviews changed code)",
                "Nina Petrov (Security Champion; deep security review, explicit request only)",
            ),
            "zara-ahmad-ml-engineer": (
                "Ethan Kumar (Data Architect; designs schemas and data pipelines)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "leo-fabbri-generalist-engineer": (
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "theo-nakamura-desktop-implementer": (
                "Penelope Sterling (Aesthetic Evaluator; reviews UI fidelity)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "mila-vasquez-mobile-implementer": (
                "Penelope Sterling (Aesthetic Evaluator; reviews UI fidelity)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "ava-thompson-testing-evangelist": (
                "Dexter Cho (Harness & Eval Engineer; builds quality gates)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "felix-anderson-devops": (
                "Nina Petrov (Security Champion; deep security review, explicit request only)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "maya-rodriguez-principal": (
                "Nina Petrov (Security Champion; deep security review, explicit request only)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "dexter-cho-harness-eval-engineer": (
                "Ava Thompson (Testing Evangelist; authors tests)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
            "priya-sharma-frontend-implementer": (
                "Penelope Sterling (Aesthetic Evaluator; reviews UI fidelity)",
                "Marcus Williams (Code Quality Critic; reviews changed code)",
            ),
        }

        for template in templates:
            frontmatter = json.loads(
                (template.path / "frontmatter/claude.json").read_text(encoding="utf-8")
            )
            for matcher in frontmatter.get("hooks", {}).get("Stop", []):
                for hook in matcher.get("hooks", []):
                    prompt = hook.get("prompt", "")
                    if "review-routing gate" not in prompt:
                        continue
                    gated_agents.add(template.name)
                    self.assertIn("current Agent roster", prompt)
                    self.assertIn("source=<specialist|general|external|none>", prompt)
                    self.assertIn("configured external review tool", prompt)
                    self.assertIn("independently inspect the changed artifact", prompt)
                    self.assertIn("return verdict ok or blocked with findings", prompt)
                    self.assertNotIn("named collaborators are defaults", prompt)
                    collaboration = (template.path / "base.md").read_text(
                        encoding="utf-8"
                    ).split("\n## Collaboration\n", 1)[1]
                    for reviewer in expected_defaults[template.name]:
                        self.assertIn(reviewer, prompt)
                        self.assertIn(reviewer, collaboration)
                    self.assertNotIn("REVIEWED: marcus", prompt)

        self.assertEqual(set(expected_defaults), gated_agents)

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
            self.assertEqual(23, len(list(destination.glob("*.md"))))

    def test_source_checkout_installs_all_twenty_three_agents(self):
        with tempfile.TemporaryDirectory() as temporary, redirect_stdout(StringIO()):
            destination = Path(temporary) / "agents"

            count = install_agents(ROOT / "plugins/essential", destination)

            self.assertEqual(23, count)
            self.assertEqual(23, len(list(destination.glob("*.md"))))
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
            (template / "base.md").write_text(
                "# Version two\n",
                encoding="utf-8",
            )
            self.assertEqual(1, install_agents(essential, destination))

            self.assertIn(
                "# Version two", (destination / "current-agent.md").read_text(encoding="utf-8")
            )
            self.assertEqual("personal", unrelated.read_text(encoding="utf-8"))
            self.assertEqual("stale", stale.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
