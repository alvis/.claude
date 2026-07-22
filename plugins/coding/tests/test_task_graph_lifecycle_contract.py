from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class TaskGraphLifecycleContractTest(unittest.TestCase):
    def test_writers_and_reviewers_bind_full_task_and_plan_identity(self) -> None:
        for relative in (
            "write-code/SKILL.md",
            "review-code/SKILL.md",
            "fix/SKILL.md",
        ):
            with self.subTest(skill=relative):
                text = compact(SKILLS / relative)
                self.assertIn("task_id", text)
                self.assertIn("plan_source", text)

    def test_write_code_schedules_leaf_ids_and_invalidates_downstream(self) -> None:
        text = compact(SKILLS / "write-code/SKILL.md")
        self.assertIn("runnable executable leaf IDs", text)
        self.assertIn("requested status delta by task ID", text)
        self.assertIn("downstream executable leaf to `! blocked`", text)
        self.assertIn("with an `unblock:` action", text)
        self.assertIn("independent branches keep", text)

    def test_cleanup_does_not_trust_a_completion_label(self) -> None:
        text = compact(SKILLS / "cleanup/SKILL.md")
        self.assertIn("every required executable leaf is `done`", text)

    def test_root_state_is_the_only_plan_definition(self) -> None:
        for relative in (
            "write-code/SKILL.md",
            "review-code/SKILL.md",
            "fix/SKILL.md",
        ):
            with self.subTest(skill=relative):
                self.assertIn("plan_source: state.md", compact(SKILLS / relative))


if __name__ == "__main__":
    unittest.main()
