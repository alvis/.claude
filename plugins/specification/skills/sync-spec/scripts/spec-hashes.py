#!/usr/bin/env python3
"""Read-only deterministic transport and semantic specification hashing."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from typing import Any


SCHEMA = "spec-hash-input-v1"
HASH_MODEL = "specification-dual-hash-v1"
CARRIER_KINDS = {
    "notion-mdc",
    "local-markdown",
    "inline-markdown",
    "derived-markdown",
}
LINEAGES = {"notion", "local", "inline"}
UNIT_KEYS = {
    "carrier_kind",
    "stable_transport_identity",
    "logical_contract_unit_id",
    "path",
    "observed_revision",
    "semantic_lineage",
}
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
NOTION_ID_RE = re.compile(r"notion:[0-9a-f]{32}\Z")
INLINE_ID_RE = re.compile(r"inline-approved:sha256:[0-9a-f]{64}\Z")
LOCAL_APPROVED_ID_RE = re.compile(r"local-approved:sha256:[0-9a-f]{64}\Z")


class ContractError(ValueError):
    """Raised when input cannot have one unambiguous hash interpretation."""


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number: {value}")


def read_manifest(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContractError("manifest must be a regular, non-symlink file")
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as error:
        raise ContractError(f"cannot read manifest as strict UTF-8: {error}") from error
    if raw.startswith(b"\xef\xbb\xbf") or "\x00" in text or "\r" in text:
        raise ContractError("manifest must be BOM-free UTF-8 with LF line endings")
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_constant,
        )
    except (json.JSONDecodeError, ContractError) as error:
        raise ContractError(f"invalid manifest JSON: {error}") from error
    if not isinstance(value, dict):
        raise ContractError("manifest root must be an object")
    if set(value) != {"schema", "units"} or value.get("schema") != SCHEMA:
        raise ContractError("manifest must contain only schema=spec-hash-input-v1 and units")
    if not isinstance(value["units"], list) or not value["units"]:
        raise ContractError("units must be a non-empty array")
    return value


def require_text(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ContractError(f"{field} must be a {'possibly empty ' if allow_empty else ''}string")
    if CONTROL_RE.search(value):
        raise ContractError(f"{field} contains a control character")
    if unicodedata.normalize("NFC", value) != value:
        raise ContractError(f"{field} must already be NFC; normalization is not implicit")
    return value


def validate_relative_path(value: Any) -> str:
    path_text = require_text(value, "path")
    if "\\" in path_text or path_text.startswith("/"):
        raise ContractError(f"path is not portable relative POSIX: {path_text}")
    pure = PurePosixPath(path_text)
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise ContractError(f"path has an empty/dot component: {path_text}")
    if pure.as_posix() != path_text:
        raise ContractError(f"path is not in canonical POSIX form: {path_text}")
    return path_text


def validate_identity(identity: str, kind: str, lineage: str) -> None:
    if kind == "notion-mdc" and lineage != "notion":
        raise ContractError("notion-mdc requires semantic_lineage=notion")
    if kind == "local-markdown" and lineage != "local":
        raise ContractError("local-markdown requires semantic_lineage=local")
    if kind == "inline-markdown" and lineage != "inline":
        raise ContractError("inline-markdown requires semantic_lineage=inline")

    if lineage == "notion":
        valid = NOTION_ID_RE.fullmatch(identity) is not None
    elif lineage == "inline":
        valid = INLINE_ID_RE.fullmatch(identity) is not None
    else:
        valid = LOCAL_APPROVED_ID_RE.fullmatch(identity) is not None
        if identity.startswith("repo:") and len(identity) > len("repo:"):
            validate_relative_path(identity[len("repo:") :])
            valid = True
    if not valid:
        raise ContractError(f"identity does not match {lineage} lineage: {identity}")


def resolve_regular_file(root: Path, relative: str) -> Path:
    current = root
    for component in PurePosixPath(relative).parts:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise ContractError(f"cannot inspect {relative}: {error}") from error
        if stat.S_ISLNK(mode):
            raise ContractError(f"symlink component is forbidden: {relative}")
    if not stat.S_ISREG(current.lstat().st_mode):
        raise ContractError(f"unit is not a regular file: {relative}")
    try:
        current.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as error:
        raise ContractError(f"unit escapes root: {relative}") from error
    return current


def resolve_root(path: Path) -> Path:
    if not path.is_absolute():
        raise ContractError("--root must be absolute")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise ContractError(f"cannot inspect --root: {error}") from error
        if stat.S_ISLNK(mode):
            raise ContractError(f"symlink component is forbidden in --root: {current}")
    if not current.is_dir():
        raise ContractError("--root must be a directory")
    return current.resolve(strict=True)


def read_contract_bytes(path: Path, relative: str) -> bytes:
    try:
        raw = path.read_bytes()
        decoded = raw.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as error:
        raise ContractError(f"cannot read {relative} as strict UTF-8: {error}") from error
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ContractError(f"UTF-8 BOM is forbidden: {relative}")
    if b"\x00" in raw or b"\r" in raw:
        raise ContractError(f"NUL/CR is forbidden; use LF-only bytes: {relative}")
    if decoded.encode("utf-8") != raw:
        raise ContractError(f"UTF-8 does not round-trip exactly: {relative}")
    return raw


def semantic_projection(raw: bytes, lineage: str, relative: str) -> bytes:
    if lineage != "notion":
        return raw
    if not raw.startswith(b"---\n"):
        raise ContractError(f"Notion-lineage carrier lacks exact frontmatter opener: {relative}")
    lines = raw.splitlines(keepends=True)
    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line == b"---\n"),
        None,
    )
    if closing_index is None:
        raise ContractError(f"Notion-lineage carrier lacks exact frontmatter closer: {relative}")

    matches: list[int] = []
    for index, line in enumerate(lines[1:closing_index], start=1):
        if line.startswith(b"last_edited_time:"):
            matches.append(index)
    if len(matches) > 1:
        raise ContractError(f"duplicate top-level last_edited_time: {relative}")
    if not matches:
        return raw

    index = matches[0]
    line = lines[index]
    value = line[len(b"last_edited_time:") :]
    if not value.endswith(b"\n"):
        raise ContractError(f"volatile metadata line must end in LF: {relative}")
    scalar = value[:-1].strip(b" \t")
    if not scalar or scalar.startswith((b"|", b">")):
        raise ContractError(f"last_edited_time must be one non-empty scalar line: {relative}")
    return b"".join(lines[:index] + lines[index + 1 :])


def frame(value: bytes) -> bytes:
    return len(value).to_bytes(8, byteorder="big", signed=False) + value


def sha256(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def normalized_units(manifest: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    identities: set[str] = set()
    logical_ids: set[str] = set()
    paths: set[str] = set()

    for index, raw_unit in enumerate(manifest["units"]):
        if not isinstance(raw_unit, dict) or set(raw_unit) != UNIT_KEYS:
            raise ContractError(f"unit {index} must contain exactly {sorted(UNIT_KEYS)}")
        kind = require_text(raw_unit["carrier_kind"], "carrier_kind")
        if kind not in CARRIER_KINDS:
            raise ContractError(f"unsupported carrier_kind: {kind}")
        lineage = require_text(raw_unit["semantic_lineage"], "semantic_lineage")
        if lineage not in LINEAGES:
            raise ContractError(f"unsupported semantic_lineage: {lineage}")
        identity = require_text(raw_unit["stable_transport_identity"], "stable_transport_identity")
        logical_id = require_text(raw_unit["logical_contract_unit_id"], "logical_contract_unit_id")
        relative = validate_relative_path(raw_unit["path"])
        revision = require_text(raw_unit["observed_revision"], "observed_revision", allow_empty=True)
        if lineage == "notion" and not revision:
            raise ContractError("Notion-lineage unit requires observed_revision")
        validate_identity(identity, kind, lineage)

        if identity in identities:
            raise ContractError(f"duplicate stable_transport_identity: {identity}")
        if logical_id in logical_ids:
            raise ContractError(f"duplicate logical_contract_unit_id: {logical_id}")
        if relative in paths:
            raise ContractError(f"duplicate path: {relative}")
        identities.add(identity)
        logical_ids.add(logical_id)
        paths.add(relative)

        raw = read_contract_bytes(resolve_regular_file(root, relative), relative)
        projected = semantic_projection(raw, lineage, relative)
        units.append(
            {
                "carrier_kind": kind,
                "stable_transport_identity": identity,
                "logical_contract_unit_id": logical_id,
                "path": relative,
                "observed_revision": revision,
                "semantic_lineage": lineage,
                "raw": raw,
                "projected": projected,
            }
        )

    lineages = {unit["semantic_lineage"] for unit in units}
    if len(lineages) != 1:
        raise ContractError("one manifest cannot mix semantic lineages")
    lineage = next(iter(lineages))
    if lineage == "notion":
        for unit in units:
            if unit["logical_contract_unit_id"] != unit["stable_transport_identity"]:
                raise ContractError("Notion logical_contract_unit_id must equal normalized notion identity")
    elif len(units) == 1:
        if units[0]["logical_contract_unit_id"] != "contract:root":
            raise ContractError("single-file local/inline logical_contract_unit_id must be contract:root")
    else:
        for unit in units:
            logical_id = unit["logical_contract_unit_id"]
            if not logical_id.startswith("contract-unit:"):
                raise ContractError("multi-file local/inline logical id must start contract-unit:")
            validate_relative_path(logical_id[len("contract-unit:") :])
    return units


def transport_hash(units: list[dict[str, Any]]) -> str:
    data = bytearray(b"spec-transport-manifest-v1\n")
    ordered = sorted(
        units,
        key=lambda item: (
            item["stable_transport_identity"].encode("utf-8"),
            item["path"].encode("utf-8"),
        ),
    )
    data.extend(len(ordered).to_bytes(8, "big"))
    for unit in ordered:
        for value in (
            unit["carrier_kind"].encode("utf-8"),
            unit["stable_transport_identity"].encode("utf-8"),
            unit["path"].encode("utf-8"),
            unit["observed_revision"].encode("utf-8"),
            unit["raw"],
        ):
            data.extend(frame(value))
    return sha256(bytes(data))


def semantic_hash(units: list[dict[str, Any]]) -> str:
    data = bytearray(b"spec-semantic-contract-v1\n")
    ordered = sorted(units, key=lambda item: item["logical_contract_unit_id"].encode("utf-8"))
    data.extend(len(ordered).to_bytes(8, "big"))
    for unit in ordered:
        data.extend(frame(unit["logical_contract_unit_id"].encode("utf-8")))
        data.extend(frame(unit["projected"]))
    return sha256(bytes(data))


def build_result(units: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "spec-dual-hash-result-v1",
        "hash_model": HASH_MODEL,
        "units": [
            {
                "carrier_kind": unit["carrier_kind"],
                "stable_transport_identity": unit["stable_transport_identity"],
                "logical_contract_unit_id": unit["logical_contract_unit_id"],
                "path": unit["path"],
                "observed_revision": unit["observed_revision"],
                "semantic_lineage": unit["semantic_lineage"],
                "exact_file_sha256": sha256(unit["raw"]),
                "semantic_projection_sha256": sha256(unit["projected"]),
            }
            for unit in sorted(units, key=lambda item: item["path"].encode("utf-8"))
        ],
    }
    if kind in {"both", "transport"}:
        manifest_hash = transport_hash(units)
        result["transport_manifest_hash"] = manifest_hash
        result["transport_manifest_key"] = manifest_hash.removeprefix("sha256:")
    if kind in {"both", "semantic"}:
        result["contract_digest"] = semantic_hash(units)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute carrier root")
    parser.add_argument("--manifest", required=True, help="input manifest JSON")
    parser.add_argument("--kind", choices=("both", "transport", "semantic"), default="both")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = resolve_root(Path(args.root))
        manifest_path = Path(args.manifest)
        if not manifest_path.is_absolute():
            raise ContractError("--manifest must be absolute")
        manifest = read_manifest(manifest_path)
        result = build_result(normalized_units(manifest, root), args.kind)
    except (ContractError, OSError) as error:
        print(f"spec-hashes: invalid: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
