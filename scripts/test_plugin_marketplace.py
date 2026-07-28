import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
SCHEMA_ROOT = ROOT / "scripts" / "schemas"
JSON_TYPES = {
    "array": lambda value: isinstance(value, list),
    "boolean": lambda value: isinstance(value, bool),
    "integer": lambda value: (
        isinstance(value, int) and not isinstance(value, bool)
    ),
    "number": lambda value: (
        isinstance(value, (int, float)) and not isinstance(value, bool)
    ),
    "object": lambda value: isinstance(value, dict),
    "string": lambda value: isinstance(value, str),
}
SCHEMA_KEYWORDS = {
    "$schema",
    "additionalProperties",
    "enum",
    "items",
    "minimum",
    "minItems",
    "minLength",
    "minProperties",
    "pattern",
    "properties",
    "required",
    "title",
    "type",
}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTEXT_PAYLOAD_EVENTS = {
    "AGENTS.md": {"SessionStart", "SubagentStart"},
    "MAINAGENT.md": {"SessionStart"},
    "SUBAGENT.md": {"SubagentStart"},
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def assert_supported_schema(schema: dict, path: str = "$") -> None:
    """Keep contracts within the dependency-free JSON Schema subset below."""
    assert not set(schema) - SCHEMA_KEYWORDS, (
        f"{path}: unsupported schema keywords "
        f"{sorted(set(schema) - SCHEMA_KEYWORDS)}"
    )
    if "type" in schema:
        assert schema["type"] in JSON_TYPES, (
            f"{path}: unsupported JSON type {schema['type']!r}"
        )
    for name, child in schema.get("properties", {}).items():
        assert_supported_schema(child, f"{path}.properties.{name}")
    if "items" in schema:
        assert_supported_schema(schema["items"], f"{path}.items")


def load_schema(name: str) -> dict:
    schema = load_json(SCHEMA_ROOT / name)
    assert schema["$schema"] == (
        "https://json-schema.org/draft/2020-12/schema"
    )
    assert_supported_schema(schema)
    return schema


def assert_matches_schema(value: object, schema: dict, path: str = "$") -> None:
    if "enum" in schema:
        assert value in schema["enum"], (
            f"{path}: {value!r} is not one of {schema['enum']!r}"
        )

    expected_type = schema.get("type")
    if expected_type is not None:
        assert JSON_TYPES[expected_type](value), (
            f"{path}: expected {expected_type}, got {type(value).__name__}"
        )

    if isinstance(value, str):
        assert len(value) >= schema.get("minLength", 0), (
            f"{path}: string is shorter than minLength"
        )
        if "pattern" in schema:
            assert re.search(schema["pattern"], value), (
                f"{path}: {value!r} does not match {schema['pattern']!r}"
            )

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema:
            assert value >= schema["minimum"], (
                f"{path}: {value!r} is below minimum {schema['minimum']!r}"
            )

    if isinstance(value, list):
        assert len(value) >= schema.get("minItems", 0), (
            f"{path}: array has fewer than minItems entries"
        )
        if "items" in schema:
            for index, item in enumerate(value):
                assert_matches_schema(item, schema["items"], f"{path}[{index}]")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        assert len(value) >= schema.get("minProperties", 0), (
            f"{path}: object has fewer than minProperties entries"
        )
        missing = set(schema.get("required", [])) - set(value)
        assert not missing, f"{path}: missing required keys {sorted(missing)}"
        if schema.get("additionalProperties") is False:
            extras = set(value) - set(properties)
            assert not extras, f"{path}: unsupported keys {sorted(extras)}"
        for key, item in value.items():
            if key in properties:
                assert_matches_schema(
                    item,
                    properties[key],
                    f"{path}.{key}",
                )


def resolve_plugin_path(plugin_root: Path, relative_path: str) -> Path:
    assert relative_path.startswith("./")
    resolved = (plugin_root / relative_path).resolve()
    assert resolved.is_relative_to(plugin_root.resolve())
    return resolved


def frontmatter_scalar(header: str, field: str) -> str:
    match = re.search(rf"(?m)^{field}:\s*(.+)$", header)
    assert match, f"missing {field}"
    raw_value = match.group(1).strip()
    if raw_value[:1] in {"'", '"'}:
        value = ast.literal_eval(raw_value)
    else:
        value = raw_value
    assert isinstance(value, str)
    return value


def skill_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text()
    assert text.startswith("---\n")
    _, header, _ = text.split("---\n", 2)
    return (
        frontmatter_scalar(header, "name"),
        frontmatter_scalar(header, "description"),
    )


def marketplace_plugins() -> list[dict]:
    marketplace = load_json(MARKETPLACE_PATH)
    assert_matches_schema(
        marketplace,
        load_schema("marketplace.schema.json"),
    )
    plugins = marketplace["plugins"]
    assert len({plugin["name"] for plugin in plugins}) == len(plugins)
    return plugins


def codex_marketplace_plugins() -> list[dict]:
    marketplace = load_json(CODEX_MARKETPLACE_PATH)
    assert_matches_schema(
        marketplace,
        load_schema("codex-marketplace.schema.json"),
    )
    plugins = marketplace["plugins"]
    assert len({plugin["name"] for plugin in plugins}) == len(plugins)
    return plugins


def hook_commands(hooks: dict, event: str) -> list[str]:
    return [
        handler["command"]
        for matcher in hooks[event]
        for handler in matcher["hooks"]
    ]


def command_references_payload(command: str, payload_name: str) -> bool:
    target = f"${{CLAUDE_PLUGIN_ROOT}}/{payload_name}"
    return f'"{target}"' in command


def test_shared_marketplace_resolves_every_plugin_for_both_harnesses() -> None:
    for plugin in marketplace_plugins():
        plugin_root = resolve_plugin_path(ROOT, plugin["source"])
        assert plugin_root.is_dir()
        assert (plugin_root / ".claude-plugin" / "plugin.json").is_file()
        assert (plugin_root / ".codex-plugin" / "plugin.json").is_file()


def test_codex_marketplace_is_a_structural_projection_of_claude_catalog() -> None:
    claude_plugins = marketplace_plugins()
    codex_plugins = codex_marketplace_plugins()

    assert [plugin["name"] for plugin in codex_plugins] == [
        plugin["name"] for plugin in claude_plugins
    ]
    for claude_plugin, codex_plugin in zip(
        claude_plugins, codex_plugins, strict=True
    ):
        assert codex_plugin["source"] == {
            "source": "local",
            "path": claude_plugin["source"],
        }
        assert codex_plugin["category"] == claude_plugin["category"]

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/generate_codex_marketplace.py"),
            "--check",
        ],
        check=True,
    )


def test_codex_manifests_are_thin_adapters_over_shared_plugin_content() -> None:
    schema = load_schema("codex-plugin.schema.json")

    for plugin in marketplace_plugins():
        plugin_root = resolve_plugin_path(ROOT, plugin["source"])
        claude_manifest = load_json(
            plugin_root / ".claude-plugin" / "plugin.json"
        )
        codex_directory = plugin_root / ".codex-plugin"
        codex_manifest = load_json(codex_directory / "plugin.json")

        assert {path.name for path in codex_directory.iterdir()} == {
            "plugin.json"
        }
        assert_matches_schema(codex_manifest, schema)
        assert codex_manifest["name"] == plugin["name"]
        assert codex_manifest["version"] == claude_manifest["version"]
        assert codex_manifest["description"] == plugin["description"]
        assert codex_manifest["skills"] == "./skills/"
        assert resolve_plugin_path(
            plugin_root, codex_manifest["skills"]
        ).is_dir()

        assert codex_manifest.get("mcpServers") == claude_manifest.get(
            "mcpServers"
        )
        if "mcpServers" in codex_manifest:
            assert resolve_plugin_path(
                plugin_root, codex_manifest["mcpServers"]
            ).is_file()


def test_shared_skills_follow_the_cross_harness_agent_skills_contract() -> None:
    for plugin in marketplace_plugins():
        plugin_root = resolve_plugin_path(ROOT, plugin["source"])
        skill_paths = sorted((plugin_root / "skills").glob("*/SKILL.md"))
        assert skill_paths

        for skill_path in skill_paths:
            name, description = skill_frontmatter(skill_path)
            assert SKILL_NAME.fullmatch(name)
            assert len(name) <= 64
            assert name == skill_path.parent.name
            assert description
            assert len(description) <= 1024


def test_shared_hooks_follow_the_cross_harness_schema() -> None:
    schema = load_schema("hooks.schema.json")
    hook_files = []

    for plugin in marketplace_plugins():
        plugin_root = resolve_plugin_path(ROOT, plugin["source"])
        hooks_path = plugin_root / "hooks" / "hooks.json"
        payload_events = {
            name: events
            for name, events in CONTEXT_PAYLOAD_EVENTS.items()
            if (plugin_root / name).is_file()
        }
        expected_events = set().union(*payload_events.values())
        claude_manifest = load_json(
            plugin_root / ".claude-plugin" / "plugin.json"
        )
        assert "hooks" not in claude_manifest

        if not expected_events:
            assert not hooks_path.exists()
            continue

        hook_files.append(hooks_path)
        hooks_document = load_json(hooks_path)
        assert_matches_schema(hooks_document, schema)
        hooks = hooks_document["hooks"]
        assert set(hooks) == expected_events

        for payload_name, events in payload_events.items():
            for event in events:
                commands = [
                    command
                    for command in hook_commands(hooks, event)
                    if command_references_payload(command, payload_name)
                ]
                assert len(commands) == 1

        for event in hooks:
            for command in hook_commands(hooks, event):
                assert "${CLAUDE_PLUGIN_ROOT}" in command
                if any(
                    command_references_payload(command, payload_name)
                    for payload_name in payload_events
                ):
                    continue
                relative_command = command.removeprefix(
                    "${CLAUDE_PLUGIN_ROOT}/"
                )
                assert relative_command != command
                assert (plugin_root / relative_command).is_file()

    assert hook_files


def test_context_hooks_replace_every_plugin_dir_placeholder() -> None:
    for plugin in marketplace_plugins():
        plugin_root = resolve_plugin_path(ROOT, plugin["source"])
        hooks_path = plugin_root / "hooks" / "hooks.json"
        if not hooks_path.is_file():
            continue

        hooks = load_json(hooks_path)["hooks"]

        for payload_name, events in CONTEXT_PAYLOAD_EVENTS.items():
            payload_path = plugin_root / payload_name
            if not payload_path.is_file():
                continue

            for event in events:
                command = next(
                    command
                    for command in hook_commands(hooks, event)
                    if command_references_payload(command, payload_name)
                )
                completed = subprocess.run(
                    ["/bin/sh", "-c", command],
                    capture_output=True,
                    check=True,
                    env=os.environ
                    | {"CLAUDE_PLUGIN_ROOT": str(plugin_root)},
                    input=json.dumps({"hook_event_name": event}),
                    text=True,
                )
                output = json.loads(completed.stdout)
                hook_output = output["hookSpecificOutput"]
                assert hook_output["hookEventName"] == event
                context = hook_output["additionalContext"]
                assert "{{PLUGIN_DIR}}" not in context
                if "{{PLUGIN_DIR}}" in payload_path.read_text():
                    assert str(plugin_root) in context


def test_codex_role_bindings_wait_for_installed_custom_agents(
    tmp_path: Path,
) -> None:
    required_agents = {
        "backend": "ai-research-lead",
        "coding": "tech-lead",
        "essential": "tech-lead",
        "web": "design-lead",
    }

    for plugin_name, agent_name in required_agents.items():
        plugin_root = ROOT / "plugins" / plugin_name
        hooks = load_json(plugin_root / "hooks" / "hooks.json")["hooks"]
        command = next(
            command
            for command in hook_commands(hooks, "SessionStart")
            if command_references_payload(command, "MAINAGENT.md")
        )
        base_env = os.environ | {
            "CLAUDE_PLUGIN_ROOT": str(plugin_root),
            "CODEX_HOME": str(tmp_path),
        }

        claude = subprocess.run(
            ["/bin/sh", "-c", command],
            capture_output=True,
            check=True,
            env=base_env,
            text=True,
        )
        assert json.loads(claude.stdout)["hookSpecificOutput"][
            "additionalContext"
        ]

        codex_env = base_env | {"PLUGIN_ROOT": str(plugin_root)}
        codex_missing = subprocess.run(
            ["/bin/sh", "-c", command],
            capture_output=True,
            check=True,
            env=codex_env,
            text=True,
        )
        assert codex_missing.stdout == ""

        agent_path = tmp_path / "agents" / f"{agent_name}.toml"
        agent_path.parent.mkdir(exist_ok=True)
        agent_path.write_text("name = \"installed\"\n")
        codex_installed = subprocess.run(
            ["/bin/sh", "-c", command],
            capture_output=True,
            check=True,
            env=codex_env,
            text=True,
        )
        assert json.loads(codex_installed.stdout)["hookSpecificOutput"][
            "additionalContext"
        ]
        agent_path.unlink()
