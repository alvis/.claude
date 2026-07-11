"""Executable contracts for the specification/Theriety ownership changes."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "plugins/backend/skills/audit-service/SKILL.md"
SPEC_CODE = ROOT / "plugins/specification/skills/spec-code/SKILL.md"
REVIEW = ROOT / "plugins/specification/skills/review-implementation/SKILL.md"
EVALS = ROOT / "plugins/specification/skills/sync-spec/evals/evals.yaml"


class SpecificationTherietyContracts(unittest.TestCase):
    def test_documentation_audit_owns_all_three_scopes(self) -> None:
        text = AUDIT.read_text()
        self.assertIn("--scope=implementation|docs|all", text)
        self.assertIn("`--scope=implementation`", text)
        self.assertIn("`--scope=docs`", text)
        self.assertIn("`--scope=all`", text)
        self.assertIn("single owner for documentation-only audits", text)

    def test_removed_service_review_has_no_source_or_eval_entry(self) -> None:
        removed = ROOT / "plugins/specification/skills" / ("review-" + "service-operation") / "SKILL.md"
        self.assertFalse(removed.exists())
        self.assertNotIn("review-" + "service-operation", EVALS.read_text())

    def test_spec_code_delegates_sync_and_has_no_private_protocol(self) -> None:
        text = SPEC_CODE.read_text()
        self.assertIn("Skill(sync-notion)", text)
        self.assertIn("does not maintain a parallel merge protocol", text)
        private_sync_ref = "references/" + "notion-sync.md"
        self.assertNotIn(private_sync_ref, text)
        self.assertFalse(
            (ROOT / "plugins/specification/skills/spec-code/references" / ("notion-" + "sync.md")).exists()
        )
        self.assertFalse(
            (ROOT / "plugins/specification/skills/spec-code/references" / ("merge-" + "resolution.md")).exists()
        )

    def test_alignment_failure_does_not_skip_general_or_security_review(self) -> None:
        text = REVIEW.read_text()
        self.assertIn("Skill(coding:review-code)", text)
        self.assertIn("general semantic review and security review", text)
        self.assertIn("even when alignment has P0/P1 findings", text)
        self.assertNotIn("fail-fast", text.lower())
        self.assertIn("general_review: completed", text)
        self.assertIn("security_review: completed", text)


if __name__ == "__main__":
    unittest.main()
