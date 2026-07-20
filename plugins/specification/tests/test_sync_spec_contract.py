from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SYNC_SPEC = PLUGIN / "skills/sync-spec/SKILL.md"


class SyncSpecMaterializationContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = SYNC_SPEC.read_text(encoding="utf-8")

    def test_dirty_or_unverifiable_work_spec_is_never_replaced(self) -> None:
        required = (
            "load its last materialization manifest",
            "hash the current tree before staging anything",
            "refuse with `materialization_conflict` when the prior manifest is absent",
            "an unrecorded file exists",
            "Preserve the existing tree byte-for-byte",
        )
        for statement in required:
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_atomic_promotion_follows_clean_manifest_comparison(self) -> None:
        comparison = self.contract.index("exactly matches its recorded manifest")
        staging = self.contract.index("stage only the selected set")
        promotion = self.contract.index("atomically rename the staged tree")
        rollback = self.contract.index("restore the rollback tree if promotion fails")

        self.assertLess(comparison, staging)
        self.assertLess(staging, promotion)
        self.assertLess(promotion, rollback)

    def test_report_exposes_conflict_without_claiming_replacement(self) -> None:
        self.assertIn(
            "status: unchanged|replaced|materialization_conflict", self.contract
        )
        self.assertIn("existing_preserved: true|false", self.contract)
        self.assertIn("conflict_diff: []", self.contract)


if __name__ == "__main__":
    unittest.main()
