import json
import os
import subprocess
import sys
import tomllib
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import install_agents as install_agents_module
from install_agents import discover_agent_templates, install_agents
from stitch_agent import (
    DESCRIPTION_LIMIT,
    AgentTemplateError,
    stitch_agent_definition,
    stitch_codex_agent_definition,
    validate_agent_contract,
)


def memory_section(name: str) -> str:
    return (
        f"\n## Memory\n\nI retain durable repository knowledge in "
        f"`.claude/agent-memory/{name}/MEMORY.md`. I follow "
        "`plugins/essential/templates/memory.md`. Current facts, reusable "
        "lessons, and watchpoints carry evidence and a last-verified date. "
        "Sources override memory; I replace contradictions "
        "and archive old claims before 150 lines or 20KB. I move detail only "
        "to `topics/<stable-area>/<specific-subject>.md`.\n"
    )


def write_template(
    plugin_root: Path,
    name: str,
    *,
    frontmatter: dict[str, object],
    body: str = "# Body\n",
) -> Path:
    template = plugin_root / "templates/agents" / name
    (template / "frontmatter").mkdir(parents=True)
    frontmatter.setdefault(
        "description",
        "A test role. Preferably named Ava, Kit, or June when the main agent spawns this role.",
    )
    frontmatter.setdefault("memory", "project")
    (template / "frontmatter/claude.json").write_text(
        json.dumps(frontmatter), encoding="utf-8"
    )
    if "## Memory" not in body:
        body += memory_section(name)
    (template / "base.md").write_text(body, encoding="utf-8")
    return template


# stitch_agent_definition and validate_agent_contract


def test_stitches_nested_json_lists_and_multiline_strings_deterministically(
    tmp_path: Path,
) -> None:
    template = write_template(
        tmp_path,
        "test-agent",
        frontmatter={
            "name": "test-agent",
            "description": "first line\nsecond line. Preferably named Ava, Kit, or June when the main agent spawns this role.",
            "emptyObject": {},
            "emptyList": []
        },
        body="\n\n# Test agent\n",
    )

    stitched = stitch_agent_definition(template)

    frontmatter_text = stitched.split("---\n", 2)[1]
    assert json.loads(
        (template / "frontmatter/claude.json").read_text()
    ) == json.loads(frontmatter_text)
    assert "---\n\n# Test agent\n" in stitched
    assert stitched == stitch_agent_definition(template)


def test_stitches_native_codex_agent_toml_from_the_same_template(
    tmp_path: Path,
) -> None:
    template = write_template(
        tmp_path,
        "test-agent",
        frontmatter={
            "name": "test-agent",
            "description": "A test role. Preferably named Ava, Kit, or June when the main agent spawns this role.",
        },
        body="# Test agent\n\nCodex instructions.\n",
    )

    definition = stitch_codex_agent_definition(template)
    parsed = tomllib.loads(definition)

    assert parsed == {
        "name": "test-agent",
        "description": "A test role. Preferably named Ava, Kit, or June when the main agent spawns this role.",
        "developer_instructions": (
            "# Test agent\n\nCodex instructions.\n" + memory_section("test-agent")
        ),
    }
    assert definition == stitch_codex_agent_definition(template)


def test_rejects_missing_base_invalid_json_and_directory_name_mismatch(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "templates/agents/missing"
    (missing / "frontmatter").mkdir(parents=True)
    (missing / "frontmatter/claude.json").write_text(
        '{"name":"missing"}', encoding="utf-8"
    )
    with pytest.raises(AgentTemplateError, match="base.md"):
        stitch_agent_definition(missing)

    invalid = tmp_path / "templates/agents/invalid"
    (invalid / "frontmatter").mkdir(parents=True)
    (invalid / "frontmatter/claude.json").write_text("{", encoding="utf-8")
    (invalid / "base.md").write_text("body", encoding="utf-8")
    with pytest.raises(AgentTemplateError, match="invalid JSON"):
        stitch_agent_definition(invalid)

    mismatch = write_template(
        tmp_path, "directory-name", frontmatter={"name": "other-name"}
    )
    with pytest.raises(AgentTemplateError, match="does not match"):
        stitch_agent_definition(mismatch)

    nonstandard_number = write_template(
        tmp_path,
        "nonstandard-number",
        frontmatter={"name": "nonstandard-number"},
    )
    (nonstandard_number / "frontmatter/claude.json").write_text(
        '{"name":"nonstandard-number","maxTurns":NaN}', encoding="utf-8"
    )
    with pytest.raises(AgentTemplateError, match="invalid JSON"):
        stitch_agent_definition(nonstandard_number)


def test_requires_three_distinct_preferred_short_names(tmp_path: Path) -> None:
    missing = write_template(
        tmp_path,
        "missing-preferences",
        frontmatter={
            "name": "missing-preferences",
            "description": "A role without names.",
        },
    )
    with pytest.raises(AgentTemplateError, match="three distinct"):
        stitch_agent_definition(missing)

    duplicate = write_template(
        tmp_path,
        "duplicate-preferences",
        frontmatter={
            "name": "duplicate-preferences",
            "description": "A role. Preferably named Ava, Ava, or June when the main agent spawns this role.",
        },
    )
    with pytest.raises(AgentTemplateError, match="three distinct"):
        stitch_agent_definition(duplicate)


@pytest.mark.parametrize(
    ("frontmatter", "body", "message"),
    (
        (
            {"name": "test-agent", "model": "haiku", "effort": "medium"},
            "A role-specific body.",
            "haiku agents must omit effort",
        ),
        (
            {
                "name": "test-agent",
                "description": "x" * (DESCRIPTION_LIMIT + 1),
            },
            "A role-specific body.",
            f"description exceeds {DESCRIPTION_LIMIT} characters",
        ),
        (
            {"name": "test-agent", "model": "claude-opus-4-8"},
            "A role-specific body.",
            "invalid model 'claude-opus-4-8'",
        ),
        (
            {"name": "test-agent", "model": "opus", "effort": "extreme"},
            "A role-specific body.",
            "invalid effort 'extreme'",
        ),
        (
            {"name": "test-agent", "permissionMode": "yolo"},
            "A role-specific body.",
            "invalid permissionMode 'yolo'",
        ),
        (
            {"name": "test-agent", "tools": ["Read"]},
            "A role-specific body.",
            "must omit tools",
        ),
        (
            {"name": "test-agent"},
            "I only spawn fixed-reviewer.",
            "fixed routing language conflicts with runtime discovery",
        ),
        (
            {
                "name": "test-agent",
                "description": "Always route reviews to fixed-reviewer",
                "initialPrompt": "Only spawn fixed-reviewer for review",
            },
            "A role-specific body.",
            "fixed routing language conflicts with runtime discovery",
        ),
    ),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_rejects_invalid_field_values_fixed_routing_and_tool_mismatches(
    frontmatter: dict[str, object], body: str, message: str
) -> None:
    with pytest.raises(AgentTemplateError, match=message):
        validate_agent_contract(frontmatter, body)


@pytest.mark.parametrize(
    "phrase",
    (
        "current `Agent` roster",
        "When I need a Dynamic Workflow",
        "For changed code, I inspect",
        "REVIEWED: source=",
        "I hold the `Agent` tool",
        "I hold `Agent`",
        "spawn target",
        "spawned by",
    ),
)
def test_rejects_shared_delegation_policy_in_agent_body(phrase: str) -> None:
    with pytest.raises(AgentTemplateError, match="repeats shared delegation policy"):
        validate_agent_contract({"name": "test-agent"}, phrase)


VALID_MEMORY_BODY = memory_section("test-agent")
VALID_MEMORY_FRONTMATTER = {"name": "test-agent", "memory": "project"}


@pytest.mark.parametrize(
    ("frontmatter", "body", "message"),
    (
        ({"name": "test-agent", "memory": "local"}, VALID_MEMORY_BODY, "project-scoped"),
        (VALID_MEMORY_FRONTMATTER, "# No memory\n", "exactly one ## Memory"),
        (
            VALID_MEMORY_FRONTMATTER,
            VALID_MEMORY_BODY + VALID_MEMORY_BODY,
            "exactly one ## Memory",
        ),
        (
            VALID_MEMORY_FRONTMATTER,
            VALID_MEMORY_BODY.replace("test-agent", "other-agent"),
            "must name exact path",
        ),
        (
            VALID_MEMORY_FRONTMATTER,
            VALID_MEMORY_BODY.replace("last-verified", "checked"),
            "missing maintenance marker: last-verified",
        ),
        (
            VALID_MEMORY_FRONTMATTER,
            VALID_MEMORY_BODY.replace(
                "topics/<stable-area>/<specific-subject>.md",
                "topics/<slug>.md",
            ),
            "missing maintenance marker: topics/",
        ),
    ),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_requires_project_memory_path_section_and_maintenance_contract(
    frontmatter: dict[str, object], body: str, message: str
) -> None:
    with pytest.raises(AgentTemplateError, match=message):
        validate_agent_contract(frontmatter, body)


# agent discovery
# Payload byte budgets belong to the plugin that ships them; essential
# declares its own in plugins/essential/tests/test_contract_footprint.py.


def test_role_hooks_expand_the_engineering_work_reference() -> None:
    essential = ROOT / "plugins/essential"
    hooks_document = json.loads(
        (essential / "hooks/hooks.json").read_text(encoding="utf-8")
    )
    expected = str(essential / "references/engineering-work.md")

    for event in ("SessionStart", "SubagentStart"):
        commands = [
            hook["command"]
            for group in hooks_document["hooks"][event]
            for hook in group["hooks"]
            if hook["type"] == "command" and ".md\"" in hook["command"]
        ]
        assert len(commands) == 2
        for command in commands:
            env = os.environ.copy()
            env["CLAUDE_PLUGIN_ROOT"] = str(essential)
            completed = subprocess.run(
                ["bash", "-c", command],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )
            assert completed.returncode == 0, (event, command, completed.stderr)
            context = json.loads(completed.stdout)["hookSpecificOutput"][
                "additionalContext"
            ]
            assert "{{PLUGIN_DIR}}" not in context, (event, command)
            assert expected in context, (event, command)


def test_session_start_emits_a_valid_session_context_payload() -> None:
    essential = ROOT / "plugins/essential"
    completed = subprocess.run(
        [
            str(essential / "bin/session-start"),
            "--plugin-dir",
            str(essential),
            "--constitution-paths",
            str(essential),
        ],
        input='{"source":"startup"}',
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)["hookSpecificOutput"]
    assert payload["hookEventName"] == "SessionStart"
    assert payload["additionalContext"].strip()


@pytest.mark.parametrize(
    ("outcome", "message"),
    (
        pytest.param(OSError("missing"), "cannot list installed plugins", id="oserror"),
        pytest.param(
            subprocess.CompletedProcess([], 1, stdout="", stderr="failed"),
            "cannot list installed plugins: failed",
            id="nonzero-exit",
        ),
        pytest.param(
            subprocess.CompletedProcess([], 0, stdout="{", stderr=""),
            "invalid JSON from claude plugin list",
            id="invalid-json",
        ),
        pytest.param(
            subprocess.CompletedProcess([], 0, stdout="{}", stderr=""),
            "did not return a list",
            id="not-a-list",
        ),
    ),
)
def test_installed_mode_reports_plugin_list_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: object,
    message: str,
) -> None:
    essential = tmp_path / "cache/alvis/essential/1"
    essential.mkdir(parents=True)

    def fake_run(*args: object, **kwargs: object) -> object:
        if isinstance(outcome, OSError):
            raise outcome
        return outcome

    monkeypatch.setattr(install_agents_module.subprocess, "run", fake_run)
    with pytest.raises(AgentTemplateError, match=message):
        discover_agent_templates(essential)


def test_each_distributed_agent_has_an_owner_routing_row() -> None:
    templates = discover_agent_templates(ROOT / "plugins/essential")
    routing: dict[str, str] = {}
    for owner in {template.owner for template in templates}:
        # NOTE: essential keeps its roster table in orchestration.md; every
        # other plugin carries a standalone ROUTING.md.
        candidates = (
            ROOT / "plugins" / owner / "references/ROUTING.md",
            ROOT / "plugins" / owner / "references/orchestration.md",
        )
        table = next((path for path in candidates if path.is_file()), None)
        assert table is not None, f"{owner} has no routing document"
        routing[owner] = table.read_text(encoding="utf-8")

    for template in templates:
        assert f"`{template.name}` |" in routing[template.owner], template.name


def test_distributed_agents_satisfy_the_delegation_contract() -> None:
    templates = discover_agent_templates(ROOT / "plugins/essential")

    for template in templates:
        stitch_agent_definition(template.path)


def test_every_distributed_agent_has_project_memory() -> None:
    templates = discover_agent_templates(ROOT / "plugins/essential")
    # parity against the on-disk template directories, not a hardcoded
    # count that breaks whenever an agent is added or removed
    on_disk = {
        path.name
        for path in (ROOT / "plugins").glob("*/templates/agents/*")
        if path.is_dir()
    }
    assert templates
    assert on_disk == {template.name for template in templates}

    for template in templates:
        frontmatter = json.loads(
            (template.path / "frontmatter/claude.json").read_text(encoding="utf-8")
        )
        body = (template.path / "base.md").read_text(encoding="utf-8")
        assert frontmatter.get("memory") == "project", template.name
        assert "tools" not in frontmatter, template.name
        assert body.count("\n## Memory\n") == 1, template.name
        assert f".claude/agent-memory/{template.name}/MEMORY.md" in body
        assert "plugins/essential/templates/memory.md" in body, template.name
        assert "topics/<stable-area>/<specific-subject>.md" in body, template.name
        assert (
            "rather than task IDs, dates, counters, result counts, or conclusions"
            in body
        ), template.name


def test_memory_template_is_essential_owned_bounded_and_covers_lifecycle_rules() -> None:
    path = ROOT / "plugins/essential/templates/memory.md"
    template = path.read_text(encoding="utf-8")

    assert not (
        ROOT / "plugins/governance/constitution/templates/agent-memory.md"
    ).exists()
    assert len(template.splitlines()) <= 150
    assert len(template.encode("utf-8")) <= 20 * 1024
    for heading in (
        "## Template Instructions — Remove After Initialization",
        "## Current Facts",
        "## Reusable Lessons",
        "## Watchpoints",
        "## Topic Index",
        "## Archive Index",
    ):
        assert heading in template
    assert "remove this entire" in template
    for marker in (
        "Evidence",
        "Last verified",
        "150 lines",
        "20KB",
        "topics/<stable-area>/<specific-subject>.md",
        "task IDs",
        "dates",
        "counters",
        "conclusion sentences",
        "never beside `MEMORY.md`",
    ):
        assert marker in template, marker


def test_memory_writers_add_no_new_write_hooks() -> None:
    templates = {
        template.name: template
        for template in discover_agent_templates(ROOT / "plugins/essential")
    }

    for name in ("security-champion", "test-runner", "workflow-optimizer"):
        frontmatter = json.loads(
            (templates[name].path / "frontmatter/claude.json").read_text(
                encoding="utf-8"
            )
        )
        assert "tools" not in frontmatter, name
        assert "Write" not in frontmatter.get("disallowedTools", []), name
        assert "Edit" not in frontmatter.get("disallowedTools", []), name
        assert "PreToolUse" not in frontmatter.get("hooks", {}), name


def test_distributed_collaboration_sections_are_point_form_only() -> None:
    templates = discover_agent_templates(ROOT / "plugins/essential")

    for template in templates:
        body = (template.path / "base.md").read_text(encoding="utf-8")
        collaboration = body.split("\n## Collaboration\n", 1)[1]
        lines = [line for line in collaboration.splitlines() if line.strip()]
        # a lead role wraps its delegation map in <IMPORTANT>; the tags
        # delimit the map without adding prose to it
        lines = [
            line for line in lines if line not in ("<IMPORTANT>", "</IMPORTANT>")
        ]
        assert lines, template.name
        assert all(line.startswith("- ") for line in lines), (template.name, lines)
        assert all("): " not in line for line in lines), (template.name, lines)
        for line in (line for line in lines if line.startswith("- `")):
            assert "`: " in line, (template.name, line)
            assert "; " in line, (template.name, line)


def test_installed_mode_uses_only_enabled_plugins_from_essential_marketplace(
    tmp_path: Path,
) -> None:
    essential = tmp_path / "cache/alvis/essential/1"
    web = tmp_path / "cache/alvis/web/1"
    disabled = tmp_path / "cache/alvis/backend/1"
    other = tmp_path / "cache/other/coding/1"
    for path in (essential, web, disabled, other):
        path.mkdir(parents=True)
    write_template(
        essential,
        "essential-agent",
        frontmatter={"name": "essential-agent"},
    )
    write_template(web, "web-agent", frontmatter={"name": "web-agent"})
    write_template(
        disabled,
        "disabled-agent",
        frontmatter={"name": "disabled-agent"},
    )
    write_template(other, "other-agent", frontmatter={"name": "other-agent"})
    records = [
        {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
        {"id": "web@alvis", "enabled": True, "installPath": str(web)},
        {"id": "backend@alvis", "enabled": False, "installPath": str(disabled)},
        {"id": "coding@other", "enabled": True, "installPath": str(other)},
    ]

    templates = discover_agent_templates(essential, records)

    assert {
        f"{template.owner}:{template.name}" for template in templates
    } == {"essential:essential-agent", "web:web-agent"}


def test_codex_installed_mode_reads_native_plugin_list_shape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    essential = tmp_path / "cache/alvis/essential/1"
    coding = tmp_path / "cache/alvis/coding/1"
    for path in (essential, coding):
        path.mkdir(parents=True)
    write_template(
        essential,
        "essential-agent",
        frontmatter={"name": "essential-agent"},
    )
    write_template(coding, "coding-agent", frontmatter={"name": "coding-agent"})
    payload = {
        "installed": [
            {
                "pluginId": "essential@alvis",
                "enabled": True,
                "source": {"source": "local", "path": str(essential)},
            },
            {
                "pluginId": "coding@alvis",
                "enabled": True,
                "source": {"source": "local", "path": str(coding)},
            },
        ],
        "available": [],
    }
    monkeypatch.setattr(
        install_agents_module.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            [], 0, stdout=json.dumps(payload), stderr=""
        ),
    )

    templates = discover_agent_templates(essential, harness="codex")

    assert {
        f"{template.owner}:{template.name}" for template in templates
    } == {"essential:essential-agent", "coding:coding-agent"}


def test_installed_mode_keeps_only_latest_record_per_plugin_id(
    tmp_path: Path,
) -> None:
    essential = tmp_path / "cache/alvis/essential/2026-07-17"
    web_old = tmp_path / "cache/alvis/web/2026-07-16"
    web_new = tmp_path / "cache/alvis/web/2026-07-17"
    web_null = tmp_path / "cache/alvis/web/unknown"
    for path in (essential, web_old, web_new, web_null):
        path.mkdir(parents=True)
    write_template(
        essential,
        "essential-agent",
        frontmatter={"name": "essential-agent"},
    )
    write_template(web_old, "old-agent", frontmatter={"name": "old-agent"})
    write_template(web_new, "new-agent", frontmatter={"name": "new-agent"})
    write_template(web_null, "null-agent", frontmatter={"name": "null-agent"})
    records = [
        {
            "id": "essential@alvis",
            "enabled": True,
            "installPath": str(essential),
            "lastUpdated": "2026-07-17T00:00:00.000Z",
        },
        {
            "id": "web@alvis",
            "enabled": True,
            "installPath": str(web_old),
            "version": "9.9.9",
            "lastUpdated": "2026-07-16T00:00:00.000Z",
        },
        {
            "id": "web@alvis",
            "enabled": True,
            "installPath": str(web_new),
            "version": "1.0.0",
            "lastUpdated": "2026-07-17T00:00:00.000Z",
        },
        {
            "id": "web@alvis",
            "enabled": True,
            "installPath": str(web_null),
            "version": "8.8.8",
            "lastUpdated": None,
        },
    ]

    templates = discover_agent_templates(essential, records)

    assert {
        f"{template.owner}:{template.name}" for template in templates
    } == {"essential:essential-agent", "web:new-agent"}


def test_installed_mode_rejects_wrong_or_ambiguous_essential_identity(
    tmp_path: Path,
) -> None:
    essential = tmp_path / "cache/alvis/essential/1"
    essential.mkdir(parents=True)
    wrong_identity = [
        {"id": "other@alvis", "enabled": True, "installPath": str(essential)}
    ]
    with pytest.raises(AgentTemplateError, match="essential plugin"):
        discover_agent_templates(essential, wrong_identity)

    duplicate_identity = [
        {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
        {"id": "essential@alvis", "enabled": True, "installPath": str(essential)},
    ]
    with pytest.raises(AgentTemplateError, match="multiple essential"):
        discover_agent_templates(essential, duplicate_identity)


# install_agents


def test_template_symlink_cannot_escape_its_plugin(tmp_path: Path) -> None:
    essential = tmp_path / "repo/plugins/essential"
    templates = essential / "templates/agents"
    templates.mkdir(parents=True)
    external = write_template(
        tmp_path / "external",
        "escaped-agent",
        frontmatter={"name": "escaped-agent"},
    )
    (templates / "escaped-agent").symlink_to(external, target_is_directory=True)

    with pytest.raises(AgentTemplateError, match="symlink"):
        install_agents(essential, tmp_path / "destination")


def test_existing_destination_symlink_is_replaced_not_followed(
    tmp_path: Path,
) -> None:
    essential = tmp_path / "repo/plugins/essential"
    destination = tmp_path / "destination"
    destination.mkdir()
    external = tmp_path / "external.md"
    external.write_text("do not overwrite", encoding="utf-8")
    target = destination / "current-agent.md"
    target.symlink_to(external)
    write_template(
        essential,
        "current-agent",
        frontmatter={"name": "current-agent"},
        body="# Current\n",
    )

    install_agents(essential, destination)

    assert not target.is_symlink()
    assert "# Current" in target.read_text(encoding="utf-8")
    assert external.read_text(encoding="utf-8") == "do not overwrite"


def test_shell_entrypoint_resolves_essential_plugin_root(tmp_path: Path) -> None:
    destination = tmp_path / "agents"
    expected_names = {
        f"{template.name}.md"
        for template in discover_agent_templates(ROOT / "plugins/essential")
    }
    completed = subprocess.run(
        [str(SCRIPTS / "install-agents.sh"), "--destination", str(destination)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert {path.name for path in destination.glob("*.md")} == expected_names


def test_source_checkout_installs_every_discovered_agent(tmp_path: Path) -> None:
    with redirect_stdout(StringIO()):
        destination = tmp_path / "agents"
        expected_names = {
            f"{template.name}.md"
            for template in discover_agent_templates(ROOT / "plugins/essential")
        }

        count = install_agents(ROOT / "plugins/essential", destination)

    assert count == len(expected_names)
    assert {path.name for path in destination.glob("*.md")} == expected_names
    assert (destination / "frontend-implementer.md").is_file()


def test_source_checkout_installs_native_codex_agents(tmp_path: Path) -> None:
    with redirect_stdout(StringIO()):
        destination = tmp_path / "agents"
        expected_names = {
            f"{template.name}.toml"
            for template in discover_agent_templates(ROOT / "plugins/essential")
        }

        count = install_agents(
            ROOT / "plugins/essential",
            destination,
            harness="codex",
        )

    assert count == len(expected_names)
    assert {path.name for path in destination.glob("*.toml")} == expected_names
    tech_lead = tomllib.loads(
        (destination / "tech-lead.toml").read_text(encoding="utf-8")
    )
    assert tech_lead["name"] == "tech-lead"
    assert tech_lead["description"]
    assert tech_lead["developer_instructions"].startswith("# Tech Lead")


def test_duplicate_names_fail_before_any_destination_write(tmp_path: Path) -> None:
    essential = tmp_path / "repo/plugins/essential"
    web = tmp_path / "repo/plugins/web"
    destination = tmp_path / "home/.claude/agents"
    destination.mkdir(parents=True)
    existing = destination / "duplicate.md"
    existing.write_text("original", encoding="utf-8")
    write_template(
        essential,
        "duplicate",
        frontmatter={"name": "duplicate"},
        body="essential",
    )
    write_template(
        web,
        "duplicate",
        frontmatter={"name": "duplicate"},
        body="web",
    )

    with pytest.raises(AgentTemplateError, match="duplicate"):
        install_agents(essential, destination)

    assert existing.read_text(encoding="utf-8") == "original"
    assert list(destination.iterdir()) == [existing]


def test_rerun_overwrites_discovered_agents_without_pruning_other_files(
    tmp_path: Path,
) -> None:
    essential = tmp_path / "repo/plugins/essential"
    destination = tmp_path / "home/.claude/agents"
    destination.mkdir(parents=True)
    unrelated = destination / "personal-agent.md"
    stale = destination / "formerly-managed.md"
    unrelated.write_text("personal", encoding="utf-8")
    stale.write_text("stale", encoding="utf-8")
    template = write_template(
        essential,
        "current-agent",
        frontmatter={"name": "current-agent"},
        body="# Version one\n",
    )

    assert install_agents(essential, destination) == 1
    (template / "base.md").write_text(
        (template / "base.md")
        .read_text(encoding="utf-8")
        .replace("# Version one", "# Version two"),
        encoding="utf-8",
    )
    assert install_agents(essential, destination) == 1

    assert "# Version two" in (destination / "current-agent.md").read_text(
        encoding="utf-8"
    )
    assert unrelated.read_text(encoding="utf-8") == "personal"
    assert stale.read_text(encoding="utf-8") == "stale"


@pytest.mark.parametrize(
    "template",
    sorted(
        path
        for path in (ROOT / "plugins").glob("*/templates/agents/*")
        if path.is_dir()
    ),
    ids=lambda path: f"{path.parents[2].name}:{path.name}",
)
def test_every_distributed_agent_template_stitches(template: Path) -> None:
    """The stitch gate itself, over the real tree — `uvx pytest` is the only command.

    Stitching validates the whole agent contract: description limit, name
    regex, model/effort enums, absent tools, project memory, and the single
    Memory section. A template that cannot stitch cannot be installed.
    """
    assert stitch_agent_definition(template).strip()
