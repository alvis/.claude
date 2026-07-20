from __future__ import annotations

from pathlib import Path
import unittest


DESIGN = Path(__file__).resolve().parents[1]
AUDIT = DESIGN.parent / "audit"


class DesignEngineeringWorkContractTest(unittest.TestCase):
    def test_design_skill_uses_shared_gate_and_defers_final_batch(self) -> None:
        text = (DESIGN / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("`engineering-work.md` path injected by Essential", text)
        self.assertIn("generated_files", text)
        self.assertIn("Do not run `wc -c`", text)
        self.assertIn("<work-dir>/design/<design-slug>.md", text)
        self.assertIn("<work-dir>/evidence/design/<design-slug>/", text)
        self.assertIn("PM-owned overview", text)

    def test_design_lifecycle_has_task_and_durable_destinations(self) -> None:
        skill = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
        workspace = (DESIGN / "references/design-workspace.md").read_text(
            encoding="utf-8"
        )

        for path in (
            "docs/design/system.md",
            "docs/design/system/*.md",
            "docs/design/<design-slug>.md",
        ):
            self.assertIn(path, skill)
        self.assertIn("design.md                         # lazy PM-owned overview", workspace)
        self.assertIn("same-stem", workspace)

    def test_legacy_paths_appear_only_in_explicit_migration_section(self) -> None:
        workspace = (DESIGN / "references/design-workspace.md").read_text(
            encoding="utf-8"
        )
        active, legacy = workspace.split("## Legacy inputs", maxsplit=1)

        for stale in (".design-", "DESIGN.md", "CONTEXT.md", "DECISIONS.md"):
            self.assertNotIn(stale, active)
            self.assertIn(stale, legacy)
        self.assertIn("never delete legacy paths automatically", legacy)

    def test_direct_design_references_do_not_use_old_active_paths(self) -> None:
        for name in (
            "component-reuse.md",
            "design-boards.md",
            "design-reference.md",
            "design.template.md",
            "facelift.md",
            "world-class-checklist.md",
        ):
            with self.subTest(name=name):
                text = (DESIGN / "references" / name).read_text(encoding="utf-8")
                for stale in (".design-", "DESIGN.md", "CONTEXT.md", "DECISIONS.md"):
                    self.assertNotIn(stale, text)


class AuditEngineeringWorkContractTest(unittest.TestCase):
    def test_audit_skill_uses_shared_gate_and_work_evidence(self) -> None:
        text = (AUDIT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("`engineering-work.md` path injected by Essential", text)
        self.assertIn("<work-dir>/evidence/web-audit/<audit-slug>/", text)
        self.assertIn("generated_files", text)
        self.assertIn("Do not run `wc -c`", text)
        self.assertIn("`review.md` is PM-owned", text)

    def test_audit_routes_to_exact_canonical_review_set(self) -> None:
        text = (AUDIT / "SKILL.md").read_text(encoding="utf-8")
        template = (AUDIT / "references/review-template.md").read_text(
            encoding="utf-8"
        )
        expected = (
            "alignment.md",
            "correctness.md",
            "security.md",
            "quality.md",
            "testing.md",
            "docs.md",
            "style.md",
        )

        for name in expected:
            self.assertIn(name, text)
            self.assertIn(name, template)
        for removed in ("audit.md", "deviations.md"):
            self.assertNotIn(removed, text.lower())
            self.assertNotIn(removed, template.lower())

    def test_review_renderer_returns_pm_reconciliation_not_competing_report(self) -> None:
        renderer = (AUDIT / "references/phase-4-output.md").read_text(
            encoding="utf-8"
        )
        template = (AUDIT / "references/review-template.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("review_reconciliation", template)
        self.assertIn("worker does not write", renderer)
        self.assertIn("reviews/<area>.md", renderer)
        self.assertNotIn("DESIGN.md", renderer)


if __name__ == "__main__":
    unittest.main()
