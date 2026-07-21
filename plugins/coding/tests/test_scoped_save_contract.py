from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
VALIDATOR = PLUGIN / "skills/commit/scripts/validate-scoped-save.sh"


class ScopedSaveValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "target"
        self.repo.mkdir()
        self.repo = self.repo.resolve()
        self.git("init", "-q")
        self.git("config", "user.name", "Scoped Save Test")
        self.git("config", "user.email", "scoped-save@example.test")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.filemode", "true")

        files = {
            ".gitignore": ".engineering/\n",
            "src.txt": "source base\n",
            "tests.txt": "test base\n",
            "docs/specs/capability/index.md": "spec base\n",
            "docs/specs/capability/provenance.json": "{}\n",
            "developer.txt": "developer base\n",
        }
        for relative, content in files.items():
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "chore: initialize target")
        self.base_rev = self.git("rev-parse", "HEAD").stdout.strip()
        self.work_root = self.repo / ".engineering/works/scoped-save"
        self.work_root.mkdir(parents=True)

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def git_bytes(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def helper(self, *args: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            ["bash", str(VALIDATOR), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if check and result.returncode:
            self.fail(f"validator failed ({result.returncode}): {result.stdout}\n{result.stderr}")
        return result, json.loads(result.stdout)

    def scope(self, publication: list[tuple[str, str]], selected: list[str]) -> Path:
        scope = self.work_root / "evidence/history/scope-request.json"
        scope.parent.mkdir(parents=True, exist_ok=True)
        child_manifest = self.work_root / "evidence/children/coding.json"
        child_manifest.parent.mkdir(parents=True, exist_ok=True)
        generated_files = []
        for relative, _ in publication:
            path = self.repo / relative
            if path.is_symlink():
                state = "symlink"
                content_hash = hashlib.sha256(path.readlink().as_posix().encode()).hexdigest()
                mode = "120000"
            elif path.is_file():
                state = "file"
                content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            else:
                state = "deleted"
                content_hash = None
                mode = None
            generated_files.append(
                {"path": relative, "state": state, "sha256": content_hash, "mode": mode}
            )
        child_manifest.write_text(
            json.dumps(
                {
                    "schema": "engineering-work-generated-files/v1",
                    "producer": "coding:test-fixture",
                    "base_rev": self.base_rev,
                    "generated_files": generated_files,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        scope.write_text(
            json.dumps(
                {
                    "schema": "engineering-work-scoped-save-request/v1",
                    "work_id": "scoped-save",
                    "scope_complete": True,
                    "publication_paths": [
                        {"path": path, "origin": origin} for path, origin in publication
                    ],
                    "selected_paths": selected,
                    "generated_file_manifests": [
                        ".engineering/works/scoped-save/evidence/children/coding.json"
                    ],
                }
            ),
            encoding="utf-8",
        )
        return scope

    def build(self, scope: Path) -> dict[str, object]:
        _, output = self.helper(
            "build",
            "--repo",
            str(self.repo),
            "--work-root",
            str(self.work_root),
            "--base-rev",
            self.base_rev,
            "--scope",
            str(scope),
        )
        return output

    def preflight(self, manifest: dict[str, object]) -> dict[str, object]:
        _, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
        )
        return output

    def commit_selected(self, preflight: dict[str, object], message: str) -> str:
        self.git(
            "commit",
            "--only",
            f"--pathspec-from-file={preflight['literal_pathspec_file']}",
            "--pathspec-file-nul",
            "-m",
            message,
        )
        return self.git("rev-parse", "HEAD").stdout.strip()

    def verify(
        self,
        manifest: dict[str, object],
        preflight: dict[str, object],
        saved_rev: str,
    ) -> dict[str, object]:
        _, output = self.helper(
            "verify",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            str(preflight["snapshot_path"]),
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--saved-rev",
            saved_rev,
        )
        return output

    def test_real_path_limited_save_preserves_unrelated_index_and_worktree(self) -> None:
        selected = [
            "src.txt",
            "tests.txt",
            "docs/specs/capability/index.md",
            "docs/specs/capability/provenance.json",
        ]
        for relative in selected:
            path = self.repo / relative
            path.write_text(path.read_text(encoding="utf-8") + "lifecycle edit\n", encoding="utf-8")
        (self.repo / "src.txt").chmod(0o755)

        developer = self.repo / "developer.txt"
        developer.write_text("developer staged\n", encoding="utf-8")
        self.git("add", "developer.txt")
        staged_before = self.git("show", ":developer.txt").stdout
        developer.write_text("developer unstaged after staged\n", encoding="utf-8")
        worktree_before = developer.read_bytes()

        scope = self.scope(
            [(path, f"child-manifest:{path}") for path in selected], selected
        )
        manifest = self.build(scope)
        manifest_json = json.loads(Path(str(manifest["manifest_path"])).read_text(encoding="utf-8"))
        self.assertEqual(set(selected), {entry["path"] for entry in manifest_json["publication_paths"]})
        self.assertEqual(
            "100755",
            next(entry for entry in manifest_json["selected_paths"] if entry["path"] == "src.txt")["mode"],
        )
        self.assertEqual({"developer.txt"}, {entry["path"] for entry in manifest_json["excluded_dirty_paths"]})

        preflight = self.preflight(manifest)
        saved = self.commit_selected(preflight, "feat: save lifecycle scope")

        self.assertEqual(staged_before, self.git("show", ":developer.txt").stdout)
        self.assertEqual(worktree_before, developer.read_bytes())
        result = self.verify(manifest, preflight, saved)
        self.assertTrue(result["non_selected_preserved"])
        self.assertEqual("pass", result["status"])
        self.assertEqual(result["receipt_path"], self.verify(manifest, preflight, saved)["receipt_path"])

    def test_exact_scoped_rename_records_and_saves_source_and_destination(self) -> None:
        self.git("mv", "src.txt", "renamed-src.txt")
        publication = [
            ("src.txt", "child-manifest:rename-source"),
            ("renamed-src.txt", "child-manifest:rename-destination"),
        ]
        selected = ["src.txt", "renamed-src.txt"]
        manifest = self.build(self.scope(publication, selected))
        manifest_json = json.loads(Path(str(manifest["manifest_path"])).read_text(encoding="utf-8"))
        selected_entries = {entry["path"]: entry for entry in manifest_json["selected_paths"]}
        self.assertEqual("deleted", selected_entries["src.txt"]["state"])
        self.assertEqual("file", selected_entries["renamed-src.txt"]["state"])
        self.assertIn("role=source", selected_entries["src.txt"]["status"])
        self.assertIn("role=destination", selected_entries["renamed-src.txt"]["status"])

        preflight = self.preflight(manifest)
        saved = self.commit_selected(preflight, "refactor: rename source")
        result = self.verify(manifest, preflight, saved)
        self.assertTrue(result["non_selected_preserved"])

    def test_preflight_rejects_stale_selected_bytes(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(self.scope([("src.txt", "child-manifest:source")], ["src.txt"]))
        (self.repo / "src.txt").write_text("changed after review\n", encoding="utf-8")
        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertEqual("blocked_scope", output["status"])
        self.assertIn("stale", str(output["error"]))

    def test_preflight_rejects_duplicate_keys_even_with_matching_filename_hash(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(self.scope([("src.txt", "child-manifest:source")], ["src.txt"]))
        original = Path(str(manifest["manifest_path"])).read_bytes()
        duplicate = original.replace(b'"base_rev":', b'"base_rev":"duplicate","base_rev":', 1)
        digest = hashlib.sha256(duplicate).hexdigest()
        duplicate_path = Path(str(manifest["manifest_path"])).parent / f"{digest}.json"
        duplicate_path.write_bytes(duplicate)

        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(duplicate_path),
            "--manifest-sha256",
            digest,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("duplicate JSON key", str(output["error"]))

    def test_preflight_rejects_unknown_manifest_fields(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(self.scope([("src.txt", "child-manifest:source")], ["src.txt"]))
        value = json.loads(Path(str(manifest["manifest_path"])).read_text(encoding="utf-8"))
        value["unexpected"] = True
        raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        digest = hashlib.sha256(raw).hexdigest()
        unknown_path = Path(str(manifest["manifest_path"])).parent / f"{digest}.json"
        unknown_path.write_bytes(raw)
        result, output = self.helper(
            "preflight", "--repo", str(self.repo), "--manifest", str(unknown_path),
            "--manifest-sha256", digest, check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("unknown=['unexpected']", str(output["error"]))

    def test_verify_rejects_snapshot_mutation(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(self.scope([("src.txt", "child-manifest:source")], ["src.txt"]))
        preflight = self.preflight(manifest)
        saved = self.commit_selected(preflight, "feat: save source")
        snapshot = Path(str(preflight["snapshot_path"]))
        snapshot.chmod(0o644)
        snapshot.write_bytes(snapshot.read_bytes() + b" ")

        result, output = self.helper(
            "verify",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            str(snapshot),
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--saved-rev",
            saved,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("snapshot", str(output["error"]))

    def test_verify_rejects_an_intervening_plain_git_commit(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(self.scope([("src.txt", "child-manifest:source")], ["src.txt"]))
        preflight = self.preflight(manifest)
        saved = self.commit_selected(preflight, "feat: save source")

        (self.repo / "developer.txt").write_text("concurrent commit\n", encoding="utf-8")
        self.git("add", "developer.txt")
        self.git("commit", "-m", "chore: concurrent developer commit")
        result, output = self.helper(
            "verify",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            str(preflight["snapshot_path"]),
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--saved-rev",
            saved,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("current HEAD no longer equals", str(output["error"]))

    def test_cli_evidence_paths_reject_lexical_traversal_before_access(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        scope = self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        escaped_scope = f"{scope.parent}/nested/../{scope.name}"
        result, output = self.helper(
            "build",
            "--repo",
            str(self.repo),
            "--work-root",
            str(self.work_root),
            "--base-rev",
            self.base_rev,
            "--scope",
            escaped_scope,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("--scope contains lexical traversal", str(output["error"]))

        manifest = self.build(scope)
        manifest_path = Path(str(manifest["manifest_path"]))
        escaped_manifest = f"{manifest_path.parent}/nested/../{manifest_path.name}"
        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            escaped_manifest,
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("--manifest contains lexical traversal", str(output["error"]))

        preflight = self.preflight(manifest)
        saved = self.commit_selected(preflight, "feat: save source")
        snapshot_path = Path(str(preflight["snapshot_path"]))
        escaped_snapshot = f"{snapshot_path.parent}/nested/../{snapshot_path.name}"
        result, output = self.helper(
            "verify",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest_path),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            escaped_snapshot,
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--saved-rev",
            saved,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("--snapshot contains lexical traversal", str(output["error"]))

    def test_generated_evidence_pointer_rejects_lexical_traversal(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        scope = self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        request = json.loads(scope.read_text(encoding="utf-8"))
        request["generated_file_manifests"] = ["evidence/children/nested/../coding.json"]
        scope.write_text(json.dumps(request), encoding="utf-8")
        result, output = self.helper(
            "build",
            "--repo",
            str(self.repo),
            "--work-root",
            str(self.work_root),
            "--base-rev",
            self.base_rev,
            "--scope",
            str(scope),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("not lexically normalized", str(output["error"]))

    def test_build_rejects_assume_unchanged_and_skip_worktree_flags(self) -> None:
        for flag, clear_flag in (
            ("--assume-unchanged", "--no-assume-unchanged"),
            ("--skip-worktree", "--no-skip-worktree"),
        ):
            with self.subTest(flag=flag):
                (self.repo / "src.txt").write_text(
                    f"lifecycle edit hidden by {flag}\n", encoding="utf-8"
                )
                self.git("update-index", flag, "src.txt")
                scope = self.scope(
                    [("src.txt", "child-manifest:source")], ["src.txt"]
                )
                result, output = self.helper(
                    "build",
                    "--repo",
                    str(self.repo),
                    "--work-root",
                    str(self.work_root),
                    "--base-rev",
                    self.base_rev,
                    "--scope",
                    str(scope),
                    check=False,
                )
                self.assertEqual(2, result.returncode)
                self.assertIn("index flag makes scoped proof ambiguous", str(output["error"]))
                self.git("update-index", clear_flag, "src.txt")
                (self.repo / "src.txt").write_text("source base\n", encoding="utf-8")

    def test_build_rejects_mode_hidden_by_core_filemode_false(self) -> None:
        (self.repo / "src.txt").chmod(0o755)
        self.git("config", "core.filemode", "false")
        scope = self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        result, output = self.helper(
            "build",
            "--repo",
            str(self.repo),
            "--work-root",
            str(self.work_root),
            "--base-rev",
            self.base_rev,
            "--scope",
            str(scope),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("core.filemode=false", str(output["error"]))
        self.assertIn("preservation ambiguous", str(output["error"]))

    def test_preflight_rejects_history_change_after_manifest_seal(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(
            self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        )
        (self.repo / "developer.txt").write_text("history writer\n", encoding="utf-8")
        self.git("add", "developer.txt")
        self.git("commit", "-q", "-m", "chore: concurrent history writer")

        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("HEAD changed after scoped manifest sealing", str(output["error"]))

    def test_preflight_rejects_mutated_producer_receipt(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(
            self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        )
        receipt_path = self.work_root / "evidence/children/coding.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["producer"] = "coding:mutated-after-seal"
        receipt_path.write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("bindings changed after sealing", str(output["error"]))

    def test_build_rejects_producer_omission_from_publication_scope(self) -> None:
        for relative in ("src.txt", "tests.txt"):
            (self.repo / relative).write_text("lifecycle edit\n", encoding="utf-8")
        scope = self.scope(
            [
                ("src.txt", "child-manifest:source"),
                ("tests.txt", "child-manifest:tests"),
            ],
            ["src.txt", "tests.txt"],
        )
        receipt_path = self.work_root / "evidence/children/coding.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["generated_files"] = [
            entry for entry in receipt["generated_files"] if entry["path"] == "src.txt"
        ]
        receipt_path.write_text(
            json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

        result, output = self.helper(
            "build",
            "--repo",
            str(self.repo),
            "--work-root",
            str(self.work_root),
            "--base-rev",
            self.base_rev,
            "--scope",
            str(scope),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("generated_files must equal publication scope exactly", str(output["error"]))
        self.assertIn("tests.txt", str(output["error"]))

    def test_recover_restores_exact_preflight_head_and_index(self) -> None:
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        developer = self.repo / "developer.txt"
        developer.write_text("developer staged\n", encoding="utf-8")
        self.git("add", "developer.txt")
        developer.write_text("developer unstaged\n", encoding="utf-8")

        manifest = self.build(
            self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        )
        preflight = self.preflight(manifest)
        index_path = Path(self.git("rev-parse", "--git-path", "index").stdout.strip())
        if not index_path.is_absolute():
            index_path = self.repo / index_path
        index_before = index_path.read_bytes()
        status_before = self.git_bytes(
            "status",
            "--porcelain=v2",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        ).stdout
        src_before = (self.repo / "src.txt").read_bytes()
        developer_before = developer.read_bytes()
        old_head = self.git("rev-parse", "HEAD").stdout.strip()
        self.git("commit", "-q", "-a", "-m", "feat: faulty save captures extra path")
        saved = self.git("rev-parse", "HEAD").stdout.strip()

        failed_verify, failed_output = self.helper(
            "verify",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            str(preflight["snapshot_path"]),
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--saved-rev",
            saved,
            check=False,
        )
        self.assertEqual(2, failed_verify.returncode)
        self.assertIn("dirty path set changed", str(failed_output["error"]))

        _, recovery = self.helper(
            "recover",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            "--snapshot",
            str(preflight["snapshot_path"]),
            "--snapshot-sha256",
            str(preflight["snapshot_sha256"]),
            "--failed-head",
            saved,
        )
        self.assertEqual("recovered", recovery["status"])
        self.assertEqual(old_head, self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual(index_before, index_path.read_bytes())
        self.assertEqual(src_before, (self.repo / "src.txt").read_bytes())
        self.assertEqual(developer_before, developer.read_bytes())
        self.assertEqual(
            status_before,
            self.git_bytes(
                "status",
                "--porcelain=v2",
                "-z",
                "--untracked-files=all",
                "--ignore-submodules=none",
            ).stdout,
        )

    def test_preflight_blocks_selected_clean_filter_before_history_mutation(self) -> None:
        self.git("config", "filter.upper.clean", "tr '[:lower:]' '[:upper:]'")
        self.git("config", "filter.upper.smudge", "cat")
        (self.repo / ".gitattributes").write_text("src.txt filter=upper\n", encoding="utf-8")
        self.git("add", ".gitattributes")
        self.git("commit", "-q", "-m", "chore: configure clean filter")
        self.base_rev = self.git("rev-parse", "HEAD").stdout.strip()
        (self.repo / "src.txt").write_text("lifecycle edit\n", encoding="utf-8")
        manifest = self.build(
            self.scope([("src.txt", "child-manifest:source")], ["src.txt"])
        )
        head_before = self.git("rev-parse", "HEAD").stdout.strip()

        result, output = self.helper(
            "preflight",
            "--repo",
            str(self.repo),
            "--manifest",
            str(manifest["manifest_path"]),
            "--manifest-sha256",
            str(manifest["manifest_sha256"]),
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("Git clean transform", str(output["error"]))
        self.assertEqual(head_before, self.git("rev-parse", "HEAD").stdout.strip())

    def test_jj_contract_is_structural_operation_pinned_and_fail_closed(self) -> None:
        source = (PLUGIN / "skills/commit/scripts/validate_scoped_save.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"git",\n                "root"', source)
        self.assertIn('"--ignore-working-copy"', source)
        self.assertIn('command.extend(["--at-operation", at_operation])', source)
        self.assertIn('"diff-index", "--cached", "--quiet", "HEAD", "--"', source)
        self.assertLess(
            source.index('staged = run_git(repo, "diff-index"'),
            source.index('run_jj(repo, "status")'),
        )
        self.assertIn('"working_copy_commit_id"', source)
        self.assertIn('"working_copy_change_id"', source)
        self.assertIn('"parent_commit_ids"', source)
        self.assertIn("require_jj_scoped_save_capabilities", source)
        self.assertIn("installed jj lacks required scoped-save capability", source)
        self.assertIn("jj saved change parents differ", source)
        self.assertIn("jj current operation does not contain the exact saved commit", source)


if __name__ == "__main__":
    unittest.main()
