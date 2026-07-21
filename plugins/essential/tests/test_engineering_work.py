from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ESSENTIAL = Path(__file__).resolve().parents[1]
REPOSITORY = ESSENTIAL.parents[1]
CHECKER = ESSENTIAL / "bin/check-markdown-size"
RESOLVER = ESSENTIAL / "bin/resolve-engineering-workspace"
NAME_HELPER = ESSENTIAL / "bin/derive-engineering-name"
SESSION_START = ESSENTIAL / "bin/session-start"
SUBAGENT_START = ESSENTIAL / "bin/subagent-start"
STATE_VALIDATOR = ESSENTIAL / "bin/validate-engineering-state"

MIGRATED_ARTIFACT_WRITERS = {
    "backend/skills/audit-data/SKILL.md",
    "backend/skills/audit-service/SKILL.md",
    "backend/skills/build-data/SKILL.md",
    "backend/skills/build-service/SKILL.md",
    "client/skills/create-screen-design/SKILL.md",
    "client/skills/update-screen-design/SKILL.md",
    "coding/skills/cleanup/SKILL.md",
    "coding/skills/complete-code/SKILL.md",
    "coding/skills/complete-test/SKILL.md",
    "coding/skills/document/SKILL.md",
    "coding/skills/draft-code/SKILL.md",
    "coding/skills/fix/SKILL.md",
    "coding/skills/handover/SKILL.md",
    "coding/skills/push-pr/SKILL.md",
    "coding/skills/review-code/SKILL.md",
    "coding/skills/takeover/SKILL.md",
    "coding/skills/write-code/SKILL.md",
    "essential/skills/autoresearch/SKILL.md",
    "essential/skills/decide/SKILL.md",
    "essential/skills/deep-research/SKILL.md",
    "essential/skills/discover/SKILL.md",
    "essential/skills/handoff/SKILL.md",
    "specification/skills/implement-code/SKILL.md",
    "specification/skills/mdc/SKILL.md",
    "specification/skills/plan-code/SKILL.md",
    "specification/skills/review-implementation/SKILL.md",
    "specification/skills/spec-code/SKILL.md",
    "specification/skills/sync-notion/SKILL.md",
    "specification/skills/sync-spec/SKILL.md",
    "web/skills/audit/SKILL.md",
    "web/skills/design/SKILL.md",
}


class MarkdownSizeCheckerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.engineering_root = self.root / ".engineering"
        self.engineering_root.mkdir()
        self.log = self.root / "wc.log"
        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        fake_wc = fake_bin / "wc"
        fake_wc.write_text(
            "#!/bin/sh\n"
            "printf 'call\\n' >>\"$WC_LOG\"\n"
            "exec /usr/bin/wc \"$@\"\n",
            encoding="utf-8",
        )
        fake_wc.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{fake_bin}:{self.env['PATH']}"
        self.env["WC_LOG"] = str(self.log)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_bytes(self, name: str, size: int) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
        return path

    def run_checker(self, *paths: Path | str) -> tuple[subprocess.CompletedProcess[str], dict]:
        completed = subprocess.run(
            [
                str(CHECKER),
                "--engineering-root",
                str(self.engineering_root),
                *(str(path) for path in paths),
            ],
            text=True,
            capture_output=True,
            check=False,
            env=self.env,
        )
        return completed, json.loads(completed.stdout)

    def calls(self) -> int:
        return len(self.log.read_text().splitlines()) if self.log.exists() else 0

    def test_keeps_fifteen_kib_and_boundary_file_in_one_pass(self) -> None:
        first = self.write_bytes(".engineering/works/eng-421/fifteen kib.md", 15 * 1024)
        second = self.write_bytes(".engineering/works/eng-421/boundary.md", 16_384)

        completed, payload = self.run_checker(first, second)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(2, payload["checked"])
        self.assertEqual([], payload["oversized"])
        self.assertEqual(1, self.calls())

    def test_returns_every_oversized_file_together_after_one_wc(self) -> None:
        first = self.write_bytes(".engineering/works/eng-421/one.md", 16_385)
        second = self.write_bytes(
            ".engineering/works/eng-421/dir with spaces/two.md", 20_000
        )
        valid = self.write_bytes(".engineering/works/eng-421/valid.md", 12_289)

        completed, payload = self.run_checker(first, second, valid)

        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertEqual("split_required", payload["status"])
        self.assertEqual(
            {str(first): 16_385, str(second): 20_000},
            {entry["path"]: entry["bytes"] for entry in payload["oversized"]},
        )
        self.assertEqual(1, self.calls())

    def test_deduplicates_and_excludes_working_and_external_markdown(self) -> None:
        measured = self.write_bytes(".engineering/works/eng-421/normal.md", 100)
        working = self.write_bytes(
            ".engineering/works/eng-421/nested/working.md", 30_000
        )
        durable = self.write_bytes("docs/specs/payments/index.md", 30_000)
        plugin_source = self.write_bytes("plugins/example/SKILL.md", 30_000)

        completed, payload = self.run_checker(
            measured, measured, working, durable, plugin_source
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(1, payload["checked"])
        self.assertCountEqual(
            [str(working), str(durable), str(plugin_source)], payload["excluded"]
        )
        self.assertEqual(1, self.calls())

    def test_all_excluded_is_a_pass_without_wc(self) -> None:
        working = self.write_bytes(
            ".engineering/works/eng-421/working.md", 30_000
        )
        durable = self.write_bytes("docs/architecture/large.md", 30_000)

        completed, payload = self.run_checker(working, durable)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["checked"])
        self.assertEqual(0, self.calls())

    def test_canonical_boundary_excludes_traversal_symlink_and_other_root(self) -> None:
        outside = self.write_bytes("docs/outside.md", 20_000)
        linked_outside = self.write_bytes("docs/linked-outside.md", 20_000)
        traversal = self.engineering_root / ".." / "docs" / "outside.md"
        symlink = self.engineering_root / "works/eng-421/linked.md"
        symlink.parent.mkdir(parents=True)
        symlink.symlink_to(linked_outside)
        other = self.write_bytes("other/.engineering/works/eng-9/other.md", 20_000)

        completed, payload = self.run_checker(traversal, symlink, other)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["checked"])
        self.assertCountEqual(
            [str(traversal), str(symlink), str(other)], payload["excluded"]
        )
        self.assertEqual(0, self.calls())

    def test_invalid_and_missing_inputs_are_distinct_from_split(self) -> None:
        not_markdown = self.write_bytes(".engineering/works/eng-421/data.mdc", 10)
        cases = (
            (),
            ("relative.md",),
            (self.root / "missing.md",),
            (not_markdown,),
        )
        for paths in cases:
            with self.subTest(paths=paths):
                completed, payload = self.run_checker(*paths)
                self.assertEqual(2, completed.returncode)
                self.assertEqual("invalid", payload["status"])
        self.assertEqual(0, self.calls())

        completed = subprocess.run(
            [str(CHECKER), str(self.root / "missing.md")],
            text=True,
            capture_output=True,
            check=False,
            env=self.env,
        )
        self.assertEqual(2, completed.returncode)
        self.assertEqual("invalid", json.loads(completed.stdout)["status"])


class EngineeringNameTest(unittest.TestCase):
    def run_name(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(NAME_HELPER), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_slug_conformance_fixtures(self) -> None:
        fixtures = (
            ("Crème brûlée déjà vu", "creme-brulee-deja-vu"),
            ("Payments / refunds?! v2.0", "payments-refunds-v2-0"),
            ("影師嗎", "item"),
            (
                "one two three four five six seven eight nine ten eleven",
                "one-two-three-four-five-six-seven-eight-nine-ten",
            ),
            (
                "one two three four five six seven eight nine twelve",
                "one-two-three-four-five-six-seven-eight-nine",
            ),
        )
        for value, expected in fixtures:
            with self.subTest(value=value):
                completed = self.run_name("slug", value)
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertEqual(expected, completed.stdout.strip())
                self.assertLessEqual(len(completed.stdout.strip().encode("ascii")), 48)

    def test_collision_suffix_is_stable_source_hash(self) -> None:
        identity = "notion:abc"
        expected = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:8]
        completed = self.run_name(
            "slug",
            "API Gateway",
            "--collision-with",
            "api-gateway",
            "--stable-id",
            identity,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(f"api-gateway--{expected}", completed.stdout.strip())
        self.assertLessEqual(len(completed.stdout.strip().encode("ascii")), 48)

    def test_collision_reserves_suffix_without_partial_trailing_token(self) -> None:
        value = "one two three four five six seven eight nine ten eleven"
        occupied = "one-two-three-four-five-six-seven-eight-nine-ten"
        completed = self.run_name(
            "slug",
            value,
            "--collision-with",
            occupied,
            "--stable-id",
            "architecture:checkout",
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        result = completed.stdout.strip()
        self.assertLessEqual(len(result.encode("ascii")), 48)
        self.assertEqual("one-two-three-four-five-six-seven", result.split("--", 1)[0])

    def test_collision_without_stable_identity_is_invalid(self) -> None:
        completed = self.run_name(
            "slug", "API Gateway", "--collision-with", "api-gateway"
        )

        self.assertEqual(2, completed.returncode)
        self.assertIn("--stable-id is required", completed.stderr)

    def test_work_id_conformance(self) -> None:
        tracker = self.run_name("tracker-work-id", "ENG 421 / Checkout Refunds")
        minted = self.run_name(
            "minted-work-id",
            "--date",
            "20260720",
            "--kind",
            "Feature Request",
            "--scope",
            "Checkout Refunds",
            "--ulid",
            "01J2Z3Y4X5W6V7T8S9R0Q1P2N3",
        )

        self.assertEqual(0, tracker.returncode, tracker.stderr)
        self.assertEqual(0, minted.returncode, minted.stderr)
        self.assertEqual("eng-421-checkout-refunds", tracker.stdout.strip())
        self.assertEqual(
            "20260720-feature-request-checkout-refunds-q1p2n3",
            minted.stdout.strip(),
        )


class EngineeringWorkStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def digest(rows: list[dict]) -> str:
        definitions = [
            {
                "acceptance": row["acceptance"],
                "depends_on": sorted(row.get("depends_on", [])),
                "id": row["id"],
                "required": row.get("required", True),
                "targets": sorted(row.get("targets", [])),
                "task": row["task"],
            }
            for row in sorted(rows, key=lambda value: value["id"])
        ]
        encoded = json.dumps(
            {"hash_kind": "engineering-plan-definition-digest-v1", "tasks": definitions},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def write_state(
        self,
        rows: list[dict],
        *,
        name: str = "state.md",
        lifecycle: str = "active",
        role: str = "root",
        parent_task: str | None = None,
        topology: str = "linear",
    ) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = [
            "# Engineering work",
            "",
            "- Schema: `engineering-work-state/v1`",
            f"- State role: `{role}`",
            "- Work ID: `eng-421-state`",
            f"- Lifecycle status: `{lifecycle}`",
        ]
        if role == "root":
            metadata.extend(
                [
                    f"- Plan source: `{name}`",
                    f"- Plan digest: `{self.digest(rows)}`",
                    "- Hash kind: `engineering-plan-definition-digest-v1`",
                    "- Next owner: `PM`",
                    "- Next action: Continue the ready task.",
                ]
            )
        else:
            metadata.append(f"- Parent task: `{parent_task}`")
        metadata.extend(
            [
                "",
                "## Status",
                "",
                f"- Lifecycle: `{lifecycle}`",
                f"- Topology: `{topology}`",
                "",
                "## Tasks",
                "",
                "| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        mark = {
            "planned": "-", "working": "⧗", "done": "✓",
            "failed": "X", "blocked": "!", "cancelled": "⊘",
        }
        for row in rows:
            targets = ", ".join(row.get("targets", [])) or "none"
            dependencies = ", ".join(row.get("depends_on", [])) or "—"
            metadata.append(
                "| {id} | {mark} | {status} | {task} [targets: {targets}] | "
                "{dependencies} | {required} | {acceptance} | {owner} | {evidence} |".format(
                    id=row["id"],
                    mark=mark[row["status"]],
                    status=row["status"],
                    task=row["task"],
                    targets=targets,
                    dependencies=dependencies,
                    required="yes" if row.get("required", True) else "no",
                    acceptance=row["acceptance"],
                    owner=row.get("owner", "PM"),
                    evidence=row.get("evidence", "Continue when ready."),
                )
            )
        path.write_text("\n".join(metadata) + "\n", encoding="utf-8")
        return path

    def run_validator(self, *arguments: str | Path) -> tuple[subprocess.CompletedProcess[str], dict]:
        completed = subprocess.run(
            [str(STATE_VALIDATOR), *(str(value) for value in arguments)],
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, json.loads(completed.stdout)

    def test_validates_branching_parent_and_child_graphs(self) -> None:
        child_rows = [
            {"id": "DSC01", "status": "done", "task": "Frame discovery", "acceptance": "Frame recorded.", "evidence": "evidence: frame.md"},
            {"id": "DSC02", "status": "planned", "task": "Probe users", "depends_on": ["DSC01"], "acceptance": "User probe recorded."},
            {"id": "DSC03", "status": "planned", "task": "Probe systems", "depends_on": ["DSC01"], "acceptance": "System probe recorded."},
            {"id": "DSC04", "status": "planned", "task": "Synthesize", "depends_on": ["DSC02", "DSC03"], "acceptance": "Synthesis recorded."},
        ]
        root_rows = [
            {
                "id": "DSC",
                "status": "working",
                "task": "Complete discovery",
                "acceptance": "Discovery is decision-ready.",
                "evidence": "Discovery probes are active.",
            },
            *child_rows,
        ]
        root = self.write_state(root_rows)
        child = self.write_state(
            child_rows,
            name="state/discovery.md",
            role="child",
            parent_task="DSC",
            topology="dag",
        )
        narrative_plan = self.root / "state/implementation-plan.md"
        narrative_plan.write_text(
            "# Implementation plan\n\nThis semantic plan is not a v1 child mirror.\n",
            encoding="utf-8",
        )

        completed, payload = self.run_validator("validate", "--state", child)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("valid", payload["status"])
        self.assertEqual("dag", payload["topology"])
        self.assertEqual(["DSC02", "DSC03"], payload["runnable_leaf_task_ids"])
        self.assertEqual([], payload["blocked_task_ids"])
        self.assertEqual("DSC01 → {DSC02,DSC03} → DSC04", payload["graph_display"])
        root_valid, root_valid_payload = self.run_validator("validate", "--state", root)
        self.assertEqual(0, root_valid.returncode, root_valid.stderr)
        self.assertEqual("valid", root_valid_payload["status"])
        direct_plan, direct_plan_payload = self.run_validator(
            "validate", "--state", narrative_plan
        )
        self.assertEqual(3, direct_plan.returncode)
        self.assertEqual("migration_required", direct_plan_payload["status"])

        child.write_text(child.read_text(encoding="utf-8").replace("Probe users", "Probe customers"), encoding="utf-8")
        drifted, drift_payload = self.run_validator("validate", "--state", child)
        self.assertEqual(2, drifted.returncode)
        self.assertTrue(any(error["code"] == "child_task_drift" for error in drift_payload["errors"]))
        root_result, root_payload = self.run_validator("validate", "--state", root)
        self.assertEqual(2, root_result.returncode)
        self.assertTrue(any(error["code"] == "child_task_drift" for error in root_payload["errors"]))

    def test_digest_excludes_runtime_fields_and_includes_targets(self) -> None:
        rows = [
            {"id": "GOL", "status": "planned", "task": "Confirm goal", "targets": ["docs/spec.md"], "acceptance": "Goal confirmed."},
            {"id": "OWN", "status": "planned", "task": "Select owner", "depends_on": ["GOL"], "acceptance": "Owner selected."},
        ]
        first = self.write_state(rows, name="first.md")
        rows[0].update(status="working", owner="Lead", evidence="Work is active.")
        second = self.write_state(rows, name="second.md")
        _, first_payload = self.run_validator("validate", "--state", first)
        _, second_payload = self.run_validator("validate", "--state", second)
        self.assertEqual(first_payload["computed_plan_digest"], second_payload["computed_plan_digest"])

        rows[0]["targets"] = ["docs/other.md"]
        third = self.write_state(rows, name="third.md")
        _, third_payload = self.run_validator("validate", "--state", third)
        self.assertNotEqual(first_payload["computed_plan_digest"], third_payload["computed_plan_digest"])

        rows[0]["targets"] = ["b", "a"]
        rows[1]["depends_on"] = ["GOL"]
        ordered = self.write_state(rows, name="ordered.md")
        _, ordered_payload = self.run_validator("validate", "--state", ordered)
        rows[0]["targets"] = ["a", "b"]
        reordered = self.write_state(rows, name="reordered.md")
        _, reordered_payload = self.run_validator("validate", "--state", reordered)
        self.assertEqual(ordered_payload["computed_plan_digest"], reordered_payload["computed_plan_digest"])

    def test_diamond_failure_blocks_only_the_join(self) -> None:
        rows = [
            {"id": "DSC", "status": "failed", "task": "Complete discovery", "acceptance": "Discovery complete.", "evidence": "attempt: probe; retry: repair branch"},
            {"id": "DSC01", "status": "done", "task": "Frame", "acceptance": "Frame complete.", "evidence": "evidence: frame"},
            {"id": "DSC02", "status": "failed", "task": "Probe A", "depends_on": ["DSC01"], "acceptance": "Probe A complete.", "evidence": "attempt: test; retry: fix"},
            {"id": "DSC03", "status": "planned", "task": "Probe B", "depends_on": ["DSC01"], "acceptance": "Probe B complete."},
            {"id": "DSC04", "status": "blocked", "task": "Join", "depends_on": ["DSC02", "DSC03"], "acceptance": "Join complete.", "evidence": "unblock: repair DSC02"},
        ]
        state = self.write_state(rows, topology="linear")
        completed, payload = self.run_validator("validate", "--state", state)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(["DSC03"], payload["runnable_leaf_task_ids"])
        self.assertEqual(["DSC04"], payload["blocked_task_ids"])

        previous_rows = [dict(row) for row in rows]
        previous_rows[2] = {**previous_rows[2], "task": "Original probe A"}
        previous = self.write_state(previous_rows, name="previous.md", topology="linear")
        _, changed = self.run_validator(
            "validate", "--state", state, "--previous-state", previous
        )
        self.assertIn("DSC02", changed["invalidated_downstream_closure"])
        self.assertIn("DSC04", changed["invalidated_downstream_closure"])
        self.assertNotIn("DSC03", changed["invalidated_downstream_closure"])

    def test_optional_terminal_rollup_and_cancelled_dependency(self) -> None:
        rows = [
            {"id": "OPT", "status": "done", "required": False, "task": "Optional exploration", "acceptance": "Optional exploration is disposed.", "evidence": "evidence: one useful result"},
            {"id": "OPT01", "status": "done", "required": False, "task": "Useful probe", "acceptance": "Probe disposed.", "evidence": "evidence: result"},
            {"id": "OPT02", "status": "cancelled", "required": False, "task": "Unneeded probe", "acceptance": "Probe disposed.", "evidence": "approved-plan-revision: 2"},
        ]
        state = self.write_state(rows)
        completed, payload = self.run_validator("validate", "--state", state)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("valid", payload["status"])

        dependency_rows = [
            {"id": "OLD", "status": "cancelled", "required": False, "task": "Retired prerequisite", "acceptance": "Prerequisite retired.", "evidence": "approved-plan-revision: 2"},
            {"id": "NEW", "status": "planned", "task": "Dependent work", "depends_on": ["OLD"], "acceptance": "Dependent work complete."},
        ]
        dependency = self.write_state(dependency_rows, name="dependency.md")
        result, result_payload = self.run_validator("validate", "--state", dependency)
        self.assertEqual(2, result.returncode)
        self.assertEqual([], result_payload["runnable_leaf_task_ids"])
        self.assertEqual(["NEW"], result_payload["blocked_task_ids"])
        self.assertTrue(any(error["code"] == "unreconciled_blocked_task" for error in result_payload["errors"]))

    def test_execution_cannot_start_before_dependencies(self) -> None:
        for status in ("working", "done", "failed"):
            with self.subTest(status=status):
                rows = [
                    {"id": "PRE", "status": "planned", "task": "Prerequisite", "acceptance": "Prerequisite complete."},
                    {
                        "id": "RUN",
                        "status": status,
                        "task": "Dependent",
                        "depends_on": ["PRE"],
                        "acceptance": "Dependent complete.",
                        "evidence": (
                            "evidence: result" if status == "done"
                            else "attempt: test; retry: after prerequisite" if status == "failed"
                            else "Work is active."
                        ),
                    },
                ]
                state = self.write_state(rows, name=f"{status}.md")
                result, payload = self.run_validator("validate", "--state", state)
                self.assertEqual(2, result.returncode)
                self.assertTrue(any(error["code"] == "task_started_before_dependencies" for error in payload["errors"]))

        blocked_rows = [
            {"id": "RUN", "status": "working", "task": "Required active work", "acceptance": "Work complete.", "evidence": "Work is active."},
        ]
        blocked = self.write_state(blocked_rows, name="blocked.md", lifecycle="blocked")
        result, payload = self.run_validator("validate", "--state", blocked)
        self.assertEqual(2, result.returncode)
        self.assertTrue(any(error["code"] == "contradictory_blocked_lifecycle" for error in payload["errors"]))

    def test_task_table_rejects_extra_columns(self) -> None:
        rows = [{"id": "GOL", "status": "planned", "task": "Confirm goal", "acceptance": "Goal confirmed."}]
        state = self.write_state(rows)
        text = state.read_text(encoding="utf-8")
        text = text.replace(
            "| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |",
            "| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action | Extra |",
        ).replace(
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ).replace("| GOL | - | planned |", "| GOL | - | planned |", 1)
        lines = text.splitlines()
        row_index = next(index for index, line in enumerate(lines) if line.startswith("| GOL |"))
        lines[row_index] = lines[row_index][:-1] + " Extra |"
        state.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result, payload = self.run_validator("validate", "--state", state)
        self.assertEqual(2, result.returncode)
        self.assertTrue(any(error["code"] == "invalid_tasks_header" for error in payload["errors"]))

    def test_snapshot_rejects_graph_and_ledger_drift_and_round_trips(self) -> None:
        rows = [
            {"id": "GOL", "status": "done", "task": "Confirm goal", "acceptance": "Goal confirmed.", "evidence": "evidence: approved spec"},
            {"id": "OWN", "status": "planned", "task": "Select owner", "depends_on": ["GOL"], "acceptance": "Owner selected."},
        ]
        state = self.write_state(rows)
        packed = subprocess.run(
            [str(STATE_VALIDATOR), "pack", "--state", str(state)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, packed.returncode, packed.stderr)
        snapshot = json.loads(packed.stdout)
        snapshot_path = self.root / "snapshot.json"
        snapshot_path.write_text(packed.stdout, encoding="utf-8")
        valid, payload = self.run_validator("validate-snapshot", "--snapshot", snapshot_path)
        self.assertEqual(0, valid.returncode, valid.stderr)
        self.assertEqual("valid", payload["status"])
        self.assertEqual("PM", payload["next_owner"])
        self.assertEqual("Continue the ready task.", payload["next_action"])
        self.assertEqual(["OWN"], payload["runnable_leaf_task_ids"])
        self.assertEqual(2, len(payload["execution_ledger"]))

        rendered = subprocess.run(
            [str(STATE_VALIDATOR), "render", "--snapshot", str(snapshot_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, rendered.returncode, rendered.stderr)
        rendered_path = self.root / "rendered.md"
        rendered_path.write_text(rendered.stdout, encoding="utf-8")
        checked, _ = self.run_validator("validate", "--state", rendered_path)
        self.assertEqual(0, checked.returncode, checked.stderr)

        for key, mutation in (
            ("graph", lambda value: value["parent_graph"].update({"OWN": []})),
            ("ledger", lambda value: value["execution_ledger"].pop()),
            ("topology", lambda value: value.update(topology="dag")),
        ):
            with self.subTest(key=key):
                tampered = json.loads(packed.stdout)
                mutation(tampered)
                target = self.root / f"{key}.json"
                target.write_text(json.dumps(tampered), encoding="utf-8")
                result, result_payload = self.run_validator("validate-snapshot", "--snapshot", target)
                self.assertEqual(2, result.returncode)
                self.assertEqual("invalid", result_payload["status"])

        pretty_path = self.root / "pretty.json"
        pretty_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        pretty, pretty_payload = self.run_validator("validate-snapshot", "--snapshot", pretty_path)
        self.assertEqual(2, pretty.returncode)
        self.assertTrue(any(error["code"] == "noncanonical_snapshot_bytes" for error in pretty_payload["errors"]))

        control = json.loads(packed.stdout)
        control["next_action"] = "unsafe\ncontinuation"
        control_path = self.root / "control.json"
        control_path.write_text(
            json.dumps(control, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        control_result, control_payload = self.run_validator("validate-snapshot", "--snapshot", control_path)
        self.assertEqual(2, control_result.returncode)
        self.assertTrue(any(error["code"] == "snapshot_control_character" for error in control_payload["errors"]))

        ordered_rows = [
            {"id": "GOL", "status": "planned", "task": "Confirm goal", "targets": ["a", "b"], "acceptance": "Goal confirmed."},
        ]
        ordered_state = self.write_state(ordered_rows, name="ordering.md")
        ordered_pack = subprocess.run(
            [str(STATE_VALIDATOR), "pack", "--state", str(ordered_state)],
            text=True, capture_output=True, check=False,
        )
        reordered_snapshot = json.loads(ordered_pack.stdout)
        reordered_snapshot["tasks"][0]["targets"] = ["b", "a"]
        reordered_path = self.root / "reordered-snapshot.json"
        reordered_path.write_text(
            json.dumps(reordered_snapshot, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        reordered_result, reordered_payload = self.run_validator("validate-snapshot", "--snapshot", reordered_path)
        self.assertEqual(2, reordered_result.returncode)
        self.assertTrue(any(error["code"] == "snapshot_roundtrip_drift" for error in reordered_payload["errors"]))

    def test_legacy_and_id_reuse_require_explicit_migration(self) -> None:
        legacy = self.root / "legacy.md"
        legacy.write_text("# Engineering work\n\n- Status: `complete`\n", encoding="utf-8")
        completed, payload = self.run_validator("validate", "--state", legacy)
        self.assertEqual(3, completed.returncode)
        self.assertEqual("migration_required", payload["status"])

        old_rows = [{"id": "OLD", "status": "cancelled", "required": False, "task": "Retired task", "acceptance": "Task retired.", "evidence": "approved-plan-revision: 2"}]
        new_rows = [{**old_rows[0], "status": "planned"}]
        old = self.write_state(old_rows, name="old.md")
        new = self.write_state(new_rows, name="new.md")
        result, result_payload = self.run_validator(
            "validate", "--state", new, "--previous-state", old
        )
        self.assertEqual(2, result.returncode)
        self.assertTrue(any(error["code"] == "recycled_cancelled_task_id" for error in result_payload["errors"]))

        renamed_rows = [{**old_rows[0], "id": "NEW"}]
        renamed = self.write_state(renamed_rows, name="renamed.md")
        renamed_result, renamed_payload = self.run_validator(
            "validate", "--state", renamed, "--previous-state", old
        )
        self.assertEqual(2, renamed_result.returncode)
        self.assertTrue(any(error["code"] == "renamed_task_id" for error in renamed_payload["errors"]))
        self.assertTrue(any(error["code"] == "removed_task_tombstone" for error in renamed_payload["errors"]))

    def test_v1_requires_explicit_role_and_work_id(self) -> None:
        rows = [{"id": "GOL", "status": "planned", "task": "Confirm goal", "acceptance": "Goal confirmed."}]
        state = self.write_state(rows)
        text = state.read_text(encoding="utf-8")
        for label in ("- State role: `root`\n", "- Work ID: `eng-421-state`\n"):
            with self.subTest(label=label):
                state.write_text(text.replace(label, ""), encoding="utf-8")
                result, payload = self.run_validator("validate", "--state", state)
                self.assertEqual(2, result.returncode)
                self.assertEqual("invalid", payload["status"])
        state.write_text(text, encoding="utf-8")

class WorkspaceResolverTest(unittest.TestCase):
    def run_resolver(
        self,
        path: Path,
        work_id: str | None = None,
        *,
        bootstrap: bool = False,
        environment_work_id: str | None = None,
        extra_environment: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [str(RESOLVER), "--path", str(path)]
        if work_id is not None:
            command.extend(("--work-id", work_id))
        if bootstrap:
            command.append("--bootstrap")
        environment = os.environ.copy()
        environment.pop("ENGINEERING_WORK_ID", None)
        if environment_work_id is not None:
            environment["ENGINEERING_WORK_ID"] = environment_work_id
        if extra_environment:
            environment.update(extra_environment)
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        return completed, json.loads(completed.stdout)

    def git(self, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "commit.gpgSign=false", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )

    def initialize_git(self, root: Path, *, ignored: bool = True) -> None:
        root.mkdir()
        self.git("init", "-q", cwd=root)
        self.git("symbolic-ref", "HEAD", "refs/heads/main", cwd=root)
        self.git("config", "user.email", "test@example.com", cwd=root)
        self.git("config", "user.name", "Test", cwd=root)
        if ignored:
            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")

    def commit_initial(self, root: Path) -> None:
        (root / "readme.md").write_text("test\n", encoding="utf-8")
        paths = ["readme.md"]
        if (root / ".gitignore").exists():
            paths.append(".gitignore")
        self.git("add", *paths, cwd=root)
        self.git("commit", "-qm", "initial", cwd=root)

    def test_suggests_but_does_not_invent_new_work_from_git_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main workspace"
            linked = Path(temporary) / "linked workspace"
            self.initialize_git(root)
            self.commit_initial(root)
            self.git(
                "worktree",
                "add",
                "-q",
                "-b",
                "feature/refunds",
                str(linked),
                cwd=root,
            )

            completed, payload = self.run_resolver(linked)

            self.assertEqual(4, completed.returncode, completed.stderr)
            self.assertEqual("work_id_required", payload["status"])
            self.assertEqual("git", payload["vcs"])
            self.assertEqual(str(linked.resolve()), payload["repo_root"])
            self.assertEqual(str(linked.resolve()), payload["durable_root"])
            self.assertEqual(str(root.resolve()), payload["default_workspace"])
            self.assertEqual(str(linked.resolve()), payload["active_workspace"])
            self.assertEqual("feature/refunds", payload["workspace_label"])
            self.assertEqual("feature-refunds", payload["suggested_work_id"])
            self.assertEqual([], payload["candidate_work_ids"])
            self.assertNotIn("work_dir", payload)

            for work_id in ("refunds", "other-work"):
                (linked / ".engineering/works" / work_id).mkdir(parents=True)
            completed, payload = self.run_resolver(linked)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("refunds", payload["work_id"])
            self.assertEqual("git_branch", payload["work_id_source"])

    def test_feature_branch_does_not_select_a_mismatched_sole_work_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main workspace"
            linked = Path(temporary) / "linked workspace"
            self.initialize_git(root)
            self.commit_initial(root)
            self.git(
                "worktree",
                "add",
                "-q",
                "-b",
                "feature/refunds",
                str(linked),
                cwd=root,
            )
            (linked / ".engineering/works/unrelated-work").mkdir(parents=True)

            completed, payload = self.run_resolver(linked)

            self.assertEqual(4, completed.returncode, completed.stderr)
            self.assertEqual("work_id_required", payload["status"])
            self.assertEqual("feature-refunds", payload["suggested_work_id"])
            self.assertEqual(["unrelated-work"], payload["candidate_work_ids"])

    def test_explicit_then_environment_then_existing_selection_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "selection"
            self.initialize_git(root)
            (root / ".engineering/works/existing").mkdir(parents=True)

            completed, payload = self.run_resolver(
                root, "explicit", environment_work_id="environment"
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("explicit", payload["work_id"])
            self.assertEqual("argument", payload["work_id_source"])

            completed, payload = self.run_resolver(
                root, environment_work_id="environment"
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("environment", payload["work_id"])
            self.assertEqual("environment", payload["work_id_source"])

            completed, payload = self.run_resolver(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("existing", payload["work_id"])
            self.assertEqual("sole_existing", payload["work_id_source"])

    def test_accepts_spaced_and_equals_option_forms(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "option forms"
            self.initialize_git(root)

            spaced, spaced_payload = self.run_resolver(root, "eng-421-spaced")
            equals = subprocess.run(
                [
                    str(RESOLVER),
                    f"--path={root}",
                    "--work-id=eng-421-equals",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            equals_payload = json.loads(equals.stdout)

            self.assertEqual(0, spaced.returncode, spaced.stderr)
            self.assertEqual("eng-421-spaced", spaced_payload["work_id"])
            self.assertEqual(0, equals.returncode, equals.stderr)
            self.assertEqual("eng-421-equals", equals_payload["work_id"])
            self.assertEqual("argument", equals_payload["work_id_source"])

            help_result = subprocess.run(
                [str(RESOLVER), "--help"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, help_result.returncode)
            self.assertIn("--work-id=<id>", help_result.stderr)
            self.assertIn("--path=<path>", help_result.stderr)
            self.assertIn("--bootstrap", help_result.stderr)

    def test_pm_bootstrap_creates_only_missing_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bootstrap"
            self.initialize_git(root)
            work_id = "eng-421-bootstrap"

            resolved, resolved_payload = self.run_resolver(root, work_id)
            work_dir = Path(resolved_payload["work_dir"])

            self.assertEqual(0, resolved.returncode, resolved.stderr)
            self.assertFalse(resolved_payload["bootstrap_requested"])
            self.assertEqual([], resolved_payload["bootstrap_created"])
            self.assertFalse(work_dir.exists())

            created, created_payload = self.run_resolver(
                root, work_id, bootstrap=True
            )

            working = work_dir / "working.md"
            state = work_dir / "state.md"
            self.assertEqual(0, created.returncode, created.stderr)
            self.assertTrue(created_payload["bootstrap_requested"])
            self.assertEqual(
                [str(working), str(state)], created_payload["bootstrap_created"]
            )
            self.assertEqual([], created_payload["bootstrap_existing"])
            working_text = working.read_text(encoding="utf-8")
            state_text = state.read_text(encoding="utf-8")
            self.assertIn(f"- Work ID: `{work_id}`", working_text)
            self.assertIn("- Status: `initialized`", working_text)
            self.assertIn("- State: [state.md](state.md)", working_text)
            self.assertIn(f"- Work ID: `{work_id}`", state_text)
            self.assertIn("- Schema: `engineering-work-state/v1`", state_text)
            self.assertIn("- Plan source: `state.md`", state_text)
            self.assertIn("| GOL | - | planned |", state_text)
            self.assertIn("| OWN | - | planned |", state_text)
            self.assertIn("## Goal and success criteria", state_text)
            self.assertIn("- Current focus: [working.md](working.md)", state_text)
            self.assertIn("- Specification provenance: Not established.", state_text)
            self.assertIn("- Sync state: Not started.", state_text)
            self.assertIn("- Review state: Not started.", state_text)
            validator = subprocess.run(
                [str(STATE_VALIDATOR), "validate", "--state", str(state)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, validator.returncode, validator.stderr)
            validation = json.loads(validator.stdout)
            self.assertEqual("valid", validation["status"])
            self.assertEqual(
                "d66c594201a4f94faf69e28ffef886bf18c5c9464604d43f3221fa9961896a68",
                validation["plan_digest"],
            )

            custom_working = "# Preserved owner state\n\nDo not replace me.\n"
            working.write_text(custom_working, encoding="utf-8")
            state.unlink()

            repaired, repaired_payload = self.run_resolver(
                root, work_id, bootstrap=True
            )

            self.assertEqual(0, repaired.returncode, repaired.stderr)
            self.assertEqual([str(state)], repaired_payload["bootstrap_created"])
            self.assertEqual([str(working)], repaired_payload["bootstrap_existing"])
            self.assertEqual(custom_working, working.read_text(encoding="utf-8"))
            self.assertTrue(state.is_file())

    def test_bootstrap_cannot_bypass_identity_or_ignore_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bootstrap gates"
            self.initialize_git(root, ignored=False)

            identity = subprocess.run(
                [str(RESOLVER), "--path", str(root), "--bootstrap"],
                text=True,
                capture_output=True,
                check=False,
            )
            identity_payload = json.loads(identity.stdout)
            self.assertEqual(4, identity.returncode)
            self.assertEqual("work_id_required", identity_payload["status"])
            self.assertFalse((root / ".engineering").exists())

            ignored, ignored_payload = self.run_resolver(
                root, "eng-421-gated", bootstrap=True
            )
            self.assertEqual(3, ignored.returncode)
            self.assertEqual("requires_ignore", ignored_payload["status"])
            self.assertFalse((root / ".engineering").exists())

    def test_bootstrap_rejects_symlinked_work_root_without_external_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "bootstrap symlink"
            outside = Path(temporary) / "outside"
            self.initialize_git(root)
            outside.mkdir()
            (root / ".engineering").mkdir()
            (root / ".engineering/works").symlink_to(outside, target_is_directory=True)

            completed, payload = self.run_resolver(
                root, "eng-421-symlink", bootstrap=True
            )

            self.assertEqual(2, completed.returncode)
            self.assertEqual("invalid", payload["status"])
            self.assertIn("must not be a symlink", payload["error"])
            self.assertEqual([], list(outside.iterdir()))

    def test_normal_resolution_rejects_symlinked_work_root_explicit_and_auto(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "normal symlink"
            outside = Path(temporary) / "outside"
            self.initialize_git(root)
            (outside / "eng-421-symlink").mkdir(parents=True)
            (root / ".engineering").mkdir()
            (root / ".engineering/works").symlink_to(outside, target_is_directory=True)

            explicit, explicit_payload = self.run_resolver(
                root, "eng-421-symlink"
            )
            automatic, automatic_payload = self.run_resolver(root)

            for completed, payload in (
                (explicit, explicit_payload),
                (automatic, automatic_payload),
            ):
                self.assertEqual(2, completed.returncode)
                self.assertEqual("invalid", payload["status"])
                self.assertIn("must not be a symlink", payload["error"])

    def test_normal_and_bootstrap_resolution_reject_symlinked_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "entrypoint symlink"
            outside = Path(temporary) / "outside-state.md"
            self.initialize_git(root)
            work_dir = root / ".engineering/works/eng-421-symlink"
            work_dir.mkdir(parents=True)
            outside.write_text("outside must remain unchanged\n", encoding="utf-8")
            (work_dir / "state.md").symlink_to(outside)

            automatic, automatic_payload = self.run_resolver(root)
            bootstrap, bootstrap_payload = self.run_resolver(
                root, "eng-421-symlink", bootstrap=True
            )

            for completed, payload in (
                (automatic, automatic_payload),
                (bootstrap, bootstrap_payload),
            ):
                self.assertEqual(2, completed.returncode)
                self.assertEqual("invalid", payload["status"])
                self.assertIn("entrypoint must not be a symlink", payload["error"])
            self.assertEqual(
                "outside must remain unchanged\n",
                outside.read_text(encoding="utf-8"),
            )

    def test_returns_structured_ambiguity_and_uses_workspace_match(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main"
            linked = Path(temporary) / "linked"
            self.initialize_git(root)
            self.commit_initial(root)
            for work_id in ("eng-42", "eng-99"):
                (root / ".engineering/works" / work_id).mkdir(parents=True)

            completed, payload = self.run_resolver(root)

            self.assertEqual(4, completed.returncode)
            self.assertEqual("work_id_required", payload["status"])
            self.assertEqual(["eng-42", "eng-99"], payload["candidate_work_ids"])
            self.assertEqual("main", payload["workspace_label"])

            self.git(
                "worktree", "add", "-q", "-b", "eng-42", str(linked), cwd=root
            )
            for work_id in ("eng-42", "eng-99"):
                (linked / ".engineering/works" / work_id).mkdir(parents=True)
            completed, payload = self.run_resolver(linked)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("eng-42", payload["work_id"])
            self.assertEqual("git_branch", payload["work_id_source"])

    def test_generic_workspace_without_existing_work_requires_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main"
            self.initialize_git(root)

            completed, payload = self.run_resolver(root)

            self.assertEqual(4, completed.returncode)
            self.assertEqual("work_id_required", payload["status"])
            self.assertEqual([], payload["candidate_work_ids"])
            self.assertIsNone(payload["suggested_work_id"])

    def test_requires_pm_ignore_bootstrap_after_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "missing ignore"
            self.initialize_git(root, ignored=False)

            completed, payload = self.run_resolver(root, "eng-421-test")

            self.assertEqual(3, completed.returncode)
            self.assertEqual("requires_ignore", payload["status"])
            self.assertEqual(str(root.resolve() / ".gitignore"), payload["ignore_file"])
            self.assertIn("PM must add .engineering/", payload["error"])

            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            completed, payload = self.run_resolver(root, "eng-421-test")

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("resolved", payload["status"])
            self.assertTrue(payload["engineering_ignored"])

    def test_rejects_later_ignore_negation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "negated ignore"
            self.initialize_git(root, ignored=False)
            (root / ".gitignore").write_text(
                ".engineering/\n!.engineering/\n", encoding="utf-8"
            )

            completed, payload = self.run_resolver(root, "eng-421-test")

            self.assertEqual(3, completed.returncode)
            self.assertEqual("requires_ignore", payload["status"])
            self.assertEqual(str(root.resolve() / ".gitignore"), payload["ignore_file"])

    def test_default_workspace_ignore_does_not_gate_active_work(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main"
            linked = Path(temporary) / "linked"
            self.initialize_git(root, ignored=False)
            self.commit_initial(root)
            self.git(
                "worktree", "add", "-q", "-b", "linked", str(linked), cwd=root
            )
            (linked / ".gitignore").write_text(".engineering/\n", encoding="utf-8")

            completed, payload = self.run_resolver(linked, "eng-421-test")

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("resolved", payload["status"])
            self.assertEqual(str(linked.resolve() / ".gitignore"), payload["ignore_file"])
            self.assertNotIn("notion_dir", payload)

    def test_refuses_invalid_work_ids_and_non_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for work_id in ("UPPER", "bad/path", "-leading"):
                with self.subTest(work_id=work_id):
                    completed, payload = self.run_resolver(root, work_id)
                    self.assertEqual(2, completed.returncode)
                    self.assertEqual("invalid", payload["status"])

            completed, payload = self.run_resolver(root, "valid-id")
            self.assertEqual(2, completed.returncode)
            self.assertEqual("invalid", payload["status"])
            self.assertIn("not inside", payload["error"])

            completed, payload = self.run_resolver(
                root, environment_work_id="INVALID"
            )
            self.assertEqual(2, completed.returncode)
            self.assertIn("environment", payload["error"])

    def test_resolves_pure_jj_workspace_with_fake_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)
            default = fixture / "jj default"
            secondary = fixture / "jj secondary"
            git_dir = fixture / "backing.git"
            fake_bin = fixture / "bin"
            default.mkdir()
            secondary.mkdir()
            fake_bin.mkdir()
            self.git("init", "--bare", "-q", str(git_dir), cwd=fixture)
            (secondary / ".gitignore").write_text(
                ".engineering/\n", encoding="utf-8"
            )
            (secondary / ".engineering/works/secondary").mkdir(parents=True)
            fake_jj = fake_bin / "jj"
            fake_jj.write_text(
                "#!/bin/sh\n"
                "[ \"$1\" = --ignore-working-copy ] && shift\n"
                "case \"$1:$2\" in\n"
                "  root:) printf '%s\\n' \"$JJ_ACTIVE_ROOT\" ;;\n"
                "  git:root) printf '%s\\n' \"$JJ_GIT_DIR\" ;;\n"
                "  workspace:list) printf 'default\\nsecondary\\n' ;;\n"
                "  workspace:root)\n"
                "    if [ \"${3:-}\" = --name ] && [ \"${4:-}\" = default ]; then\n"
                "      printf '%s\\n' \"$JJ_DEFAULT_ROOT\"\n"
                "    elif [ \"${3:-}\" = --name ] && [ \"${4:-}\" = secondary ]; then\n"
                "      printf '%s\\n' \"$JJ_ACTIVE_ROOT\"\n"
                "    else\n"
                "      printf '%s\\n' \"$JJ_ACTIVE_ROOT\"\n"
                "    fi ;;\n"
                "  *) exit 1 ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            fake_jj.chmod(0o755)
            environment = {
                "PATH": f"{fake_bin}:{os.environ['PATH']}",
                "JJ_ACTIVE_ROOT": str(secondary),
                "JJ_DEFAULT_ROOT": str(default),
                "JJ_GIT_DIR": str(git_dir),
            }

            completed, payload = self.run_resolver(
                secondary, extra_environment=environment
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("jj", payload["vcs"])
            self.assertEqual(str(default.resolve()), payload["default_workspace"])
            self.assertEqual(str(secondary.resolve()), payload["active_workspace"])
            self.assertEqual("secondary", payload["work_id"])
            self.assertEqual("jj_workspace", payload["work_id_source"])

    @unittest.skipUnless(shutil.which("jj"), "jj is unavailable")
    def test_resolves_default_and_secondary_jj_workspaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "jj default"
            secondary = Path(temporary) / "jj secondary"
            subprocess.run(
                ["jj", "git", "init", "--colocate", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            subprocess.run(
                ["jj", "workspace", "add", "--name", "secondary", str(secondary)],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            )
            (secondary / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            (secondary / ".engineering/works/secondary").mkdir(parents=True)

            completed, payload = self.run_resolver(secondary)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("jj", payload["vcs"])
            self.assertEqual(str(root.resolve()), payload["default_workspace"])
            self.assertEqual(str(secondary.resolve()), payload["active_workspace"])
            self.assertEqual(str(secondary.resolve()), payload["durable_root"])
            self.assertEqual(str(secondary.resolve()), payload["repo_root"])
            self.assertEqual("secondary", payload["work_id"])
            self.assertEqual("jj_workspace", payload["work_id_source"])
            self.assertEqual(
                str(secondary.resolve() / ".gitignore"), payload["ignore_file"]
            )
            self.assertTrue(payload["engineering_ignored"])

    @unittest.skipUnless(shutil.which("jj"), "jj is unavailable")
    def test_allows_jj_repository_without_registered_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "jj primary"
            subprocess.run(
                ["jj", "git", "init", "--colocate", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["jj", "workspace", "rename", "primary"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            )
            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            (root / ".engineering/works/primary").mkdir(parents=True)

            completed, payload = self.run_resolver(root)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("resolved", payload["status"])
            self.assertIsNone(payload["default_workspace"])
            self.assertEqual("primary", payload["work_id"])


class ArtifactSkillContractTest(unittest.TestCase):
    def test_all_migrated_artifact_writers_load_contract_and_return_manifest(self) -> None:
        actual = {
            str(path.relative_to(REPOSITORY / "plugins"))
            for path in (REPOSITORY / "plugins").glob("*/skills/**/SKILL.md")
            if "engineering-work.md" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(MIGRATED_ARTIFACT_WRITERS, actual)

        for relative in sorted(MIGRATED_ARTIFACT_WRITERS):
            with self.subTest(skill=relative):
                text = (REPOSITORY / "plugins" / relative).read_text(encoding="utf-8")
                self.assertIn("engineering-work.md", text)
                self.assertRegex(text, r"(?i)if unavailable|refuse.*missing|stop artifact")
                self.assertIn("generated_files", text)

    def test_reviewed_consumers_use_optional_resolution_and_generic_context(self) -> None:
        audit_data = (
            REPOSITORY / "plugins/backend/skills/audit-data/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("[--work-id=<id>]", audit_data)
        self.assertIn("Essential's workspace resolver", audit_data)
        self.assertIn("work_id_required", audit_data)

        for skill_name in ("create-screen-design", "update-screen-design"):
            with self.subTest(skill=skill_name):
                client = (
                    REPOSITORY / f"plugins/client/skills/{skill_name}/SKILL.md"
                ).read_text(encoding="utf-8")
                normalized_client = " ".join(client.split())
                self.assertNotIn("specification:", normalized_client)
                self.assertIn("source, location, and direction", normalized_client)
                self.assertIn(
                    "Never assume a synchronization skill", normalized_client
                )

    def test_pm_owns_deterministic_first_use_bootstrap(self) -> None:
        contract = (ESSENTIAL / "references/engineering-work.md").read_text(
            encoding="utf-8"
        )
        main_agent = (ESSENTIAL / "MAINAGENT.md").read_text(encoding="utf-8")
        normalized_contract = " ".join(contract.split())
        normalized_main_agent = " ".join(main_agent.split())

        self.assertIn("### First-use work-memory bootstrap", contract)
        self.assertIn(
            "After the user has confirmed any new work identity",
            normalized_contract,
        )
        self.assertIn(
            "`--bootstrap` never derives or mints an ID", normalized_contract
        )
        self.assertIn("created with no-clobber semantics", normalized_contract)
        self.assertIn("`bootstrap_created`", contract)
        self.assertIn("`bootstrap_existing`", contract)
        self.assertIn(
            "invoke the resolver with the confirmed ID and `--bootstrap`",
            normalized_main_agent,
        )
        self.assertIn("never mint an ID silently", normalized_main_agent)

    def test_shared_contract_supports_portable_specs_and_handover(self) -> None:
        contract = (ESSENTIAL / "references/engineering-work.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(contract.split())

        self.assertIn("provenance.json", contract)
        self.assertIn("explicit local path, approved inline candidate", normalized)
        self.assertIn("Neither path claims a Notion round trip", normalized)
        self.assertIn("checksum-bound portable receipt", normalized)
        self.assertIn("isolated post-anchor tree", normalized)

    def test_persistent_discovery_accepts_optional_explicit_work_id(self) -> None:
        discover = (ESSENTIAL / "skills/discover/SKILL.md").read_text(
            encoding="utf-8"
        )
        frontmatter = discover.split("---", 2)[1]
        normalized = " ".join(discover.split())

        self.assertIn("[--work-id=<id>]", frontmatter)
        self.assertIn("only when the user supplied that explicit override", normalized)
        self.assertIn("ask only on `work_id_required`", normalized)
        self.assertIn("no-clobber bootstrap", normalized)
        self.assertIn("Parent task: DSC", normalized)
        self.assertIn("DSC01 → {DSC02,DSC03} → DSC04", normalized)
        self.assertIn("root as the complete task registry", normalized)
        self.assertIn("validate-engineering-state validate", normalized)


class EngineeringIgnoreContractTest(unittest.TestCase):
    def test_engineering_transport_and_work_state_are_ignored(self) -> None:
        paths = (
            ".engineering/notion/example.mdc",
            ".engineering/works/test/state.md",
        )
        completed = subprocess.run(
            ["git", "check-ignore", "--no-index", *paths],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(list(paths), completed.stdout.splitlines())


class ContextHookContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "context fixture"
        self.root.mkdir()
        subprocess.run(
            ["git", "init", "-q"], cwd=self.root, text=True, capture_output=True, check=True
        )
        subprocess.run(
            ["git", "symbolic-ref", "HEAD", "refs/heads/main"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        (self.root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
        for relative in (
            "README.md",
            "CONTEXT.md",
            ".engineering/works/eng-42/working.md",
            ".engineering/works/eng-42/state.md",
            "docs/index.md",
            "docs/architecture/overview.md",
            "docs/architecture/runtime-boundaries.md",
            "docs/design/system.md",
            "docs/design/checkout-flow.md",
            "docs/specs/accounts/index.md",
            "docs/specs/accounts/session.md",
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_hook(self, executable: Path, input_text: str = "") -> str:
        environment = os.environ.copy()
        environment.pop("ENGINEERING_WORK_ID", None)
        completed = subprocess.run(
            [str(executable)],
            cwd=self.root,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        return payload["hookSpecificOutput"]["additionalContext"]

    def assert_context_contract(self, context: str) -> None:
        self.assertNotIn("\\n", context)
        self.assertNotIn("CONTEXT.md", context)
        expected = (
            ".engineering/works/eng-42/working.md",
            ".engineering/works/eng-42/state.md",
            "docs/index.md",
            "docs/architecture/overview.md",
            "docs/design/system.md",
        )
        for path in expected:
            self.assertIn(path, context)
        for first, second in zip(expected, expected[1:]):
            self.assertLess(context.index(first), context.index(second))
        for detail in (
            "docs/architecture/runtime-boundaries.md",
            "docs/design/checkout-flow.md",
            "docs/specs/accounts/index.md",
            "docs/specs/accounts/session.md",
        ):
            self.assertNotIn(detail, context)

    def test_session_start_injects_ordered_engineering_entrypoints(self) -> None:
        context = self.run_hook(SESSION_START, '{"source":"startup"}\n')
        self.assert_context_contract(context)

    def test_subagent_start_omits_repository_and_work_catalogs(self) -> None:
        context = self.run_hook(SUBAGENT_START)
        self.assertIn("**Working directory**", context)
        self.assertIn("Standards:", context)
        self.assertNotIn("## Target Repo Documents", context)
        for path in (
            "README.md",
            ".engineering/works/eng-42/working.md",
            ".engineering/works/eng-42/state.md",
            "docs/index.md",
        ):
            self.assertNotIn(path, context)

    def test_context_root_discovery_supports_pure_jj_subdirectories(self) -> None:
        jj_root = Path(self.temporary.name) / "pure jj"
        subdirectory = jj_root / "nested/project"
        fake_bin = Path(self.temporary.name) / "fake-bin"
        subdirectory.mkdir(parents=True)
        fake_bin.mkdir()
        fake_jj = fake_bin / "jj"
        fake_jj.write_text(
            "#!/bin/sh\n"
            "[ \"$1\" = --ignore-working-copy ] && shift\n"
            "[ \"$1\" = root ] || exit 1\n"
            "printf '%s\\n' \"$JJ_ACTIVE_ROOT\"\n",
            encoding="utf-8",
        )
        fake_jj.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
        environment["JJ_ACTIVE_ROOT"] = str(jj_root)
        completed = subprocess.run(
            [
                "bash",
                "-c",
                f'source "{ESSENTIAL / "scripts/context.sh"}"; get_repo_root',
            ],
            cwd=subdirectory,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(str(jj_root), completed.stdout.strip())


if __name__ == "__main__":
    unittest.main()
