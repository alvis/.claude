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
        (self.repo / ".gitignore").write_text(".engineering/\n", encoding="utf-8")

        payload = self.resolve("--work-id", "sample-stream", "--bootstrap")

        self.assertEqual(payload["status"], "resolved")
        self.assertTrue(payload["engineering_ignored"])
        self.assertEqual(payload["bootstrap_existing"], [])
        created = {Path(path).name for path in payload["bootstrap_created"]}
        self.assertEqual(created, {"goal.md", "working.md", "state.md", "journal.md"})

    def test_second_bootstrap_reports_existing_entrypoints(self) -> None:
        (self.repo / ".gitignore").write_text(".engineering/\n", encoding="utf-8")
        self.resolve("--work-id", "sample-stream", "--bootstrap")

        payload = self.resolve("--work-id", "sample-stream", "--bootstrap")

        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["bootstrap_created"], [])
        self.assertEqual(len(payload["bootstrap_existing"]), 4)


if __name__ == "__main__":
    unittest.main()
