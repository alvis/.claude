import json
import os
from pathlib import Path
import shutil
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


def test_merged_skill_resolves_bundled_helpers_for_resource_lifetimes() -> None:
    router = (WRITE_PR / "SKILL.md").read_text()
    create_update = (WRITE_PR / "references" / "create-update.md").read_text()
    review_extraction = (
        WRITE_PR / "references" / "review-extraction.md"
    ).read_text()
    review = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "set `CODING_PR_SKILL_DIR` to the absolute directory" in router
    helper_consumers = {
        "scripts/temp-tree.sh": (create_update, review_extraction, review),
        "scripts/review-scan.sh": (review,),
    }
    for helper, consumers in helper_consumers.items():
        assert (WRITE_PR / helper).is_file()
        assert all(helper in consumer for consumer in consumers)
    assert "cleanup() {" not in create_update


def test_review_scan_self_resolves_and_propagates_helper_failure(
    tmp_path: Path,
) -> None:
    plugin = tmp_path / "plugin"
    helper = plugin / "skills" / "pr" / "scripts" / "review-scan.sh"
    helper.parent.mkdir(parents=True)
    shutil.copyfile(WRITE_PR / "scripts" / "review-scan.sh", helper)
    scripts = plugin / "scripts"
    scripts.mkdir()
    marker = tmp_path / "review-scan-argv"
    pyrun = scripts / "pyrun.sh"
    pyrun.write_text(
        "#!/usr/bin/env bash\n"
        'expected="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)'
        '/scan_potential_violations.py"\n'
        '[ "$1" = "$expected" ] || exit 98\n'
        'printf "%s\\n" "$@" > "$REVIEW_SCAN_MARKER"\n'
        "exit 99\n"
    )
    pyrun.chmod(0o755)
    scanner = scripts / "scan_potential_violations.py"
    scanner.write_text("")
    other_cwd = tmp_path / "elsewhere"
    other_cwd.mkdir()
    env = os.environ.copy()
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    env.pop("CLAUDE_SKILL_DIR", None)
    env["REVIEW_SCAN_MARKER"] = str(marker)

    completed = subprocess.run(
        ["bash", str(helper), "--area=security", "target path.py"],
        cwd=other_cwd,
        env=env,
        check=False,
    )

    assert completed.returncode == 99
    assert marker.read_text().splitlines() == [
        str(scanner),
        "--area=security",
        "target path.py",
    ]


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
    assert "context-owning parent passes only" in create_update
    assert "neither removes the worktree nor closes or reports on the parent-owned" in create_update
    assert "After consuming each batch report" in create_update
    assert "never transfers cleanup ownership" in create_update
    assert (
        'open-clone "https://$HOST/$OWNER/$REPO" "$PR_NUMBER" "$HEAD_OID"'
        in extraction
    )
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

    assert "bounded mission capsule" not in review
    assert "`PR_SURFACES` array" in review
    assert "one clean `REVIEW_DIR` at the top head" in review
    assert "reviews the complete stack diff against the bottom base" in review
    assert "holistically" in review
    assert "one holistic map" in review
    assert "A stack never receives a second lease" in review


def test_stacked_local_checks_are_batched_and_cleanup_every_lease() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()

    assert "batches of at most ten" in workflow
    assert "one fresh small-model" in workflow
    assert "retain every returned lease/tree" in workflow
    assert "closes only a completed batch's leases" in workflow
    assert "retains" in workflow
    assert "undispatched batches" in workflow
    assert "recreate the affected" in workflow
    assert "neither removes the worktree nor closes or reports on" in workflow
    report = workflow.split("<report>", 1)[1].split("</report>", 1)[0]
    assert "temporary_worktree_cleanup" not in report


def test_pr_metadata_stays_internal_and_template_owns_rationale() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()
    standard = (
        PLUGIN
        / "constitution"
        / "standards"
        / "git"
        / "rules"
        / "GIT-PR-SIZE-03.md"
    ).read_text()

    assert "specific indivisibility prose" in workflow
    assert "## Why this size" in template
    assert "reviewer-time estimates" in template
    assert "reviewer-time estimate" not in standard
    assert "size counts, zone metadata" in workflow
    assert "## 🧪 Verification" in template


def test_archetype_is_a_preflighted_label_not_pr_content() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "Preflight the repository labels before any push" in workflow
    assert "never create or silently substitute a label" in workflow
    assert "exactly one archetype label remains" in workflow
    assert '--label "$ARCHETYPE"' in workflow
    assert 'PR=$(gh pr create' in workflow
    assert '--remove-label "$label"' in workflow
    assert 'gh pr view "$PR" --json labels' in workflow
    assert 'EXPECTED_ARCHETYPES=$(jq -cn --arg label "$ARCHETYPE"' in workflow
    assert 'test "$ACTUAL_ARCHETYPES" = "$EXPECTED_ARCHETYPES"' in workflow
    assert workflow.index("ARCHETYPE_LABELS='[") < workflow.index('PR=$(gh pr create')
    assert "The label is never rendered in the title or" in template
    assert "## Category" not in template


def test_generated_files_section_is_conditional_and_emoji_named() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()
    template = (WRITE_PR / "references" / "templates" / "pr.md").read_text()

    assert "## 🏭 Generated Files" in template
    assert "whenever any generated files exist" in template
    assert "`{{generated_files_body}}`" in workflow


def test_repo_local_templates_enforce_conditional_evidence_before_emission() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()
    local_template_gate = workflow.split(
        "<IMPORTANT>A repo-local template is emitted verbatim", 1
    )[1].split("When no repo-local template exists", 1)[0]

    assert "every predicate" in local_template_gate
    assert "archetype-required, and diff-required" in local_template_gate
    assert "never inserts category, label, title, or body metadata" in local_template_gate
    assert "exact `## 🏭 Generated Files` heading" in local_template_gate
    assert "generated path or" in local_template_gate
    assert "its source or generator" in local_template_gate
    assert "path-free summary is generic" in local_template_gate


def test_repo_templates_validate_zone_evidence_before_verbatim_emission() -> None:
    workflow = (WRITE_PR / "references" / "create-update.md").read_text()

    assert "apply step 6's evidence" in workflow
    assert "predicates to the content" in workflow
    assert "A heading's presence alone never passes" in workflow
    assert "specific indivisibility prose" in workflow


def test_github_stack_bridge_preserves_plugin_ownership() -> None:
    stacked = (WRITE_PR / "references" / "stacked-prs.md").read_text()
    github_stacks = (WRITE_PR / "references" / "github-stacks.md").read_text()

    assert "[github-stacks.md](github-stacks.md)" in stacked
    assert "`gh stack link`" in github_stacks
    assert "`gh stack unstack <stack-number>`" in github_stacks
    assert "Shape or rewrite history" in github_stacks
    assert "through `coding:commit`" in github_stacks
    assert "Do not trust exit status alone" in github_stacks
    assert "--publish-only" not in github_stacks
    assert "If linking changes any review surface" in github_stacks
    assert "14fc42ed9b6c376a53b2f999f138d3bd26dac546" in github_stacks
    assert "`gh stack link --open` marks new and" in github_stacks
    assert "head branch name of every open stacked PR" in github_stacks
    assert "close-and-recreate migration" in github_stacks


def test_pr_router_exposes_explicit_github_stack_discovery_and_checkout() -> None:
    router = (WRITE_PR / "SKILL.md").read_text()

    assert "/coding:pr stack list" in router
    assert (
        "/coding:pr stack checkout "
        "<stack-number-or-pr-number-or-pr-url-or-local-branch>"
    ) in router
    assert "references/github-stacks.md" in router


def test_github_stack_checkout_is_deterministic_and_safe() -> None:
    github_stacks = (WRITE_PR / "references" / "github-stacks.md").read_text()

    assert 'GET /repos/{owner}/{repo}/stacks' in github_stacks
    assert "paginated" in github_stacks
    assert "`gh stack checkout <stack-number>`" in github_stacks
    assert "bare `gh stack checkout`" in github_stacks
    assert "human-only discovery" in github_stacks
    assert "numeric stack number first" in github_stacks
    assert "PR URL" in github_stacks
    assert "local-only branch" in github_stacks
    assert "clean worktree" in github_stacks
    assert "fetch" in github_stacks
    assert "setup" in github_stacks
    assert "divergent composition" in github_stacks
    assert "stop and report" in github_stacks
    assert "multiple remotes" in github_stacks


def test_github_stack_snippets_stop_before_consuming_failed_commands() -> None:
    github_stacks = (WRITE_PR / "references" / "github-stacks.md").read_text()
    discovery = github_stacks.split("Fetch every page", 1)[1].split("```bash", 1)[1]
    discovery = discovery.split("```", 1)[0]
    checkout = github_stacks.split("for the preferred selector", 1)[1]
    checkout = checkout.split("```bash", 1)[1].split("```", 1)[0]

    assert "mktemp" not in discovery
    assert "trap " not in discovery
    assert "rm " not in discovery
    assert discovery.count("\njq ") == 1
    repo_command = discovery.index("REPOSITORY=$(gh repo view")
    repo_guard = discovery.index(") || exit $?", repo_command)
    api_command = discovery.index("STACKS_JSON=$(gh api --paginate --slurp")
    api_guard = discovery.index(") || exit $?", api_command)
    parsing = discovery.index("jq '[.[][]")
    parsing_guard = discovery.index('<<<"$STACKS_JSON" || exit $?', parsing)
    assert repo_command < repo_guard < api_command < api_guard < parsing < parsing_guard

    checkout_command = checkout.index(
        'gh stack checkout "$STACK_SELECTOR" || exit $?'
    )
    branch_verification = checkout.index("git branch --show-current || exit $?")
    stack_verification = checkout.index("gh stack view --json || exit $?")
    assert checkout_command < branch_verification < stack_verification


def test_review_resolves_canonical_coordinates_before_api_calls() -> None:
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()
    publishing = (WRITE_PR / "references" / "review-publishing.md").read_text()
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()

    assert "scripts/resolve-pr.sh" in workflow
    assert "scripts/resolve-pr.sh" in loop
    assert "baseRefName,baseRefOid" in workflow
    assert "$PR_NUMBER" in workflow
    assert "$PR_NUMBER" in publishing
    assert "pulls/$PR/" not in workflow
    assert "pulls/$PR/" not in publishing
    for content in (workflow, publishing, loop):
        assert 'gh api "repos/' not in content
        assert "gh api graphql -F" not in content
        assert "gh api --method" not in content
    assert '--hostname "$HOST"' in workflow
    assert '--hostname "$HOST"' in publishing
    assert '--hostname "$HOST"' in loop


def test_resolver_accepts_canonical_enterprise_url(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gh = fake_bin / "gh"
    gh.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$PR_METADATA"\n')
    gh.chmod(0o755)
    metadata = {
        "number": 42,
        "url": "https://github.example.test/octo/repo/pull/42",
    }
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PR_METADATA"] = json.dumps(metadata)
    resolved = subprocess.run(
        [
            "bash",
            str(WRITE_PR / "scripts" / "resolve-pr.sh"),
            "42",
            "--repo",
            "octo/repo",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = json.loads(resolved.stdout)
    assert payload["host"] == "github.example.test"
    assert payload["owner"] == "octo"
    assert payload["repo"] == "repo"
    assert payload["number"] == 42


def test_review_fetches_and_verifies_pinned_head_and_base_objects() -> None:
    extraction = (WRITE_PR / "references" / "review-extraction.md").read_text()
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert 'fetch origin "pull/$PR_NUMBER/head"' in extraction
    assert 'fetch origin "$BASE_OID"' in extraction
    assert 'cat-file -e "$HEAD_OID^{commit}"' in extraction
    assert 'cat-file -e "$BASE_OID^{commit}"' in extraction
    assert "if either object is unavailable" in extraction
    load = workflow.index("load [review-extraction.md]")
    reuse = workflow.index("Search for a candidate")
    assert load < reuse
    assert "before inspecting reuse candidates" in workflow


def test_review_provisions_distinct_ledger_and_payload_paths() -> None:
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()
    publishing = (WRITE_PR / "references" / "review-publishing.md").read_text()

    assert 'REVIEW_LEDGER="$REVIEW_ARTIFACT_DIR/ledger.json"' in workflow
    assert 'REVIEW_PAYLOAD="$REVIEW_ARTIFACT_DIR/payload.json"' in workflow
    assert '--input "$REVIEW_PAYLOAD"' in workflow
    assert '--input "$REVIEW_PAYLOAD"' in publishing
    assert "reviewer may write only those two files" in workflow


def test_stack_review_uses_one_tip_and_rechecks_every_surface() -> None:
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()
    publishing = (WRITE_PR / "references" / "review-publishing.md").read_text()

    assert "one clean `REVIEW_DIR` at the top head" in workflow
    assert "reviews the complete stack diff against the bottom base" in workflow
    assert "PR_SURFACES" in workflow
    assert "baseRefName" in workflow
    assert "baseRefOid" in workflow
    assert "for every `PR_SURFACES` entry" in workflow
    assert "one holistic" in loop
    assert "checkout or lease per PR" in loop
    assert "re-reads and compares those three" in publishing


def test_adr_skill_references_follow_the_injected_essential_root() -> None:
    document = (WRITE_PR.parent / "document" / "SKILL.md").read_text()
    plugins = WRITE_PR.parent.parent.parent
    doctor = (plugins / "essential" / "skills" / "doctor" / "SKILL.md").read_text()
    plan = (plugins / "specification" / "skills" / "plan-code" / "SKILL.md").read_text()

    for skill in (document, doctor, plan):
        assert "${ESSENTIAL_ROOT}/references/adr.md" in skill
        assert "plugins/essential/references/adr.md" not in skill
    assert "${ESSENTIAL_ROOT}/templates/docs/adr.template.md" in document


def test_convergence_dispatch_is_already_the_dedicated_reviewer() -> None:
    router = (WRITE_PR / "SKILL.md").read_text()
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "preprovisioned stack capsule" in router
    assert "fresh critic" in loop
    assert "do not invoke another" in loop
    assert "router or delegate" in loop
    assert "already the" in workflow
    assert "dedicated reviewer" in workflow


def test_review_tracks_unanchored_findings_until_convergence() -> None:
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert "findings with no inline anchor" in loop
    assert "evidence OID" in loop
    assert "still_applies`, `fixed`, or `does_not_apply" in loop
    assert "null-anchor finding" in workflow
    assert "anchored or unanchored" in workflow


def test_dedicated_reviewer_reads_discussion_after_tree_provisioning() -> None:
    workflow = (WRITE_PR / "references" / "review-workflow.md").read_text()

    assert workflow.index("### Locate or create the review tree") < workflow.index(
        "### Read the existing discussion"
    )
    assert "dedicated reviewer performs this phase after the parent has located or" in workflow
    assert "created and verified `REVIEW_DIR`" in workflow


def test_batch_review_returns_and_cleans_every_stack_ledger() -> None:
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()

    assert "distinct artifact" in loop
    assert "directory for each stack" in loop
    assert "stack-to-ledger-path map" in loop
    assert "missing, duplicate, or cross-stack path" in loop
    assert "same\nper-stack cleanup" in loop


def test_red_ci_routes_to_repair_without_spending_review_retry() -> None:
    loop = (WRITE_PR / "references" / "review-loop.md").read_text()
    create_update = (WRITE_PR / "references" / "create-update.md").read_text()

    assert "`action: repair_ci_then_review`" in loop
    assert "retry count unchanged" in loop
    assert "`action: repair_ci_then_review`" in create_update
    assert "Never retry a review against unchanged red-CI" in create_update
    assert "evidence." in create_update
