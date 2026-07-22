from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
ESSENTIAL_SKILLS = PLUGIN.parent / "essential/skills"
WRITE_CODE = SKILLS / "write-code/SKILL.md"
STACK_SPLIT = SKILLS / "write-code/references/stack-split.md"
HANDOVER = ESSENTIAL_SKILLS / "handover/SKILL.md"
HANDOVER_TEMPLATE = ESSENTIAL_SKILLS / "handover/references/document-templates.md"
HANDOVER_OUTPUT = ESSENTIAL_SKILLS / "handover/references/output-format.md"
TAKEOVER = ESSENTIAL_SKILLS / "takeover/SKILL.md"
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
        self.assertIn("blocked, non-rehydratable status", handover)
        self.assertIn("handover: blocked", output)
        self.assertIn("rehydratable: false", output)

    def test_receipt_is_plain_markdown_with_ordered_sections(self) -> None:
        template = HANDOVER_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("## Handover receipt", template)
        self.assertIn("## Source anchor", template)
        self.assertIn("## Work state", template)
        self.assertIn("## Continuation", template)
        self.assertIn("Work ID:", template)
        self.assertIn("Base commit:", template)
        self.assertIn("no schema version line", template)
        self.assertNotIn("engineering-work-handover/v3", template)
        self.assertNotIn("engineering-work-state+json", template)

    def test_receipt_transfers_state_by_embedding_raw_file_contents(self) -> None:
        output = " ".join(HANDOVER_OUTPUT.read_text(encoding="utf-8").split())

        self.assertIn("raw contents of every `## Work state` file", output)
        self.assertIn("embed the verbatim raw contents", output)

    def test_takeover_parses_plain_markdown_not_a_snapshot(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        verification = " ".join(takeover.split("## Verification", 1)[1].split())

        self.assertIn("plain-Markdown handover receipt", takeover)
        self.assertIn("no schema version line, JSON snapshot", takeover)
        self.assertIn("no snapshot was parsed or re-rendered", verification)
        self.assertIn("no validator gate was run", verification)

    def test_takeover_routes_by_declared_continuation_intent(self) -> None:
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        self.assertIn("declared continuation intent", takeover)
        self.assertIn("reject only a missing or source-contradictory descriptor", takeover)
        self.assertIn("no fixed skill name and no silent fallback", takeover)

    def test_takeover_validates_post_anchor_tree_before_clean_destination(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]
        normalized = " ".join(workflow.split())

        work_state = normalized.index("2. Read the `## Work state` blocks")
        anchor = normalized.index("3. Confirm the current checkout")
        spec = normalized.index("4. Stage the `## Specifications`")
        destination = normalized.index("6. Require and record a clean compatible")

        self.assertLess(work_state, anchor)
        self.assertLess(anchor, spec)
        self.assertLess(spec, destination)
        self.assertIn("post-anchor disposable tree", normalized)
        self.assertIn("clean compatible destination baseline", normalized)

    def test_takeover_bootstraps_only_after_portable_validation(self) -> None:
        takeover = TAKEOVER.read_text(encoding="utf-8")
        main_agent = " ".join(ESSENTIAL_MAIN.read_text(encoding="utf-8").split())
        workflow = takeover.split("## Workflow", 1)[1].split("## Verification", 1)[0]
        normalized = " ".join(workflow.split())

        self.assertLess(
            normalized.index("1. Parse the plain-Markdown handover receipt"),
            normalized.index("6. Require and record a clean compatible"),
        )
        self.assertLess(
            normalized.index("3. Confirm the current checkout"),
            normalized.index("with that ID and `--bootstrap`"),
        )
        self.assertIn("explicit takeover exception", main_agent)
        self.assertIn("exact work ID and `--bootstrap`", main_agent)
        self.assertIn(
            "contains exactly regular `state/working.md` and `state.md`", normalized
        )
        self.assertIn(
            "byte-for-byte the resolver's untouched `initialized` template", normalized
        )
        self.assertIn("only this verified skeleton may later be replaced", normalized)

    def test_takeover_replaces_only_verified_skeleton_and_rolls_back_safely(self) -> None:
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        self.assertIn("Replace only the verified initialized skeleton", takeover)
        self.assertIn("private same-filesystem rollback sibling", takeover)
        self.assertIn(
            "Never merge receipt state into, delete, or rename an unrecognized", takeover
        )
        self.assertIn("preserve both sides and return `partial`", takeover)

    def test_takeover_rejects_unsafe_or_incomplete_payloads(self) -> None:
        takeover = " ".join(TAKEOVER.read_text(encoding="utf-8").split())

        for protection in (
            "credentials, tokens, private keys",
            "absolute paths",
            "symlink traversal",
        ):
            with self.subTest(protection=protection):
                self.assertIn(protection, takeover)


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
