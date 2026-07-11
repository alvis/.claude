#!/usr/bin/env python3
"""Regression checks for operational procedures that compression must preserve."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


def body(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class CoreProcedureContract(unittest.TestCase):
    def test_implement_code_retains_execution_spine(self) -> None:
        text = body("plugins/specification/skills/implement-code/SKILL.md")
        for token in (
            "COMMIT_PLAN",
            "PI_ITERATE",
            "DRAFT_THEN_ASK",
            "AUDIT_AND_COMPLETE",
            "VERIFY_ONLY",
            "FLAG_MISMATCH",
            "REFUSE",
            "pending_decision",
            "base_rev",
            "child_dispatch_log",
            "thought-experiment.md",
            "worktree_relocation",
        ):
            self.assertIn(token, text)
        modes = body("plugins/specification/skills/implement-code/references/modes.md")
        self.assertIn("Explicit production stubs", modes)
        self.assertIn("Unmarked, missing, or newly requested functionality", modes)
        self.assertIn("Test TODOs", modes)
        self.assertNotIn("finish TODOs", modes)
        self.assertNotIn("complete-code for gaps", modes)

    def test_sync_notion_exposes_modes_not_cli_verbs(self) -> None:
        text = body("plugins/specification/skills/sync-notion/SKILL.md")
        self.assertIn("<local-to-notion|notion-to-local|two-way-merge>", text)
        self.assertIn("post_sync_diff", text)
        self.assertNotIn("--- Merged from Notion ---", body(
            "plugins/specification/skills/sync-notion/references/two-way-merge.md"
        ))
        merge = body("plugins/specification/skills/sync-notion/references/two-way-merge.md")
        self.assertIn("modifications:", merge)
        self.assertIn("MUST NOT push", merge)

    def test_test_and_document_skills_keep_quality_gates(self) -> None:
        tests = body("plugins/coding/skills/complete-test/SKILL.md")
        for token in ("100%", "test → measure → keep", "remove → measure → restore", "per-source", "independent final"):
            self.assertIn(token, tests)
        docs = body("plugins/coding/skills/document/SKILL.md")
        for token in ("Project resolution order", "evidence map", "ARCHITECTURE", "toc_width.py", "independent read-only review"):
            self.assertIn(token, docs)

    def test_review_and_commit_contracts_are_honest(self) -> None:
        review = body("plugins/specification/skills/review-implementation/SKILL.md")
        self.assertIn("--area=alignment", review)
        self.assertIn("mandatory general semantic and security", review)
        self.assertIn("Never label a run complete", review)
        finalize = body("plugins/coding/skills/finalize-commits/SKILL.md")
        self.assertIn("references/markers.md", finalize)
        self.assertIn("skipped_by_marker", finalize)
        self.assertIn("pending_decision", finalize)
        self.assertLess(finalize.index("marker"), finalize.index("skippable lint/test"))

    def test_backend_and_composite_ownership(self) -> None:
        backend = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "plugins/backend/skills").glob("*/SKILL.md")
        )
        self.assertNotIn("`coding:review`", backend)
        self.assertIn("pages_expected", body("plugins/backend/skills/audit-service/SKILL.md"))
        build_data = body("plugins/backend/skills/build-data/SKILL.md")
        self.assertIn("Step 5 is their sole implementation stage", build_data)
        write = body("plugins/coding/skills/write-code/SKILL.md")
        self.assertIn("coding:complete-test", write)
        self.assertIn("Do not pass it to `complete-code` or `complete-test`", write)
        self.assertIn("Mechanical standards violations route to `coding:lint`", write)
        self.assertIn("Fixture, mock, pending-test, and coverage work routes to `coding:complete-test`", write)
        self.assertNotIn("Fixing test issues and standards compliance", write)
        self.assertNotIn("Optimizing test fixtures and mocks", write)
        self.assertNotIn("write integration tests", build_data.lower())


if __name__ == "__main__":
    unittest.main()
