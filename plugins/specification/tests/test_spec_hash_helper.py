from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
HELPER = PLUGIN / "skills/sync-spec/scripts/spec-hashes.py"


class SpecificationHashHelperTest(unittest.TestCase):
    def _manifest(
        self,
        *,
        kind: str,
        identity: str,
        logical_id: str,
        path: str = "contract.md",
        revision: str = "",
        lineage: str,
    ) -> dict[str, object]:
        return {
            "schema": "spec-hash-input-v1",
            "units": [
                {
                    "carrier_kind": kind,
                    "stable_transport_identity": identity,
                    "logical_contract_unit_id": logical_id,
                    "path": path,
                    "observed_revision": revision,
                    "semantic_lineage": lineage,
                }
            ],
        }

    def _run(
        self,
        root: Path,
        manifest: dict[str, object],
        *,
        kind: str = "both",
        manifest_arg: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        manifest_path = root / "input.json"
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return subprocess.run(
            [
                "python3",
                str(HELPER),
                "--root",
                str(root.resolve()),
                "--manifest",
                manifest_arg or str(manifest_path.resolve()),
                "--kind",
                kind,
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=root,
        )

    def test_local_hash_is_deterministic_and_returns_portable_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            contract = root / "contract.md"
            original = b"# Contract\n\nExact bytes.\n"
            contract.write_bytes(original)
            manifest = self._manifest(
                kind="local-markdown",
                identity="repo:docs/source.md",
                logical_id="contract:root",
                lineage="local",
            )

            first = self._run(root, manifest)
            second = self._run(root, manifest)

            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(original, contract.read_bytes())
            result = json.loads(first.stdout)
            self.assertEqual("specification-dual-hash-v1", result["hash_model"])
            self.assertRegex(result["transport_manifest_hash"], r"^sha256:[0-9a-f]{64}$")
            self.assertRegex(result["contract_digest"], r"^sha256:[0-9a-f]{64}$")
            self.assertRegex(result["transport_manifest_key"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                "sha256:f1f569a561a15cc04935f43e627e8a28dc647ebde0a2ac332514a2cbbde57bf7",
                result["transport_manifest_hash"],
            )
            self.assertEqual(
                "sha256:5baef69e9271e1e16f2f0411be887bce6ff608647a20c0449fbd5b58720d59c1",
                result["contract_digest"],
            )
            self.assertEqual(
                result["transport_manifest_hash"].removeprefix("sha256:"),
                result["transport_manifest_key"],
            )

    def test_transport_and_semantic_kinds_can_be_verified_independently(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "contract.md").write_text("# Contract\n", encoding="utf-8")
            manifest = self._manifest(
                kind="inline-markdown",
                identity="inline-approved:sha256:" + "a" * 64,
                logical_id="contract:root",
                lineage="inline",
            )

            transport = json.loads(self._run(root, manifest, kind="transport").stdout)
            semantic = json.loads(self._run(root, manifest, kind="semantic").stdout)

            self.assertIn("transport_manifest_hash", transport)
            self.assertIn("transport_manifest_key", transport)
            self.assertNotIn("contract_digest", transport)
            self.assertIn("contract_digest", semantic)
            self.assertNotIn("transport_manifest_hash", semantic)

    def test_notion_revision_line_is_the_only_excluded_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            contract = root / "contract.md"
            manifest = self._manifest(
                kind="notion-mdc",
                identity="notion:" + "1" * 32,
                logical_id="notion:" + "1" * 32,
                revision="r1",
                lineage="notion",
            )
            contract.write_bytes(
                b"---\ntitle: Contract\nlast_edited_time: r1\nref: stable\n---\n# Body\n"
            )
            first = json.loads(self._run(root, manifest).stdout)

            contract.write_bytes(
                b"---\ntitle: Contract\nlast_edited_time: r2\nref: stable\n---\n# Body\n"
            )
            manifest["units"][0]["observed_revision"] = "r2"  # type: ignore[index]
            second = json.loads(self._run(root, manifest).stdout)

            self.assertNotEqual(first["transport_manifest_hash"], second["transport_manifest_hash"])
            self.assertEqual(first["contract_digest"], second["contract_digest"])

            contract.write_bytes(
                b"---\ntitle: Changed\nlast_edited_time: r2\nref: stable\n---\n# Body\n"
            )
            third = json.loads(self._run(root, manifest).stdout)
            self.assertNotEqual(second["contract_digest"], third["contract_digest"])

    def test_path_rename_is_not_detectable_from_semantic_digest_alone(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            content = b"---\nlast_edited_time: r1\nref: stable\n---\n# Body\n"
            (root / "before.mdc").write_bytes(content)
            before_manifest = self._manifest(
                kind="notion-mdc",
                identity="notion:" + "7" * 32,
                logical_id="notion:" + "7" * 32,
                path="before.mdc",
                revision="r1",
                lineage="notion",
            )
            before = json.loads(self._run(root, before_manifest).stdout)

            (root / "before.mdc").rename(root / "after.mdc")
            after_manifest = self._manifest(
                kind="notion-mdc",
                identity="notion:" + "7" * 32,
                logical_id="notion:" + "7" * 32,
                path="after.mdc",
                revision="r1",
                lineage="notion",
            )
            after = json.loads(self._run(root, after_manifest).stdout)

            self.assertEqual(before["contract_digest"], after["contract_digest"])
            self.assertNotEqual(
                before["transport_manifest_hash"], after["transport_manifest_hash"]
            )
            self.assertNotEqual(before["units"][0]["path"], after["units"][0]["path"])

    def test_local_line_named_last_edited_time_remains_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            contract = root / "contract.md"
            manifest = self._manifest(
                kind="local-markdown",
                identity="repo:docs/source.md",
                logical_id="contract:root",
                lineage="local",
            )
            contract.write_text("---\nlast_edited_time: one\n---\n# Body\n", encoding="utf-8")
            first = json.loads(self._run(root, manifest).stdout)
            contract.write_text("---\nlast_edited_time: two\n---\n# Body\n", encoding="utf-8")
            second = json.loads(self._run(root, manifest).stdout)
            self.assertNotEqual(first["contract_digest"], second["contract_digest"])

    def test_ambiguous_or_non_scalar_volatile_metadata_is_rejected(self) -> None:
        manifest = self._manifest(
            kind="notion-mdc",
            identity="notion:" + "2" * 32,
            logical_id="notion:" + "2" * 32,
            revision="r1",
            lineage="notion",
        )
        invalid_contents = (
            b"---\nlast_edited_time: one\nlast_edited_time: two\n---\n# Body\n",
            b"---\nlast_edited_time: |\n  multiline\n---\n# Body\n",
            b"---\nlast_edited_time:\n---\n# Body\n",
        )
        for content in invalid_contents:
            with self.subTest(content=content):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir).resolve()
                    (root / "contract.md").write_bytes(content)
                    result = self._run(root, manifest)
                    self.assertEqual(2, result.returncode)
                    self.assertIn("spec-hashes: invalid", result.stderr)

    def test_manifest_and_carrier_boundaries_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            contract = root / "contract.md"
            contract.write_text("# Contract\n", encoding="utf-8")
            manifest = self._manifest(
                kind="local-markdown",
                identity="repo:docs/source.md",
                logical_id="contract:root",
                lineage="local",
            )

            relative_manifest = self._run(root, manifest, manifest_arg="input.json")
            self.assertEqual(2, relative_manifest.returncode)
            self.assertIn("--manifest must be absolute", relative_manifest.stderr)

            outside = root.parent / f"{root.name}-outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            try:
                contract.unlink()
                contract.symlink_to(outside)
                symlinked_file = self._run(root, manifest)
                self.assertEqual(2, symlinked_file.returncode)
                self.assertIn("symlink component is forbidden", symlinked_file.stderr)
            finally:
                outside.unlink(missing_ok=True)

    def test_root_symlink_component_and_logical_id_remap_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            container = Path(temp_dir).resolve()
            root = container / "real"
            root.mkdir()
            (root / "contract.md").write_text("# Contract\n", encoding="utf-8")
            manifest = self._manifest(
                kind="local-markdown",
                identity="repo:docs/source.md",
                logical_id="arbitrary",
                lineage="local",
            )
            remapped = self._run(root, manifest)
            self.assertEqual(2, remapped.returncode)
            self.assertIn("must be contract:root", remapped.stderr)

            manifest["units"][0]["logical_contract_unit_id"] = "contract:root"  # type: ignore[index]
            alias = container / "alias"
            alias.symlink_to(root, target_is_directory=True)
            manifest_path = root / "input.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            symlink_root = subprocess.run(
                [
                    "python3",
                    str(HELPER),
                    "--root",
                    str(alias),
                    "--manifest",
                    str(manifest_path.resolve()),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, symlink_root.returncode)
            self.assertIn("symlink component is forbidden in --root", symlink_root.stderr)

    def test_duplicate_json_keys_and_duplicate_identities_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            (root / "one.md").write_text("# One\n", encoding="utf-8")
            (root / "two.md").write_text("# Two\n", encoding="utf-8")
            manifest_path = root / "input.json"
            manifest_path.write_text(
                '{"schema":"spec-hash-input-v1","schema":"spec-hash-input-v1","units":[]}\n',
                encoding="utf-8",
            )
            duplicate_key = subprocess.run(
                [
                    "python3",
                    str(HELPER),
                    "--root",
                    str(root),
                    "--manifest",
                    str(manifest_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, duplicate_key.returncode)
            self.assertIn("duplicate JSON key", duplicate_key.stderr)

            identity = "repo:docs/shared.md"
            units = []
            for path in ("one.md", "two.md"):
                units.append(
                    {
                        "carrier_kind": "local-markdown",
                        "stable_transport_identity": identity,
                        "logical_contract_unit_id": f"contract-unit:{path}",
                        "path": path,
                        "observed_revision": "",
                        "semantic_lineage": "local",
                    }
                )
            duplicate_identity = self._run(
                root,
                {"schema": "spec-hash-input-v1", "units": units},
            )
            self.assertEqual(2, duplicate_identity.returncode)
            self.assertIn("duplicate stable_transport_identity", duplicate_identity.stderr)


if __name__ == "__main__":
    unittest.main()
