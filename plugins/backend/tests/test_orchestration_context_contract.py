from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]


class BackendOrchestrationContextContractTest(unittest.TestCase):
    def test_interactive_orchestrators_run_in_the_main_context(self) -> None:
        for name in ("audit-data", "audit-service", "build-data", "build-service"):
            with self.subTest(skill=name):
                text = (PLUGIN / "skills" / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                frontmatter = text.split("---", 2)[1]
                self.assertNotIn("context: fork", frontmatter)
                self.assertIn("AskUserQuestion", frontmatter)


if __name__ == "__main__":
    unittest.main()
