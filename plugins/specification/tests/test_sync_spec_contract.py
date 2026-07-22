from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
SYNC_SPEC = SKILLS / "sync-spec/SKILL.md"
SYNC_NOTION = SKILLS / "sync-notion/SKILL.md"
CONCURRENT_MATRIX = SKILLS / "sync-spec/references/concurrent-edit-matrix.md"
TWO_WAY = SKILLS / "sync-notion/references/two-way-merge.md"
SYNC_MODE = SKILLS / "sync-notion/references/sync-mode-execution.md"
SPEC_CODE = SKILLS / "spec-code/SKILL.md"
PLAN_CODE = SKILLS / "plan-code/SKILL.md"
IMPLEMENT_CODE = SKILLS / "implement-code/SKILL.md"
REVIEW_IMPLEMENTATION = SKILLS / "review-implementation/SKILL.md"
STACK_AWARE = SKILLS / "implement-code/references/stack-aware-sizing.md"
SPEC_FRONTMATTER = SKILLS / "spec-code/references/frontmatter.md"
NEUTRAL_TEMPLATE = SKILLS / "spec-code/assets/technical-spec-template.md"


def compact(text: str) -> str:
    return " ".join(text.split())


class SyncSpecMaterializationContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = compact(SYNC_SPEC.read_text(encoding="utf-8"))
        self.matrix = compact(CONCURRENT_MATRIX.read_text(encoding="utf-8"))

    def test_three_copies_and_immutable_hash_addressed_base_are_explicit(self) -> None:
        for statement in (
            "**B — immutable base**",
            "**L — authored local**",
            "**R — fresh remote staging**",
            "materializations/<base-id>.json",
            "bases/<base-id>/",
            "never rewrites an existing receipt or base",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.matrix)

        self.assertNotIn(
            "materialization_receipt = <work-dir>/artifacts/spec-sync/materialization.json",
            self.contract,
        )

    def test_materialize_matrix_preserves_dirty_local_bytes(self) -> None:
        for statement in (
            "absent B with existing L returns `status: refused`",
            "`classification: baseline_required`",
            "dirty L plus unchanged R returns `status: success`",
            "`classification: local_only`",
            "`classification: materialization_conflict`",
            "preserves every canonical byte",
            "clean L plus changed R atomically refreshes L/mirror",
            "`classification: remote_only`",
            "`next_action: revalidate`",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_complete_uses_base_local_remote_decision_table(self) -> None:
        for classification in (
            "`baseline_required`",
            "`local_only`",
            "`remote_only`",
            "`converged`",
            "`concurrent`",
        ):
            with self.subTest(classification=classification):
                self.assertIn(classification, self.matrix)


class PublicationSafetyContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sync_spec = compact(SYNC_SPEC.read_text(encoding="utf-8"))
        self.sync_notion = compact(SYNC_NOTION.read_text(encoding="utf-8"))
        self.two_way = compact(TWO_WAY.read_text(encoding="utf-8"))
        self.sync_mode = compact(SYNC_MODE.read_text(encoding="utf-8"))

    def test_stage_gate_is_bound_to_exact_final_hash(self) -> None:
        self.assertIn("--stage=specification|implementation", self.sync_spec)
        self.assertIn("explicit specification approval of the exact final specification content", self.sync_spec)
        self.assertIn("require the clean implementation review to have been performed against that exact final content", self.sync_spec)
        self.assertIn("Any semantic edit after the gate invalidates it", self.sync_spec)

    def test_remote_is_rechecked_immediately_before_push(self) -> None:
        for contract in (self.sync_spec, self.sync_notion, self.sync_mode):
            with self.subTest(contract=contract[:40]):
                self.assertIn("immediately", contract.lower())
                self.assertTrue(
                    "conditional update" in contract
                    or "conditional-update" in contract
                )
                normalized = contract.lower()
                self.assertTrue(
                    "abort/restart" in normalized or "abort and restart" in normalized
                )

        for contract in (self.sync_spec, self.sync_notion, self.sync_mode):
            with self.subTest(contract=contract[:40]):
                self.assertNotIn("quiet", contract.lower())
                self.assertNotIn("residual_race", contract.lower())

    def test_missing_conditional_transport_refuses_without_mutation(self) -> None:
        for contract in (self.sync_spec, self.sync_notion, self.sync_mode):
            with self.subTest(contract=contract[:40]):
                self.assertIn("status: refused", contract)
                self.assertIn("provide_conditional_transport", contract)
                self.assertIn("B/L/R", contract)
                self.assertTrue(
                    "canonical-local" in contract or "canonical L/mirror" in contract
                )

    def test_skip_and_keep_both_cannot_take_unsafe_old_paths(self) -> None:
        self.assertIn("Workers never invoke `AskUserQuestion`", self.two_way)
        self.assertIn("Keep Both", self.two_way)
        self.assertIn("explicit approval of its candidate content", self.two_way)
        self.assertIn("Skip never inserts a TODO", self.two_way)
        self.assertIn("do not edit canonical local/mirror bytes or push", self.sync_mode)
        self.assertNotIn("Add TODO marker on the local side", self.two_way)
        self.assertNotIn("All conflicts resolved or skipped", self.two_way)

    def test_local_to_notion_reviews_fresh_diff_before_push(self) -> None:
        pull = self.sync_mode.index("Pull the current remote page")
        review = self.sync_mode.index("Compute and present a structured")
        recheck = self.sync_mode.index("immediately re-fetch/re-diff")
        push = self.sync_mode.index("Invoke the frozen `conditional_update` vector")
        self.assertLess(pull, review)
        self.assertLess(review, recheck)
        self.assertLess(recheck, push)

    def test_ambiguous_remote_mutation_is_never_retried(self) -> None:
        self.assertIn(
            "After a possible, unknown, or partial remote mutation, stop `partial`",
            self.sync_notion,
        )
        self.assertIn("never retry from an ambiguous remote state", self.sync_notion)

    def test_conditional_create_is_not_inferred_from_conditional_update(self) -> None:
        for contract in (self.sync_notion, self.sync_mode):
            with self.subTest(contract=contract[:40]):
                self.assertIn("conditional_create", contract)
                self.assertIn("conditional-update", contract.lower())
        self.assertIn(
            "Conditional update support never suppresses this creation gate",
            self.sync_notion,
        )

    def test_operational_status_is_separate_from_relationship_classification(self) -> None:
        self.assertIn("status: success|partial|refused", self.sync_spec)
        self.assertIn("classification: initial|unchanged|metadata_only", self.sync_spec)
        self.assertIn("next_action: none|revalidate|establish_baseline", self.sync_spec)
        self.assertIn("status: success|partial|failure|refused", self.sync_notion)
        self.assertIn("classification: initial|created|updated|pulled", self.sync_notion)
        self.assertIn("next_action: none|revalidate|establish_baseline", self.sync_notion)
        self.assertIn("provide_conditional_transport", self.sync_spec)
        self.assertIn("provide_conditional_transport", self.sync_notion)


class SpecificationLifecycleOrderingTest(unittest.TestCase):
    def test_orchestrators_run_in_live_context(self) -> None:
        for path in (
            SPEC_CODE,
            PLAN_CODE,
            IMPLEMENT_CODE,
            REVIEW_IMPLEMENTATION,
            SYNC_SPEC,
            SYNC_NOTION,
        ):
            with self.subTest(path=path):
                self.assertNotIn("context: fork", path.read_text(encoding="utf-8"))

    def test_implementation_publication_follows_review_and_sync(self) -> None:
        contract = IMPLEMENT_CODE.read_text(encoding="utf-8")
        execution = contract.index("8. Execute by capability")
        review = contract.index("9. Re-run the Step 2 source/carrier authority")
        sync = contract.index("10. Use the selected source's owning completion path")
        publication = contract.index("11. Only after review/usage")
        self.assertLess(execution, review)
        self.assertLess(review, sync)
        self.assertLess(sync, publication)
        self.assertIn("`--defer-publication`", contract)
        self.assertIn("whether or not local specification content changed", compact(contract))
        self.assertIn("With public `--defer-publication`", compact(contract))
        self.assertIn("`ready_for_finalization`", contract)

    def test_remote_only_refreshes_local_before_revalidation_restart(self) -> None:
        contract = compact(IMPLEMENT_CODE.read_text(encoding="utf-8"))

        remote_only = contract.index("`classification: remote_only`")
        materialize = contract.index("`materialize` mode", remote_only)
        refresh = contract.index("atomic promotion of verified R")
        restart = contract.index("only then return to Step 3")
        self.assertLess(remote_only, materialize)
        self.assertLess(materialize, refresh)
        self.assertLess(refresh, restart)
        self.assertIn("do not reread stale L", contract)
        self.assertIn("B/L/R packet and immutable M proposal", contract)
        self.assertIn("explicit resolution", contract)
        self.assertIn("approval of M's exact content", contract)

    def test_deferred_history_status_reflects_dirty_saved_and_empty_states(self) -> None:
        contract = compact(IMPLEMENT_CODE.read_text(encoding="utf-8"))

        self.assertIn("record `history_state`", contract)
        self.assertIn("`needs_save` when any relevant worktree change remains dirty", contract)
        self.assertIn("the complete `/coding:commit --paths-from=<manifest>", contract)
        self.assertIn("stop `blocked_scope`", contract)
        self.assertIn("`Skill(coding:commit --prepare-paths-from=<scope-request>)`", contract)
        self.assertIn(
            "`ready_for_finalization` only when the worktree is clean and saved unpushed",
            contract,
        )
        self.assertIn(
            "`no_change` when neither relevant dirty changes nor saved unpushed",
            contract,
        )

    def test_spec_plan_and_review_are_content_bound(self) -> None:
        self.assertIn("require approval of its content before derivation", compact(SPEC_CODE.read_text(encoding="utf-8")))
        plan = compact(PLAN_CODE.read_text(encoding="utf-8"))
        self.assertIn("require explicit approval of those task definitions", plan)
        self.assertIn("plan approval binds to the exact approved task definitions", plan)
        self.assertIn("status-only reconciliation retains approval", plan)
        review = REVIEW_IMPLEMENTATION.read_text(encoding="utf-8")
        normalized_review = compact(review)
        self.assertIn("bound to the exact approved specification content", review)
        self.assertIn("Bind the review to the exact approved specification content", review)
        self.assertNotIn("contract_digest", review)
        self.assertNotIn("transport_manifest_hash", review)
        self.assertNotIn("spec-hashes.py", review)
        self.assertIn("local, inline-origin, or Notion", review)
        self.assertIn("invoke `sync-spec` to materialize only a selected Notion source", compact(review))
        self.assertIn("reachable `repo:` local source", normalized_review)
        self.assertIn("compare the source and carrier content directly", normalized_review)
        self.assertIn("returns `ready_for_specification`", normalized_review)
        self.assertIn("Re-run the complete Step 2 source/carrier authority", normalized_review)

    def test_final_history_qa_cannot_be_bypassed(self) -> None:
        contract = STACK_AWARE.read_text(encoding="utf-8")
        commit = contract.index("`coding:commit --paths-from=<scoped_save_manifest>")
        finalization = contract.index("Invoke `coding:finalize-commits`")
        publication = contract.index("invoke `coding:push-pr`")
        self.assertLess(commit, finalization)
        self.assertLess(finalization, publication)
        self.assertIn("Never use\n   the `--create-pr` compatibility shortcut", contract)
        self.assertIn("public `--defer-publication` is set", contract)
        self.assertIn("every non-selected dirty worktree", compact(contract))


class SpecDerivationContractTest(unittest.TestCase):
    def test_inline_evidence_is_promoted_to_a_content_bound_durable_contract(self) -> None:
        contract = compact(SPEC_CODE.read_text(encoding="utf-8"))

        evidence = contract.index("Inline prompt text is requirements evidence")
        candidate = contract.index(
            "<work-root>/design/<capability>-specification-candidate.md"
        )
        approval = contract.index("explicit approval of the candidate content")
        promotion = contract.index("content-preserving promotion")
        self.assertLess(evidence, candidate)
        self.assertLess(candidate, approval)
        self.assertLess(approval, promotion)
        self.assertIn("docs/specs/<capability>/index.md", contract)
        self.assertIn("docs/specs/<capability>/provenance.json", contract)
        self.assertIn("reachable authoritative entry for `plan-code` and `implement-code`", contract)
        self.assertIn("never depend on the prompt transcript", contract)
        self.assertIn("exact `authoritative_spec_path`", contract)
        self.assertIn("approved specification content reference", contract)

    def test_skip_notion_does_not_skip_local_or_inline_promotion(self) -> None:
        contract = compact(SPEC_CODE.read_text(encoding="utf-8"))

        self.assertIn("`--skip-notion-sync` controls Notion transport only", contract)
        self.assertIn(
            "For every approved local or inline contract, regardless of `--skip-notion-sync`",
            contract,
        )
        self.assertIn("A local source requires its exact explicit path", contract)
        self.assertIn("For a selected Notion source, `--skip-notion-sync` leaves", contract)

    def test_durable_docs_are_manifested_but_excluded_from_the_size_gate(self) -> None:
        contract = compact(SPEC_FRONTMATTER.read_text(encoding="utf-8"))

        self.assertIn("all derived `.md` files and", contract)
        self.assertIn("`generated_files`", contract)
        self.assertIn("versioned `docs/**` remains excluded", contract)
        self.assertIn("only eligible Markdown inside `.engineering/`", contract)


class DirectComparisonAndReconciliationContractTest(unittest.TestCase):
    def test_change_detection_uses_direct_content_comparison(self) -> None:
        sync_spec = compact(SYNC_SPEC.read_text(encoding="utf-8"))
        matrix = compact(CONCURRENT_MATRIX.read_text(encoding="utf-8"))

        for contract in (sync_spec, matrix):
            with self.subTest(contract=contract[:50]):
                self.assertNotIn("contract_digest", contract)
                self.assertNotIn("transport_manifest_hash", contract)
                self.assertNotIn("spec-hashes.py", contract)
        self.assertIn("comparing the specification content", sync_spec)
        self.assertIn("the specification content directly", matrix)

    def test_metadata_only_refreshes_evidence_without_semantic_invalidation(self) -> None:
        sync_spec = compact(SYNC_SPEC.read_text(encoding="utf-8"))
        matrix = compact(CONCURRENT_MATRIX.read_text(encoding="utf-8"))

        for contract in (sync_spec, matrix):
            with self.subTest(contract=contract[:50]):
                self.assertIn("`metadata_only`", contract)
                self.assertIn("last_edited_time", contract)
        self.assertIn("without invalidating approval, plan, code, or review", sync_spec)

    def test_metadata_only_rejects_path_or_unit_structure_change(self) -> None:
        sync_spec = compact(SYNC_SPEC.read_text(encoding="utf-8"))
        matrix = compact(CONCURRENT_MATRIX.read_text(encoding="utf-8"))

        for contract in (sync_spec, matrix):
            with self.subTest(contract=contract[:50]):
                self.assertIn("structural_change", contract)
                self.assertIn("path", contract)
                self.assertIn("metadata-only", contract.lower())
        for caller in (IMPLEMENT_CODE, REVIEW_IMPLEMENTATION, SPEC_CODE):
            with self.subTest(caller=caller):
                self.assertIn("structural_change", compact(caller.read_text(encoding="utf-8")))

    def test_implementation_concurrency_returns_to_specification_stage(self) -> None:
        contract = compact(IMPLEMENT_CODE.read_text(encoding="utf-8"))
        concurrent = contract.index("`next_action: specification_reconciliation`")
        spec_stage = contract.index("`complete --stage=specification`")
        verification = contract.index("independent verification pull", concurrent)
        new_base = contract.index("new immutable base/receipt", concurrent)
        materialize = contract.index("in `materialize` mode", concurrent)
        invalidate = contract.index("Invalidate the old plan approval", concurrent)
        restart = contract.index("restart from Step 3", concurrent)

        self.assertLess(concurrent, spec_stage)
        self.assertLess(spec_stage, verification)
        self.assertLess(verification, new_base)
        self.assertLess(new_base, materialize)
        self.assertLess(materialize, invalidate)
        self.assertLess(invalidate, restart)
        self.assertIn("No implementation-stage push of unreviewed M", contract)

    def test_provenance_never_hashes_itself(self) -> None:
        for path in (SPEC_CODE, SPEC_FRONTMATTER):
            contract = compact(path.read_text(encoding="utf-8"))
            with self.subTest(path=path):
                self.assertTrue(
                    "excludes `provenance.json` itself" in contract
                    or "must exclude `provenance.json` itself" in contract
                )
        self.assertIn("store that self-hash in ignored work evidence", compact(SPEC_FRONTMATTER.read_text(encoding="utf-8")))

    def test_neutral_template_is_local_inline_fallback_only(self) -> None:
        contract = compact(SPEC_CODE.read_text(encoding="utf-8"))
        self.assertTrue(NEUTRAL_TEMPLATE.is_file())
        self.assertIn("Only for local or inline work", contract)
        self.assertIn("assets/technical-spec-template.md", contract)
        self.assertIn("plugin:specification/spec-code/assets/technical-spec-template.md", contract)
        self.assertIn("exact installed Specification plugin version", contract)
        self.assertIn("never publish its machine-local install path", contract)
        self.assertIn("A Notion-backed source must use the selected **live** Notion template", contract)
        self.assertIn("never substitute a bundled snapshot", contract)

    def test_reachable_local_source_cannot_drift_behind_derived_carrier(self) -> None:
        plan = compact(PLAN_CODE.read_text(encoding="utf-8"))
        implement = compact(IMPLEMENT_CODE.read_text(encoding="utf-8"))
        review = compact(REVIEW_IMPLEMENTATION.read_text(encoding="utf-8"))
        provenance = compact(SPEC_FRONTMATTER.read_text(encoding="utf-8"))

        for contract in (plan, implement, review):
            with self.subTest(contract=contract[:50]):
                self.assertIn("reachable `repo:`", contract)
                self.assertIn("source and carrier content directly", contract)
                self.assertIn("ready_for_specification", contract)
                self.assertIn("Git blob oid", contract)
        self.assertIn("the sole reachable authority", plan)
        self.assertIn("the sole reachable authority", implement)
        self.assertIn("Never treat both an unreachable origin and its carrier", provenance)

    def test_new_notion_identity_is_approved_after_creation(self) -> None:
        authoring = compact(SPEC_CODE.read_text(encoding="utf-8"))
        materialization = compact(SYNC_SPEC.read_text(encoding="utf-8"))

        authorization = authoring.index("creation authorization")
        verification = authoring.index("Verification-pull the new stable")
        approval = authoring.index("obtain final specification approval of its post-create content")
        base = authoring.index("establish verified R as initial L/B")
        self.assertLess(authorization, verification)
        self.assertLess(verification, approval)
        self.assertLess(approval, base)
        self.assertIn("Never pretend pre/post-create content matches", authoring)
        self.assertIn("post-create approval plus exact verification evidence", materialization)


if __name__ == "__main__":
    unittest.main()
