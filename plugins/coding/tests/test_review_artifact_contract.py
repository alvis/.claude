from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
REPOSITORY = PLUGIN.parents[1]
REVIEW_SKILL = PLUGIN / "skills/review-code/SKILL.md"
REVIEW_TEMPLATE = PLUGIN / "skills/review-code/references/review.template.md"
REVIEW_OUTPUT = PLUGIN / "skills/review-code/references/output-formats.md"
CLEANUP_SKILL = PLUGIN / "skills/cleanup/SKILL.md"
WRITE_CODE = PLUGIN / "skills/write-code/SKILL.md"
WRITE_PR_SKILL = PLUGIN / "skills/write-pr/SKILL.md"
REPAIR_RED_CI = PLUGIN / "skills/write-pr/references/repair-red-ci.md"
ESSENTIAL_CONTRACT = REPOSITORY / "plugins/essential/references/engineering-work.md"
ESSENTIAL_MAIN = REPOSITORY / "plugins/essential/MAINAGENT.md"
ESSENTIAL_SUB = REPOSITORY / "plugins/essential/SUBAGENT.md"
DEVIATION_LIFECYCLE = REPOSITORY / "plugins/specification/skills/review-implementation/references/deviation-lifecycle.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class ReviewDispositionContractTest(unittest.TestCase):
    def test_template_has_required_disposition_fields_and_status_semantics(self) -> None:
        template = REVIEW_TEMPLATE.read_text(encoding="utf-8")

        for field in (
            "**Rationale**",
            "**Owner**",
            "**Recheck condition**",
            "**Risk acceptance**",
        ):
            with self.subTest(field=field):
                self.assertIn(field, template)
        for status in ("`open` means", "`fixed` is closed only"):
            with self.subTest(status=status):
                self.assertIn(status, template)
        self.assertIn("closed non-fixed risk dispositions", template)
        self.assertIn("count it as outstanding", template)

    def test_reviewer_validates_non_fixed_dispositions(self) -> None:
        skill = normalized(REVIEW_SKILL)

        self.assertIn("closed non-fixed risk dispositions", skill)
        self.assertIn("reject malformed disposition metadata", skill)

    def test_partial_review_preserves_unselected_area_findings(self) -> None:
        skill = REVIEW_SKILL.read_text(encoding="utf-8")
        output = REVIEW_OUTPUT.read_text(encoding="utf-8")

        self.assertIn("aggregate every existing", skill)
        self.assertIn("partial rerun cannot hide unselected findings", skill)
        self.assertIn("Report every existing canonical area", output)
        self.assertIn("not_run", output)

    def test_one_coordinator_lease_prevents_summary_and_state_multiwriters(self) -> None:
        contracts = {
            "essential": normalized(ESSENTIAL_CONTRACT),
            "main": normalized(ESSENTIAL_MAIN),
            "subagent": normalized(ESSENTIAL_SUB),
            "write-code": normalized(WRITE_CODE),
            "review-code": normalized(REVIEW_SKILL),
        }

        for owner, contract in contracts.items():
            with self.subTest(owner=owner):
                self.assertIn("coordinator lease", contract)
        self.assertIn("exactly one actor", contracts["main"])
        self.assertIn("without that explicit grant, remain a worker", contracts["subagent"])
        self.assertIn("otherwise return the complete roll-up delta", contracts["review-code"])

    def test_cleanup_refuses_malformed_review_history(self) -> None:
        cleanup = CLEANUP_SKILL.read_text(encoding="utf-8")

        self.assertIn("non-placeholder rationale", cleanup)
        self.assertIn("accountable owner", cleanup)
        self.assertIn("explicit recheck", cleanup)
        self.assertIn("Malformed entries", cleanup)
        self.assertIn("make the work ineligible", cleanup)

    def test_status_semantics_are_consistent_across_all_owners(self) -> None:
        owners = {
            "essential": normalized(ESSENTIAL_CONTRACT),
            "coding": normalized(REVIEW_SKILL),
            "specification": normalized(DEVIATION_LIFECYCLE),
        }
        for owner, contract in owners.items():
            with self.subTest(owner=owner):
                self.assertRegex(contract, r"`fixed` (is closed|closes) only")
                self.assertRegex(
                    contract,
                    r"`acknowledged` and `skipped`.*closed|close only",
                )
                self.assertIn("P0/P1", contract)
                self.assertIn("risk-acceptance authority", contract)
                self.assertRegex(
                    contract,
                    r"`open` and `deferred`.*outstanding|`open`, `deferred`.*outstanding",
                )
                self.assertIn("block review closure", contract)

        essential = owners["essential"]
        coding = owners["coding"]
        specification = owners["specification"]
        self.assertIn("five disposition counts", essential)
        self.assertIn("derived `closed` and `outstanding` counts", coding)
        self.assertIn("derived closed/outstanding counts", specification)

        cleanup = normalized(CLEANUP_SKILL)
        self.assertIn("zero outstanding findings", cleanup)
        self.assertIn("no `open`, `deferred`, or malformed risk", cleanup)


class WritePrReferenceContractTest(unittest.TestCase):
    def test_red_ci_repair_links_back_to_the_existing_publication_phase(self) -> None:
        repair = REPAIR_RED_CI.read_text(encoding="utf-8")

        self.assertIn(
            "[core publication phase](../SKILL.md#3-publish-bottom-up)", repair
        )
        self.assertTrue(WRITE_PR_SKILL.is_file())
        self.assertIn(
            "### 3. Publish bottom-up",
            WRITE_PR_SKILL.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
