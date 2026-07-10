import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGINS = ROOT / "plugins"
CODING_LINT = PLUGINS / "coding/skills/lint/SKILL.md"
REACT_LINT = PLUGINS / "react/skills/lint/SKILL.md"
REACT_PROFILE = PLUGINS / "react/skills/lint/profile.md"
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"


class PluginDependencyContract(unittest.TestCase):
    def test_plugin_manifests_declare_exact_dependencies(self):
        expected = {
            "react": ["coding"],
            "essential": ["coding"],
            "specification": ["coding"],
            "theriety": ["coding", "specification"],
            "web": ["coding"],
            "coding": None,
            "client": None,
            "governance": None,
        }
        actual = {}
        for manifest_path in PLUGINS.glob("*/.claude-plugin/plugin.json"):
            manifest = json.loads(manifest_path.read_text())
            actual[manifest["name"]] = manifest.get("dependencies")
        self.assertEqual(expected, actual)

    def test_marketplace_does_not_duplicate_dependencies(self):
        marketplace = json.loads(MARKETPLACE.read_text())
        for plugin in marketplace["plugins"]:
            self.assertNotIn("dependencies", plugin, plugin["name"])


class LintCompositionContract(unittest.TestCase):
    def test_react_lint_is_a_single_call_inline_adapter(self):
        text = REACT_LINT.read_text()
        frontmatter = text.split("---", 2)[1]
        body = text.split("---", 2)[2]
        self.assertNotIn("context:", frontmatter)
        self.assertIn('allowed-tools: "Skill(coding:lint *)"', frontmatter)
        invocations = re.findall(r"(?:Skill\(|`)(?:/)?coding:lint", body)
        self.assertEqual(1, len(invocations), text)
        self.assertIn("$ARGUMENTS", text)
        self.assertIn('--profile="${CLAUDE_SKILL_DIR}/profile.md"', text)
        self.assertIn("return its report unchanged", text.lower())
        self.assertLessEqual(len(text.splitlines()), 120)

    def test_coding_lint_is_framework_neutral_and_supports_profiles(self):
        text = CODING_LINT.read_text()
        self.assertIn("--profile=<absolute-path>", text)
        self.assertNotRegex(text, re.compile(r"react|\.tsx|\.jsx", re.IGNORECASE))
        self.assertNotIn("framework dispatch", text.lower())
        self.assertIn("profile may narrow", text.lower())
        self.assertIn("add standards", text.lower())
        self.assertIn("add scanners", text.lower())
        self.assertIn("report label", text.lower())

    def test_react_profile_owns_react_conditions_and_scanner(self):
        text = REACT_PROFILE.read_text().lower()
        for required in (
            ".tsx",
            ".jsx",
            ".stories.tsx",
            ".spec.tsx",
            ".test.tsx",
            "accessibility",
            "components",
            "hooks",
            "project-structure",
            "storybook",
            "plugins/react/scripts/scan_potential_violations.py",
            "exclusions",
            "report label",
        ):
            self.assertIn(required, text)

    def test_react_router_routes_lint_to_react_lint_without_hard_web_call(self):
        text = (PLUGINS / "react/skills/react/SKILL.md").read_text()
        self.assertIn("react:lint", text)
        self.assertNotRegex(text, re.compile(r"(?:Skill\(|`/?)web:"))
        self.assertIn("if available", text.lower())


if __name__ == "__main__":
    unittest.main()
