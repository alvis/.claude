from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
TRANSFER = PLUGIN / "skills/handover/scripts/blr-transfer.py"
SPEC_HASHES = (
    PLUGIN.parent / "specification/skills/sync-spec/scripts/spec-hashes.py"
)


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


class BlrTransferTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.base_root = self.root / "base-source"
        self.local_root = self.root / "local-source"
        self.base_root.mkdir()
        self.local_root.mkdir()
        self.base_bytes = (
            b"---\nref: 11111111111111111111111111111111\n"
            b"last_edited_time: r1\n---\n# Contract\n\nBase.\n"
        )
        self.local_bytes = self.base_bytes.replace(b"Base.", b"Authored local.")
        (self.base_root / "spec.mdc").write_bytes(self.base_bytes)
        (self.local_root / "spec.mdc").write_bytes(self.local_bytes)
        unit = {
            "carrier_kind": "notion-mdc",
            "logical_contract_unit_id": "notion:" + "1" * 32,
            "observed_revision": "r1",
            "path": "spec.mdc",
            "semantic_lineage": "notion",
            "stable_transport_identity": "notion:" + "1" * 32,
        }
        self.base_manifest = self.root / "base-manifest.json"
        self.local_manifest = self.root / "local-manifest.json"
        manifest = {"schema": "spec-hash-input-v1", "units": [unit]}
        self.base_manifest.write_bytes(canonical(manifest))
        self.local_manifest.write_bytes(canonical(manifest))
        base_hash_result = subprocess.run(
            [
                "python3",
                str(SPEC_HASHES.resolve()),
                "--root",
                str(self.base_root),
                "--manifest",
                str(self.base_manifest),
                "--kind",
                "both",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        base_hashes = json.loads(base_hash_result.stdout)
        self.base_receipt = self.root / "base-receipt.json"
        self.base_receipt_bytes = canonical(
            {
                "contract_digest": base_hashes["contract_digest"],
                "hash_model": "specification-dual-hash-v1",
                "schema": "spec-materialization-receipt/v1",
                "transport_manifest_hash": base_hashes["transport_manifest_hash"],
            }
        )
        self.base_receipt.write_bytes(self.base_receipt_bytes)
        self.package = self.root / "transfer.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(TRANSFER), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def pack(self) -> dict[str, object]:
        result = self.run_cli(
            "pack",
            "--base-root",
            str(self.base_root),
            "--base-manifest",
            str(self.base_manifest),
            "--base-receipt",
            str(self.base_receipt),
            "--local-root",
            str(self.local_root),
            "--local-manifest",
            str(self.local_manifest),
            "--spec-hash-helper",
            str(SPEC_HASHES.resolve()),
            "--output",
            str(self.package),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def validate(
        self, package: Path, package_sha256: str, output: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "validate",
            "--package",
            str(package),
            "--package-sha256",
            package_sha256,
            "--spec-hash-helper",
            str(SPEC_HASHES.resolve()),
            "--output-root",
            str(output),
        )

    def write_package(self, name: str, value: object) -> tuple[Path, str]:
        path = self.root / name
        raw = canonical(value)
        path.write_bytes(raw)
        return path, digest(raw)

    def test_round_trip_preserves_exact_base_local_and_receipt(self) -> None:
        packed = self.pack()
        raw = self.package.read_bytes()
        parsed = json.loads(raw)

        self.assertEqual(canonical(parsed), raw)
        self.assertEqual(digest(raw), packed["package_sha256"])
        self.assertEqual("specification-blr-transfer+json/v1", parsed["schema"])
        self.assertNotIn(str(self.root), raw.decode("utf-8"))

        output = self.root / "validated"
        result = self.validate(self.package, str(packed["package_sha256"]), output)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.base_bytes, (output / "base/spec.mdc").read_bytes())
        self.assertEqual(self.local_bytes, (output / "local/spec.mdc").read_bytes())
        self.assertEqual(
            self.base_receipt_bytes,
            (output / "metadata/base-receipt.json").read_bytes(),
        )

    def test_validate_rejects_traversal_even_with_matching_outer_checksum(self) -> None:
        self.pack()
        value = json.loads(self.package.read_bytes())
        value["local"]["files"][0]["path"] = "../escape.mdc"
        malicious, checksum = self.write_package("traversal.json", value)
        output = self.root / "traversal-output"

        result = self.validate(malicious, checksum, output)

        self.assertEqual(2, result.returncode)
        self.assertIn("traversal component", result.stderr)
        self.assertFalse((self.root / "escape.mdc").exists())
        self.assertFalse(output.exists())

    def test_validate_rejects_duplicate_keys_and_case_collisions(self) -> None:
        duplicate = self.root / "duplicate.json"
        duplicate_raw = b'{"schema":"one","schema":"two"}\n'
        duplicate.write_bytes(duplicate_raw)
        duplicate_result = self.validate(
            duplicate, digest(duplicate_raw), self.root / "duplicate-output"
        )
        self.assertEqual(2, duplicate_result.returncode)
        self.assertIn("duplicate JSON key", duplicate_result.stderr)

        self.pack()
        value = json.loads(self.package.read_bytes())
        second_unit = dict(value["local"]["manifest"]["units"][0])
        second_unit["path"] = "SPEC.mdc"
        second_unit["stable_transport_identity"] = "notion:" + "2" * 32
        second_unit["logical_contract_unit_id"] = "notion:" + "2" * 32
        value["local"]["manifest"]["units"].append(second_unit)
        malicious, checksum = self.write_package("case-collision.json", value)
        collision_result = self.validate(
            malicious, checksum, self.root / "case-output"
        )
        self.assertEqual(2, collision_result.returncode)
        self.assertIn("path collision", collision_result.stderr)

    def test_validate_recomputes_dual_hashes_instead_of_trusting_package(self) -> None:
        self.pack()
        value = json.loads(self.package.read_bytes())
        value["local"]["hash_result"]["contract_digest"] = "sha256:" + "0" * 64
        tampered, checksum = self.write_package("tampered-hash.json", value)

        result = self.validate(tampered, checksum, self.root / "tampered-output")

        self.assertEqual(2, result.returncode)
        self.assertIn("recomputed local dual-hash evidence", result.stderr)

    def test_pack_rejects_a_base_receipt_for_different_bytes(self) -> None:
        self.base_receipt.write_bytes(
            canonical(
                {
                    "contract_digest": "sha256:" + "a" * 64,
                    "hash_model": "specification-dual-hash-v1",
                    "schema": "spec-materialization-receipt/v1",
                    "transport_manifest_hash": "sha256:" + "b" * 64,
                }
            )
        )

        result = self.run_cli(
            "pack",
            "--base-root",
            str(self.base_root),
            "--base-manifest",
            str(self.base_manifest),
            "--base-receipt",
            str(self.base_receipt),
            "--local-root",
            str(self.local_root),
            "--local-manifest",
            str(self.local_manifest),
            "--spec-hash-helper",
            str(SPEC_HASHES.resolve()),
            "--output",
            str(self.package),
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("do not describe bundled Base", result.stderr)
        self.assertFalse(self.package.exists())

    def test_pack_rejects_symlinks_and_origin_paths_in_base_receipt(self) -> None:
        origin_receipt = self.root / "origin-receipt.json"
        origin_receipt.write_bytes(canonical({"mirror": "/Users/alice/project/mirror"}))
        self.base_receipt = origin_receipt
        origin_result = self.run_cli(
            "pack",
            "--base-root",
            str(self.base_root),
            "--base-manifest",
            str(self.base_manifest),
            "--base-receipt",
            str(self.base_receipt),
            "--local-root",
            str(self.local_root),
            "--local-manifest",
            str(self.local_manifest),
            "--spec-hash-helper",
            str(SPEC_HASHES.resolve()),
            "--output",
            str(self.package),
        )
        self.assertEqual(2, origin_result.returncode)
        self.assertIn("origin absolute path", origin_result.stderr)

        self.base_receipt = self.root / "base-receipt-safe.json"
        self.base_receipt.write_bytes(self.base_receipt_bytes)
        outside = self.root / "outside.mdc"
        outside.write_bytes(self.local_bytes)
        (self.local_root / "spec.mdc").unlink()
        (self.local_root / "spec.mdc").symlink_to(outside)
        symlink_result = self.run_cli(
            "pack",
            "--base-root",
            str(self.base_root),
            "--base-manifest",
            str(self.base_manifest),
            "--base-receipt",
            str(self.base_receipt),
            "--local-root",
            str(self.local_root),
            "--local-manifest",
            str(self.local_manifest),
            "--spec-hash-helper",
            str(SPEC_HASHES.resolve()),
            "--output",
            str(self.package),
        )
        self.assertEqual(2, symlink_result.returncode)
        self.assertIn("symlink component", symlink_result.stderr)


if __name__ == "__main__":
    unittest.main()
