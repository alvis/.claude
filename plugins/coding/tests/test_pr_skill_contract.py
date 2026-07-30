from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
WRITE_PR = PLUGIN / "skills" / "pr"


def test_authoring_binds_all_deterministic_inputs_and_publication_output() -> None:
    skill = (WRITE_PR / "references" / "create-update.md").read_text()

    assert "`git hash-object -t tree /dev/null`" in skill
    assert "head's `TITLE` and `BODY`" in skill
    assert "base/empty-tree OID" in skill
    assert "template, thresholds, and placeholder map" in skill
    assert "`BREAKING CHANGE:` footers" in skill


def test_canonical_template_carries_section_authoring_guidance() -> None:
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "what problem it solves and why" in template
    assert "design patterns" in template
    assert "anything a reader would reasonably expect here" in template
    assert "RFCs, specs, and discussions" in template


def test_new_stack_authors_against_existing_commit_oids() -> None:
    skill = (WRITE_PR / "references" / "create-update.md").read_text()

    assert "`AUTHOR_BASE_OID`" in skill
    assert "predecessor change/commit OID" in skill
    assert "New-stack bookmarks do not yet exist" in skill
    assert '--base "$PR_BASE"' in skill


def test_reviewer_evidence_binds_to_the_complete_review_surface() -> None:
    skill = (WRITE_PR / "references" / "create-update.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "`headRefOid` and" in skill
    assert "`baseRefOid`" in skill
    assert "Reset those tasks when either OID differs" in skill
    assert "head/base OID pairs" in template
    assert "no-op publication preserves evidence" in template
    assert "unchanged pair" in template
    assert "standard-owned" in template
    assert "<base-oid>" in template


def test_merged_skill_uses_authorized_helpers_for_resource_lifetimes() -> None:
    router = (WRITE_PR / "SKILL.md").read_text()
    create_update = (WRITE_PR / "references" / "create-update.md").read_text()
    review = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "skills/pr/scripts/*" in router
    assert "scripts/temp-tree.sh" in create_update
    assert "scripts/temp-tree.sh" in review
    assert "scripts/review-scan.sh" in review
    assert "cleanup() {" not in create_update


def test_review_uses_canonical_verification_section_name() -> None:
    review = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "Summary, Verification" in review
    assert "Summary, Checklist" not in review


def test_correct_merged_monitoring_stays_read_only() -> None:
    workflow = (
        WRITE_PR.parent
        / "commit"
        / "references"
        / "workflow-correct-merged.md"
    ).read_text()
    followups = workflow.split("## Mandatory follow-ups", 1)[1]

    assert "read-only `gh pr checks`" in followups
    assert "`coding:pr update`" not in followups
