import json
import tempfile
import unittest
from pathlib import Path

from analyze_agent_usage import Invocation, discover_plugin_agents, tally


class DiscoverPluginAgentsTest(unittest.TestCase):
    def test_unqualified_installed_agent_usage_maps_to_its_unique_owner(
        self,
    ) -> None:
        defined = {
            "web:priya-sharma-frontend-implementer": {
                "plugin": "web",
                "agent": "priya-sharma-frontend-implementer",
                "path": "frontmatter.json",
            }
        }
        invocation = Invocation(
            canonical_id="priya-sharma-frontend-implementer",
            plugin="built-in",
            agent="priya-sharma-frontend-implementer",
            timestamp=None,
            session_id="session",
            source_file="session.jsonl",
        )

        stats = tally([invocation], defined, files_scanned=1)

        self.assertEqual(1, stats.tallies["web:priya-sharma-frontend-implementer"].count)
        self.assertNotIn("priya-sharma-frontend-implementer", stats.tallies)

    def test_discovers_distributed_json_frontmatter_by_owner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugins = Path(temporary) / "plugins"
            frontmatter = (
                plugins
                / "web/templates/agents/priya-sharma-frontend-implementer/frontmatter/claude.json"
            )
            frontmatter.parent.mkdir(parents=True)
            frontmatter.write_text(
                json.dumps({"name": "priya-sharma-frontend-implementer"}),
                encoding="utf-8",
            )
            legacy = plugins / "web/agents/legacy.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("---\nname: legacy\n---\n", encoding="utf-8")

            agents = discover_plugin_agents(plugins)

            self.assertEqual(
                {"web:priya-sharma-frontend-implementer"}, set(agents)
            )
            self.assertEqual(str(frontmatter), agents["web:priya-sharma-frontend-implementer"]["path"])

    def test_ignores_malformed_or_nameless_frontmatter_and_missing_root(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugins = Path(temporary) / "plugins"
            malformed = plugins / "web/templates/agents/malformed/frontmatter/claude.json"
            nameless = plugins / "web/templates/agents/nameless/frontmatter/claude.json"
            malformed.parent.mkdir(parents=True)
            nameless.parent.mkdir(parents=True)
            malformed.write_text("{", encoding="utf-8")
            nameless.write_text("{}", encoding="utf-8")

            self.assertEqual({}, discover_plugin_agents(plugins))
            self.assertEqual({}, discover_plugin_agents(Path(temporary) / "missing"))


if __name__ == "__main__":
    unittest.main()
