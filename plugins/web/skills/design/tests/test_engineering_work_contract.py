from __future__ import annotations

from pathlib import Path
import unittest


DESIGN = Path(__file__).resolve().parents[1]
AUDIT = DESIGN.parent / "audit"
CODING_REVIEW_TEMPLATE = (
    DESIGN.parents[2] / "coding/skills/review-code/references/review.template.md"
)


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

    def test_web_details_use_the_canonical_coding_area_schema(self) -> None:
        web = (AUDIT / "references/review-template.md").read_text(
            encoding="utf-8"
        )
        coding = CODING_REVIEW_TEMPLATE.read_text(encoding="utf-8")
        required = (
            "area: <alignment|correctness|security|quality|testing|docs|style>",
            "prefix: <ALIGN|CORR|SEC|QUAL|TEST|DOCS|STYL>",
            "reviewed_at: <ISO-8601 timestamp>",
            "files_reviewed_count: <N>",
            "closed_findings: <N>",
            "outstanding_findings: <N>",
            "**Verdict**",
            "**Status**",
            "**Source**",
            "**Issue**",
            "**Evidence**",
            "**Direction**",
            "**Rationale**",
            "**Owner**",
            "**Recheck condition**",
            "**Risk acceptance**",
        )

        for field in required:
            with self.subTest(field=field):
                self.assertIn(field, coding)
                self.assertIn(field, web)

    def test_web_priority_and_identity_mapping_preserves_p3_and_stable_ids(self) -> None:
        template = (AUDIT / "references/review-template.md").read_text(
            encoding="utf-8"
        )
        renderer = (AUDIT / "references/phase-4-output.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`critical|high|medium|low`", template)
        self.assertIn("`P0|P1|P2|P3`", template)
        self.assertIn("<PREFIX>-P<n>-<seq>", template)
        self.assertIn("reuse its canonical ID", template)
        self.assertIn("Never renumber old IDs", renderer)
        self.assertIn("raw CLI IDs", renderer)

    def test_web_reconciliation_exposes_full_disposition_and_priority_counts(self) -> None:
        template = (AUDIT / "references/review-template.md").read_text(
            encoding="utf-8"
        )

        for field in (
            "open: 0",
            "fixed: 0",
            "acknowledged: 0",
            "deferred: 0",
            "skipped: 0",
            "closed: 0",
            "outstanding: 0",
            "p0: 0",
            "p1: 0",
            "p2: 0",
            "p3: 0",
        ):
            with self.subTest(field=field):
                self.assertIn(field, template)
        self.assertIn("An absent area is `not_run`, not `pass`", template)


if __name__ == "__main__":
    unittest.main()
