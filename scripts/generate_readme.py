#!/usr/bin/env python3
"""Generate the repository README from plugin manifests and skill sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
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


def agent_team_section() -> str:
    """Preserve the manually maintained cross-plugin team reference."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    start = readme.find(AGENT_TEAM_HEADING)
    end = readme.find("\n## Validation", start)
    return readme[start:end].strip() if start >= 0 and end >= 0 else ""


def render() -> str:
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
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
    ]
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
    team_reference = agent_team_section()
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
