"""Tests for the engineering-lease coordinator lease tool.

Every case runs the tool under `/bin/bash` explicitly. On stock macOS that is
bash 3.2, which keeps the backslash in a `"${2:-{\\}}"` default — so every
status-only report (`takeover_required`, `contended`, `expired`, `free`,
`refused`, `released`) fed jq invalid JSON and died. These tests cover the
non-happy paths a transferred work directory relies on.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


LEASE = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "essential"
    / "bin"
    / "engineering-lease"
)

SYSTEM_BASH = "/bin/bash"

CAPABILITY = "essential:takeover"


@unittest.skipUnless(Path(SYSTEM_BASH).exists(), "no /bin/bash on this platform")
@unittest.skipUnless(shutil.which("jq"), "engineering-lease requires jq")
class EngineeringLeaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work_dir = Path(tempfile.mkdtemp(prefix="lease-test-"))
        self.addCleanup(shutil.rmtree, self.work_dir, ignore_errors=True)
        self.lease_path = self.work_dir / "lease.json"

    def lease(self, *args: str) -> tuple[dict, int]:
        """Run the lease tool under the system bash; return parsed JSON and status."""
        result = subprocess.run(
            [SYSTEM_BASH, str(LEASE), *args, "--work-dir", str(self.work_dir)],
            capture_output=True,
            text=True,
        )
        self.assertNotIn("invalid JSON", result.stderr, result.stderr)
        self.assertNotIn("unbound variable", result.stderr, result.stderr)
        return json.loads(result.stdout), result.returncode

    def expire_lease_as_foreign(self) -> None:
        """Age the lease and reassign it, as a work directory copied from elsewhere."""
        payload = json.loads(self.lease_path.read_text(encoding="utf-8"))
        payload.update(
            owner_session="session-from-another-machine",
            host="othermachine.local",
            expires_at="2000-01-01T00:00:00Z",
            expires_at_epoch=946684800,
        )
        self.lease_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def test_ensure_acquires_a_free_lease(self) -> None:
        payload, code = self.lease("ensure", "--capability", CAPABILITY)

        self.assertEqual(payload["status"], "acquired")
        self.assertEqual(code, 0)
        self.assertTrue(payload["token"])

    def test_status_reports_a_free_lease(self) -> None:
        payload, _ = self.lease("status")

        self.assertEqual(payload["status"], "free")
        self.assertIsNone(payload["lease"])

    def test_ensure_on_an_expired_foreign_lease_requires_takeover(self) -> None:
        """The transferred-work-directory path: never silently inherit the lease."""
        self.lease("ensure", "--capability", CAPABILITY)
        self.expire_lease_as_foreign()

        payload, code = self.lease("ensure", "--capability", CAPABILITY)

        self.assertEqual(payload["status"], "takeover_required")
        self.assertEqual(code, 4)

    def test_takeover_claims_an_expired_foreign_lease(self) -> None:
        self.lease("ensure", "--capability", CAPABILITY)
        self.expire_lease_as_foreign()

        payload, code = self.lease("takeover", "--capability", CAPABILITY)

        self.assertEqual(payload["status"], "taken_over")
        self.assertEqual(code, 0)
        self.assertEqual(payload["previous_lease"]["host"], "othermachine.local")
        self.assertTrue(payload["token"])

    def test_ensure_on_a_live_foreign_lease_is_contended(self) -> None:
        self.lease("ensure", "--capability", CAPABILITY)

        payload, code = self.lease("ensure", "--capability", "essential:handover")

        self.assertEqual(payload["status"], "contended")
        self.assertEqual(code, 3)

    def test_heartbeat_without_the_token_is_refused(self) -> None:
        self.lease("ensure", "--capability", CAPABILITY)

        payload, code = self.lease("heartbeat", "--token", "not-the-real-token")

        self.assertEqual(payload["status"], "refused")
        self.assertEqual(code, 5)

    def test_release_removes_an_owned_lease(self) -> None:
        acquired, _ = self.lease("ensure", "--capability", CAPABILITY)

        payload, code = self.lease("release", "--token", acquired["token"])

        self.assertEqual(payload["status"], "released")
        self.assertEqual(code, 0)
        self.assertFalse(self.lease_path.exists())


if __name__ == "__main__":
    unittest.main()
