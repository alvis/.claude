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
            [str(CHECKER), *(str(path) for path in paths)],
            text=True,
            capture_output=True,
            check=False,
            env=self.env,
        )
        return completed, json.loads(completed.stdout)

    def calls(self) -> int:
        return len(self.log.read_text().splitlines()) if self.log.exists() else 0

    def test_keeps_fifteen_kib_and_boundary_file_in_one_pass(self) -> None:
        first = self.write_bytes("fifteen kib.md", 15 * 1024)
        second = self.write_bytes("boundary.md", 16_384)

        completed, payload = self.run_checker(first, second)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(2, payload["checked"])
        self.assertEqual([], payload["oversized"])
        self.assertEqual(1, self.calls())

    def test_returns_every_oversized_file_together_after_one_wc(self) -> None:
        first = self.write_bytes("one.md", 16_385)
        second = self.write_bytes("dir with spaces/two.md", 20_000)
        valid = self.write_bytes("valid.md", 12_289)

        completed, payload = self.run_checker(first, second, valid)

        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertEqual("split_required", payload["status"])
        self.assertEqual(
            {str(first): 16_385, str(second): 20_000},
            {entry["path"]: entry["bytes"] for entry in payload["oversized"]},
        )
        self.assertEqual(1, self.calls())

    def test_deduplicates_and_excludes_mdc_and_working(self) -> None:
        measured = self.write_bytes("normal.md", 100)
        working = self.write_bytes("nested/working.md", 30_000)
        notion = self.write_bytes("notion/page.mdc", 30_000)

        completed, payload = self.run_checker(measured, measured, working, notion)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(1, payload["checked"])
        self.assertCountEqual([str(working), str(notion)], payload["excluded"])
        self.assertEqual(1, self.calls())

    def test_all_excluded_is_a_pass_without_wc(self) -> None:
        working = self.write_bytes("working.md", 30_000)
        notion = self.write_bytes("page.mdc", 30_000)

        completed, payload = self.run_checker(working, notion)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["checked"])
        self.assertEqual(0, self.calls())

    def test_invalid_and_missing_inputs_are_distinct_from_split(self) -> None:
        cases = ((), ("relative.md",), (self.root / "missing.md",))
        for paths in cases:
            with self.subTest(paths=paths):
                completed, payload = self.run_checker(*paths)
                self.assertEqual(2, completed.returncode)
                self.assertEqual("invalid", payload["status"])
        self.assertEqual(0, self.calls())


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

class WorkspaceResolverTest(unittest.TestCase):
    def run_resolver(self, path: Path, work_id: str = "eng-421-test") -> tuple[subprocess.CompletedProcess[str], dict]:
        completed = subprocess.run(
            [str(RESOLVER), "--path", str(path), "--work-id", work_id],
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, json.loads(completed.stdout)

    def git(self, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=cwd, text=True, capture_output=True, check=True
        )

    def test_resolves_registered_git_main_and_linked_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "main workspace"
            linked = Path(temporary) / "linked workspace"
            root.mkdir()
            self.git("init", "-q", cwd=root)
            self.git("config", "user.email", "test@example.com", cwd=root)
            self.git("config", "user.name", "Test", cwd=root)
            (root / "readme.md").write_text("test\n", encoding="utf-8")
            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            self.git("add", "readme.md", ".gitignore", cwd=root)
            self.git("commit", "-qm", "initial", cwd=root)
            self.git("worktree", "add", "-q", "-b", "linked", str(linked), cwd=root)

            completed, payload = self.run_resolver(linked)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("resolved", payload["status"])
            self.assertEqual("git", payload["vcs"])
            self.assertEqual(str(linked.resolve()), payload["repo_root"])
            self.assertEqual(str(linked.resolve()), payload["durable_root"])
            self.assertEqual(str(root.resolve()), payload["default_workspace"])
            self.assertEqual(str(linked.resolve()), payload["active_workspace"])
            self.assertEqual(
                str(linked.resolve() / ".engineering/work/eng-421-test"),
                payload["work_dir"],
            )
            self.assertEqual(
                str(root.resolve() / ".engineering/notion"), payload["notion_dir"]
            )
            self.assertTrue(payload["engineering_ignored"])
            self.assertEqual(
                str(linked.resolve() / ".gitignore"), payload["ignore_file"]
            )

    def test_requires_pm_ignore_bootstrap_before_resolving(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "missing ignore"
            root.mkdir()
            self.git("init", "-q", cwd=root)

            completed, payload = self.run_resolver(root)

            self.assertEqual(3, completed.returncode)
            self.assertEqual("requires_ignore", payload["status"])
            self.assertEqual(str(root.resolve() / ".gitignore"), payload["ignore_file"])
            self.assertIn("PM must add .engineering/", payload["error"])

            (root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
            completed, payload = self.run_resolver(root)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("resolved", payload["status"])
            self.assertTrue(payload["engineering_ignored"])

    def test_rejects_later_ignore_negation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "negated ignore"
            root.mkdir()
            self.git("init", "-q", cwd=root)
            (root / ".gitignore").write_text(
                ".engineering/\n!.engineering/\n", encoding="utf-8"
            )

            completed, payload = self.run_resolver(root)

            self.assertEqual(3, completed.returncode)
            self.assertEqual("requires_ignore", payload["status"])
            self.assertEqual(str(root.resolve() / ".gitignore"), payload["ignore_file"])

    def test_refuses_invalid_work_id_and_non_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for work_id in ("UPPER", "bad/path", "-leading"):
                with self.subTest(work_id=work_id):
                    completed, payload = self.run_resolver(root, work_id)
                    self.assertEqual(2, completed.returncode)
                    self.assertEqual("invalid", payload["status"])

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

            completed, payload = self.run_resolver(secondary)

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("jj", payload["vcs"])
            self.assertEqual(str(root.resolve()), payload["default_workspace"])
            self.assertEqual(str(secondary.resolve()), payload["active_workspace"])
            self.assertEqual(str(secondary.resolve()), payload["durable_root"])
            self.assertEqual(str(secondary.resolve()), payload["repo_root"])
            self.assertEqual(
                str(secondary.resolve() / ".gitignore"), payload["ignore_file"]
            )
            self.assertTrue(payload["engineering_ignored"])

    @unittest.skipUnless(shutil.which("jj"), "jj is unavailable")
    def test_refuses_jj_repository_without_registered_default(self) -> None:
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

            completed, payload = self.run_resolver(root)

            self.assertEqual(2, completed.returncode)
            self.assertEqual("invalid", payload["status"])
            self.assertIn("workspace 'default' is not registered", payload["error"])


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


class EngineeringIgnoreContractTest(unittest.TestCase):
    def test_engineering_transport_and_work_state_are_ignored(self) -> None:
        paths = (
            ".engineering/notion/example.mdc",
            ".engineering/work/test/state.md",
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
        (self.root / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
        for relative in (
            "README.md",
            "CONTEXT.md",
            ".engineering/work/eng-42/working.md",
            ".engineering/work/eng-42/state.md",
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
        completed = subprocess.run(
            [str(executable)],
            cwd=self.root,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        return payload["hookSpecificOutput"]["additionalContext"]

    def assert_context_contract(self, context: str) -> None:
        self.assertNotIn("\\n", context)
        self.assertNotIn("CONTEXT.md", context)
        expected = (
            ".engineering/work/eng-42/working.md",
            ".engineering/work/eng-42/state.md",
            "docs/index.md",
            "docs/architecture/overview.md",
            "docs/design/system.md",
            "docs/specs/accounts/index.md",
        )
        for path in expected:
            self.assertIn(path, context)
        for first, second in zip(expected, expected[1:]):
            self.assertLess(context.index(first), context.index(second))
        for detail in (
            "docs/architecture/runtime-boundaries.md",
            "docs/design/checkout-flow.md",
            "docs/specs/accounts/session.md",
        ):
            self.assertNotIn(detail, context)

    def test_session_start_injects_ordered_engineering_entrypoints(self) -> None:
        context = self.run_hook(SESSION_START, '{"source":"startup"}\n')
        self.assert_context_contract(context)

    def test_subagent_start_injects_ordered_engineering_entrypoints(self) -> None:
        context = self.run_hook(SUBAGENT_START)
        self.assert_context_contract(context)


if __name__ == "__main__":
    unittest.main()
