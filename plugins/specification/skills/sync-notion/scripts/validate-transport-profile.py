#!/usr/bin/env python3
"""Validate a notion-sync transport profile without executing its binary."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


HEX64 = re.compile(r"^[0-9a-f]{64}$")
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
FLAG = re.compile(r"^--?[A-Za-z0-9][A-Za-z0-9._-]*$")
VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]*$")
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
CAPABILITY_NAMES = (
    "recursive_pull",
    "search",
    "create",
    "push",
    "conditional_update",
    "conditional_create",
)
OUTPUT_CONTRACTS = {
    "recursive_pull": "notion-page-tree-json-v1",
    "search": "notion-search-json-v1",
    "create": "notion-created-page-json-v1",
    "push": "notion-page-write-json-v1",
    "conditional_update": "notion-page-write-json-v1",
    "conditional_create": "notion-created-page-json-v1",
}
SECRET_TEXT = re.compile(
    r"(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|\bBearer\s+[A-Za-z0-9._~-]+|"
    r"(?:secret|token|password|api[_-]?key|cookie|authorization)\s*[:=])",
    re.IGNORECASE,
)
PLACEHOLDER_TEXT = re.compile(
    r"(?:\breplace[-_ ]with(?:[-_ ]|\b)|\bplaceholder\b|<[^>]+>)",
    re.IGNORECASE,
)

HELP_TEXT = """\
Validate a destination-owned notion-sync transport profile without executing it.

Usage:
  validate-transport-profile.py <absolute-profile-file>
  validate-transport-profile.py --print-template
  validate-transport-profile.py --help

The positional form preserves the original validation interface and emits one
compact JSON report. --print-template emits a secret-free, deliberately
unverified starter profile; it does not authorize any remote operation.
"""


def unverified_template() -> dict[str, Any]:
    """Return a strict-shape starter wrapped as explicitly unverified output."""

    unavailable = {
        "support": "unavailable",
        "command": None,
        "flags": [],
        "output_contract": None,
    }
    evidence = {
        "binary_sha256": "0" * 64,
        "version": "replace-with-exact-version",
        "help_stdout_sha256": "0" * 64,
        "capability_vectors": {
            "recursive_pull": ["pull", "--recursive", "--json"],
            "search": ["search", "--json"],
            "create": ["create", "--json"],
            "push": ["push", "--json"],
            "conditional_update": [],
            "conditional_create": [],
        },
        "output_contracts": {
            "recursive_pull": OUTPUT_CONTRACTS["recursive_pull"],
            "search": OUTPUT_CONTRACTS["search"],
            "create": OUTPUT_CONTRACTS["create"],
            "push": OUTPUT_CONTRACTS["push"],
            "conditional_update": "unavailable",
            "conditional_create": "unavailable",
        },
        "results": {
            "recursive_pull": "pass",
            "search": "pass",
            "create": "pass",
            "push": "pass",
            "conditional_update": "unavailable",
            "conditional_create": "unavailable",
        },
        "tested_at": "1970-01-01T00:00:00Z",
    }
    profile = {
        "schema": "notion-sync-transport-profile/v1",
        "name": "replace-with-profile-name",
        "installation": {
            "source": "team-artifact",
            "package": "replace-with-exact-package",
            "version": "replace-with-exact-version",
            "executable": "/absolute/path/to/notion-sync",
            "sha256": "0" * 64,
        },
        "probes": {
            "version_argv": ["--version"],
            "version_stdout_sha256": "0" * 64,
            "help_argv": ["--help"],
            "help_stdout_sha256": "0" * 64,
        },
        "capabilities": {
            "recursive_pull": {
                "command": "pull",
                "flags": ["--recursive", "--json"],
                "output_contract": OUTPUT_CONTRACTS["recursive_pull"],
            },
            "search": {
                "command": "search",
                "flags": ["--json"],
                "output_contract": OUTPUT_CONTRACTS["search"],
            },
            "create": {
                "command": "create",
                "flags": ["--json"],
                "output_contract": OUTPUT_CONTRACTS["create"],
            },
            "push": {
                "command": "push",
                "flags": ["--json"],
                "output_contract": OUTPUT_CONTRACTS["push"],
            },
            "conditional_update": dict(unavailable),
            "conditional_create": dict(unavailable),
        },
        "conformance": {
            "schema": "notion-sync-conformance/v1",
            "evidence": evidence,
            "evidence_sha256": "0" * 64,
        },
    }
    return {
        "status": "unverified_template",
        "warning": (
            "Replace every placeholder and attach checksum-bound conformance "
            "evidence before validation; this output authorizes no remote operation."
        ),
        "profile": profile,
    }


class ProfileError(ValueError):
    pass


def fail(message: str) -> None:
    print(
        json.dumps(
            {"status": "transport_unverified", "error": message},
            sort_keys=True,
            separators=(",", ":"),
        ),
        file=sys.stderr,
    )
    raise SystemExit(2)


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def require_keys(value: Any, expected: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProfileError(f"{location} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ProfileError(
            f"{location} fields mismatch; missing={missing}, unknown={unknown}"
        )
    return value


def require_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProfileError(f"{location} must be a non-empty string")
    if any(ord(character) < 0x20 for character in value):
        raise ProfileError(f"{location} contains a control character")
    if SECRET_TEXT.search(value):
        raise ProfileError(f"{location} appears to contain a secret")
    if PLACEHOLDER_TEXT.search(value):
        raise ProfileError(f"{location} contains a placeholder")
    return value


def require_hex(value: Any, location: str) -> str:
    text = require_string(value, location)
    if not HEX64.fullmatch(text):
        raise ProfileError(f"{location} must be 64 lowercase hex characters")
    return text


def require_token(value: Any, location: str, *, flag: bool = False) -> str:
    text = require_string(value, location)
    pattern = FLAG if flag else TOKEN
    if not pattern.fullmatch(text):
        raise ProfileError(f"{location} must be one literal argv token")
    return text


def safe_absolute_file(path_text: str, label: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute() or os.path.normpath(path_text) != path_text:
        raise ProfileError(f"{label} must be an absolute normalized path")

    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except OSError as error:
            raise ProfileError(f"cannot inspect {label} component {current}: {error}") from error
        if stat.S_ISLNK(mode):
            raise ProfileError(f"{label} contains a symlink component: {current}")
        if current != path and not stat.S_ISDIR(mode):
            raise ProfileError(f"{label} parent is not a directory: {current}")

    mode = os.lstat(path).st_mode
    if not stat.S_ISREG(mode):
        raise ProfileError(f"{label} must be a regular file")
    if mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise ProfileError(f"{label} must not be group/world-writable")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_evidence(evidence: dict[str, Any]) -> bytes:
    # v1 evidence uses only validated strings and arrays in a fixed nested shape.
    return json.dumps(
        evidence,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def validate_capability(
    capabilities: dict[str, Any], name: str
) -> tuple[str, list[str], str]:
    value = require_keys(
        capabilities[name],
        {"command", "flags", "output_contract"},
        f"capabilities.{name}",
    )
    command = require_token(value["command"], f"capabilities.{name}.command")
    flags = value["flags"]
    if not isinstance(flags, list):
        raise ProfileError(f"capabilities.{name}.flags must be an array")
    checked = [
        require_token(flag, f"capabilities.{name}.flags[{index}]", flag=True)
        for index, flag in enumerate(flags)
    ]
    if len(set(checked)) != len(checked):
        raise ProfileError(f"capabilities.{name}.flags contains duplicates")
    output_contract = require_string(
        value["output_contract"], f"capabilities.{name}.output_contract"
    )
    if output_contract != OUTPUT_CONTRACTS[name]:
        raise ProfileError(
            f"capabilities.{name}.output_contract must be {OUTPUT_CONTRACTS[name]}"
        )
    return command, checked, output_contract


def validate_conditional_capability(
    capabilities: dict[str, Any],
    name: str,
    core_name: str,
    core_command: str,
    core_flags: list[str],
) -> dict[str, Any]:
    value = require_keys(
        capabilities[name],
        {"support", "command", "flags", "output_contract"},
        f"capabilities.{name}",
    )
    support = require_string(value["support"], f"capabilities.{name}.support")
    if support not in {"supported", "unavailable"}:
        raise ProfileError(f"capabilities.{name}.support must be supported or unavailable")
    flags = value["flags"]
    if not isinstance(flags, list):
        raise ProfileError(f"capabilities.{name}.flags must be an array")
    if support == "supported":
        command = require_token(value["command"], f"capabilities.{name}.command")
        if command != core_command:
            raise ProfileError(
                f"capabilities.{name}.command must equal capabilities.{core_name}.command"
            )
        checked_flags = [
            require_token(flag, f"capabilities.{name}.flags[{index}]", flag=True)
            for index, flag in enumerate(flags)
        ]
        if not checked_flags:
            raise ProfileError(f"supported {name} requires a precondition flag")
        if len(set(checked_flags)) != len(checked_flags):
            raise ProfileError(f"capabilities.{name}.flags contains duplicates")
        if set(core_flags) & set(checked_flags):
            raise ProfileError(
                f"capabilities.{name}.flags duplicates a capabilities.{core_name} flag"
            )
        output_contract = require_string(
            value["output_contract"], f"capabilities.{name}.output_contract"
        )
        if output_contract != OUTPUT_CONTRACTS[name]:
            raise ProfileError(
                f"capabilities.{name}.output_contract must be {OUTPUT_CONTRACTS[name]}"
            )
        vector = [command, *core_flags, *checked_flags]
    else:
        if (
            value["command"] is not None
            or flags != []
            or value["output_contract"] is not None
        ):
            raise ProfileError(
                f"unavailable {name} requires null command/output_contract and empty flags"
            )
        command = None
        checked_flags = []
        output_contract = None
        vector = []
    return {
        "support": support,
        "command": command,
        "flags": checked_flags,
        "output_contract": output_contract,
        "vector": vector,
    }


def validate(profile_path_text: str) -> dict[str, Any]:
    profile_path = safe_absolute_file(profile_path_text, "profile file")
    profile_bytes = profile_path.read_bytes()
    if b"\x00" in profile_bytes:
        raise ProfileError("profile file contains NUL")
    try:
        profile = json.loads(profile_bytes, object_pairs_hook=no_duplicate_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ProfileError) as error:
        raise ProfileError(f"invalid profile JSON: {error}") from error

    profile = require_keys(
        profile,
        {"schema", "name", "installation", "probes", "capabilities", "conformance"},
        "profile",
    )
    if profile["schema"] != "notion-sync-transport-profile/v1":
        raise ProfileError("unsupported profile schema")
    name = require_token(profile["name"], "name")

    installation = require_keys(
        profile["installation"],
        {"source", "package", "version", "executable", "sha256"},
        "installation",
    )
    source = require_string(installation["source"], "installation.source")
    if source not in {"npm", "pipx", "homebrew", "system-package", "team-artifact"}:
        raise ProfileError("installation.source is not supported by v1")
    package = require_string(installation["package"], "installation.package")
    version = require_string(installation["version"], "installation.version")
    if not VERSION.fullmatch(version) or version.lower() in {"latest", "current"}:
        raise ProfileError("installation.version must be an exact non-range version")
    expected_executable_hash = require_hex(installation["sha256"], "installation.sha256")
    executable = safe_absolute_file(
        require_string(installation["executable"], "installation.executable"),
        "installation.executable",
    )
    if not os.access(executable, os.X_OK):
        raise ProfileError("installation.executable is not executable")
    actual_executable_hash = sha256_file(executable)
    if actual_executable_hash != expected_executable_hash:
        raise ProfileError("installation.executable SHA-256 mismatch")

    probes = require_keys(
        profile["probes"],
        {"version_argv", "version_stdout_sha256", "help_argv", "help_stdout_sha256"},
        "probes",
    )
    if probes["version_argv"] != ["--version"] or probes["help_argv"] != ["--help"]:
        raise ProfileError("v1 probe argv must be exactly --version and --help")
    version_stdout_hash = require_hex(
        probes["version_stdout_sha256"], "probes.version_stdout_sha256"
    )
    help_stdout_hash = require_hex(
        probes["help_stdout_sha256"], "probes.help_stdout_sha256"
    )

    capabilities = require_keys(
        profile["capabilities"],
        set(CAPABILITY_NAMES),
        "capabilities",
    )
    checked_capabilities: dict[str, Any] = {}
    for capability_name in ("recursive_pull", "search", "create", "push"):
        command, flags, output_contract = validate_capability(
            capabilities, capability_name
        )
        checked_capabilities[capability_name] = {
            "command": command,
            "flags": flags,
            "output_contract": output_contract,
            "vector": [command, *flags],
        }

    for conditional_name, core_name in (
        ("conditional_update", "push"),
        ("conditional_create", "create"),
    ):
        core = checked_capabilities[core_name]
        checked_capabilities[conditional_name] = validate_conditional_capability(
            capabilities,
            conditional_name,
            core_name,
            core["command"],
            core["flags"],
        )

    conformance = require_keys(
        profile["conformance"],
        {"schema", "evidence", "evidence_sha256"},
        "conformance",
    )
    if conformance["schema"] != "notion-sync-conformance/v1":
        raise ProfileError("unsupported conformance schema")
    evidence = require_keys(
        conformance["evidence"],
        {
            "binary_sha256",
            "version",
            "help_stdout_sha256",
            "capability_vectors",
            "output_contracts",
            "results",
            "tested_at",
        },
        "conformance.evidence",
    )
    for key in ("binary_sha256", "version", "help_stdout_sha256", "tested_at"):
        require_string(evidence[key], f"conformance.evidence.{key}")
    if evidence["binary_sha256"] != expected_executable_hash:
        raise ProfileError("conformance binary hash does not match installation")
    if evidence["version"] != version:
        raise ProfileError("conformance version does not match installation")
    if evidence["help_stdout_sha256"] != help_stdout_hash:
        raise ProfileError("conformance help hash does not match probes")
    vectors = require_keys(
        evidence["capability_vectors"],
        set(CAPABILITY_NAMES),
        "conformance.evidence.capability_vectors",
    )
    outputs = require_keys(
        evidence["output_contracts"],
        set(CAPABILITY_NAMES),
        "conformance.evidence.output_contracts",
    )
    results = require_keys(
        evidence["results"],
        set(CAPABILITY_NAMES),
        "conformance.evidence.results",
    )
    for capability_name in CAPABILITY_NAMES:
        expected_vector = checked_capabilities[capability_name]["vector"]
        if vectors[capability_name] != expected_vector:
            raise ProfileError(
                f"conformance {capability_name} vector does not match capabilities"
            )
        expected_output = (
            checked_capabilities[capability_name]["output_contract"]
            or "unavailable"
        )
        if require_string(
            outputs[capability_name],
            f"conformance.evidence.output_contracts.{capability_name}",
        ) != expected_output:
            raise ProfileError(
                f"conformance {capability_name} output contract does not match capabilities"
            )
        expected_result = (
            "pass"
            if capability_name in {"recursive_pull", "search", "create", "push"}
            or checked_capabilities[capability_name]["support"] == "supported"
            else "unavailable"
        )
        if require_string(
            results[capability_name],
            f"conformance.evidence.results.{capability_name}",
        ) != expected_result:
            raise ProfileError(
                f"conformance {capability_name} result disagrees with capabilities"
            )
    if not UTC_TIME.fullmatch(evidence["tested_at"]):
        raise ProfileError("conformance tested_at must be UTC ISO-8601")
    evidence_hash = hashlib.sha256(canonical_evidence(evidence)).hexdigest()
    if evidence_hash != require_hex(
        conformance["evidence_sha256"], "conformance.evidence_sha256"
    ):
        raise ProfileError("conformance evidence SHA-256 mismatch")

    return {
        "status": "profile_structure_verified",
        "profile_schema": profile["schema"],
        "profile_name": name,
        "profile_file": str(profile_path),
        "profile_file_sha256": hashlib.sha256(profile_bytes).hexdigest(),
        "installation_source": source,
        "package": package,
        "expected_version": version,
        "executable": str(executable),
        "expected_executable_sha256": expected_executable_hash,
        "actual_executable_sha256": actual_executable_hash,
        "expected_version_stdout_sha256": version_stdout_hash,
        "expected_help_stdout_sha256": help_stdout_hash,
        "conformance_evidence_sha256": evidence_hash,
        "capabilities": checked_capabilities,
    }


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] in {"-h", "--help"}:
        print(HELP_TEXT, end="")
        return 0
    if len(argv) == 2 and argv[1] in {"--print-template", "--template"}:
        print(json.dumps(unverified_template(), indent=2, sort_keys=True))
        return 0
    if len(argv) != 2 or argv[1].startswith("-"):
        fail(
            "usage: validate-transport-profile.py "
            "<absolute-profile-file>|--print-template|--help"
        )
    try:
        result = validate(argv[1])
    except (OSError, ProfileError) as error:
        fail(str(error))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
