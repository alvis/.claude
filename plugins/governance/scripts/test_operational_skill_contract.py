#!/usr/bin/env python3
"""Regression checks that consolidation preserves executable skill contracts."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OperationalSkillContractTest(unittest.TestCase):
    def test_main_skill_files_stay_below_limit_but_keep_procedure(self) -> None:
        targets = (
            "plugins/web/skills/design/SKILL.md",
            "plugins/web/skills/audit/SKILL.md",
            "plugins/web/skills/storybook/SKILL.md",
            "plugins/web/skills/css/SKILL.md",
            "plugins/client/skills/create-screen-design/SKILL.md",
            "plugins/client/skills/update-screen-design/SKILL.md",
            "plugins/governance/skills/create-agent/SKILL.md",
            "plugins/governance/skills/update-agent/SKILL.md",
            "plugins/governance/skills/create-standard/SKILL.md",
            "plugins/governance/skills/update-standard/SKILL.md",
        )
        for target in targets:
            with self.subTest(target=target):
                text = read(target)
                self.assertLess(len(text.splitlines()), 500)
                self.assertGreaterEqual(text.count("## "), 3)
                self.assertGreaterEqual(len(text.splitlines()), 30)

    def test_web_audit_matches_bundled_parser(self) -> None:
        text = read("plugins/web/skills/audit/SKILL.md")
        self.assertIn('PYTHONPATH="$SKILL_DIR/cli"', text)
        self.assertIn('--project', text)
        self.assertIn('--viewport all', text)
        self.assertIn('--cdp-url "$CDP_URL"', text)
        self.assertNotIn("[--scope=", text)
        self.assertIn("final line is the absolute path to `report.json`", text)

    def test_storybook_documents_every_script_in_order(self) -> None:
        text = read("plugins/web/skills/storybook/SKILL.md")
        scripts = (
            "detect.sh",
            "lifecycle-up.sh",
            "smoke.sh",
            "list-stories.sh",
            "capture-states.sh",
            "scrape-panels.sh",
            "ground.sh",
            "report.sh",
            "lifecycle-down.sh",
        )
        positions = [text.index(script) for script in scripts]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("spawned:true", text)
        self.assertNotIn(" Edit,", text.split("---", 2)[1])

    def test_client_contract_keeps_canonical_ids_and_safe_push(self) -> None:
        for name in ("create-screen-design", "update-screen-design"):
            text = read(f"plugins/client/skills/{name}/SKILL.md")
            self.assertIn("4555730e74b44592b77dd8a97620d3f2", text)
            self.assertIn("110161382ea64eefa46a4907574d4530", text)
            self.assertIn("collection://c7bc479b-71db-41b1-b5ab-a07c641816b5", text)
            self.assertIn("NOTION_TOKEN", text)
            self.assertIn("notion-sync diff", text)
            self.assertIn("notion-sync push", text)
            self.assertIn("ref:", text)

    def test_skill_validation_commands_are_installed_path_portable(self) -> None:
        for name in ("create-skill", "update-skill", "verify-skill"):
            text = read(f"plugins/governance/skills/{name}/SKILL.md")
            self.assertIn("${CLAUDE_SKILL_DIR}", text)
            self.assertNotIn("<governance-plugin>", text)

    def test_authoring_policy_forbids_procedure_erasure(self) -> None:
        text = read("plugins/governance/constitution/references/authoring-invariants.md")
        self.assertIn("never trim the executable contract", text)
        self.assertIn("failure behavior", text)


if __name__ == "__main__":
    unittest.main()
