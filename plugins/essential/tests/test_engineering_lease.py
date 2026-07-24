from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ESSENTIAL = Path(__file__).resolve().parents[1]
LEASE = ESSENTIAL / "bin/engineering-lease"


class EngineeringLeaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temporary.name) / "works" / "demo"
        self.work_dir.mkdir(parents=True)
        self.lease_path = self.work_dir / "lease.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_lease(self, verb: str, *arguments: str) -> tuple[int, dict]:
        completed = subprocess.run(
            [str(LEASE), verb, "--work-dir", str(self.work_dir), *arguments],
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        return completed.returncode, payload

    def acquire(self, session: str = "s1", *arguments: str) -> dict:
        code, payload = self.run_lease(
            "acquire", "--capability", "pm", "--session", session, *arguments
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["status"], "acquired")
        return payload

    def test_acquire_creates_well_formed_lease(self) -> None:
        payload = self.acquire()
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        for key in (
            "work_id",
            "owner_session",
            "owner_capability",
            "host",
            "pid",
            "token_sha256",
            "acquired_at",
            "acquired_epoch",
            "heartbeat_at",
            "expires_at",
            "expires_at_epoch",
            "ttl_seconds",
        ):
            self.assertIn(key, lease)
        self.assertEqual(lease["work_id"], "demo")
        self.assertEqual(lease["owner_session"], "s1")
        self.assertEqual(lease["owner_capability"], "pm")
        self.assertNotIn("token", lease)  # digest only; plaintext never stored
        digest = hashlib.sha256(payload["token"].encode()).hexdigest()
        self.assertEqual(lease["token_sha256"], digest)

    def test_second_acquire_is_contended(self) -> None:
        self.acquire()
        code, payload = self.run_lease(
            "acquire", "--capability", "pm", "--session", "s2"
        )
        self.assertEqual(code, 3)
        self.assertEqual(payload["status"], "contended")
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(lease["owner_session"], "s1")

    def test_status_reports_free_held_foreign(self) -> None:
        code, payload = self.run_lease("status")
        self.assertEqual(payload["status"], "free")
        token = self.acquire()["token"]
        _, payload = self.run_lease("status", "--token", token)
        self.assertEqual(payload["status"], "held")
        _, payload = self.run_lease("status", "--token", "deadbeef")
        self.assertEqual(payload["status"], "foreign")
        _, payload = self.run_lease("status")
        self.assertEqual(payload["status"], "foreign")

    def test_heartbeat_requires_matching_token(self) -> None:
        token = self.acquire()["token"]
        code, payload = self.run_lease("heartbeat", "--token", "deadbeef")
        self.assertEqual(code, 5)
        self.assertEqual(payload["status"], "refused")
        code, payload = self.run_lease(
            "heartbeat", "--token", token, "--state-revision", "7"
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "renewed")
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(lease["state_revision"], 7)
        self.assertEqual(lease["owner_session"], "s1")

    def test_release_requires_matching_token(self) -> None:
        token = self.acquire()["token"]
        code, payload = self.run_lease("release", "--token", "deadbeef")
        self.assertEqual(code, 5)
        self.assertEqual(payload["status"], "refused")
        self.assertTrue(self.lease_path.exists())
        code, payload = self.run_lease("release", "--token", token)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "released")
        self.assertFalse(self.lease_path.exists())

    def test_takeover_refused_on_live_lease(self) -> None:
        self.acquire()
        code, payload = self.run_lease(
            "takeover", "--capability", "pm", "--session", "s2"
        )
        self.assertEqual(code, 5)
        self.assertEqual(payload["status"], "refused")
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(lease["owner_session"], "s1")

    def test_takeover_succeeds_on_expired_lease(self) -> None:
        self.acquire("s1", "--ttl", "1")
        time.sleep(2)
        code, payload = self.run_lease(
            "acquire", "--capability", "pm", "--session", "s2"
        )
        self.assertEqual(code, 4)
        self.assertEqual(payload["status"], "takeover_required")
        code, payload = self.run_lease(
            "takeover", "--capability", "essential:takeover", "--session", "s2"
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "taken_over")
        self.assertEqual(payload["journal_event"], "lease")
        self.assertEqual(payload["previous_lease"]["owner_session"], "s1")
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(lease["owner_session"], "s2")
        self.assertEqual(lease["owner_capability"], "essential:takeover")

    def test_symlinked_lease_path_refused(self) -> None:
        victim = Path(self.temporary.name) / "victim.json"
        victim.write_text("{}", encoding="utf-8")
        self.lease_path.symlink_to(victim)
        code, payload = self.run_lease("status")
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "invalid")

    def test_no_partial_files_left_behind(self) -> None:
        token = self.acquire()["token"]
        self.run_lease("heartbeat", "--token", token)
        self.run_lease("release", "--token", token)
        self.assertEqual(os.listdir(self.work_dir), [])


    def test_session_defaults_when_flag_absent(self) -> None:
        completed = subprocess.run(
            [str(LEASE), "acquire", "--work-dir", str(self.work_dir),
             "--capability", "pm"],
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_SESSION_ID": "env-session"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(lease["owner_session"], "env-session")

    def test_session_falls_back_to_pid_identity(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_SESSION_ID"}
        completed = subprocess.run(
            [str(LEASE), "acquire", "--work-dir", str(self.work_dir),
             "--capability", "pm"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lease = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertTrue(lease["owner_session"].startswith("pid-"))

    def test_heartbeat_preserves_acquired_at_without_date_parsing(self) -> None:
        token = self.acquire()["token"]
        before = json.loads(self.lease_path.read_text(encoding="utf-8"))
        time.sleep(1.1)
        code, payload = self.run_lease("heartbeat", "--token", token)
        self.assertEqual(code, 0)
        after = json.loads(self.lease_path.read_text(encoding="utf-8"))
        self.assertEqual(after["acquired_at"], before["acquired_at"])
        self.assertEqual(after["acquired_epoch"], before["acquired_epoch"])
        self.assertGreaterEqual(
            after["heartbeat_epoch"], before["heartbeat_epoch"]
        )

    def test_ensure_acquires_renews_and_refuses(self) -> None:
        code, payload = self.run_lease(
            "ensure", "--capability", "pm", "--session", "s1"
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "acquired")
        token = payload["token"]
        code, payload = self.run_lease(
            "ensure", "--capability", "pm", "--token", token
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "renewed")
        code, payload = self.run_lease("ensure", "--capability", "pm")
        self.assertEqual(code, 3)
        self.assertEqual(payload["status"], "contended")

    def test_ensure_revives_own_expired_lease_only(self) -> None:
        code, payload = self.run_lease(
            "ensure", "--capability", "pm", "--session", "s1", "--ttl", "1"
        )
        token = payload["token"]
        time.sleep(2)
        code, payload = self.run_lease("ensure", "--capability", "pm")
        self.assertEqual(code, 4)
        self.assertEqual(payload["status"], "takeover_required")
        code, payload = self.run_lease(
            "ensure", "--capability", "pm", "--token", token
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "renewed")


if __name__ == "__main__":
    unittest.main()
