#!/usr/bin/env python3
"""Discover, preflight, stitch, and install enabled plugin agent templates."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from stitch_agent import AgentTemplateError, load_agent_frontmatter, stitch_agent_definition


@dataclass(frozen=True)
class AgentTemplate:
    owner: str
    name: str
    path: Path


def _plugin_templates(owner: str, plugin_root: Path) -> Iterable[AgentTemplate]:
    templates_root = plugin_root / "templates/agents"
    if not templates_root.is_dir():
        return
    resolved_plugin_root = plugin_root.resolve()
    for path in sorted(templates_root.iterdir()):
        if path.is_dir():
            try:
                path.resolve().relative_to(resolved_plugin_root)
            except ValueError as error:
                raise AgentTemplateError(
                    f"template symlink or path escapes plugin root: {path}"
                ) from error
            yield AgentTemplate(owner=owner, name=path.name, path=path)


def _read_plugin_records() -> list[dict[str, Any]]:
    try:
        completed = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise AgentTemplateError(f"cannot list installed plugins: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AgentTemplateError(f"cannot list installed plugins: {detail}")
    try:
        records = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise AgentTemplateError(f"invalid JSON from claude plugin list: {error}") from error
    if not isinstance(records, list):
        raise AgentTemplateError("claude plugin list --json did not return a list")
    return [record for record in records if isinstance(record, dict)]


def _last_updated(record: dict[str, Any]) -> str:
    value = record.get("lastUpdated")
    return value if isinstance(value, str) else ""


def _installed_plugin_roots(
    essential_root: Path, records: list[dict[str, Any]]
) -> list[tuple[str, Path]]:
    resolved_essential = essential_root.resolve()
    essential_records = [
        record
        for record in records
        if isinstance(record.get("installPath"), str)
        and Path(record["installPath"]).resolve() == resolved_essential
        and isinstance(record.get("id"), str)
        and record["id"].count("@") == 1
        and record["id"].split("@", 1)[0] == "essential"
    ]
    if not essential_records:
        raise AgentTemplateError(
            f"essential plugin is absent from claude plugin list: {essential_root}"
        )
    if len(essential_records) != 1:
        raise AgentTemplateError(
            f"multiple essential plugin records use install path: {essential_root}"
        )
    essential_record = essential_records[0]
    essential_id = essential_record["id"]
    if "@" not in essential_id:
        raise AgentTemplateError(f"installed plugin id has no marketplace: {essential_id}")
    marketplace = essential_id.rsplit("@", 1)[1]
    if not marketplace:
        raise AgentTemplateError(f"installed plugin id has no marketplace: {essential_id}")
    best_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        plugin_id = record.get("id")
        install_path = record.get("installPath")
        if (
            record.get("enabled") is not True
            or not isinstance(plugin_id, str)
            or not isinstance(install_path, str)
            or "@" not in plugin_id
        ):
            continue
        record_marketplace = plugin_id.rsplit("@", 1)[1]
        if record_marketplace != marketplace:
            continue
        current = best_by_id.get(plugin_id)
        if current is None or _last_updated(record) > _last_updated(current):
            best_by_id[plugin_id] = record

    roots = sorted(
        (
            (plugin_id.rsplit("@", 1)[0], Path(record["installPath"]))
            for plugin_id, record in best_by_id.items()
        ),
        key=lambda item: item[0],
    )
    return roots


def discover_agent_templates(
    essential_root: Path, plugin_records: list[dict[str, Any]] | None = None
) -> list[AgentTemplate]:
    """Discover source-checkout siblings or enabled same-marketplace installs."""
    essential_root = Path(essential_root)
    if essential_root.parent.name == "plugins":
        roots = [
            (path.name, path)
            for path in sorted(essential_root.parent.iterdir())
            if path.is_dir()
        ]
    else:
        roots = _installed_plugin_roots(
            essential_root,
            plugin_records if plugin_records is not None else _read_plugin_records(),
        )
    return [
        template
        for owner, plugin_root in roots
        for template in _plugin_templates(owner, plugin_root)
    ]


def _preflight(templates: list[AgentTemplate]) -> list[tuple[str, str]]:
    if not templates:
        raise AgentTemplateError("no agent templates discovered")
    seen: dict[str, AgentTemplate] = {}
    staged: list[tuple[str, str]] = []
    for template in templates:
        frontmatter = load_agent_frontmatter(template.path)
        name = frontmatter["name"]
        previous = seen.get(name)
        if previous is not None:
            raise AgentTemplateError(
                f"duplicate agent name {name!r}: {previous.path} and {template.path}"
            )
        seen[name] = template
        staged.append((name, stitch_agent_definition(template.path)))
    return staged


def install_agents(
    essential_root: Path,
    destination: Path,
    plugin_records: list[dict[str, Any]] | None = None,
) -> int:
    """Install every discovered template after a complete roster preflight."""
    staged_definitions = _preflight(
        discover_agent_templates(essential_root, plugin_records)
    )
    destination = Path(destination)
    with tempfile.TemporaryDirectory(prefix="claude-agents-") as temporary:
        stage = Path(temporary)
        for name, content in staged_definitions:
            (stage / f"{name}.md").write_text(content, encoding="utf-8")
        destination.mkdir(parents=True, exist_ok=True)
        for name, _ in staged_definitions:
            target = destination / f"{name}.md"
            with tempfile.NamedTemporaryFile(
                dir=destination, prefix=f".{name}.", suffix=".tmp", delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
            try:
                shutil.copy2(stage / target.name, temporary_path)
                os.replace(temporary_path, target)
            finally:
                temporary_path.unlink(missing_ok=True)
            print(f"installed: {target}")
    print(f"done — installed {len(staged_definitions)} agent(s) into {destination}")
    return len(staged_definitions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
    )
    parser.add_argument(
        "--destination", type=Path, default=Path.home() / ".claude/agents"
    )
    args = parser.parse_args()
    try:
        install_agents(args.plugin_root, args.destination)
    except AgentTemplateError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
