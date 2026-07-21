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
                self.assertIn("plan_digest", text)
                self.assertIn("engineering-plan-definition-digest-v1", text)
                self.assertIn("validate-engineering-state validate", text)

    def test_write_code_schedules_leaf_ids_and_invalidates_downstream(self) -> None:
        text = compact(SKILLS / "write-code/SKILL.md")
        self.assertIn("runnable executable leaf IDs", text)
        self.assertIn("requested status delta by task ID", text)
        self.assertIn("downstream executable leaf to `! blocked`", text)
        self.assertIn("with an `unblock:` action", text)
        self.assertIn("independent branches keep", text)
        self.assertIn("Status-only changes retain the plan digest", text)

    def test_cleanup_does_not_trust_a_completion_label(self) -> None:
        text = compact(SKILLS / "cleanup/SKILL.md")
        self.assertIn("every required executable leaf is `done`", text)
        self.assertIn("migration_required", text)
        self.assertIn("plan-digest drift", text)

    def test_handover_and_takeover_use_essential_json_operations(self) -> None:
        handover = compact(SKILLS / "handover/SKILL.md")
        takeover = compact(SKILLS / "takeover/SKILL.md")
        template = compact(SKILLS / "handover/references/document-templates.md")

        self.assertIn("engineering-work-state+json/v1", template)
        self.assertNotIn("engineering-work-state+yaml/v1", template)
        self.assertIn("validate-engineering-state pack", handover)
        self.assertIn("validate-snapshot", handover)
        self.assertIn("validate-snapshot", takeover)
        self.assertIn("validate-engineering-state render", takeover)

    def test_plan_digest_examples_use_the_validator_bare_hex_shape(self) -> None:
        paths = (
            SKILLS / "fix/SKILL.md",
            SKILLS / "handover/references/document-templates.md",
            SKILLS / "handover/references/output-format.md",
            SKILLS / "review-code/references/output-formats.md",
            SKILLS / "review-code/references/review.template.md",
            PLUGIN.parent / "specification/skills/review-implementation/SKILL.md",
        )
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(
                    text,
                    r"(?:plan_digest|Plan digest|reviewed_plan_digest)[^\n]*sha256:",
                )

    def test_root_state_is_the_only_plan_definition(self) -> None:
        for relative in (
            "write-code/SKILL.md",
            "review-code/SKILL.md",
            "fix/SKILL.md",
            "handover/SKILL.md",
            "takeover/SKILL.md",
        ):
            with self.subTest(skill=relative):
                self.assertIn("plan_source: state.md", compact(SKILLS / relative))

        handover_template = compact(
            SKILLS / "handover/references/document-templates.md"
        )
        self.assertIn("role: <implementation_detail|", handover_template)
        self.assertNotIn("role: <plan|", handover_template)
        self.assertIn("cannot duplicate/override IDs, edges", handover_template)


if __name__ == "__main__":
    unittest.main()
