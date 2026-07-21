from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"


def compact(relative: str) -> str:
    return " ".join((SKILLS / relative).read_text(encoding="utf-8").split())


class SpecificationTaskGraphContractTest(unittest.TestCase):
    def test_plan_code_defines_stable_hierarchical_ids_and_digest(self) -> None:
        text = compact("plan-code/SKILL.md")
        self.assertIn("^[A-Z]{3}$", text)
        self.assertIn("its parent's ID plus `01`-`99`", text)
        self.assertIn("prohibit cross-parent child edges", text.lower())
        self.assertIn("engineering-plan-definition-digest-v1", text)
        self.assertIn("status-only reconciliation retains approval", text)
        self.assertIn("complete registry of parents and children", text)
        self.assertIn("plan_source: state.md", text)
        self.assertIn("is non-authoritative implementation detail", text)
        self.assertIn("always after Step 5 assigns stable IDs", text)
        self.assertIn("must not duplicate or override IDs, dependencies", text)

    def test_implementation_schedules_validator_reported_leaf_ids(self) -> None:
        text = compact("implement-code/SKILL.md")
        self.assertIn("runnable leaf IDs", text)
        self.assertIn("reconcile results by ID rather than arrival order", text)
        self.assertIn("downstream executable leaf to `! blocked`", text)
        self.assertIn("records an `unblock:` action", text)
        self.assertIn("independent branches keep", text)
        self.assertIn("reviewed_plan_digest", text)
        self.assertIn("task-status deltas", text)

    def test_review_binds_specification_and_plan_digests(self) -> None:
        text = compact("review-implementation/SKILL.md")
        self.assertIn("reviewed_spec_hash", text)
        self.assertIn("reviewed_plan_digest", text)
        self.assertIn("engineering-plan-definition-digest-v1", text)
        self.assertIn("root `state.md` is authoritative", text.lower())
        self.assertIn("never guess between directory children", text.lower())


if __name__ == "__main__":
    unittest.main()
