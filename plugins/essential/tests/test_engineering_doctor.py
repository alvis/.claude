from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

import pytest


ESSENTIAL = Path(__file__).resolve().parents[1]
DOCTOR = ESSENTIAL / "bin/engineering-doctor"
RESOLVER = ESSENTIAL / "bin/resolve-engineering-workspace"

HEADER = (
    "| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner "
    "| Evidence / next action |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


def row(
    task_id: str,
    mark: str = "-",
    status: str = "planned",
    depends: str = "—",
    required: str = "yes",
    evidence: str = "Pending.",
) -> str:
    return (
        f"| {task_id} | {mark} | {status} | Do {task_id}. [targets: none] "
        f"| {depends} | {required} | Done when done. | PM | {evidence} |\n"
    )


class Workspace:
    """A scratch work directory plus doctor invocation helpers."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.work_dir = root / ".state" / "works" / "demo"
        (self.work_dir / "state").mkdir(parents=True)

    def write_state(
        self, task_rows: str, metadata: str = "", lifecycle: str = "active"
    ) -> None:
        (self.work_dir / "state.md").write_text(
            "# Engineering work\n\n"
            "- State role: `root`\n"
            "- Work ID: `demo`\n"
            f"- Lifecycle status: `{lifecycle}`\n"
            "- State revision: `3`\n"
            f"{metadata}"
            "\n## Tasks\n\n" + HEADER + task_rows,
            encoding="utf-8",
        )

    def run_doctor(
        self, *arguments: str, repository_root: Path | None = None
    ) -> tuple[int, list[dict]]:
        command = [str(DOCTOR), "--work-dir", str(self.work_dir)]
        if repository_root is not None:
            command.extend(["--repository-root", str(repository_root)])
        command.extend(["--json", *arguments])
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        return completed.returncode, payload["findings"]

    @staticmethod
    def checks(findings: list[dict]) -> set[str]:
        return {finding["check"] for finding in findings}


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    return Workspace(tmp_path)


def run_engineering_root(root: Path) -> tuple[int, list[dict]]:
    completed = subprocess.run(
        [str(DOCTOR), "--engineering-root", str(root / ".state"), "--json"],
        capture_output=True,
        text=True,
    )
    return completed.returncode, json.loads(completed.stdout)["findings"]


def write_effective_adr(
    root: Path, name: str = "0001-choice.md", body: str = ""
) -> Path:
    architecture = root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True, exist_ok=True)
    path = decisions / name
    path.write_text(
        "# ADR: Choice\n\n- Status: `Accepted`\n\n" + body,
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "# Architecture\n\n"
        "| Document | Status |\n| --- | --- |\n"
        f"| [ADR]({decisions.name}/{name}) | Accepted |\n",
        encoding="utf-8",
    )
    return path


def test_clean_fixture_has_zero_findings(workspace: Workspace) -> None:
    workspace.write_state(
        row("AAA", "✓", "done", evidence="Merged in abc123.")
        + row("BBB", "-", "planned", depends="AAA")
    )
    code, findings = workspace.run_doctor()
    assert code == 0
    assert findings == []


def test_reviewing_is_part_of_the_lifecycle_vocabulary(workspace: Workspace) -> None:
    workspace.write_state(
        row("AAA", "✓", "done", evidence="Merged in abc123."),
        lifecycle="reviewing",
    )
    code, findings = workspace.run_doctor()
    assert code == 0
    assert findings == []


def test_retired_lifecycle_value_is_flagged(workspace: Workspace) -> None:
    # `complete` was renamed to `completed`; the old value is not vocabulary
    workspace.write_state(
        row("AAA", "✓", "done", evidence="Merged in abc123."),
        lifecycle="complete",
    )
    _, findings = workspace.run_doctor()
    assert "lifecycle" in workspace.checks(findings)


def test_bootstrap_output_has_zero_findings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    (repo / ".gitignore").write_text(".state/\n", encoding="utf-8")
    resolved = subprocess.run(
        [str(RESOLVER), "--work-id=demo", "--bootstrap"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    work_dir = json.loads(resolved.stdout)["work_dir"]
    completed = subprocess.run(
        [str(DOCTOR), "--work-dir", work_dir, "--json"],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["findings"] == []


def test_malformed_and_duplicate_ids(workspace: Workspace) -> None:
    workspace.write_state(row("AAAA") + row("BBB") + row("BBB"))
    _, findings = workspace.run_doctor()
    messages = [finding["message"] for finding in findings]
    assert any("malformed task ID" in message for message in messages)
    assert any("duplicate task ID" in message for message in messages)


def test_dangling_dependency(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", depends="ZZZ"))
    _, findings = workspace.run_doctor()
    assert "dependency" in workspace.checks(findings)


def test_dependency_cycle(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", depends="BBB") + row("BBB", depends="AAA"))
    _, findings = workspace.run_doctor()
    assert any("cycle" in finding["message"] for finding in findings)


def test_contradictory_mark_status(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "✓", "working"))
    _, findings = workspace.run_doctor()
    assert "mark-status" in workspace.checks(findings)


def test_done_without_evidence(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "✓", "done", evidence=""))
    _, findings = workspace.run_doctor()
    assert "evidence" in workspace.checks(findings)


def test_failed_without_attempt_annotations(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "X", "failed", evidence="it broke"))
    _, findings = workspace.run_doctor()
    assert "evidence" in workspace.checks(findings)


def test_blocked_without_unblock(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "!", "blocked", evidence="waiting"))
    _, findings = workspace.run_doctor()
    assert "evidence" in workspace.checks(findings)


def test_required_cancelled(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "⊘", "cancelled"))
    _, findings = workspace.run_doctor()
    assert "roll-up" in workspace.checks(findings)


def test_parent_done_with_unfinished_required_child(workspace: Workspace) -> None:
    workspace.write_state(
        row("AAA", "✓", "done", evidence="rolled up")
        + row("AAA01", "-", "planned")
    )
    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "roll-up" and "AAA" in finding["message"]
        for finding in findings
    )


def test_broken_file_reference_and_absolute_path(workspace: Workspace) -> None:
    workspace.write_state(
        row("AAA"),
        metadata="- Charter: [goal.md](goal.md)\n"
        "- Notes: [notes](/etc/absolute.md)\n",
    )
    _, findings = workspace.run_doctor()
    assert "file-reference" in workspace.checks(findings)
    assert "portability" in workspace.checks(findings)


def test_superseded_decision_without_successor(workspace: Workspace) -> None:
    workspace.write_state(row("AAA"))
    decisions = workspace.work_dir / "decisions"
    decisions.mkdir()
    (decisions / "old-choice.md").write_text(
        "- status: `superseded`\n- headline: Old choice.\n", encoding="utf-8"
    )
    _, findings = workspace.run_doctor()
    assert "decision" in workspace.checks(findings)
    (decisions / "new-choice.md").write_text(
        "- status: `accepted`\n- supersedes: `old-choice`\n", encoding="utf-8"
    )
    _, findings = workspace.run_doctor()
    assert "decision" not in workspace.checks(findings)


def test_adr_supersession_requires_archive_header_and_current_index(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-old-choice.md").write_text(
        "# ADR-0001: Old choice\n\n- Status: `Superseded`\n", encoding="utf-8"
    )
    (architecture / "README.md").write_text(
        "# Architecture\n\n"
        "| Document | Status |\n| --- | --- |\n"
        "| [ADR-0001](decisions/0001-old-choice.md) | Accepted |\n",
        encoding="utf-8",
    )
    _, findings = workspace.run_doctor()
    assert "adr-superseded" in workspace.checks(findings)

    old = decisions / "0001-old-choice.md"
    archived = decisions / "superseded"
    archived.mkdir()
    old.rename(archived / old.name)
    (decisions / "0002-new-choice.md").write_text(
        "# ADR-0002: New choice\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — New choice](../0002-new-choice.md)\n>\n"
        "> **What changed:** The complete choice changed.\n\n"
        "# ADR-0001: Old choice\n\n- Status: `Accepted`\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "# Architecture\n\n"
        "| Document | Status |\n| --- | --- |\n"
        "| [ADR-0002](decisions/0002-new-choice.md) | Accepted |\n",
        encoding="utf-8",
    )
    _, findings = workspace.run_doctor()
    assert not any(finding["check"].startswith("adr-") for finding in findings)


def test_adr_integrity_finding_offers_a_fix(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-choice.md").write_text(
        "# ADR-0001: Choice\n\n- Status: `Accepted`\n\n"
        "This ADR supersedes an earlier choice.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0001](decisions/0001-choice.md) | Accepted |\n",
        encoding="utf-8",
    )
    _, findings = workspace.run_doctor()
    integrity = [finding for finding in findings if finding["check"] == "adr-integrity"]
    assert integrity
    assert all(finding.get("fix") for finding in integrity)


def test_adr_filenames_are_canonical_for_effective_and_archived_records(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "database.md").write_text(
        "# ADR-0001: Database\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (decisions / "0002-current.md").write_text(
        "# ADR-0002: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — Current](../0002-current.md)\n>\n"
        "> **What changed:** The complete choice changed.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| Document | Status |\n| --- | --- |\n"
        "| [Database](decisions/database.md) | Accepted |\n"
        "| [Current](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    filename_findings = [
        finding
        for finding in findings
        if finding["check"] == "adr-layout"
        and "filename must use" in finding["message"]
    ]
    assert {finding["work"] for finding in filename_findings} == {
        "docs/architecture/decisions/database.md",
        "docs/architecture/decisions/superseded/old-choice.md",
    }
    assert all(finding.get("fix") for finding in filename_findings)


def test_adr_index_status_must_match_effective_status(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-current.md").write_text(
        "# ADR-0001: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (architecture / "README.md").write_text(
        "| Document | Status |\n| --- | --- |\n"
        "| [ADR-0001](decisions/0001-current.md) | Superseded |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "adr-index"
        and "contradicts effective ADR" in finding["message"]
        for finding in findings
    )


def test_adr_template_comment_is_ignored_by_integrity_checks(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-choice.md").write_text(
        "# ADR-0001: Choice\n\n- Status: `Accepted`\n\n"
        "## Context\n\nThe accepted choice.\n\n"
        "<!-- Optional superseded guidance says TODO and Superseded by. -->\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0001](decisions/0001-choice.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert "adr-integrity" not in workspace.checks(findings)


def test_adr_archive_rejects_duplicate_header_fields(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "0002-current.md").write_text(
        "# ADR-0002: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — Current](../0002-current.md)\n"
        "> **Superseded by:** [ADR-0002 — Current](../0002-current.md)\n>\n"
        "> **What changed:** The complete choice changed.\n"
        "> **What changed:** The complete choice changed again.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0002](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    duplicate = [
        finding
        for finding in findings
        if finding["check"] == "adr-superseded"
        and "exactly one" in finding["message"]
    ]
    assert duplicate
    assert "Superseded by" in duplicate[0]["message"]
    assert "What changed" in duplicate[0]["message"]


def test_adr_archive_successor_label_must_match_target(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "0003-database.md").write_text(
        "# ADR-0003: Database\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — Cache](../0003-database.md)\n>\n"
        "> **What changed:** The complete choice changed.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0003](decisions/0003-database.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "adr-superseded"
        and "label does not match target ADR" in finding["message"]
        for finding in findings
    )


def test_adr_archive_change_summary_must_classify_scope(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "0002-current.md").write_text(
        "# ADR-0002: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — Current](../0002-current.md)\n>\n"
        "> **What changed:** Switched databases.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0002](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "adr-superseded"
        and "partial or complete" in finding["message"]
        for finding in findings
    )


def test_adr_scan_uses_explicit_active_repository_root(workspace: Workspace) -> None:
    wrong_architecture = workspace.root / "docs" / "architecture"
    wrong_decisions = wrong_architecture / "decisions"
    wrong_decisions.mkdir(parents=True)
    (wrong_decisions / "0001-wrong.md").write_text(
        "# ADR-0001: Wrong tree\n\n- Status: `Superseded`\n",
        encoding="utf-8",
    )

    active_root = workspace.root / "active-worktree"
    active_decisions = active_root / "docs" / "architecture" / "decisions"
    active_decisions.mkdir(parents=True)
    (active_decisions / "0002-current.md").write_text(
        "# ADR-0002: Current tree\n\n- Status: `Accepted`\n",
        encoding="utf-8",
    )
    (active_root / "docs" / "architecture" / "README.md").write_text(
        "| [ADR-0002](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor(repository_root=active_root)
    assert not any(finding["check"].startswith("adr-") for finding in findings)


def test_adr_scan_runs_when_engineering_root_is_absent(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    decisions = repository / "docs" / "architecture" / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-current.md").write_text(
        "# ADR-0001: Current\n\n- Status: `Accepted`\n",
        encoding="utf-8",
    )
    (repository / "docs" / "architecture" / "README.md").write_text(
        "| [ADR-0001](decisions/0001-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            str(DOCTOR),
            "--engineering-root",
            str(repository / ".state"),
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["findings"] == []


def test_adr_status_in_body_example_does_not_contradict_metadata(
    workspace: Workspace,
) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "0001-current.md").write_text(
        "# ADR-0001: Current\n\n- Status: `Accepted`\n\n"
        "## Context\n\n```yaml\nstatus: pending\n```\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0001](decisions/0001-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert "adr-integrity" not in workspace.checks(findings)


def test_adr_unrecognized_subdirectory_is_reported(workspace: Workspace) -> None:
    decisions = workspace.root / "docs" / "architecture" / "decisions"
    misplaced = decisions / "legacy"
    misplaced.mkdir(parents=True)
    (misplaced / "0001-old.md").write_text(
        "# ADR-0001: Old\n\n- Status: `Accepted`\n", encoding="utf-8"
    )

    _, findings = workspace.run_doctor()
    layout = [finding for finding in findings if finding["check"] == "adr-layout"]
    assert layout
    assert layout[0].get("fix")


def test_adr_archive_rejects_unfilled_change_summary(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "0002-current.md").write_text(
        "# ADR-0002: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — Current](../0002-current.md)\n>\n"
        "> **What changed:** <State whether the change is partial or complete and summarize the changed choice.>\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0002](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "adr-superseded"
        and "What changed" in finding["message"]
        for finding in findings
    )


def test_adr_archive_rejects_absolute_successor_link(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    current = decisions / "0002-current.md"
    current.write_text(
        "# ADR-0002: Current\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    old = archived / "0001-old.md"
    old.write_text(
        "> **Status:** Superseded\n>\n"
        f"> **Superseded by:** [ADR-0002 — Current]({current.resolve()})\n>\n"
        "> **What changed:** The complete choice changed.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0002](decisions/0002-current.md) | Accepted |\n",
        encoding="utf-8",
    )

    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "adr-superseded"
        and "portable relative path" in finding["message"]
        for finding in findings
    )


def test_adr_index_rejects_archived_entries(workspace: Workspace) -> None:
    architecture = workspace.root / "docs" / "architecture"
    decisions = architecture / "decisions"
    archived = decisions / "superseded"
    archived.mkdir(parents=True)
    (decisions / "0002-new-choice.md").write_text(
        "# ADR-0002: New choice\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR-0002 — New choice](../0002-new-choice.md)\n>\n"
        "> **What changed:** The complete choice changed.\n",
        encoding="utf-8",
    )
    (architecture / "README.md").write_text(
        "| [ADR-0002](decisions/0002-new-choice.md) | Accepted |\n"
        "| [ADR-0001](decisions/superseded/0001-old-choice.md) | Superseded |\n",
        encoding="utf-8",
    )
    _, findings = workspace.run_doctor()
    assert "adr-index" in workspace.checks(findings)


def test_expired_and_conflicting_lease(workspace: Workspace) -> None:
    workspace.write_state(row("AAA"))
    (workspace.work_dir / "lease.json").write_text(
        json.dumps(
            {
                "work_id": "demo",
                "token": "t",
                "expires_at_epoch": int(time.time()) - 60,
                "state_revision": 9,
            }
        ),
        encoding="utf-8",
    )
    _, findings = workspace.run_doctor()
    lease_findings = [f for f in findings if f["check"] == "lease"]
    severities = {finding["severity"] for finding in lease_findings}
    assert "warning" in severities  # expired
    assert "error" in severities  # revision ahead of state.md


def test_unparseable_state_is_only_info(workspace: Workspace) -> None:
    (workspace.work_dir / "state.md").write_text(
        "totally free-form notes\n", encoding="utf-8"
    )
    code, findings = workspace.run_doctor("--strict")
    assert code == 0
    assert {finding["severity"] for finding in findings} == {"info"}


def test_strict_exit_code(workspace: Workspace) -> None:
    workspace.write_state(row("AAA", "✓", "working"))
    code, _ = workspace.run_doctor()
    assert code == 0
    code, _ = workspace.run_doctor("--strict")
    assert code == 1


def test_overview_drift(workspace: Workspace) -> None:
    workspace.write_state(row("AAA"))
    engineering_root = workspace.root / ".state"
    (engineering_root / "overview.md").write_text(
        "# Overview\n\n"
        "| Work ID | Lifecycle | Headline |\n| --- | --- | --- |\n"
        "| demo | completed | Demo. |\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [str(DOCTOR), "--engineering-root", str(engineering_root), "--json"],
        capture_output=True,
        text=True,
    )
    findings = json.loads(completed.stdout)["findings"]
    assert any(finding["check"] == "overview" for finding in findings)


def test_unparseable_rows_surface_as_warning(workspace: Workspace) -> None:
    workspace.write_state(
        row("AAA")
        + "| BBB | - | planned | truncated row |\n"
        + "| CCC | broken |\n"
    )
    _, findings = workspace.run_doctor()
    warnings = [
        finding
        for finding in findings
        if finding["severity"] == "warning" and finding["check"] == "layout"
    ]
    assert len(warnings) == 1
    assert "2 task row(s) unparseable" in warnings[0]["message"]


def test_long_journal_gets_compaction_hint(workspace: Workspace) -> None:
    workspace.write_state(row("AAA"))
    journal = workspace.work_dir / "state" / "journal.md"
    lines = ["# Journal", ""] + [
        f"- 2026-07-24T00:00:00Z PM@pm rev:1 status AAA: tick {index}"
        for index in range(510)
    ]
    journal.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _, findings = workspace.run_doctor()
    assert any(
        finding["check"] == "journal" and "compacting" in finding["message"]
        for finding in findings
    )


def test_written_under_drift_is_informational(workspace: Workspace) -> None:
    workspace.write_state(row("AAA"), metadata="- Written under: `00000000`\n")
    _, findings = workspace.run_doctor()
    drift = [f for f in findings if f["check"] == "written-under"]
    assert len(drift) == 1
    assert drift[0]["severity"] == "info"
    assert "written under contract 00000000" in drift[0]["message"]


def test_missing_state_root_still_checks_repository_adrs(tmp_path: Path) -> None:
    write_effective_adr(tmp_path)
    code, findings = run_engineering_root(tmp_path)
    assert code == 0
    assert findings == []


def test_adr_filename_and_numeric_prefix_are_validated(tmp_path: Path) -> None:
    write_effective_adr(tmp_path)
    architecture = tmp_path / "docs" / "architecture"
    (architecture / "decisions" / "choice.md").write_text(
        "# Invalid\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    archived = architecture / "decisions" / "superseded"
    archived.mkdir()
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR](../choice.md)\n>\n"
        "> **What changed:** Replaced.\n",
        encoding="utf-8",
    )
    _, findings = run_engineering_root(tmp_path)
    assert any(finding["check"] == "adr-filename" for finding in findings)
    assert any("duplicate ADR numeric prefix 0001" in finding["message"] for finding in findings)


def test_html_comments_do_not_trigger_adr_integrity_checks(tmp_path: Path) -> None:
    write_effective_adr(
        tmp_path,
        body="<!-- - Status: Superseded; TODO <fill this> -->\n",
    )
    _, findings = run_engineering_root(tmp_path)
    assert not any(finding["check"] == "adr-integrity" for finding in findings)


def test_nested_adr_files_are_reported_as_layout_errors(tmp_path: Path) -> None:
    write_effective_adr(tmp_path)
    nested = tmp_path / "docs" / "architecture" / "decisions" / "archive"
    nested.mkdir()
    (nested / "0002-nested.md").write_text(
        "# Nested\n\n- Status: `Accepted`\n", encoding="utf-8"
    )
    _, findings = run_engineering_root(tmp_path)
    assert any(finding["check"] == "adr-layout" for finding in findings)


def test_narrative_adr_link_does_not_satisfy_index_table(tmp_path: Path) -> None:
    write_effective_adr(tmp_path)
    readme = tmp_path / "docs" / "architecture" / "README.md"
    readme.write_text(
        "See [the choice](decisions/0001-choice.md).\n\n"
        "| Document | Status |\n| --- | --- |\n",
        encoding="utf-8",
    )
    _, findings = run_engineering_root(tmp_path)
    assert any(finding["check"] == "adr-index" for finding in findings)


def test_absolute_successor_link_is_rejected(tmp_path: Path) -> None:
    write_effective_adr(tmp_path, "0002-new-choice.md")
    archived = tmp_path / "docs" / "architecture" / "decisions" / "superseded"
    archived.mkdir()
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR](/docs/architecture/decisions/0002-new-choice.md)\n>\n"
        "> **What changed:** Replaced.\n",
        encoding="utf-8",
    )
    _, findings = run_engineering_root(tmp_path)
    assert any(
        finding["check"] == "adr-superseded"
        and "must be relative" in finding["message"]
        for finding in findings
    )


def test_archive_placeholder_summary_is_rejected(tmp_path: Path) -> None:
    write_effective_adr(tmp_path, "0002-new-choice.md")
    archived = tmp_path / "docs" / "architecture" / "decisions" / "superseded"
    archived.mkdir()
    (archived / "0001-old-choice.md").write_text(
        "> **Status:** Superseded\n>\n"
        "> **Superseded by:** [ADR](../0002-new-choice.md)\n>\n"
        "> **What changed:** <State whether the decision changed>.\n",
        encoding="utf-8",
    )
    _, findings = run_engineering_root(tmp_path)
    assert any(
        finding["check"] == "adr-superseded"
        and "What changed" in finding["message"]
        for finding in findings
    )
