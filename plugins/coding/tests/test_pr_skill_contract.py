import json
from pathlib import Path
import subprocess


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
    assert "change/commit OID" in skill
    assert "New-stack bookmarks do not yet exist" in skill
    assert '--base "$PR_BASE"' in skill


def test_reviewer_evidence_binds_to_the_complete_review_surface() -> None:
    skill = (WRITE_PR / "references" / "create-update.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "capture an existing PR's `headRefOid` and" in skill
    assert "`baseRefOid`" in skill
    assert "only where the head or base OID changed" in skill
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


def test_owned_trees_bind_outputs_and_keep_cleanup_in_parent() -> None:
    create_update = (WRITE_PR / "references" / "create-update.md").read_text()
    extraction = (WRITE_PR / "references" / "review-extraction.md").read_text()
    helper = (WRITE_PR / "scripts" / "temp-tree.sh").read_text()

    assert "TEST_WORKTREE=$(jq -er .tree" in create_update
    assert "context-owning parent retains `TREE_LEASE`" in create_update
    assert 'open-clone "$OWNER/$REPO" "$PR_NUMBER" "$HEAD_OID"' in extraction
    assert "signal trap protects construction only" in extraction
    assert 'workspace="pr-tree-$(basename "$lease")"' in helper
    assert "workspace add --name" in helper
    assert 'workspace forget "$workspace"' in helper


def test_git_tree_lease_opens_and_closes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch=main", str(repo)],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
    )
    (repo / "tracked").write_text("one\n")
    subprocess.run(["git", "-C", str(repo), "add", "tracked"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--quiet", "--no-gpg-sign", "-m", "base"],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    helper = WRITE_PR / "scripts" / "temp-tree.sh"
    opened = subprocess.run(
        ["bash", str(helper), "open-git", str(repo), head],
        check=True,
        capture_output=True,
        text=True,
    )
    lease = json.loads(opened.stdout)
    tree = Path(lease["tree"])
    assert tree.is_dir()
    assert subprocess.run(
        ["git", "-C", str(tree), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == head
    subprocess.run(["bash", str(helper), "close", lease["lease"]], check=True)
    assert not Path(lease["lease"]).exists()


def test_restack_requires_explicit_root_base_and_reports_partial_progress() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()
    helper = (WRITE_PR / "scripts" / "restack.sh").read_text()

    assert '--base "$ROOT_BASE"' in workflow
    assert "for a suffix restack this is its unselected" in workflow
    assert "forge operations are not transactional" in workflow
    assert "missing-base" in helper
    assert "duplicate-bookmark" in helper
    assert "multiple-open" in helper
    assert "closed-head" in helper
    assert "nonlinear" in helper
    assert "vcs_is_ancestor" in helper
    assert "previous_base=$root_base" in helper
    discovery = helper.index("if ! state=$(gh pr list")
    ancestry = helper.index('if [ "$state" != MERGED ]')
    assert discovery < ancestry
    post_verify = helper.split(
        '[ "$remote_sha" = "$expected_sha" ]', 1
    )[1]
    assert post_verify.index("restacked[") < post_verify.index('gh pr edit "$bookmark"')


def test_rewrites_route_unpublished_stacks_to_create() -> None:
    references = [
        WRITE_PR.parent / "commit" / "references" / "workflow-edit.md",
        WRITE_PR.parent / "commit" / "references" / "workflow-reorder.md",
        WRITE_PR.parent / "commit" / "references" / "workflow-retrospective.md",
    ]

    for reference in references:
        workflow = reference.read_text()
        assert "`coding:pr create` when none has one" in workflow
        assert "`coding:pr update` against the lowest open head" in workflow


def test_reviewer_receives_the_pinned_mission_capsule() -> None:
    review = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "bounded mission capsule" in review
    assert "`HEAD_OID`, base ref and" in review
    assert "OID, body, author, status rollup" in review
    assert "body, author, status rollup, requested areas, and dry-run state" in review
