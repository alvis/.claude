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
PLUGINS = ROOT / "plugins"
# A shipped prompt may cap what gets *published*, but never what gets *found*:
# a finding an agent talks itself out of making is one nothing downstream can
# recover. Each pattern pairs a hedging directive with a reporting verb, so
# "report only" in the sense of "report, don't edit" stays legal.
SUPPRESSED_REPORTING = (
    re.compile(
        r"be conservative[^.!?\n]*?\b(?:report|flag|raise|surface|mention)\w*",
        re.IGNORECASE,
    ),
    re.compile(r"err on the side of (?:caution|silence|not reporting)", re.IGNORECASE),
    re.compile(
        r"only report (?:\w+ ){0,3}(?:problems|issues|findings|violations)",
        re.IGNORECASE,
    ),
    re.compile(
        r"when in doubt,? (?:omit|skip|stay silent|do ?n[o']t report)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:report|flag|raise) (?:\w+ ){0,4}only (?:if|when) you (?:are|'re) "
        r"(?:certain|sure|confident)",
        re.IGNORECASE,
    ),
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
    return (plugin / "ALLAGENT.md").read_text() + (
        plugin / "references" / INSTRUCTION_FILE
    ).read_text()


def test_marketplace_plugins_ship_action_instruction_contracts() -> None:
    plugins = marketplace_plugins()
    assert set(plugins) == DOMAIN_PLUGINS

    for name, plugin in plugins.items():
        domain = plugin / "references" / INSTRUCTION_FILE
        agents = plugin / "ALLAGENT.md"
        manifest = load_json(plugin / ".claude-plugin" / "plugin.json")
        hooks = load_json(plugin / "hooks" / "hooks.json")

        assert domain.is_file(), name
        assert agents.is_file(), name
        assert "hooks" not in manifest, name
        assert f"{{{{PLUGIN_DIR}}}}/references/{INSTRUCTION_FILE}" in agents.read_text()
        for event in ("SessionStart", "SubagentStart"):
            assert any("/ALLAGENT.md" in command for command in hook_commands(hooks, event))


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


def test_no_shipped_prompt_suppresses_reporting() -> None:
    offenders = [
        f"{path.relative_to(ROOT)}:{text.count(chr(10), 0, match.start()) + 1}: "
        f"{match.group(0)}"
        for path in sorted(PLUGINS.rglob("*.md"))
        for text in (path.read_text(),)
        for pattern in SUPPRESSED_REPORTING
        for match in pattern.finditer(text)
    ]

    assert offenders == [], "\n".join(offenders)


def test_suppressed_reporting_patterns_catch_known_phrasings() -> None:
    suppressing = (
        "Be conservative: only report problems clearly visible in the image.",
        "Err on the side of caution and leave it out.",
        "When in doubt, omit the finding.",
        "Report a violation only if you are certain it is one.",
    )
    legitimate = (
        "Do not use for: deleting or modifying code (report only).",
        "A claim survives into the report only when an independent source agrees.",
        "Report context usage only when the runtime measures it.",
        "Cap published nits at five; rank what you found.",
        "Be conservative with resource consumption and migration blast radius.",
    )

    for text in suppressing:
        assert any(pattern.search(text) for pattern in SUPPRESSED_REPORTING), text
    for text in legitimate:
        assert not any(pattern.search(text) for pattern in SUPPRESSED_REPORTING), text


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
