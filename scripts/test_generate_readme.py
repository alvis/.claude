from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import generate_readme


class GenerateReadmeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        detail_root = self.root / "readme"
        self.patch = mock.patch.multiple(
            generate_readme,
            ROOT=self.root,
            README_PATH=self.root / "README.md",
            README_DETAIL_ROOT=detail_root,
            AGENT_TEAM_PATH=detail_root / "90-agent-team.md",
        )
        self.patch.start()

        marketplace = {
            "plugins": [
                {"source": "./plugins/alpha"},
                {"source": "./plugins/beta"},
            ]
        }
        marketplace_path = self.root / ".claude-plugin/marketplace.json"
        marketplace_path.parent.mkdir(parents=True)
        marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")
        self.write_plugin("alpha", "Alpha tools", [], "one", "First skill")
        self.write_plugin("beta", "Beta tools", ["alpha"], "two", "Second skill")
        (self.root / "README.md").write_text(
            "# Legacy overview\n\n"
            "## Agent team\n\n"
            "Maintained team introduction.\n\n"
            "### Roster\n\n"
            "| Agent | Role |\n| --- | --- |\n| lead | Lead |\n\n"
            "## Validation\n\nLegacy validation.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.patch.stop()
        self.temporary.cleanup()

    def write_plugin(
        self,
        name: str,
        description: str,
        dependencies: list[str],
        skill: str,
        skill_description: str,
    ) -> None:
        plugin = self.root / f"plugins/{name}"
        manifest = plugin / ".claude-plugin/plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "name": name,
                    "description": description,
                    "dependencies": dependencies,
                }
            ),
            encoding="utf-8",
        )
        skill_file = plugin / f"skills/{skill}/SKILL.md"
        skill_file.parent.mkdir(parents=True)
        skill_file.write_text(
            f"---\nname: {skill}\ndescription: {skill_description}\n---\n",
            encoding="utf-8",
        )

    def generated_files(self) -> dict[Path, bytes]:
        paths = [self.root / "README.md", *sorted((self.root / "readme").glob("*.md"))]
        return {path: path.read_bytes() for path in paths}

    def test_generates_small_overview_and_numbered_details_idempotently(self) -> None:
        self.assertEqual(0, generate_readme.generate(check=False))

        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(readme.encode("utf-8")), 16_384)
        self.assertIn("## Plugins and skills", readme)
        self.assertIn("## Agent team", readme)
        self.assertIn("## Install", readme)
        self.assertIn("readme/10-alpha-skills.md", readme)
        self.assertIn("readme/20-beta-skills.md", readme)
        self.assertIn("readme/90-agent-team.md", readme)
        self.assertNotIn("`alpha:one`", readme)
        self.assertIn('<a id="alpha"></a>', readme)
        self.assertIn('<a id="beta-depends-on-alpha"></a>', readme)
        self.assertIn('<a id="roster"></a>', readme)

        alpha = (self.root / "readme/10-alpha-skills.md").read_text(encoding="utf-8")
        team = (self.root / "readme/90-agent-team.md").read_text(encoding="utf-8")
        self.assertIn("`alpha:one` — First skill", alpha)
        self.assertTrue(team.startswith("# Agent team\n"))
        self.assertIn("## Roster", team)
        self.assertNotIn("### Roster", team)
        self.assertTrue(generate_readme.local_links_resolve(generate_readme.expected_outputs()))

        first_generation = self.generated_files()
        self.assertEqual(0, generate_readme.generate(check=False))
        self.assertEqual(first_generation, self.generated_files())
        self.assertEqual(0, generate_readme.generate(check=True))

    def test_check_detects_source_drift_and_generation_removes_stale_catalog(self) -> None:
        self.assertEqual(0, generate_readme.generate(check=False))
        stale = self.root / "readme/30-removed-skills.md"
        stale.write_text("stale\n", encoding="utf-8")
        skill = self.root / "plugins/alpha/skills/one/SKILL.md"
        skill.write_text(
            "---\nname: one\ndescription: Updated skill\n---\n",
            encoding="utf-8",
        )

        self.assertEqual(1, generate_readme.generate(check=True))
        self.assertEqual(0, generate_readme.generate(check=False))
        self.assertFalse(stale.exists())
        self.assertIn(
            "Updated skill",
            (self.root / "readme/10-alpha-skills.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(0, generate_readme.generate(check=True))

    def test_link_validation_rejects_missing_files_and_anchors(self) -> None:
        source = self.root / "README.md"
        target = self.root / "readme/10-alpha-skills.md"
        outputs = {
            source: "# Root\n\n[Alpha](readme/10-alpha-skills.md#missing)\n",
            target: "# Alpha skills\n",
        }

        self.assertFalse(generate_readme.local_links_resolve(outputs))
        outputs[source] = "# Root\n\n[Alpha](readme/missing.md)\n"
        self.assertFalse(generate_readme.local_links_resolve(outputs))
        outputs[source] = "# Root\n\n[Alpha](readme/10-alpha-skills.md#alpha-skills)\n"
        self.assertTrue(generate_readme.local_links_resolve(outputs))

    def test_generation_rejects_an_oversized_child(self) -> None:
        skill = self.root / "plugins/alpha/skills/one/SKILL.md"
        skill.write_text(
            f"---\nname: one\ndescription: {'x' * 17_000}\n---\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "10-alpha-skills.md"):
            generate_readme.generate(check=False)


if __name__ == "__main__":
    unittest.main()
