from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
TRANSPORT_PROFILE_VALIDATOR = (
    SKILLS / "sync-notion/scripts/validate-transport-profile.py"
)
MDC_METADATA_CHECK = SKILLS / "mdc/scripts/validate-transport-metadata.sh"


class TransportProfileSchemaContractTest(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict[str, object]]:
        executable = root / "notion-sync"
        executable.write_bytes(b"#!/bin/sh\nexit 0\n")
        executable.chmod(0o700)
        executable_hash = hashlib.sha256(executable.read_bytes()).hexdigest()
        version_hash = hashlib.sha256(b"notion-sync 1.2.3\n").hexdigest()
        help_hash = hashlib.sha256(
            b"pull --recursive --json\nsearch --json\ncreate --json --create-if-absent\n"
            b"push --json --expected-revision\n"
        ).hexdigest()
        capability_vectors = {
            "recursive_pull": ["pull", "--recursive", "--json"],
            "search": ["search", "--json"],
            "create": ["create", "--json"],
            "push": ["push", "--json"],
            "conditional_update": ["push", "--json", "--expected-revision"],
            "conditional_create": ["create", "--json", "--create-if-absent"],
        }
        output_contracts = {
            "recursive_pull": "notion-page-tree-json-v1",
            "search": "notion-search-json-v1",
            "create": "notion-created-page-json-v1",
            "push": "notion-page-write-json-v1",
            "conditional_update": "notion-page-write-json-v1",
            "conditional_create": "notion-created-page-json-v1",
        }
        evidence = {
            "binary_sha256": executable_hash,
            "version": "1.2.3",
            "help_stdout_sha256": help_hash,
            "capability_vectors": capability_vectors,
            "output_contracts": output_contracts,
            "results": {
                "recursive_pull": "pass",
                "search": "pass",
                "create": "pass",
                "push": "pass",
                "conditional_update": "pass",
                "conditional_create": "pass",
            },
            "tested_at": "2026-07-20T12:00:00Z",
        }
        evidence_bytes = json.dumps(
            evidence,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        profile: dict[str, object] = {
            "schema": "notion-sync-transport-profile/v1",
            "name": "product-specs",
            "installation": {
                "source": "team-artifact",
                "package": "notion-sync",
                "version": "1.2.3",
                "executable": str(executable),
                "sha256": executable_hash,
            },
            "probes": {
                "version_argv": ["--version"],
                "version_stdout_sha256": version_hash,
                "help_argv": ["--help"],
                "help_stdout_sha256": help_hash,
            },
            "capabilities": {
                "recursive_pull": {
                    "command": "pull",
                    "flags": ["--recursive", "--json"],
                    "output_contract": "notion-page-tree-json-v1",
                },
                "search": {
                    "command": "search",
                    "flags": ["--json"],
                    "output_contract": "notion-search-json-v1",
                },
                "create": {
                    "command": "create",
                    "flags": ["--json"],
                    "output_contract": "notion-created-page-json-v1",
                },
                "push": {
                    "command": "push",
                    "flags": ["--json"],
                    "output_contract": "notion-page-write-json-v1",
                },
                "conditional_update": {
                    "support": "supported",
                    "command": "push",
                    "flags": ["--expected-revision"],
                    "output_contract": "notion-page-write-json-v1",
                },
                "conditional_create": {
                    "support": "supported",
                    "command": "create",
                    "flags": ["--create-if-absent"],
                    "output_contract": "notion-created-page-json-v1",
                },
            },
            "conformance": {
                "schema": "notion-sync-conformance/v1",
                "evidence": evidence,
                "evidence_sha256": hashlib.sha256(evidence_bytes).hexdigest(),
            },
        }
        profile_path = root / "transport-profile.json"
        profile_path.write_text(json.dumps(profile), encoding="utf-8")
        profile_path.chmod(0o600)
        return profile_path, profile

    def test_bundled_validator_emits_exact_profile_byte_digest_without_token(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            profile_path, _ = self._fixture(root)
            environment = dict(os.environ)
            environment["NOTION_TOKEN"] = "should-never-appear"
            result = subprocess.run(
                ["python3", str(TRANSPORT_PROFILE_VALIDATOR), str(profile_path)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual("profile_structure_verified", report["status"])
            self.assertEqual(str(profile_path), report["profile_file"])
            self.assertEqual(
                hashlib.sha256(profile_path.read_bytes()).hexdigest(),
                report["profile_file_sha256"],
            )
            self.assertNotIn("should-never-appear", result.stdout + result.stderr)

    def test_bundled_validator_help_is_functional(self) -> None:
        result = subprocess.run(
            ["python3", str(TRANSPORT_PROFILE_VALIDATOR), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("<absolute-profile-file>", result.stdout)
        self.assertIn("--print-template", result.stdout)
        self.assertEqual("", result.stderr)

    def test_bundled_validator_emits_secret_free_unverified_template(self) -> None:
        environment = dict(os.environ)
        environment["NOTION_TOKEN"] = "should-never-appear"
        result = subprocess.run(
            ["python3", str(TRANSPORT_PROFILE_VALIDATOR), "--print-template"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        template = json.loads(result.stdout)
        self.assertEqual("unverified_template", template["status"])
        self.assertEqual(
            "notion-sync-transport-profile/v1", template["profile"]["schema"]
        )
        self.assertEqual(
            "unavailable",
            template["profile"]["capabilities"]["conditional_update"]["support"],
        )
        self.assertEqual(
            "unavailable",
            template["profile"]["capabilities"]["conditional_create"]["support"],
        )
        self.assertNotIn("NOTION_TOKEN", result.stdout)
        self.assertNotIn("should-never-appear", result.stdout + result.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            profile_path = Path(temporary).resolve() / "template-profile.json"
            profile_path.write_text(json.dumps(template["profile"]), encoding="utf-8")
            profile_path.chmod(0o600)
            validation = subprocess.run(
                ["python3", str(TRANSPORT_PROFILE_VALIDATOR), str(profile_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(2, validation.returncode)
        refusal = json.loads(validation.stderr)
        self.assertEqual("transport_unverified", refusal["status"])
        self.assertIn("placeholder", refusal["error"])

    def test_bundled_validator_rejects_noncanonical_conformance_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            profile_path, profile = self._fixture(root)
            profile["conformance"]["evidence_sha256"] = "0" * 64  # type: ignore[index]
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            profile_path.chmod(0o600)
            result = subprocess.run(
                ["python3", str(TRANSPORT_PROFILE_VALIDATOR), str(profile_path)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(2, result.returncode)
            refusal = json.loads(result.stderr)
            self.assertEqual("transport_unverified", refusal["status"])
            self.assertIn("conformance evidence SHA-256 mismatch", refusal["error"])

    def test_bundled_validator_rejects_reused_evidence_for_changed_vector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            profile_path, profile = self._fixture(root)
            profile["capabilities"]["push"]["flags"] = ["--json", "--force"]  # type: ignore[index]
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            profile_path.chmod(0o600)
            result = subprocess.run(
                ["python3", str(TRANSPORT_PROFILE_VALIDATOR), str(profile_path)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(2, result.returncode)
            refusal = json.loads(result.stderr)
            self.assertIn(
                "conformance push vector does not match capabilities",
                refusal["error"],
            )

    def test_conditional_create_is_independent_from_conditional_update(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            profile_path, profile = self._fixture(root)
            conditional_create = profile["capabilities"]["conditional_create"]  # type: ignore[index]
            conditional_create.update(  # type: ignore[union-attr]
                {"support": "unavailable", "command": None, "flags": [], "output_contract": None}
            )
            evidence = profile["conformance"]["evidence"]  # type: ignore[index]
            evidence["capability_vectors"]["conditional_create"] = []  # type: ignore[index]
            evidence["output_contracts"]["conditional_create"] = "unavailable"  # type: ignore[index]
            evidence["results"]["conditional_create"] = "unavailable"  # type: ignore[index]
            evidence_bytes = json.dumps(
                evidence,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            profile["conformance"]["evidence_sha256"] = hashlib.sha256(evidence_bytes).hexdigest()  # type: ignore[index]
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            profile_path.chmod(0o600)
            result = subprocess.run(
                ["python3", str(TRANSPORT_PROFILE_VALIDATOR), str(profile_path)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual("supported", report["capabilities"]["conditional_update"]["support"])
            self.assertEqual("unavailable", report["capabilities"]["conditional_create"]["support"])


class RemoteRevisionOwnershipContractTest(unittest.TestCase):
    def _run_validator(self, content: bytes) -> tuple[subprocess.CompletedProcess[str], bytes]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "page.mdc"
            path.write_bytes(content)
            result = subprocess.run(
                ["bash", str(MDC_METADATA_CHECK), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            return result, path.read_bytes()

    def test_validator_reports_existing_revision_without_mutating_bytes(self) -> None:
        original = (
            b"---\n"
            b"title: Contract\n"
            b"last_edited_time: 2026-07-20T10:30:00.000Z\n"
            b"ref: 01234567-89ab-cdef-0123-456789abcdef\n"
            b"---\n"
            b"# Contract\n"
        )
        result, final = self._run_validator(original)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(original, final)
        self.assertIn(
            "transport_last_edited_time=2026-07-20T10:30:00.000Z",
            result.stdout,
        )

    def test_validator_allows_unsynced_absence_without_inserting_field(self) -> None:
        original = b"---\ntitle: New child\nparent: parent-ref\n---\n# New child\n"
        result, final = self._run_validator(original)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(original, final)
        self.assertIn("transport_last_edited_time=<absent>", result.stdout)

    def test_validator_rejects_duplicate_revision_without_mutating_bytes(self) -> None:
        original = (
            b"---\n"
            b"last_edited_time: first\n"
            b"last_edited_time: second\n"
            b"---\n"
            b"# Duplicate\n"
        )
        result, final = self._run_validator(original)

        self.assertNotEqual(0, result.returncode)
        self.assertEqual(original, final)
        self.assertIn("malformed, duplicate", result.stderr)

    def test_validator_reports_identity_and_detects_a_changed_ref(self) -> None:
        before = (
            b"---\n"
            b"ref: 01234567-89ab-cdef-0123-456789abcdef\n"
            b"parent: fedcba98-7654-3210-fedc-ba9876543210\n"
            b"last_edited_time: 2026-07-20T10:30:00.000Z\n"
            b"---\n# Contract\n"
        )
        after = before.replace(
            b"ref: 01234567-89ab-cdef-0123-456789abcdef",
            b"ref: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        )

        before_result, _ = self._run_validator(before)
        after_result, _ = self._run_validator(after)

        self.assertEqual(0, before_result.returncode, before_result.stderr)
        self.assertEqual(0, after_result.returncode, after_result.stderr)
        self.assertIn(
            "transport_ref=01234567-89ab-cdef-0123-456789abcdef",
            before_result.stdout,
        )
        self.assertIn(
            "transport_parent=fedcba98-7654-3210-fedc-ba9876543210",
            before_result.stdout,
        )
        self.assertNotEqual(before_result.stdout, after_result.stdout)

    def test_validator_rejects_duplicate_or_missing_identity(self) -> None:
        duplicate_ref = b"---\nref: first\nref: second\n---\n# Duplicate\n"
        missing_identity = b"---\ntitle: No identity\n---\n# Missing\n"

        for original in (duplicate_ref, missing_identity):
            with self.subTest(original=original):
                result, final = self._run_validator(original)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(original, final)
                self.assertIn("transport identity metadata", result.stderr)

    def test_validator_rejects_non_exact_delimiter_and_symlink_input(self) -> None:
        non_exact = b"---\nref: stable-ref\n---   \n# Contract\n"
        result, final = self._run_validator(non_exact)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(non_exact, final)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target.mdc"
            target.write_bytes(b"---\nref: stable-ref\n---\n# Contract\n")
            alias = root / "alias.mdc"
            alias.symlink_to(target)
            result = subprocess.run(
                ["bash", str(MDC_METADATA_CHECK), str(alias)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("regular non-symlink", result.stderr)


if __name__ == "__main__":
    unittest.main()
