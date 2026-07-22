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
SYNC_NOTION = SKILLS / "sync-notion/SKILL.md"
TRANSPORT_PROFILE = SKILLS / "sync-notion/references/transport-profile.md"
DATABASE_RESOLUTION = SKILLS / "sync-notion/references/database-resolution.md"
TRANSPORT_PROFILE_VALIDATOR = (
    SKILLS / "sync-notion/scripts/validate-transport-profile.py"
)
MDC = SKILLS / "mdc/SKILL.md"
MDC_EDITING = SKILLS / "mdc/references/editing-rules.md"
MDC_METADATA_CHECK = SKILLS / "mdc/scripts/validate-transport-metadata.sh"
MDC_LEGACY_STAMP = SKILLS / "mdc/scripts/stamp-last-edited.sh"
SPEC_FRONTMATTER = SKILLS / "spec-code/references/frontmatter.md"
SPEC_CODE = SKILLS / "spec-code/SKILL.md"
IMPLEMENT_CODE = SKILLS / "implement-code/SKILL.md"
SYNC_SPEC = SKILLS / "sync-spec/SKILL.md"
REVIEW_IMPLEMENTATION = SKILLS / "review-implementation/SKILL.md"


def compact(text: str) -> str:
    return " ".join(text.split())


class SharedTransportLeaseContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = compact(SYNC_NOTION.read_text(encoding="utf-8"))

    def test_lease_scope_is_deterministic_and_not_caller_arbitrary(self) -> None:
        for statement in (
            "one exact destination-local shared transport/mirror root",
            "A staging or evidence directory is not a transport root",
            "<transport-root>/.sync-locks/<sha256(normalized-ref)>.lease/",
            "atomic no-clobber directory creation",
            "every participating client for that transport root therefore contends on the same path",
            "require its `.sync-locks/` directory to be ignored and untracked",
            "Reject a symlinked lock component",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

        self.assertNotIn(
            "Acquire an exclusive per-pair lease by atomic creation in the caller-declared evidence/staging root",
            self.contract,
        )

    def test_absent_transport_root_creation_is_gated_and_reported(self) -> None:
        for statement in (
            "Never infer a missing root",
            "deepest existing ancestor",
            "establish the exact owning checkout",
            "lexically and canonically contained",
            "hypothetical paths to be untracked",
            "atomic no-clobber",
            "revalidate containment and ignore state",
            "created_directories: []",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_transport_binary_and_capabilities_are_reproducibly_verified(self) -> None:
        for statement in (
            "destination/team-owned transport profile",
            "installation source",
            "exact version",
            "executable SHA-256",
            "help-output fingerprint",
            "checksum-bound conformance evidence",
            "recursive pull, search, create, push",
            "This plugin does not claim or install a bundled",
            "hashes the exact profile and executable bytes, and never runs the executable",
            "run only the returned canonical executable's inert version/help probes",
            "Do not search `PATH`",
            "transport_unverified",
            "help-text presence alone is not proof of runtime semantics",
            "expected_help_sha256:",
            "actual_help_sha256:",
            "conformance_evidence_sha256:",
            "capabilities:",
            "--transport-profile=<absolute-file>",
            "profile_schema: notion-sync-transport-profile/v1",
            "profile_file_sha256:",
            "Immediately before **every** executable invocation",
            "a mismatch after a possible or confirmed remote mutation",
            "invocation_fingerprints:",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_lease_ownership_and_recovery_are_compare_token_guarded(self) -> None:
        for statement in (
            "cryptographically unguessable token",
            "`created_at`, and `heartbeat_at`",
            "release only after final evidence is durable",
            "fresh compare confirms the on-disk token still equals this run's token",
            "fresh read-only remote pull",
            "Archive/replace only if a final compare still matches the observed old token",
            "let one owner's cleanup remove another owner's lease",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_local_lease_does_not_claim_cross_client_remote_exclusion(self) -> None:
        self.assertIn(
            "serializes only participating clients that share the exact same transport root",
            self.contract,
        )
        self.assertIn("It is not a cross-machine Notion lock", self.contract)
        self.assertIn(
            "independently proven conditional update or conditional create matching that operation",
            self.contract,
        )
        self.assertIn(
            "A local lease, user approval, repeated read, or timing assumption is never a substitute",
            self.contract,
        )

    def test_completion_schema_reports_contention_and_lease_evidence(self) -> None:
        self.assertIn(
            "status: success|partial|failure|refused|requires_ignore|concurrent_sync|transport_unverified",
            self.contract,
        )
        for field in (
            "normalized_ref:",
            "token_fingerprint:",
            "heartbeat_at:",
            "outcome: acquired|released|contended|recovered|not_required",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.contract)

    def test_creation_and_update_have_independent_remote_guards(self) -> None:
        for statement in (
            "conditional update and atomic conditional create independently",
            "Conditional update support never suppresses this creation gate",
            "validated core `create` vector plus its",
            "conditional_create: false",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

    def test_missing_conditional_capability_is_fail_closed(self) -> None:
        for statement in (
            "`status: refused`",
            "preserve the already observed B/L/R `classification`",
            "`next_action: provide_conditional_transport`",
            "no remote or canonical-local mutation",
            "distinct from `transport_unverified`",
            "User acknowledgement cannot override either refusal",
            "preflight the required capability for every selected pair",
            "refuses the whole selected mutation set",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.contract)

        for forbidden in (
            "quiet publication window",
            "quiet creation window",
            "quiet-window",
            "residual-race",
            "residual race",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.contract.lower())

    def test_database_resolution_uses_only_validated_profile_vectors(self) -> None:
        resolution = DATABASE_RESOLUTION.read_text(encoding="utf-8")
        normalized = compact(resolution)

        self.assertIn("canonical executable", normalized)
        self.assertIn("notion-search-json-v1", normalized)
        self.assertIn("independently proven `conditional_create`", normalized)
        self.assertIn("invoke that exact vector once", normalized)
        self.assertIn("notion-created-page-json-v1", normalized)
        self.assertNotIn("Bash: notion-sync", resolution)
        self.assertNotIn("notion-sync search", resolution)
        self.assertNotIn("notion-sync push", resolution)


class TransportProfileSchemaContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = compact(TRANSPORT_PROFILE.read_text(encoding="utf-8"))

    def test_profile_has_concrete_strict_reproducibility_schema(self) -> None:
        for statement in (
            "notion-sync-transport-profile/v1",
            '"source": "npm|pipx|homebrew|system-package|team-artifact"',
            '"package": "exact distribution/package identity"',
            '"version": "exact non-range version"',
            '"executable": "/absolute/canonical/path/to/notion-sync"',
            '"sha256": "64 lowercase hex characters"',
            '"help_stdout_sha256"',
            '"recursive_pull"',
            '"conditional_update"',
            '"conditional_create"',
            '"capability_vectors"',
            '"output_contracts"',
            "Update-CAS evidence never proves atomic create-if-absent",
            "bundled v1 canonical evidence serializer",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.profile)

    def test_profile_is_explicit_destination_local_and_secret_free(self) -> None:
        for statement in (
            "--transport-profile=<absolute-profile-file>",
            "There is no implicit profile",
            "contains no credential",
            "non-symlink regular file",
            "Reject group/world-writable files",
            "Do not interpolate profile values into a shell command",
            "never records `NOTION_TOKEN` or its value",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, self.profile)

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


class NotionCallerProfilePropagationTest(unittest.TestCase):
    def test_sync_spec_requires_resolves_passes_and_reports_profile(self) -> None:
        contract = compact(SYNC_SPEC.read_text(encoding="utf-8"))

        for statement in (
            "--transport-profile=<absolute-file>",
            "last verified exact-byte SHA-256",
            "Never infer a profile path",
            "pass the absolute file explicitly to every transport call",
            "profile_file_sha256:",
            "transport_unverified",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, contract)

    def test_public_notion_orchestrators_propagate_exact_profile(self) -> None:
        contracts = {
            "spec-code": compact(SPEC_CODE.read_text(encoding="utf-8")),
            "implement-code": compact(IMPLEMENT_CODE.read_text(encoding="utf-8")),
            "review-implementation": compact(
                REVIEW_IMPLEMENTATION.read_text(encoding="utf-8")
            ),
        }
        for name, contract in contracts.items():
            with self.subTest(skill=name):
                self.assertIn("--transport-profile=<absolute-file>", contract)
                self.assertIn("destination-local", contract)
                self.assertIn("exact-byte SHA-256", contract)
                self.assertIn("Skill(sync-spec)", contract)

        self.assertIn("Skill(sync-notion)", contracts["spec-code"])
        self.assertIn("pass the profile explicitly", contracts["implement-code"])
        self.assertIn("the child revalidates", contracts["review-implementation"])


class RemoteRevisionOwnershipContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mdc = compact(MDC.read_text(encoding="utf-8"))
        cls.editing = compact(MDC_EDITING.read_text(encoding="utf-8"))
        cls.frontmatter = compact(SPEC_FRONTMATTER.read_text(encoding="utf-8"))
        cls.script = MDC_METADATA_CHECK.read_text(encoding="utf-8")
        cls.legacy_script = MDC_LEGACY_STAMP.read_text(encoding="utf-8")

    def test_local_authoring_never_rewrites_remote_revision_metadata(self) -> None:
        for contract in (self.mdc, self.editing, self.frontmatter):
            with self.subTest(contract=contract[:50]):
                self.assertIn("last_edited_time", contract)
                self.assertIn("transport", contract.lower())
                self.assertTrue(
                    "never add, stamp, or rewrite it" in contract
                    or "Never stamp it with the local clock" in contract
                    or "never replaces it with a local clock" in contract
                )

        self.assertIn("work evidence or a receipt", self.mdc)
        self.assertIn("pre-edit capture", self.mdc)
        self.assertIn("did not change their bytes", self.mdc)

    def test_validator_and_legacy_entrypoint_are_read_only_by_construction(self) -> None:
        self.assertIn("This script never changes file bytes", self.script)
        self.assertNotIn("date -u", self.script)
        self.assertNotIn("mktemp", self.script)
        self.assertNotIn("mv ", self.script)
        self.assertNotIn("last_edited_time: \" ts", self.script)
        self.assertIn("Deprecated compatibility entrypoint", self.legacy_script)
        self.assertIn("validate-transport-metadata.sh", self.legacy_script)
        self.assertNotIn("date -u", self.legacy_script)

    def test_versioned_provenance_does_not_require_notion_for_local_or_inline(self) -> None:
        for field in (
            '"source_kind": "local"',
            '"source_locators":',
            '"source_revision":',
            '"carrier_revision":',
            '"receipt_anchor": "github-pr:owner/repository#123"',
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.frontmatter)

        self.assertIn("`source_kind` is exactly `notion`, `local`, or `inline`", self.frontmatter)
        self.assertIn("`inline-approved:sha256:<exact-byte-hash>`", self.frontmatter)
        self.assertIn("`local-approved:sha256:<exact-byte-hash>`", self.frontmatter)
        self.assertIn(
            "Neither local nor inline provenance requires a Notion id, page revision, or Notion receipt",
            self.frontmatter,
        )
        self.assertNotIn("notion_ids:", self.frontmatter)

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
