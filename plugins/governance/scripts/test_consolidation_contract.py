#!/usr/bin/env python3
"""Executable policy checks for the plugin consolidation workstream."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TEXT_ROOTS = (ROOT / "plugins", ROOT / "README.md", ROOT / ".claude-plugin")
DELETED = {"create-command", "update-command", "review-service-operation"}


def files_under(path: Path):
    if path.is_file():
        yield path
    else:
        yield from (item for item in path.rglob("*") if item.is_file() and ".git" not in item.parts)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}
    values: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if value in {">", ">-", "|", "|-"}:
            chunks: list[str] = []
            index += 1
            while index < end and (lines[index].startswith(" ") or not lines[index].strip()):
                chunks.append(lines[index].strip())
                index += 1
            values[key] = " ".join(chunks).strip()
            continue
        values[key] = value.strip(" '\"")
        index += 1
    return values


def main() -> int:
    failures: list[str] = []
    current_test = Path(__file__).resolve()
    all_text = "\n".join(
        read_text(path)
        for root in TEXT_ROOTS
        for path in files_under(root)
        if path.resolve() != current_test
    )

    for name in DELETED:
        if re.search(rf"(?:skills/|:){re.escape(name)}(?:[/\s`]|$)", all_text):
            failures.append(f"deleted skill reference remains: {name}")
        if any(path.name == name for path in (ROOT / "plugins").rglob("*")):
            failures.append(f"deleted skill directory remains: {name}")

    client_scripts = ROOT / "plugins/client/shared/scripts"
    expected_scripts = ROOT / "scripts"
    if not client_scripts.is_symlink() or client_scripts.resolve() != expected_scripts.resolve():
        failures.append("client shared scripts must symlink to repository scripts")

    scoped_roots = (ROOT / "plugins/web", ROOT / "plugins/client", ROOT / "plugins/governance")
    skill_files = [path for root in scoped_roots for path in (root / "skills").rglob("SKILL.md")]
    for root in (ROOT / "plugins",):
        for path in files_under(root):
            if path.resolve() == current_test:
                continue
            if "/Users/" in read_text(path) or "/Users\\" in read_text(path):
                failures.append(f"hard-coded user path: {path.relative_to(ROOT)}")
    for path in skill_files:
        text = read_text(path)
        body = text.split("---", 2)[-1]
        if len(body.splitlines()) > 500:
            failures.append(f"skill exceeds 500 body lines: {path.relative_to(ROOT)}")
        if "Coherence Mandate" in text or "```plaintext" in text or re.search(r"\bPhase [0-9]", text):
            failures.append(f"ceremonial/personalized prose remains: {path.relative_to(ROOT)}")
        metadata = frontmatter(text)
        words = len(metadata.get("description", "").split())
        if not 25 <= words <= 60:
            failures.append(f"description outside 25-60 words ({words}): {path.relative_to(ROOT)}")

    create = read_text(ROOT / "plugins/client/skills/create-screen-design/SKILL.md")
    update = read_text(ROOT / "plugins/client/skills/update-screen-design/SKILL.md")
    design = read_text(ROOT / "plugins/web/skills/design/SKILL.md")
    audit = read_text(ROOT / "plugins/web/skills/audit/SKILL.md")
    next_skill = read_text(ROOT / "plugins/web/skills/next/SKILL.md")
    storybook = read_text(ROOT / "plugins/web/skills/storybook/SKILL.md")
    required = {
        "create/update screen boundary": "does not update" in create.lower() and "does not create" in update.lower(),
        "bulk update selector": "--all" in update and "selector" in update.lower(),
        "design owns creation": "creates a visual" in design.lower(),
        "audit owns assessment": "audit" in audit.lower(),
        "next owns runtime diagnosis": any(word in next_skill.lower() for word in ("debug", "diagnos")),
        "storybook owns story states": "story" in storybook.lower() and "state" in storybook.lower(),
    }
    failures.extend(f"missing ownership contract: {name}" for name, passed in required.items() if not passed)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print(f"PASS: {len(skill_files)} scoped skills satisfy consolidation contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
