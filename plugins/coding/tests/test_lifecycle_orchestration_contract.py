from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
CRITIC_FRONTMATTER = (
    PLUGIN / "templates/agents/code-quality-critic/frontmatter/claude.json"
)


class OrchestrationContextContractTest(unittest.TestCase):
    def test_nested_or_interactive_orchestrators_do_not_fork_the_skill_context(self) -> None:
        paths = (
            SKILLS / "write-code/SKILL.md",
            SKILLS / "review-code/SKILL.md",
            SKILLS / "complete-test/SKILL.md",
            SKILLS / "lint/SKILL.md",
            SKILLS / "document/SKILL.md",
            SKILLS / "finalize-commits/SKILL.md",
            SKILLS / "find-unused/SKILL.md",
            SKILLS / "fix/SKILL.md",
        )

        for path in paths:
            with self.subTest(skill=path.parent.name):
                frontmatter = path.read_text(encoding="utf-8").split("---", 2)[1]
                self.assertNotIn("context: fork", frontmatter)


@unittest.skipUnless(shutil.which("jq"), "code-quality hook requires jq")
class CodeQualityCriticFenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data = json.loads(CRITIC_FRONTMATTER.read_text(encoding="utf-8"))
        cls.command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    def run_hook(self, path: str) -> str:
        result = subprocess.run(
            ["bash", "-c", self.command],
            input=json.dumps({"tool_input": {"file_path": path}}),
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def test_canonical_correctness_and_quality_artifacts_are_allowed(self) -> None:
        for path in (
            ".engineering/works/checkout-refunds/reviews/correctness.md",
            "/tmp/target/.engineering/works/checkout-refunds/reviews/quality.md",
        ):
            with self.subTest(path=path):
                self.assertEqual("", self.run_hook(path))

    def test_other_engineering_paths_remain_denied(self) -> None:
        for path in (
            ".engineering/works/checkout-refunds/reviews/security.md",
            ".engineering/works/checkout-refunds/extra/reviews/quality.md",
            "src/payment.ts",
        ):
            with self.subTest(path=path):
                output = json.loads(self.run_hook(path))
                self.assertEqual(
                    "deny",
                    output["hookSpecificOutput"]["permissionDecision"],
                )

    def test_existing_safe_report_paths_stay_allowed(self) -> None:
        for path in (
            ".claude/agent-memory/code-quality-critic/MEMORY.md",
            "reports/report-quality.md",
            "notes/change.review.md",
        ):
            with self.subTest(path=path):
                self.assertEqual("", self.run_hook(path))


if __name__ == "__main__":
    unittest.main()
