from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


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


class EngineeringDoctorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.work_dir = self.root / ".engineering" / "works" / "demo"
        (self.work_dir / "state").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_state(self, task_rows: str, metadata: str = "") -> None:
        (self.work_dir / "state.md").write_text(
            "# Engineering work\n\n"
            "- State role: `root`\n"
            "- Work ID: `demo`\n"
            "- Lifecycle status: `active`\n"
            "- State revision: `3`\n"
            f"{metadata}"
            "\n## Tasks\n\n" + HEADER + task_rows,
            encoding="utf-8",
        )

    def run_doctor(self, *arguments: str) -> tuple[int, dict]:
        completed = subprocess.run(
            [str(DOCTOR), "--work-dir", str(self.work_dir), "--json", *arguments],
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        return completed.returncode, payload["findings"]

    def checks(self, findings: list[dict]) -> set[str]:
        return {finding["check"] for finding in findings}

    def test_clean_fixture_has_zero_findings(self) -> None:
        self.write_state(
            row("AAA", "✓", "done", evidence="Merged in abc123.")
            + row("BBB", "-", "planned", depends="AAA")
        )
        code, findings = self.run_doctor()
        self.assertEqual(code, 0)
        self.assertEqual(findings, [])

    def test_bootstrap_output_has_zero_findings(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            subprocess.run(
                ["git", "init", "-q", str(repo)], check=True, capture_output=True
            )
            (repo / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
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
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["findings"], [])

    def test_malformed_and_duplicate_ids(self) -> None:
        self.write_state(row("AAAA") + row("BBB") + row("BBB"))
        _, findings = self.run_doctor()
        messages = [finding["message"] for finding in findings]
        self.assertTrue(any("malformed task ID" in message for message in messages))
        self.assertTrue(any("duplicate task ID" in message for message in messages))

    def test_dangling_dependency(self) -> None:
        self.write_state(row("AAA", depends="ZZZ"))
        _, findings = self.run_doctor()
        self.assertIn("dependency", self.checks(findings))

    def test_dependency_cycle(self) -> None:
        self.write_state(row("AAA", depends="BBB") + row("BBB", depends="AAA"))
        _, findings = self.run_doctor()
        self.assertTrue(
            any("cycle" in finding["message"] for finding in findings)
        )

    def test_contradictory_mark_status(self) -> None:
        self.write_state(row("AAA", "✓", "working"))
        _, findings = self.run_doctor()
        self.assertIn("mark-status", self.checks(findings))

    def test_done_without_evidence(self) -> None:
        self.write_state(row("AAA", "✓", "done", evidence=""))
        _, findings = self.run_doctor()
        self.assertIn("evidence", self.checks(findings))

    def test_failed_without_attempt_annotations(self) -> None:
        self.write_state(row("AAA", "X", "failed", evidence="it broke"))
        _, findings = self.run_doctor()
        self.assertIn("evidence", self.checks(findings))

    def test_blocked_without_unblock(self) -> None:
        self.write_state(row("AAA", "!", "blocked", evidence="waiting"))
        _, findings = self.run_doctor()
        self.assertIn("evidence", self.checks(findings))

    def test_required_cancelled(self) -> None:
        self.write_state(row("AAA", "⊘", "cancelled"))
        _, findings = self.run_doctor()
        self.assertIn("roll-up", self.checks(findings))

    def test_parent_done_with_unfinished_required_child(self) -> None:
        self.write_state(
            row("AAA", "✓", "done", evidence="rolled up")
            + row("AAA01", "-", "planned")
        )
        _, findings = self.run_doctor()
        self.assertTrue(
            any(
                finding["check"] == "roll-up" and "AAA" in finding["message"]
                for finding in findings
            )
        )

    def test_broken_file_reference_and_absolute_path(self) -> None:
        self.write_state(
            row("AAA"),
            metadata="- Charter: [goal.md](goal.md)\n"
            "- Notes: [notes](/etc/absolute.md)\n",
        )
        _, findings = self.run_doctor()
        self.assertIn("file-reference", self.checks(findings))
        self.assertIn("portability", self.checks(findings))

    def test_superseded_decision_without_successor(self) -> None:
        self.write_state(row("AAA"))
        decisions = self.work_dir / "decisions"
        decisions.mkdir()
        (decisions / "old-choice.md").write_text(
            "- status: `superseded`\n- headline: Old choice.\n", encoding="utf-8"
        )
        _, findings = self.run_doctor()
        self.assertIn("decision", self.checks(findings))
        (decisions / "new-choice.md").write_text(
            "- status: `accepted`\n- supersedes: `old-choice`\n", encoding="utf-8"
        )
        _, findings = self.run_doctor()
        self.assertNotIn("decision", self.checks(findings))

    def test_expired_and_conflicting_lease(self) -> None:
        self.write_state(row("AAA"))
        (self.work_dir / "lease.json").write_text(
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
        _, findings = self.run_doctor()
        lease_findings = [f for f in findings if f["check"] == "lease"]
        severities = {finding["severity"] for finding in lease_findings}
        self.assertIn("warning", severities)  # expired
        self.assertIn("error", severities)  # revision ahead of state.md

    def test_checkpoint_worthy_history_without_checkpoint(self) -> None:
        self.write_state(row("AAA"))
        journal = self.work_dir / "state" / "journal.md"
        journal.write_text(
            "# Journal\n\n"
            "- 2026-07-24T00:00:00Z PM@pm rev:2 decision DEC-1: accepted\n",
            encoding="utf-8",
        )
        _, findings = self.run_doctor()
        self.assertIn("checkpoint", self.checks(findings))
        journal.write_text(
            "# Journal\n\n"
            "- 2026-07-24T00:00:00Z PM@pm rev:2 decision DEC-1: accepted\n"
            "- 2026-07-24T00:00:01Z PM@pm rev:2 checkpoint DEC-1: published\n",
            encoding="utf-8",
        )
        _, findings = self.run_doctor()
        self.assertNotIn("checkpoint", self.checks(findings))

    def test_unparseable_state_is_only_info(self) -> None:
        (self.work_dir / "state.md").write_text(
            "totally free-form notes\n", encoding="utf-8"
        )
        code, findings = self.run_doctor("--strict")
        self.assertEqual(code, 0)
        self.assertEqual(
            {finding["severity"] for finding in findings}, {"info"}
        )

    def test_strict_exit_code(self) -> None:
        self.write_state(row("AAA", "✓", "working"))
        code, _ = self.run_doctor()
        self.assertEqual(code, 0)
        code, _ = self.run_doctor("--strict")
        self.assertEqual(code, 1)

    def test_overview_drift(self) -> None:
        self.write_state(row("AAA"))
        engineering_root = self.root / ".engineering"
        (engineering_root / "overview.md").write_text(
            "# Overview\n\n"
            "| Work ID | Lifecycle | Headline |\n| --- | --- | --- |\n"
            "| demo | complete | Demo. |\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [str(DOCTOR), "--engineering-root", str(engineering_root), "--json"],
            capture_output=True,
            text=True,
        )
        findings = json.loads(completed.stdout)["findings"]
        self.assertTrue(
            any(finding["check"] == "overview" for finding in findings)
        )


    def test_unparseable_rows_surface_as_warning(self) -> None:
        self.write_state(
            row("AAA")
            + "| BBB | - | planned | truncated row |\n"
            + "| CCC | broken |\n"
        )
        _, findings = self.run_doctor()
        warnings = [
            finding
            for finding in findings
            if finding["severity"] == "warning" and finding["check"] == "layout"
        ]
        self.assertEqual(len(warnings), 1)
        self.assertIn("2 task row(s) unparseable", warnings[0]["message"])

    def test_long_journal_gets_compaction_hint(self) -> None:
        self.write_state(row("AAA"))
        journal = self.work_dir / "state" / "journal.md"
        lines = ["# Journal", ""] + [
            f"- 2026-07-24T00:00:00Z PM@pm rev:1 status AAA: tick {index}"
            for index in range(510)
        ]
        journal.write_text("\n".join(lines) + "\n", encoding="utf-8")
        _, findings = self.run_doctor()
        self.assertTrue(
            any(
                finding["check"] == "journal"
                and "compacting" in finding["message"]
                for finding in findings
            )
        )

    def test_written_under_drift_is_informational(self) -> None:
        self.write_state(
            row("AAA"), metadata="- Written under: `00000000`\n"
        )
        _, findings = self.run_doctor()
        drift = [f for f in findings if f["check"] == "written-under"]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0]["severity"], "info")
        self.assertIn("written under contract 00000000", drift[0]["message"])


if __name__ == "__main__":
    unittest.main()
