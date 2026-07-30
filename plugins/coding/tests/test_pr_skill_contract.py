from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
WRITE_PR = PLUGIN / "skills" / "write-pr"


def test_authoring_binds_all_deterministic_inputs_and_publication_output() -> None:
    skill = (WRITE_PR / "SKILL.md").read_text()

    assert "empty tree from `git hash-object -t tree /dev/null`" in skill
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
    skill = (WRITE_PR / "SKILL.md").read_text()

    assert "`AUTHOR_BASE_OID`" in skill
    assert "predecessor change/commit OID" in skill
    assert "New-stack bookmarks do not yet exist" in skill
    assert '--base "$PR_BASE"' in skill


def test_reviewer_evidence_resets_only_for_a_changed_head() -> None:
    skill = (WRITE_PR / "SKILL.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "only when the two OIDs differ" in skill
    assert "no-op push or publication retry preserves" in skill
    assert "pre-push and verified post-push head OIDs" in template
    assert "a no-op push preserves valid" in template
    assert "evidence already bound to the unchanged OID" in template
