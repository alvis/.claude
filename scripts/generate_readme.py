#!/usr/bin/env python3
"""Generate the repository README from plugin manifests and skill sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENT_TEAM_HEADING = "## Agent team"
README_PATH = ROOT / "README.md"
README_DETAIL_ROOT = ROOT / "readme"
AGENT_TEAM_PATH = README_DETAIL_ROOT / "90-agent-team.md"
README_HARD_LIMIT = 16_384
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def frontmatter_value(text: str, key: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return ""
    for index, line in enumerate(lines[1:end]):
        match = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value in {">", ">-", "|", "|-"}:
            chunks: list[str] = []
            for child in lines[index + 2 : end]:
                if child.startswith(" ") or not child.strip():
                    chunks.append(child.strip())
                else:
                    break
            return " ".join(chunks).strip()
        return value.strip(" '\"")
    return ""


def skill_rows(plugin: Path) -> list[tuple[str, str]]:
    rows = []
    for skill in sorted((plugin / "skills").glob("*/SKILL.md")):
        name = frontmatter_value(skill.read_text(encoding="utf-8"), "name") or skill.parent.name
        description = frontmatter_value(skill.read_text(encoding="utf-8"), "description")
        rows.append((name, description))
    return rows


def plugin_entries() -> list[tuple[dict[str, object], Path]]:
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    entries = []
    for entry in marketplace["plugins"]:
        plugin = ROOT / entry["source"].lstrip("./")
        manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        entries.append((manifest, plugin))
    return entries


def table_text(value: object) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def plugin_catalog_path(index: int, manifest: dict[str, object]) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", str(manifest["name"]).lower()).strip("-") or "plugin"
    return README_DETAIL_ROOT / f"{index * 10:02d}-{slug}-skills.md"


def agent_team_document() -> str:
    """Load the maintained team reference, migrating the legacy README section once."""
    if AGENT_TEAM_PATH.is_file():
        return AGENT_TEAM_PATH.read_text(encoding="utf-8").rstrip() + "\n"

    readme = README_PATH.read_text(encoding="utf-8")
    start = readme.find(AGENT_TEAM_HEADING)
    end = readme.find("\n## Validation", start)
    if start < 0 or end < 0:
        raise ValueError("missing maintained Agent team source")

    section = readme[start:end].strip()
    section = section.replace(AGENT_TEAM_HEADING, "# Agent team", 1)
    section = re.sub(r"^### ", "## ", section, flags=re.MULTILINE)
    heading, body = section.split("\n", 1)
    return f"{heading}\n\n[Back to marketplace overview](../README.md#agent-team)\n{body.rstrip()}\n"


def markdown_anchor(value: str) -> str:
    plain = re.sub(r"[`*_\[\]]", "", value).lower()
    anchor = re.sub(r"[^\w\s-]", "", plain)
    return re.sub(r"\s+", "-", anchor).strip("-")


def render_readme() -> str:
    entries = plugin_entries()
    lines = [
        "# Claude Code Plugin Marketplace",
        "",
        "Eight focused plugins provide composable Claude Code skills. Plugin manifests and each skill's `SKILL.md` are the source of truth; this file is generated.",
        "",
        "## Install",
        "",
        "```bash",
        "claude plugin install ./plugins/<plugin>",
        "```",
        "",
        "Dependencies are declared in each plugin's `.claude-plugin/plugin.json`; installing a dependent plugin enables its required providers automatically.",
        "",
        "## Plugins and skills",
        "",
        "Use the overview below to choose a plugin, then open only that plugin's generated skill catalog.",
        "",
        "<!-- Stable fragment entrypoints retained after moving plugin detail. -->",
    ]
    for manifest, _plugin in entries:
        dependencies = manifest.get("dependencies", [])
        suffix = f" (depends on: {', '.join(dependencies)})" if dependencies else ""
        heading = f"{manifest['name']}{suffix}"
        lines.append(f'<a id="{markdown_anchor(heading)}"></a>')
    lines.extend([
        "",
        "| Plugin | Focus | Requires |",
        "| --- | --- | --- |",
    ])
    for index, (manifest, _plugin) in enumerate(entries, 1):
        dependencies = manifest.get("dependencies", [])
        dependency_text = ", ".join(f"`{name}`" for name in dependencies) or "—"
        catalog = plugin_catalog_path(index, manifest).relative_to(ROOT).as_posix()
        lines.append(
            f"| [`{table_text(manifest['name'])}`]({catalog}) | {table_text(manifest.get('description', ''))} | {dependency_text} |"
        )
    lines.extend([
        "",
        "## Agent team",
        "",
        "<a id=\"roster\"></a><a id=\"delegation-topology\"></a><a id=\"team-shapes\"></a><a id=\"gates\"></a><a id=\"team-operation\"></a><a id=\"notes\"></a>",
        "",
        "Install the 23-agent team with the `essential:install-agents` skill by asking Claude to \"install the agents\". The [agent-team reference](readme/90-agent-team.md) contains the roster, delegation topology, gates, and operating notes.",
        "",
        "## Validation",
        "",
        "```bash",
        "claude plugin validate --strict .",
        "python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .",
        "```",
        "",
        "Run `python3 scripts/generate_readme.py --check` to confirm the overview and generated catalog are current.",
        "",
    ])
    rendered = "\n".join(lines)
    if len(rendered.encode("utf-8")) > README_HARD_LIMIT:
        raise ValueError(f"generated README exceeds {README_HARD_LIMIT} bytes")
    return rendered


def render_plugin_catalog(manifest: dict[str, object], plugin: Path) -> str:
    dependencies = manifest.get("dependencies", [])
    suffix = f" (depends on: {', '.join(dependencies)})" if dependencies else ""
    lines = [
        f"# {manifest['name']} skills{suffix}",
        "",
        "[Back to marketplace overview](../README.md#plugins-and-skills)",
        "",
        str(manifest.get("description", "")),
        "",
        "This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.",
        "",
    ]
    for name, description in skill_rows(plugin):
        summary = description or "No description provided."
        lines.append(f"- `{manifest['name']}:{name}` — {summary}")
    lines.append("")
    return "\n".join(lines)


def expected_outputs() -> dict[Path, str]:
    outputs = {
        README_PATH: render_readme(),
        AGENT_TEAM_PATH: agent_team_document(),
    }
    for index, (manifest, plugin) in enumerate(plugin_entries(), 1):
        outputs[plugin_catalog_path(index, manifest)] = render_plugin_catalog(manifest, plugin)
    return outputs


def markdown_anchors(content: str) -> set[str]:
    anchors = set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", content, flags=re.MULTILINE):
        anchors.add(markdown_anchor(heading))
    anchors.update(re.findall(r"<a\s+id=\"([^\"]+)\"", content))
    return anchors


def local_links_resolve(outputs: dict[Path, str]) -> bool:
    generated_paths = {path.resolve(): content for path, content in outputs.items()}
    for source, content in outputs.items():
        for target in MARKDOWN_LINK.findall(content):
            if "://" in target or target.startswith("mailto:"):
                continue
            destination, separator, fragment = target.partition("#")
            resolved = (source.parent / destination).resolve()
            if not destination:
                resolved = source.resolve()
            if resolved not in generated_paths and not resolved.is_file():
                return False
            if separator:
                target_content = generated_paths.get(resolved)
                if target_content is None:
                    target_content = resolved.read_text(encoding="utf-8")
                if fragment not in markdown_anchors(target_content):
                    return False
    return True


def generate(*, check: bool) -> int:
    outputs = expected_outputs()
    oversized = [
        path for path, content in outputs.items()
        if len(content.encode("utf-8")) > README_HARD_LIMIT
    ]
    if oversized:
        paths = ", ".join(path.relative_to(ROOT).as_posix() for path in oversized)
        raise ValueError(f"generated Markdown exceeds {README_HARD_LIMIT} bytes: {paths}")
    expected_catalogs = {path for path in outputs if path.name.endswith("-skills.md")}
    actual_catalogs = set(README_DETAIL_ROOT.glob("[0-9][0-9]-*-skills.md"))
    if check:
        contents_match = all(
            path.is_file() and path.read_text(encoding="utf-8") == content
            for path, content in outputs.items()
        )
        return 0 if (
            contents_match
            and actual_catalogs == expected_catalogs
            and local_links_resolve(outputs)
        ) else 1

    if not local_links_resolve(outputs):
        raise ValueError("generated README contains an unresolved local link")

    README_DETAIL_ROOT.mkdir(parents=True, exist_ok=True)
    for stale_path in actual_catalogs - expected_catalogs:
        stale_path.unlink()
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return generate(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
