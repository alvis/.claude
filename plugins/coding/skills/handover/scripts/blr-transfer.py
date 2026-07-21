#!/usr/bin/env python3
"""Pack and validate deterministic portable Notion Base/Local evidence."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import unicodedata
from typing import Any


SCHEMA = "specification-blr-transfer+json/v1"
HASH_MODEL = "specification-dual-hash-v1"
HASH_IMPLEMENTATION = "plugin:specification/sync-spec/scripts/spec-hashes.py"
MANIFEST_SCHEMA = "spec-hash-input-v1"
HASH_RESULT_SCHEMA = "spec-dual-hash-result-v1"
SHA256_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
WINDOWS_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/]")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
UNIT_KEYS = {
    "carrier_kind",
    "stable_transport_identity",
    "logical_contract_unit_id",
    "path",
    "observed_revision",
    "semantic_lineage",
}
HASH_UNIT_KEYS = UNIT_KEYS | {"exact_file_sha256", "semantic_projection_sha256"}


class ContractError(ValueError):
    """Raised when a transfer has no single safe interpretation."""


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number: {value}")


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def parse_json(raw: bytes, label: str, *, require_canonical: bool) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ContractError(f"{label} is not strict UTF-8: {error}") from error
    if raw.startswith(b"\xef\xbb\xbf") or b"\x00" in raw or b"\r" in raw:
        raise ContractError(f"{label} must be BOM-free, NUL-free UTF-8 with LF line endings")
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except (json.JSONDecodeError, ContractError) as error:
        raise ContractError(f"invalid {label}: {error}") from error
    if require_canonical and raw != canonical_json(value):
        raise ContractError(f"{label} is not canonical JSON with one final LF")
    return value


def require_mapping(value: Any, label: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ContractError(f"{label} must contain exactly {sorted(keys)}")
    return value


def require_text(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        qualifier = "possibly empty " if allow_empty else ""
        raise ContractError(f"{label} must be a {qualifier}string")
    if CONTROL_RE.search(value):
        raise ContractError(f"{label} contains a control character")
    if unicodedata.normalize("NFC", value) != value:
        raise ContractError(f"{label} must already be NFC")
    return value


def require_sha256(value: Any, label: str) -> str:
    text = require_text(value, label)
    if SHA256_RE.fullmatch(text) is None:
        raise ContractError(f"{label} must be sha256:<64-lowercase-hex>")
    return text


def portable_path(value: Any, label: str) -> str:
    text = require_text(value, label)
    if "\\" in text or text.startswith("/"):
        raise ContractError(f"{label} is not a portable relative POSIX path: {text}")
    pure = PurePosixPath(text)
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise ContractError(f"{label} contains an empty/dot/traversal component: {text}")
    if pure.as_posix() != text:
        raise ContractError(f"{label} is not canonical POSIX form: {text}")
    return text


def reject_case_collisions(paths: list[str], label: str) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        folded = path.casefold()
        if folded in seen:
            raise ContractError(f"{label} path collision: {seen[folded]} and {path}")
        seen[folded] = path


def require_safe_existing(path: Path, label: str, *, directory: bool) -> Path:
    if not path.is_absolute():
        raise ContractError(f"{label} must be absolute")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise ContractError(f"cannot inspect {label}: {error}") from error
        if stat.S_ISLNK(mode):
            raise ContractError(f"symlink component is forbidden in {label}: {current}")
    final_mode = path.lstat().st_mode
    if directory and not stat.S_ISDIR(final_mode):
        raise ContractError(f"{label} must be a directory")
    if not directory and not stat.S_ISREG(final_mode):
        raise ContractError(f"{label} must be a regular file")
    return path.resolve(strict=True)


def require_new_path(path: Path, label: str) -> Path:
    if not path.is_absolute():
        raise ContractError(f"{label} must be absolute")
    if path.exists() or path.is_symlink():
        raise ContractError(f"{label} must not already exist")
    require_safe_existing(path.parent, f"{label} parent", directory=True)
    return path


def read_regular(path: Path, label: str) -> bytes:
    safe = require_safe_existing(path, label, directory=False)
    try:
        return safe.read_bytes()
    except OSError as error:
        raise ContractError(f"cannot read {label}: {error}") from error


def resolve_unit(root: Path, relative: str, label: str) -> Path:
    current = root
    for component in PurePosixPath(relative).parts:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise ContractError(f"cannot inspect {label} {relative}: {error}") from error
        if stat.S_ISLNK(mode):
            raise ContractError(f"symlink component is forbidden in {label}: {relative}")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise ContractError(f"{label} unit is not a regular file: {relative}")
    try:
        current.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as error:
        raise ContractError(f"{label} unit escapes its root: {relative}") from error
    return current


def validate_manifest(value: Any, label: str) -> dict[str, Any]:
    manifest = require_mapping(value, label, {"schema", "units"})
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise ContractError(f"{label}.schema must be {MANIFEST_SCHEMA}")
    units = manifest["units"]
    if not isinstance(units, list) or not units:
        raise ContractError(f"{label}.units must be a non-empty array")
    paths: list[str] = []
    identities: set[str] = set()
    logical_ids: set[str] = set()
    for index, raw_unit in enumerate(units):
        unit = require_mapping(raw_unit, f"{label}.units[{index}]", UNIT_KEYS)
        for key in UNIT_KEYS:
            require_text(
                unit[key],
                f"{label}.units[{index}].{key}",
                allow_empty=key == "observed_revision",
            )
        path = portable_path(unit["path"], f"{label}.units[{index}].path")
        identity = unit["stable_transport_identity"]
        logical_id = unit["logical_contract_unit_id"]
        if path in paths:
            raise ContractError(f"duplicate manifest path: {path}")
        if identity in identities:
            raise ContractError(f"duplicate stable transport identity: {identity}")
        if logical_id in logical_ids:
            raise ContractError(f"duplicate logical contract unit id: {logical_id}")
        paths.append(path)
        identities.add(identity)
        logical_ids.add(logical_id)
    reject_case_collisions(paths, f"{label}.units")
    return manifest


def validate_hash_result(value: Any, label: str, manifest: dict[str, Any]) -> dict[str, Any]:
    result = require_mapping(
        value,
        label,
        {
            "schema",
            "hash_model",
            "units",
            "transport_manifest_hash",
            "transport_manifest_key",
            "contract_digest",
        },
    )
    if result["schema"] != HASH_RESULT_SCHEMA or result["hash_model"] != HASH_MODEL:
        raise ContractError(f"{label} has an unsupported hash schema/model")
    transport_hash = require_sha256(
        result["transport_manifest_hash"], f"{label}.transport_manifest_hash"
    )
    require_sha256(result["contract_digest"], f"{label}.contract_digest")
    if result["transport_manifest_key"] != transport_hash.removeprefix("sha256:"):
        raise ContractError(f"{label}.transport_manifest_key does not match its hash")
    units = result["units"]
    if not isinstance(units, list):
        raise ContractError(f"{label}.units must be an array")
    manifest_paths = sorted(unit["path"] for unit in manifest["units"])
    result_paths: list[str] = []
    for index, raw_unit in enumerate(units):
        unit = require_mapping(raw_unit, f"{label}.units[{index}]", HASH_UNIT_KEYS)
        for key in UNIT_KEYS:
            require_text(
                unit[key],
                f"{label}.units[{index}].{key}",
                allow_empty=key == "observed_revision",
            )
        result_paths.append(portable_path(unit["path"], f"{label}.units[{index}].path"))
        require_sha256(unit["exact_file_sha256"], f"{label}.units[{index}].exact_file_sha256")
        require_sha256(
            unit["semantic_projection_sha256"],
            f"{label}.units[{index}].semantic_projection_sha256",
        )
    if result_paths != manifest_paths:
        raise ContractError(f"{label}.units do not match the manifest's sorted paths")
    return result


def file_entries(root: Path, manifest: dict[str, Any], label: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for relative in sorted(
        (unit["path"] for unit in manifest["units"]), key=lambda item: item.encode("utf-8")
    ):
        raw = read_regular(resolve_unit(root, relative, label), f"{label} unit {relative}")
        entries.append(
            {
                "content_base64": base64.b64encode(raw).decode("ascii"),
                "path": relative,
                "sha256": sha256(raw),
            }
        )
    return entries


def decode_file_entries(
    value: Any, manifest: dict[str, Any], label: str
) -> list[tuple[str, bytes]]:
    if not isinstance(value, list) or not value:
        raise ContractError(f"{label} must be a non-empty array")
    decoded: list[tuple[str, bytes]] = []
    paths: list[str] = []
    for index, raw_entry in enumerate(value):
        entry = require_mapping(
            raw_entry, f"{label}[{index}]", {"content_base64", "path", "sha256"}
        )
        path = portable_path(entry["path"], f"{label}[{index}].path")
        encoded = require_text(entry["content_base64"], f"{label}[{index}].content_base64")
        require_sha256(entry["sha256"], f"{label}[{index}].sha256")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ContractError(f"invalid base64 for {label}[{index}]: {error}") from error
        if base64.b64encode(raw).decode("ascii") != encoded:
            raise ContractError(f"non-canonical base64 for {label}[{index}]")
        if sha256(raw) != entry["sha256"]:
            raise ContractError(f"exact file checksum mismatch for {path}")
        paths.append(path)
        decoded.append((path, raw))
    if paths != sorted(paths, key=lambda item: item.encode("utf-8")):
        raise ContractError(f"{label} entries are not in raw UTF-8 path order")
    if len(set(paths)) != len(paths):
        raise ContractError(f"{label} contains duplicate paths")
    reject_case_collisions(paths, label)
    manifest_paths = sorted(
        (unit["path"] for unit in manifest["units"]), key=lambda item: item.encode("utf-8")
    )
    if paths != manifest_paths:
        raise ContractError(f"{label} paths do not exactly equal its manifest")
    return decoded


def reject_origin_paths(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            reject_origin_paths(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_origin_paths(child, f"{label}[{index}]")
    elif isinstance(value, str):
        if (
            value.startswith(("/", "\\", "~/", "file://"))
            or WINDOWS_ABSOLUTE_RE.match(value) is not None
        ):
            raise ContractError(f"origin absolute path is forbidden in {label}")


def validate_receipt(
    raw: bytes, expected_hashes: dict[str, Any] | None = None
) -> dict[str, Any]:
    value = parse_json(raw, "base receipt", require_canonical=False)
    if not isinstance(value, dict):
        raise ContractError("base receipt must be a JSON object")
    reject_origin_paths(value, "base receipt")
    if value.get("hash_model") != HASH_MODEL:
        raise ContractError(f"base receipt hash_model must be {HASH_MODEL}")
    receipt_transport = require_sha256(
        value.get("transport_manifest_hash"),
        "base receipt.transport_manifest_hash",
    )
    receipt_contract = require_sha256(
        value.get("contract_digest"), "base receipt.contract_digest"
    )
    if expected_hashes is not None and (
        receipt_transport != expected_hashes.get("transport_manifest_hash")
        or receipt_contract != expected_hashes.get("contract_digest")
    ):
        raise ContractError("base receipt dual hashes do not describe bundled Base")
    return value


def require_helper(path: Path) -> Path:
    return require_safe_existing(path, "--spec-hash-helper", directory=False)


def run_hash_helper(helper: Path, root: Path, manifest: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            str(helper),
            "--root",
            str(root),
            "--manifest",
            str(manifest),
            "--kind",
            "both",
        ],
        check=False,
        capture_output=True,
        text=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ContractError(f"Specification hash helper refused the carrier: {detail}")
    value = parse_json(completed.stdout, "Specification hash result", require_canonical=False)
    if not isinstance(value, dict):
        raise ContractError("Specification hash helper returned a non-object")
    return value


def write_new_file(path: Path, raw: bytes, label: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise ContractError(f"cannot create {label} without clobbering: {error}") from error
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise ContractError(f"cannot write {label}: {error}") from error


def create_output_root(path: Path) -> Path:
    require_new_path(path, "--output-root")
    try:
        os.mkdir(path, 0o700)
    except OSError as error:
        raise ContractError(f"cannot create isolated --output-root: {error}") from error
    return require_safe_existing(path, "--output-root", directory=True)


def ensure_relative_parent(root: Path, relative: str) -> None:
    current = root
    for component in PurePosixPath(relative).parts[:-1]:
        current = current / component
        try:
            os.mkdir(current, 0o700)
        except FileExistsError:
            pass
        except OSError as error:
            raise ContractError(f"cannot create isolated output directory: {error}") from error
        mode = current.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ContractError(f"unsafe component appeared in isolated output: {current}")


def materialize_files(root: Path, entries: list[tuple[str, bytes]], label: str) -> None:
    for relative, raw in entries:
        ensure_relative_parent(root, relative)
        write_new_file(root / relative, raw, f"{label} {relative}")


def validate_side(value: Any, label: str, *, has_receipt: bool) -> tuple[
    dict[str, Any], list[tuple[str, bytes]], dict[str, Any], bytes | None
]:
    keys = {"files", "hash_result", "manifest"}
    if has_receipt:
        keys.add("receipt")
    side = require_mapping(value, label, keys)
    manifest = validate_manifest(side["manifest"], f"{label}.manifest")
    entries = decode_file_entries(side["files"], manifest, f"{label}.files")
    expected_hashes = validate_hash_result(
        side["hash_result"], f"{label}.hash_result", manifest
    )
    receipt_raw: bytes | None = None
    if has_receipt:
        receipt = require_mapping(
            side["receipt"], f"{label}.receipt", {"content_base64", "sha256"}
        )
        encoded = require_text(
            receipt["content_base64"], f"{label}.receipt.content_base64"
        )
        require_sha256(receipt["sha256"], f"{label}.receipt.sha256")
        try:
            receipt_raw = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ContractError(f"invalid base receipt base64: {error}") from error
        if base64.b64encode(receipt_raw).decode("ascii") != encoded:
            raise ContractError("base receipt uses non-canonical base64")
        if sha256(receipt_raw) != receipt["sha256"]:
            raise ContractError("base receipt checksum mismatch")
        validate_receipt(receipt_raw, expected_hashes)
    return manifest, entries, expected_hashes, receipt_raw


def command_pack(args: argparse.Namespace) -> dict[str, Any]:
    helper = require_helper(Path(args.spec_hash_helper))
    base_root = require_safe_existing(Path(args.base_root), "--base-root", directory=True)
    local_root = require_safe_existing(Path(args.local_root), "--local-root", directory=True)
    base_manifest_path = require_safe_existing(
        Path(args.base_manifest), "--base-manifest", directory=False
    )
    local_manifest_path = require_safe_existing(
        Path(args.local_manifest), "--local-manifest", directory=False
    )
    receipt_raw = read_regular(Path(args.base_receipt), "--base-receipt")
    validate_receipt(receipt_raw)

    base_manifest = validate_manifest(
        parse_json(
            base_manifest_path.read_bytes(), "base manifest", require_canonical=False
        ),
        "base manifest",
    )
    local_manifest = validate_manifest(
        parse_json(
            local_manifest_path.read_bytes(), "local manifest", require_canonical=False
        ),
        "local manifest",
    )
    base_hashes = run_hash_helper(helper, base_root, base_manifest_path)
    local_hashes = run_hash_helper(helper, local_root, local_manifest_path)
    validate_hash_result(base_hashes, "base hash result", base_manifest)
    validate_hash_result(local_hashes, "local hash result", local_manifest)
    validate_receipt(receipt_raw, base_hashes)

    package = {
        "base": {
            "files": file_entries(base_root, base_manifest, "base"),
            "hash_result": base_hashes,
            "manifest": base_manifest,
            "receipt": {
                "content_base64": base64.b64encode(receipt_raw).decode("ascii"),
                "sha256": sha256(receipt_raw),
            },
        },
        "hash_implementation": HASH_IMPLEMENTATION,
        "hash_model": HASH_MODEL,
        "local": {
            "files": file_entries(local_root, local_manifest, "local"),
            "hash_result": local_hashes,
            "manifest": local_manifest,
        },
        "schema": SCHEMA,
    }
    raw = canonical_json(package)
    output = require_new_path(Path(args.output), "--output")
    write_new_file(output, raw, "--output")
    return {
        "base": {
            "contract_digest": base_hashes["contract_digest"],
            "transport_manifest_hash": base_hashes["transport_manifest_hash"],
        },
        "local": {
            "contract_digest": local_hashes["contract_digest"],
            "transport_manifest_hash": local_hashes["transport_manifest_hash"],
        },
        "package": str(output),
        "package_sha256": sha256(raw),
        "schema": SCHEMA,
        "status": "packed",
    }


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    helper = require_helper(Path(args.spec_hash_helper))
    package_path = require_safe_existing(Path(args.package), "--package", directory=False)
    raw = package_path.read_bytes()
    expected_package_hash = require_sha256(args.package_sha256, "--package-sha256")
    if sha256(raw) != expected_package_hash:
        raise ContractError("outer package checksum mismatch")
    package = require_mapping(
        parse_json(raw, "B/L transfer package", require_canonical=True),
        "B/L transfer package",
        {"base", "hash_implementation", "hash_model", "local", "schema"},
    )
    if package["schema"] != SCHEMA:
        raise ContractError(f"unsupported B/L transfer schema: {package['schema']}")
    if package["hash_model"] != HASH_MODEL:
        raise ContractError(f"unsupported B/L transfer hash model: {package['hash_model']}")
    if package["hash_implementation"] != HASH_IMPLEMENTATION:
        raise ContractError("unsupported portable hash implementation identifier")

    base_manifest, base_entries, base_expected, receipt_raw = validate_side(
        package["base"], "base", has_receipt=True
    )
    local_manifest, local_entries, local_expected, _ = validate_side(
        package["local"], "local", has_receipt=False
    )
    if receipt_raw is None:
        raise ContractError("base receipt is missing")

    output_root = create_output_root(Path(args.output_root))
    base_root = output_root / "base"
    local_root = output_root / "local"
    metadata_root = output_root / "metadata"
    for directory in (base_root, local_root, metadata_root):
        os.mkdir(directory, 0o700)
        require_safe_existing(directory, "isolated output directory", directory=True)
    materialize_files(base_root, base_entries, "base")
    materialize_files(local_root, local_entries, "local")
    base_manifest_path = metadata_root / "base-manifest.json"
    local_manifest_path = metadata_root / "local-manifest.json"
    receipt_path = metadata_root / "base-receipt.json"
    write_new_file(base_manifest_path, canonical_json(base_manifest), "base manifest")
    write_new_file(local_manifest_path, canonical_json(local_manifest), "local manifest")
    write_new_file(receipt_path, receipt_raw, "base receipt")

    base_actual = run_hash_helper(helper, base_root, base_manifest_path)
    local_actual = run_hash_helper(helper, local_root, local_manifest_path)
    validate_hash_result(base_actual, "recomputed base hash result", base_manifest)
    validate_hash_result(local_actual, "recomputed local hash result", local_manifest)
    if base_actual != base_expected:
        raise ContractError("recomputed base dual-hash evidence does not match the package")
    if local_actual != local_expected:
        raise ContractError("recomputed local dual-hash evidence does not match the package")

    return {
        "base": {
            "contract_digest": base_actual["contract_digest"],
            "transport_manifest_hash": base_actual["transport_manifest_hash"],
        },
        "local": {
            "contract_digest": local_actual["contract_digest"],
            "transport_manifest_hash": local_actual["transport_manifest_hash"],
        },
        "materialized_root": str(output_root),
        "package": str(package_path),
        "package_sha256": expected_package_hash,
        "schema": SCHEMA,
        "status": "validated",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    pack = subparsers.add_parser("pack", help="create one canonical B/L package")
    pack.add_argument("--base-root", required=True)
    pack.add_argument("--base-manifest", required=True)
    pack.add_argument("--base-receipt", required=True)
    pack.add_argument("--local-root", required=True)
    pack.add_argument("--local-manifest", required=True)
    pack.add_argument("--spec-hash-helper", required=True)
    pack.add_argument("--output", required=True)

    validate = subparsers.add_parser(
        "validate", help="validate and materialize one package in isolation"
    )
    validate.add_argument("--package", required=True)
    validate.add_argument("--package-sha256", required=True)
    validate.add_argument("--spec-hash-helper", required=True)
    validate.add_argument("--output-root", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "pack":
            result = command_pack(args)
        else:
            result = command_validate(args)
    except (ContractError, OSError) as error:
        print(f"blr-transfer: refused: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
