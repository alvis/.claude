"""Contract tests for neighboring Coding and Essential workflow skills."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


def skill(plugin: str, name: str) -> str:
    return (ROOT / "plugins" / plugin / "skills" / name / "SKILL.md").read_text()


class WorkflowOwnershipTest(unittest.TestCase):
    def test_complete_code_accepts_only_production_stub_markers(self) -> None:
        body = skill("coding", "complete-code")
        for marker in (
            "TODO(implementation):",
            "legacy implementation TODO",
            "TEMP:",
            "throw new Error('IMPLEMENTATION: ...')",
        ):
            self.assertIn(marker, body)

    def test_complete_code_routes_neighboring_work(self) -> None:
        body = skill("coding", "complete-code")
        for route in (
            "FIXME",
            "coding:fix",
            "it.todo",
            "describe.todo",
            "coding:complete-test",
            "coding:write-code",
            "HACK",
            "WORKAROUND",
            "blocked",
        ):
            self.assertIn(route, body)

    def test_complete_code_rejects_removed_test_only_flag(self) -> None:
        body = skill("coding", "complete-code")
        self.assertIn(
            "`--test-only` was removed; use `coding:complete-test <scope>`.", body
        )
        self.assertNotIn("[--test-only]", body)
        self.assertNotIn("only write tests without implementation", body)

    def test_draft_code_emits_canonical_marker(self) -> None:
        self.assertIn("TODO(implementation):", skill("coding", "draft-code"))

    def test_handoff_and_handover_have_distinct_ownership(self) -> None:
        handoff = skill("essential", "handoff")
        handover = skill("coding", "handover")
        self.assertIn("context-complete cross-domain plan", handoff)
        self.assertIn("create or execute", handoff.lower())
        for artifact in ("CONTEXT.md", "NOTES.md", "PLAN.md"):
            self.assertIn(artifact, handover)
        self.assertIn("later continuation", handover)

    def test_takeover_is_a_single_resume_adapter(self) -> None:
        body = skill("coding", "takeover")
        self.assertIn("validate", body.lower())
        self.assertEqual(body.count("coding:write-code --resume"), 1)
        self.assertNotIn("coding:handover", body)

    def test_neighboring_descriptions_state_boundaries(self) -> None:
        expected = {
            "find-unused": "read-only",
            "fix": "diagnosed",
            "review-code": "semantic",
            "complete-test": "pending test",
            "refactor": "green",
            "modernize": "version-supported",
        }
        for name, phrase in expected.items():
            self.assertIn(phrase, skill("coding", name).lower(), name)

    def test_finalize_commits_delegates_every_history_mutation(self) -> None:
        body = skill("coding", "finalize-commits")
        self.assertIn("isolated per-commit QA", body)
        self.assertIn("coding:commit", body)
        self.assertIn("sole owner of history mutations", body)


if __name__ == "__main__":
    unittest.main()
