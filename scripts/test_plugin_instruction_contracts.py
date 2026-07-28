from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
DOMAIN_PLUGINS = {
    "backend",
    "client",
    "coding",
    "governance",
    "production",
    "react",
    "specification",
    "web",
}
INSTRUCTION_FILE = "WORKFLOW.md"
STANDARD_REFERENCE = re.compile(
    r"(?<![\w-])(?:(?P<plugin>[a-z][a-z0-9-]*):)?constitution/standards/"
)
SEMVER = re.compile(
    r"""
    ^
    (?P<major>0|[1-9]\d*)\.
    (?P<minor>0|[1-9]\d*)\.
    (?P<patch>0|[1-9]\d*)
    (?:
        -
        (?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)
        (?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*
    )?
    (?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?
    $
    """,
    re.VERBOSE,
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def marketplace_plugins() -> dict[str, Path]:
    payload = load_json(MARKETPLACE)
    entries = payload["plugins"]
    assert isinstance(entries, list)
    return {
        entry["name"]: (ROOT / entry["source"]).resolve()
        for entry in entries
        if isinstance(entry, dict) and entry["name"] != "essential"
    }


def marketplace_names() -> set[str]:
    payload = load_json(MARKETPLACE)
    entries = payload["plugins"]
    assert isinstance(entries, list)
    return {
        entry["name"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }


def hook_commands(manifest: dict[str, object], event: str) -> list[str]:
    hooks = manifest.get("hooks")
    assert isinstance(hooks, dict)
    groups = hooks.get(event)
    assert isinstance(groups, list)
    return [
        hook["command"]
        for group in groups
        if isinstance(group, dict)
        for hook in group.get("hooks", [])
        if isinstance(hook, dict) and isinstance(hook.get("command"), str)
    ]


def mentioned_plugins(text: str, names: set[str]) -> set[str]:
    mentioned: set[str] = set()
    for name in names:
        label = name.capitalize()
        patterns = (
            rf"plugins/{re.escape(name)}/",
            rf"plugin:{re.escape(name)}:",
            rf"(?<![\w-]){re.escape(name)}:[a-z]",
            rf"\b{re.escape(label)} plugin\b",
        )
        if any(re.search(pattern, text) for pattern in patterns):
            mentioned.add(name)
    return mentioned


def instruction_text(plugin: Path) -> str:
    return (plugin / "CLAUDE.md").read_text() + (
        plugin / "references" / INSTRUCTION_FILE
    ).read_text()


def test_marketplace_plugins_ship_action_instruction_contracts() -> None:
    plugins = marketplace_plugins()
    assert set(plugins) == DOMAIN_PLUGINS

    for name, plugin in plugins.items():
        domain = plugin / "references" / INSTRUCTION_FILE
        claude = plugin / "CLAUDE.md"
        manifest = load_json(plugin / ".claude-plugin" / "plugin.json")

        assert domain.is_file(), name
        assert claude.is_file(), name
        assert f"{{{{PLUGIN_DIR}}}}/references/{INSTRUCTION_FILE}" in claude.read_text()
        for event in ("SessionStart", "SubagentStart"):
            assert any("/CLAUDE.md" in command for command in hook_commands(manifest, event))


def test_marketplace_and_plugin_versions_use_semver_from_one() -> None:
    marketplace = load_json(MARKETPLACE)
    versions = [marketplace["metadata"]["version"]]
    versions.extend(
        load_json((ROOT / entry["source"]) / ".claude-plugin" / "plugin.json")[
            "version"
        ]
        for entry in marketplace["plugins"]
    )

    for version in versions:
        match = SEMVER.fullmatch(version)
        assert match, version
        assert int(match.group("major")) >= 1, version


def test_semver_schema_rejects_invalid_identifiers() -> None:
    valid = ("1.0.0", "2.1.3-alpha.1", "10.20.30+build.7")
    invalid = ("1.0", "01.0.0", "1.0.0-01", "1.0.0-.", "1.0.0-alpha..beta")

    assert all(SEMVER.fullmatch(version) for version in valid)
    assert not any(SEMVER.fullmatch(version) for version in invalid)


def test_instruction_contracts_reference_declared_dependencies_only() -> None:
    plugins = marketplace_plugins()
    names = marketplace_names()

    for name, plugin in plugins.items():
        manifest = load_json(plugin / ".claude-plugin" / "plugin.json")
        dependencies = manifest.get("dependencies", [])
        assert isinstance(dependencies, list)
        allowed = {name, *dependencies}
        text = instruction_text(plugin)

        assert mentioned_plugins(text, names) <= allowed, name
        for reference in STANDARD_REFERENCE.finditer(text):
            prefix = reference.group("plugin")
            assert prefix is not None, f"{name}: unprefixed standard reference"
            assert prefix in allowed, f"{name}: undeclared standard prefix {prefix}"


def test_instruction_contracts_list_every_owned_standard() -> None:
    for name, plugin in marketplace_plugins().items():
        standards = plugin / "constitution" / "standards"
        if not standards.is_dir():
            continue

        text = (plugin / "references" / INSTRUCTION_FILE).read_text()
        for standard in standards.iterdir():
            suffix = "/" if standard.is_dir() else ""
            expected = f"{name}:constitution/standards/{standard.name}{suffix}"
            assert expected in text, f"{name}: missing {expected}"
