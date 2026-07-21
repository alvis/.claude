#!/usr/bin/env python3
"""Generate the repository README from plugin manifests and skill sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEVELOPER_WORKFLOW_HEADING = "## Developer workflow"
PLUGIN_CATALOG_HEADING = "## Plugins and skills"
AGENT_TEAM_HEADING = "## Agent team"


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


def manual_section(start_heading: str, end_heading: str) -> str:
    """Preserve a manually maintained section between two generated headings."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    start = readme.find(start_heading)
    end = readme.find(f"\n{end_heading}", start)
    return readme[start:end].strip() if start >= 0 and end >= 0 else ""


def render() -> str:
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    lines = [
        "# Claude Code Plugin Marketplace",
        "",
        "Eight focused plugins provide composable Claude Code skills. Plugin manifests and each skill's `SKILL.md` are the source of truth; the inventory in this file is generated while the developer workflow and agent-team guide are preserved.",
        "",
        "## Install",
        "",
        "```bash",
        "cd /path/to/target-project",
        "claude plugin marketplace add alvis/.claude --scope project",
        "claude plugin install specification@alvis --scope project",
        "```",
        "",
        "`specification` is the recommended end-to-end bundle; its declared dependencies install `coding` and `essential`. Use `--scope local` for a private trial or `--scope user` across your projects. For a private source-checkout trial, add its absolute path at local scope rather than committing a machine-specific project path.",
        "",
    ]
    developer_workflow = manual_section(
        DEVELOPER_WORKFLOW_HEADING, PLUGIN_CATALOG_HEADING
    )
    if developer_workflow:
        lines.extend([developer_workflow, ""])
    lines.extend([PLUGIN_CATALOG_HEADING, ""])
    for entry in marketplace["plugins"]:
        plugin = ROOT / entry["source"].lstrip("./")
        manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        dependencies = manifest.get("dependencies", [])
        suffix = f" (depends on: {', '.join(dependencies)})" if dependencies else ""
        lines.extend([f"### {manifest['name']}{suffix}", "", manifest.get("description", entry.get("description", "")), ""])
        for name, description in skill_rows(plugin):
            summary = description or "No description provided."
            lines.append(f"- `{manifest['name']}:{name}` — {summary}")
        lines.append("")
    team_reference = manual_section(AGENT_TEAM_HEADING, "## Validation")
    if team_reference:
        lines.extend([team_reference, ""])
    lines.extend([
        "## Validation",
        "",
        "```bash",
        "claude plugin validate --strict .",
        "python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py .",
        "```",
        "",
        "Run `python3 scripts/generate_readme.py --check` to confirm this inventory is current.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    readme = ROOT / "README.md"
    if args.check:
        return 0 if readme.read_text(encoding="utf-8") == rendered else 1
    readme.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
