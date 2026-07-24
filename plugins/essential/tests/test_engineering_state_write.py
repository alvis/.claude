from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ESSENTIAL = Path(__file__).resolve().parents[1]
LEASE = ESSENTIAL / "bin/engineering-lease"
STATE_WRITE = ESSENTIAL / "bin/engineering-state-write"


class EngineeringStateWriteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temporary.name) / "works" / "demo"
        (self.work_dir / "state").mkdir(parents=True)
        self.lease_path = self.work_dir / "lease.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def acquire(self, *arguments: str) -> str:
        completed = subprocess.run(
            [
                str(LEASE),
                "acquire",
                "--work-dir",
                str(self.work_dir),
                "--capability",
                "pm",
                "--session",
                "s1",
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(completed.stdout)["token"]

    def write(
        self, token: str, target: str, content: str = "content\n"
    ) -> tuple[int, dict]:
        completed = subprocess.run(
            [
                str(STATE_WRITE),
                "--work-dir",
                str(self.work_dir),
                "--token",
                token,
                "--target",
                target,
            ],
            input=content,
            capture_output=True,
            text=True,
        )
        return completed.returncode, json.loads(completed.stdout)

    def test_write_applies_content_and_heartbeats(self) -> None:
        token = self.acquire()
        before = json.loads(self.lease_path.read_text(encoding="utf-8"))
        time.sleep(1.1)
        code, payload = self.write(token, "state.md", "fresh state\n")
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "written")
        self.assertEqual(
            (self.work_dir / "state.md").read_text(encoding="utf-8"),
            "fresh state\n",
        )
        after = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertGreater(after["expires_at_epoch"], before["expires_at_epoch"])
        self.assertEqual(after["acquired_at"], before["acquired_at"])

    def test_write_creates_nested_target(self) -> None:
        token = self.acquire()
        code, payload = self.write(token, "state/journal.md", "line\n")
        self.assertEqual(code, 0)
        self.assertTrue((self.work_dir / "state/journal.md").is_file())

    def test_refuses_without_lease(self) -> None:
        code, payload = self.write("anything", "state.md")
        self.assertEqual(code, 4)
        self.assertEqual(payload["status"], "lease_free")
        self.assertFalse((self.work_dir / "state.md").exists())

    def test_refuses_expired_lease(self) -> None:
        token = self.acquire("--ttl", "1")
        time.sleep(2)
        code, payload = self.write(token, "state.md")
        self.assertEqual(code, 4)
        self.assertEqual(payload["status"], "lease_expired")

    def test_refuses_foreign_token(self) -> None:
        self.acquire()
        code, payload = self.write("deadbeef", "state.md")
        self.assertEqual(code, 5)
        self.assertEqual(payload["status"], "lease_foreign")
        self.assertFalse((self.work_dir / "state.md").exists())

    def test_refuses_traversal_and_absolute_targets(self) -> None:
        token = self.acquire()
        for target in ("../escape.md", "/etc/escape.md", "state/../../up.md"):
            code, payload = self.write(token, target)
            self.assertEqual(code, 2, target)
            self.assertEqual(payload["status"], "invalid")

    def test_refuses_symlinked_target(self) -> None:
        token = self.acquire()
        victim = Path(self.temporary.name) / "victim.md"
        victim.write_text("original", encoding="utf-8")
        (self.work_dir / "state.md").symlink_to(victim)
        code, payload = self.write(token, "state.md")
        self.assertEqual(code, 2)
        self.assertEqual(victim.read_text(encoding="utf-8"), "original")

    def test_no_temp_files_left_behind(self) -> None:
        token = self.acquire()
        self.write(token, "state.md")
        self.write("wrong", "state.md")
        leftovers = [
            name
            for name in (entry.name for entry in self.work_dir.iterdir())
            if name.startswith(".state-write.")
        ]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
