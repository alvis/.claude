from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
WRITE_CODE = SKILLS / "write-code/SKILL.md"
STACK_SPLIT = SKILLS / "write-code/references/stack-split.md"
HANDOVER = SKILLS / "handover/SKILL.md"
HANDOVER_TEMPLATE = SKILLS / "handover/references/document-templates.md"
HANDOVER_OUTPUT = SKILLS / "handover/references/output-format.md"
HANDOVER_EXAMPLES = SKILLS / "handover/references/examples.md"
TAKEOVER = SKILLS / "takeover/SKILL.md"
ESSENTIAL_MAIN = PLUGIN.parent / "essential/MAINAGENT.md"
CRITIC_FRONTMATTER = (
    PLUGIN / "templates/agents/code-quality-critic/frontmatter/claude.json"
)


class OrchestrationContextContractTest(unittest.TestCase):
    def test_nested_or_interactive_orchestrators_do_not_fork_the_skill_context(self) -> None:
        paths = (
            SKILLS / "write-code/SKILL.md",
            SKILLS / "review-code/SKILL.md",
            SKILLS / "complete-test/SKILL.md",
            SKILLS / "lint/SKILL.md",
            SKILLS / "document/SKILL.md",
            SKILLS / "finalize-commits/SKILL.md",
            SKILLS / "find-unused/SKILL.md",
            SKILLS / "fix/SKILL.md",
        )

        for path in paths:
            with self.subTest(skill=path.parent.name):
                frontmatter = path.read_text(encoding="utf-8").split("---", 2)[1]
                self.assertNotIn("context: fork", frontmatter)


class WriteCodeLifecycleContractTest(unittest.TestCase):
    def test_review_lint_and_final_gates_precede_history_and_publication(self) -> None:
        skill = WRITE_CODE.read_text(encoding="utf-8")
        workflow = skill.split("## Workflow", 1)[1].split("## Verification", 1)[0]

        review = workflow.index("6. Invoke `coding:review-code`")
        lint = workflow.index("`coding:lint <touched-specifier>")
        final_validation = workflow.index("9. Run the final verification sequence")
        history = workflow.index("10. Apply the history/publication decision last")

        self.assertLess(review, lint)
        self.assertLess(lint, final_validation)
        self.assertLess(final_validation, history)

    def test_deferred_publication_leaves_final_lifecycle_ownership_to_parent(self) -> None:
        skill = WRITE_CODE.read_text(encoding="utf-8")
        frontmatter = skill.split("---", 2)[1]

        self.assertIn("Internal `--defer-publication`", skill)
        self.assertNotIn("--defer-publication", next(
            line for line in frontmatter.splitlines() if line.startswith("argument-hint:")
        ))
        self.assertIn("do not invoke", skill)
        self.assertIn("`coding:commit --create-pr`", skill)
        self.assertIn("`coding:finalize-commits`", skill)
        self.assertIn("`coding:push-pr`", skill)
        self.assertIn("do not rewrite or restack any published revision", skill)
        self.assertIn("publication_deferred", skill)

    def test_deferred_result_distinguishes_dirty_saved_and_no_change(self) -> None:
        skill = " ".join(WRITE_CODE.read_text(encoding="utf-8").split())

        self.assertIn("Capture immutable `base_rev`", skill)
        self.assertIn("record `history_state` as `dirty`, `saved`, or `none`", skill)
        self.assertIn("slice commits are optional", skill)
        self.assertIn("`needs_save` with the exact immutable manifest path/hash", skill)
        self.assertIn("Never return an unscoped `/coding:commit` next action", skill)
        self.assertIn("`coding:commit --prepare-paths-from=<scope-request>`", skill)
        self.assertIn(
            "`/coding:commit --paths-from=<manifest> --manifest-sha256=<sha256>`",
            skill,
        )
        self.assertIn(
            "`ready_for_finalization` only when the relevant tree is clean and saved unpushed",
            skill,
        )
        self.assertIn(
            "`no_change` when neither dirty nor saved relevant changes exist",
            skill,
        )

    def test_spec_stack_saves_dirty_work_before_finalization(self) -> None:
        policy = (
            PLUGIN.parent
            / "specification/skills/implement-code/references/stack-aware-sizing.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(policy.split())

        self.assertIn(
            "Do not skip merely because `local_commits` is empty when relevant dirty changes exist",
            normalized,
        )
        save = policy.index("`coding:commit --paths-from=<scoped_save_manifest>")
        finalize = policy.index("Invoke `coding:finalize-commits`")
        self.assertLess(save, finalize)
        self.assertIn("both `relevant_dirty_paths` and saved unpushed `local_commits` are empty", normalized)
        self.assertIn("every non-selected dirty worktree", normalized)

    def test_documentation_and_scoped_lint_precede_manifest_sealing(self) -> None:
        skill = WRITE_CODE.read_text(encoding="utf-8")
        workflow = skill.split("## Workflow", 1)[1].split("## Verification", 1)[0]

        documentation = workflow.index("invoke\n   `coding:document`")
        review = workflow.index("6. Invoke `coding:review-code`")
        scoped_lint = workflow.index(
            "`coding:lint <touched-specifier> --scope=uncommitted --skip-unused`"
        )
        sealing = workflow.index("`coding:commit --prepare-paths-from=<scope-request>`")
        self.assertLess(documentation, review)
        self.assertLess(review, scoped_lint)
        self.assertLess(scoped_lint, sealing)
        self.assertIn(
            "does not authorize project-wide unused-code deletion",
            " ".join(workflow.split()),
        )
        self.assertIn("Any project artifact writer\n   after sealing invalidates", workflow)

    def test_stack_publication_cannot_bypass_commit_finalization(self) -> None:
        policy = STACK_SPLIT.read_text(encoding="utf-8")
        normalized = " ".join(policy.split())

        commit = policy.index("Dispatch plain `coding:commit`")
        finalize = policy.index("Then run `coding:finalize-commits`")
        publish = policy.index("may `coding:push-pr` publish")

        self.assertLess(commit, finalize)
        self.assertLess(finalize, publish)
        self.assertIn("Do not use the `--create-pr` compatibility shortcut", policy)
        self.assertIn(
            "Do not load or execute it for `--defer-publication`", normalized
        )


class PortableHandoverContractTest(unittest.TestCase):
    def test_handover_refuses_local_only_source_changes(self) -> None:
        handover = HANDOVER.read_text(encoding="utf-8")
        output = HANDOVER_OUTPUT.read_text(encoding="utf-8")

        self.assertIn("destination-reachable carrier", handover)
        self.assertIn("patch/bundle payload", handover)
        self.assertIn("blocked, non-rehydratable status", handover)
        self.assertIn("handover: blocked", output)
        self.assertIn("rehydratable: false", output)

    def test_receipt_carries_source_and_lifecycle_identity(self) -> None:
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("schema: engineering-work-handover/v3", template)
        self.assertIn("source_anchor:", template)
        self.assertIn("state_snapshot:", template)
        self.assertIn("format: engineering-work-state+json/v1", template)
        self.assertIn("content: <complete inline payload or null>", template)
        self.assertIn("destination_root: .engineering/works/<work-id>/", template)
        self.assertIn(
            "render: [state.md]", template
        )
        self.assertIn("checksum:", template)
        self.assertIn("application:", template)
        self.assertIn("workflow_owner:", template)
        for kind in ("local", "inline", "notion"):
            with self.subTest(kind=kind):
                self.assertIn(kind, template)

    def test_notion_receipt_is_logical_and_destination_portable(self) -> None:
        handover = " ".join(HANDOVER.read_text(encoding="utf-8").split())
        template = " ".join(HANDOVER_TEMPLATE.read_text(encoding="utf-8").split())
        output = " ".join(HANDOVER_OUTPUT.read_text(encoding="utf-8").split())
        examples = " ".join(HANDOVER_EXAMPLES.read_text(encoding="utf-8").split())

        for field in (
            "logical_profile:",
            "stable_ref:",
            "captured_revision:",
            "hash_model: specification-dual-hash-v1",
            "transport_manifest_hash:",
            "contract_digest:",
            "suggested_root:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, template)
        self.assertIn("discard the origin transport root", handover)
        self.assertIn("contained repository-relative suggested root", handover)
        self.assertIn("Do not emit or redact-and-retain the origin's", output)
        self.assertIn("mapped to an exact destination-local ignored root", examples)

    def test_notion_handover_preserves_dual_hashes_and_non_clean_blr_state(self) -> None:
        handover = " ".join(HANDOVER.read_text(encoding="utf-8").split())
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())
        template = " ".join(HANDOVER_TEMPLATE.read_text(encoding="utf-8").split())
        output = " ".join(HANDOVER_OUTPUT.read_text(encoding="utf-8").split())

        for contract in (handover, takeover, template, output):
            with self.subTest(contract=contract[:60]):
                self.assertIn("transport_manifest_hash", contract)
                self.assertIn("contract_digest", contract)
        self.assertNotIn("captured_hash:", template)
        self.assertNotIn("revision_or_hash:", template)
        self.assertIn("specification-blr-transfer+json/v1", template)
        self.assertIn("local_only", template)
        self.assertIn("remote_only", template)
        self.assertIn("structural_change", template)
        self.assertIn("concurrent", template)
        self.assertIn("status:", template)
        self.assertIn("classification:", template)
        self.assertIn("next_action:", template)
        self.assertIn("exact immutable B receipt/bytes", handover)
        self.assertIn("authored L bytes", handover)
        self.assertIn("never overwrite L from R", takeover)
        self.assertIn("lacks a complete portable B/L package", output)
        self.assertNotIn("verified_clean", template)
        self.assertIn("Never map a sync result", template)

    def test_v3_continuity_is_checksum_bound_and_not_local_only(self) -> None:
        handover = HANDOVER.read_text(encoding="utf-8")
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")
        output = HANDOVER_OUTPUT.read_text(encoding="utf-8")
        normalized = " ".join((handover + template + output).split())

        for required in (
            "complete hierarchical task definitions/graph",
            "task status/owner/evidence execution ledger",
            "plan identity",
            "exact next owner and action",
            "work_artifacts",
            "full goal/acceptance narrative",
            "review dispositions",
            "sync/revalidation",
            "file status",
        ):
            with self.subTest(required=required):
                self.assertIn(required, normalized)
        self.assertIn("SHA-256", normalized)
        self.assertIn("ignored local path", normalized)
        self.assertIn("response-only receipt", normalized)
        self.assertIn("embed the complete", normalized)

    def test_state_snapshot_uses_the_single_essential_json_codec(self) -> None:
        handover = " ".join(HANDOVER.read_text(encoding="utf-8").split())
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("engineering-work-state+json/v1", template)
        self.assertNotIn("engineering-work-state+yaml/v1", template)
        self.assertIn("validate-engineering-state pack --state <state.md>", handover)
        self.assertIn("validate-engineering-state validate-snapshot --snapshot <file|->", handover)
        self.assertIn("validate-engineering-state validate-snapshot --snapshot <file|->", takeover)
        self.assertIn("validate-engineering-state render --snapshot <file|->", takeover)
        self.assertIn("Stable task IDs, DAG edges, statuses, plan digest", takeover)

    def test_task_snapshot_and_narrative_carriers_have_distinct_ownership(self) -> None:
        handover = " ".join(HANDOVER.read_text(encoding="utf-8").split())
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())
        template = " ".join(HANDOVER_TEMPLATE.read_text(encoding="utf-8").split())

        self.assertIn("snapshot guarantees only the complete hierarchical task", handover)
        self.assertIn("It does not contain the full goal or acceptance narrative", template)
        self.assertIn("work_artifacts:", template)
        self.assertIn("Never assume the task snapshot contains narrative sections", takeover)

    def test_continuation_uses_only_essential_report_fields(self) -> None:
        handover = " ".join(HANDOVER.read_text(encoding="utf-8").split())
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        for field in ("execution_ledger", "active_task_ids", "next_owner", "next_action"):
            with self.subTest(field=field):
                self.assertIn(field, handover)
                self.assertIn(field, takeover)
        self.assertIn("ledger status is `working`, `failed`, or `blocked`", handover)
        self.assertIn("ledger status is `working`, `failed`, or `blocked`", takeover)
        self.assertIn("working-only `active_task_ids`", handover)
        self.assertIn("working-only `active_task_ids`", takeover)
        self.assertIn("no applicable executable leaf", handover)
        self.assertIn("no applicable executable leaf", takeover)
        self.assertIn("Do not reproduce any of these checks with a takeover-owned parser", takeover)

    def test_takeover_revalidates_the_promoted_destination(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]

        render = workflow.index("validate-engineering-state render --snapshot")
        validate = workflow.index(
            "validate-engineering-state validate --state <destination-state.md>"
        )
        resume = workflow.index("11. Resume exactly once")
        self.assertLess(render, validate)
        self.assertLess(validate, resume)
        self.assertIn("missing/mislocated plan", workflow)
        self.assertIn("child/root row drift", workflow)
        self.assertIn("same compare-and-restore rollback path", workflow)

    def test_each_source_carrier_has_explicit_portable_application_contract(self) -> None:
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")

        for carrier in ("remote_revision", "patch", "bundle"):
            with self.subTest(carrier=carrier):
                self.assertIn(f"`{carrier}`", template)
        for field in (
            "format:",
            "encoding:",
            "content:",
            "locator:",
            "checksum:",
            "application:",
        ):
            with self.subTest(field=field):
                self.assertIn(field, template)
        for mode in ("checkout_revision", "apply_patch", "fetch_bundle_ref"):
            with self.subTest(mode=mode):
                self.assertIn(mode, template)

    def test_v2_requires_deliberate_migration_to_v3(self) -> None:
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")
        takeover = TAKEOVER.read_text(encoding="utf-8")
        examples = HANDOVER_EXAMPLES.read_text(encoding="utf-8")

        self.assertIn("## v2 migration", template)
        self.assertIn("not directly rehydratable", template)
        self.assertIn("A v2 receipt is accepted only after", takeover)
        self.assertIn("produces a complete v3 receipt", takeover)
        self.assertIn("A v2 receipt is an input to migration", examples)

    def test_takeover_routes_by_source_kind_and_declared_owner(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        normalized = " ".join(takeover.split())

        self.assertIn("A `local` source", normalized)
        self.assertIn("complete `inline` content", normalized)
        self.assertIn("For a `notion` source", normalized)
        self.assertIn("Notion tooling is required only for", normalized)
        self.assertIn("`specification:implement-code`", normalized)
        self.assertIn("`coding:write-code --resume`", normalized)
        self.assertIn("Reject an unknown or source-inconsistent", normalized)

    def test_takeover_validates_post_anchor_tree_before_clean_destination(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]
        normalized = " ".join(workflow.split())

        isolated = workflow.index("2. Retrieve/decode carriers")
        anchor = workflow.index("3. Confirm the current checkout")
        spec = workflow.index("4. Stage and verify specifications")
        snapshot = workflow.index("5. Verify the decoded `state_snapshot`")
        destination = workflow.index("7. Require and record a clean compatible")

        self.assertLess(isolated, anchor)
        self.assertLess(anchor, spec)
        self.assertLess(spec, snapshot)
        self.assertLess(snapshot, destination)
        self.assertIn("post-anchor disposable tree", normalized)
        self.assertIn("never the pre-patch destination checkout", normalized)
        self.assertIn("clean compatible destination baseline", normalized)
        self.assertIn("Reject every other pre-existing root", normalized)
        self.assertIn("pre-bootstrap baseline", normalized)

    def test_takeover_bootstraps_only_after_portable_validation(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        main_agent = " ".join(ESSENTIAL_MAIN.read_text(encoding="utf-8").split())
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]
        normalized = " ".join(workflow.split())

        self.assertLess(
            workflow.index("1. Parse the `engineering-work-handover/v3`"),
            workflow.index("7. Require and record a clean compatible"),
        )
        self.assertLess(
            workflow.index("3. Confirm the current checkout"),
            workflow.index("with that ID and `--bootstrap`"),
        )
        self.assertIn("explicit takeover exception", main_agent)
        self.assertIn("exact work ID and `--bootstrap`", main_agent)
        self.assertIn("contains exactly regular `state/working.md` and `state.md`", normalized)
        self.assertIn("byte-for-byte the resolver's untouched `initialized` template", normalized)
        self.assertIn("only this verified skeleton may later be replaced", normalized)

    def test_takeover_maps_notion_transport_in_destination_before_fetch(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]
        normalized = " ".join(workflow.split())

        mapping = workflow.index("8. For each Notion carrier")
        fetch = workflow.index("Only after this mapping passes")
        promotion = workflow.index("9. Immediately before promotion")
        self.assertLess(mapping, fetch)
        self.assertLess(fetch, promotion)
        self.assertIn("ask the user for the exact destination-local profile file and root", normalized)
        self.assertIn("--transport-profile=<absolute-file>", normalized)
        self.assertIn("never derive a file location from the logical name", normalized)
        self.assertIn("internal `name` to equal the receipt's `logical_profile`", normalized)
        self.assertIn("destination profile-file digest", normalized)
        self.assertIn("suggested_root` is only a proposal", normalized)
        self.assertIn("record the mapping", normalized)
        self.assertIn("no origin-workspace path selected it", takeover)

    def test_takeover_replaces_only_verified_skeleton_and_rolls_back_safely(self) -> None:
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        self.assertIn("Replace only the verified initialized skeleton", takeover)
        self.assertIn("private same-filesystem rollback sibling", takeover)
        self.assertIn("Never merge receipt state into, delete, or rename an unrecognized", takeover)
        self.assertIn("compare every target with its recorded bytes/token before rollback", takeover)
        self.assertIn("preserve both sides and return `partial`", takeover)

    def test_takeover_does_not_mislabel_source_drift_as_revalidation(self) -> None:
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        self.assertIn("yields `revalidated` only after it passes", takeover)
        self.assertIn("For a no-B/L carrier, a changed Notion revision", takeover)
        self.assertIn("or missing evidence, is a contradiction", takeover)
        self.assertIn("For a required-B/L carrier, fresh remote movement updates R evidence", takeover)
        self.assertIn("does not invalidate the checksum-verified B/L transfer", takeover)
        self.assertIn("Never bless stale state", takeover)

    def test_takeover_rejects_unsafe_or_incomplete_payloads(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        normalized = " ".join(takeover.split())

        for protection in (
            "checksum",
            "credentials, tokens, private keys",
            "absolute paths",
            "symlink traversal",
            "Reject missing task fields",
            "ignored local path",
        ):
            with self.subTest(protection=protection):
                self.assertIn(protection, normalized)


@unittest.skipUnless(shutil.which("jq"), "code-quality hook requires jq")
class CodeQualityCriticFenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data = json.loads(CRITIC_FRONTMATTER.read_text(encoding="utf-8"))
        cls.command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    def run_hook(self, path: str) -> str:
        result = subprocess.run(
            ["bash", "-c", self.command],
            input=json.dumps({"tool_input": {"file_path": path}}),
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()

    def test_canonical_correctness_and_quality_artifacts_are_allowed(self) -> None:
        for path in (
            ".engineering/works/checkout-refunds/reviews/correctness.md",
            "/tmp/target/.engineering/works/checkout-refunds/reviews/quality.md",
        ):
            with self.subTest(path=path):
                self.assertEqual("", self.run_hook(path))

    def test_other_engineering_paths_remain_denied(self) -> None:
        for path in (
            ".engineering/works/checkout-refunds/reviews/security.md",
            ".engineering/works/checkout-refunds/extra/reviews/quality.md",
            "src/payment.ts",
        ):
            with self.subTest(path=path):
                output = json.loads(self.run_hook(path))
                self.assertEqual(
                    "deny",
                    output["hookSpecificOutput"]["permissionDecision"],
                )

    def test_existing_safe_report_paths_stay_allowed(self) -> None:
        for path in (
            ".claude/agent-memory/code-quality-critic/MEMORY.md",
            "reports/report-quality.md",
            "notes/change.review.md",
        ):
            with self.subTest(path=path):
                self.assertEqual("", self.run_hook(path))


if __name__ == "__main__":
    unittest.main()
