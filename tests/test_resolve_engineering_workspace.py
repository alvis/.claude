"""Tests for the resolve-engineering-workspace shell resolver.

Every case runs the resolver under `/bin/bash` explicitly. On stock macOS that
is bash 3.2, where expanding an empty array under `set -u` is an unbound
variable error — the failure mode these tests exist to prevent.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


RESOLVER = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "essential"
    / "bin"
    / "resolve-engineering-workspace"
)

SYSTEM_BASH = "/bin/bash"


@unittest.skipUnless(Path(SYSTEM_BASH).exists(), "no /bin/bash on this platform")
@unittest.skipUnless(shutil.which("jq"), "resolver requires jq")
class ResolveEngineeringWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(tempfile.mkdtemp(prefix="resolver-test-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        subprocess.run(
            ["git", "init", "--quiet", str(self.repo)],
            check=True,
            capture_output=True,
        )

    def resolve(self, *args: str) -> dict:
        """Run the resolver under the system bash and return its parsed JSON."""
        result = subprocess.run(
            [SYSTEM_BASH, str(RESOLVER), *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull},
        )
        self.assertNotIn(
            "unbound variable",
            result.stderr,
            f"resolver hit an unbound variable under {SYSTEM_BASH}: {result.stderr}",
        )
        return json.loads(result.stdout)

    def test_resolves_with_no_work_streams_present(self) -> None:
        """An empty candidate array must not abort the resolver."""
        payload = self.resolve()

        self.assertEqual(payload["status"], "work_id_required")
        self.assertEqual(payload["candidate_work_ids"], [])

    def test_requires_ignore_before_bootstrap(self) -> None:
        payload = self.resolve("--work-id", "sample-stream")

        self.assertEqual(payload["status"], "requires_ignore")
        self.assertTrue(payload["ignore_file"].endswith(".gitignore"))

    def test_bootstrap_reports_created_and_empty_existing_entrypoints(self) -> None:
        """`bootstrap_existing` is empty on a first bootstrap — the original crash."""
        (self.repo / ".gitignore").write_text(".state/\n", encoding="utf-8")

        payload = self.resolve("--work-id", "sample-stream", "--bootstrap")

        self.assertEqual(payload["status"], "resolved")
        self.assertTrue(payload["engineering_ignored"])
        self.assertEqual(payload["bootstrap_existing"], [])
        created = {Path(path).name for path in payload["bootstrap_created"]}
        self.assertEqual(created, {"goal.md", "working.md", "state.md", "journal.md"})

    def add_worktree(self, name: str) -> Path:
        """Commit once and add a linked worktree, returning its path."""
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "base"],
            cwd=self.repo,
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_AUTHOR_NAME": "Test",
                "GIT_AUTHOR_EMAIL": "test@example.com",
                "GIT_COMMITTER_NAME": "Test",
                "GIT_COMMITTER_EMAIL": "test@example.com",
            },
        )
        linked = self.repo.parent / f"{self.repo.name}-{name}"
        self.addCleanup(shutil.rmtree, linked, ignore_errors=True)
        subprocess.run(
            ["git", "worktree", "add", "--quiet", "-b", name, str(linked)],
            cwd=self.repo,
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull},
        )
        return linked

    def test_secondary_worktree_roots_state_in_the_default_tree(self) -> None:
        """`.state/` belongs to the main worktree, whichever tree calls."""
        (self.repo / ".gitignore").write_text(".state/\n", encoding="utf-8")
        linked = self.add_worktree("secondary")

        payload = self.resolve(
            "--path", str(linked), "--work-id", "sample-stream"
        )

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["state_root"], str(self.repo.resolve()))
        self.assertEqual(payload["default_workspace"], str(self.repo.resolve()))
        self.assertEqual(payload["active_workspace"], str(linked.resolve()))
        self.assertEqual(payload["durable_root"], str(linked.resolve()))
        self.assertEqual(
            payload["work_dir"],
            str(self.repo.resolve() / ".state/works/sample-stream"),
        )

    def test_state_root_falls_back_to_a_sole_workspace(self) -> None:
        (self.repo / ".gitignore").write_text(".state/\n", encoding="utf-8")

        payload = self.resolve("--work-id", "sample-stream")

        self.assertEqual(payload["state_root"], payload["active_workspace"])

    def test_requires_ignore_names_the_default_tree_gitignore(self) -> None:
        """Ignoring `.state/` in a secondary tree never clears the gate."""
        linked = self.add_worktree("secondary")
        (linked / ".gitignore").write_text(".state/\n", encoding="utf-8")

        payload = self.resolve(
            "--path", str(linked), "--work-id", "sample-stream"
        )

        self.assertEqual(payload["status"], "requires_ignore")
        self.assertEqual(
            payload["ignore_file"], str(self.repo.resolve() / ".gitignore")
        )

    def test_second_bootstrap_reports_existing_entrypoints(self) -> None:
        (self.repo / ".gitignore").write_text(".state/\n", encoding="utf-8")
        self.resolve("--work-id", "sample-stream", "--bootstrap")

        payload = self.resolve("--work-id", "sample-stream", "--bootstrap")

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["bootstrap_created"], [])
        self.assertEqual(len(payload["bootstrap_existing"]), 4)


if __name__ == "__main__":
    unittest.main()
