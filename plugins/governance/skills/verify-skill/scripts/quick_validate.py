"""Repository policy checks for Claude Code skills.

Claude Code owns manifest and frontmatter schema validation. This script runs
``claude plugin validate --strict`` first, then checks only local authoring
policies that the official validator does not cover.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


MAX_BODY_LINES = 500
MIN_DESCRIPTION_WORDS = 25
MAX_DESCRIPTION_WORDS = 60
PLACEHOLDERS = (
    re.compile(r"\[(?:TODO|PLACEHOLDER|INSERT(?: [^]]*)?)\]", re.IGNORECASE),
    re.compile(r"\[(?:skill-name|Skill Name|Description|Step Name)\]"),
)
LOCAL_LINK = re.compile(r"\[[^]]+\]\((?![a-z]+:|#)([^)]+)\)", re.IGNORECASE)
LOCAL_DIRECTORIES = {"agents", "assets", "evals", "hooks", "references", "scripts", "templates"}
CLAUDE_TIMEOUT_SECONDS = 30


def discover_skills(target: Path) -> list[Path]:
    """Return all SKILL.md files represented by a file, skill, or tree."""
    target = target.resolve()
    if target.is_file():
        return [target] if target.name == "SKILL.md" else []
    if (target / "SKILL.md").is_file():
        return [target / "SKILL.md"]
    return sorted(target.glob("**/SKILL.md")) if target.is_dir() else []


def issue(message: str, *, line: int | None = None) -> dict[str, object]:
    result: dict[str, object] = {"message": message}
    if line is not None:
        result["line"] = line
    return result


def frontmatter_and_body(text: str) -> tuple[list[str], list[str]]:
    """Split frontmatter without attempting to interpret Claude's schema."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return [], lines
    return lines[1:end], lines[end + 1 :]


def scalar_value(frontmatter: list[str], key: str) -> str | None:
    """Read one plain or quoted scalar for policy metrics, not schema checks."""
    prefix = f"{key}:"
    for line in frontmatter:
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return None


def is_local_file_destination(destination: str) -> bool:
    """Return whether a Markdown destination clearly denotes a local file."""
    destination = destination.strip().split("#", 1)[0]
    if not destination or destination in {"url", "...", "…"}:
        return False
    if destination[0] in "<[" or destination[-1] in ">]":
        return False
    path = Path(destination)
    return (
        destination.startswith(("./", "../"))
        or (path.parts and path.parts[0] in LOCAL_DIRECTORIES)
        or bool(path.suffix)
    )


def validate_policy(skill: Path) -> dict[str, object]:
    """Validate repository-specific content policies for one skill."""
    text = skill.read_text(encoding="utf-8")
    frontmatter, body = frontmatter_and_body(text)
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if len(body) > MAX_BODY_LINES:
        errors.append(issue(f"Skill body exceeds {MAX_BODY_LINES} lines ({len(body)})."))

    description = scalar_value(frontmatter, "description")
    if description:
        count = len(description.split())
        if not MIN_DESCRIPTION_WORDS <= count <= MAX_DESCRIPTION_WORDS:
            warnings.append(
                issue(
                    f"Description has {count} words; repository target is "
                    f"{MIN_DESCRIPTION_WORDS}-{MAX_DESCRIPTION_WORDS}."
                )
            )

    for number, line in enumerate(text.splitlines(), 1):
        if any(pattern.search(line) for pattern in PLACEHOLDERS):
            errors.append(issue("Placeholder text remains in the skill.", line=number))
        for match in LOCAL_LINK.finditer(line):
            raw = match.group(1).split("#", 1)[0]
            if not is_local_file_destination(raw):
                continue
            reference = (skill.parent / raw).resolve()
            if not reference.exists():
                errors.append(
                    issue(f"Unresolved local reference: {match.group(1)}", line=number)
                )

    return {"path": str(skill), "errors": errors, "warnings": warnings}


def claude_targets(target: Path) -> list[Path]:
    """Find marketplace and plugin roots for official Claude validation."""
    target = target.resolve()
    if (target / ".claude-plugin" / "plugin.json").is_file():
        return [target]
    marketplace = None
    if (target / ".claude-plugin" / "marketplace.json").is_file():
        marketplace = target
    if (target / "plugins").is_dir():
        plugins = target / "plugins"
    else:
        plugins = target
    if plugins.is_dir():
        roots = sorted(
            path.parent.parent
            for path in plugins.glob("*/.claude-plugin/plugin.json")
        )
        return ([marketplace] if marketplace else []) + roots
    for parent in target.parents:
        if (parent / ".claude-plugin" / "plugin.json").is_file():
            return [parent]
    return []


def run_claude_validation(targets: list[Path]) -> tuple[int, list[dict[str, object]]]:
    """Run Claude's validator; do not reproduce or reinterpret its schema."""
    results = []
    failed = False
    for target in targets:
        command = ["claude", "plugin", "validate", "--strict", str(target)]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=CLAUDE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failed = True
            results.append(
                {
                    "path": str(target),
                    "status": "fail",
                    "output": (
                        "Claude validator timed out after "
                        f"{CLAUDE_TIMEOUT_SECONDS} seconds: {' '.join(command)}"
                    ),
                }
            )
            continue
        except OSError as error:
            failed = True
            results.append(
                {
                    "path": str(target),
                    "status": "fail",
                    "output": f"Unable to launch Claude validator: {error}",
                }
            )
            continue
        failed = failed or completed.returncode != 0
        results.append(
            {
                "path": str(target),
                "status": "pass" if completed.returncode == 0 else "fail",
                "output": (completed.stdout + completed.stderr).strip(),
            }
        )
    return (1 if failed else 0), results


def run(argv: list[str] | None = None) -> int:
    """Execute the CLI and return a process-compatible status code."""
    parser = argparse.ArgumentParser(
        description="Run official Claude validation and repository skill-policy checks."
    )
    parser.add_argument("target", type=Path, help="SKILL.md, skill, plugin, marketplace, or plugins directory")
    parser.add_argument(
        "--policy-only",
        action="store_true",
        help="Skip the official validator (intended for unit tests and focused policy checks).",
    )
    args = parser.parse_args(argv)

    skills = discover_skills(args.target)
    if not skills:
        parser.error(f"No SKILL.md files found under {args.target}")

    claude_status, claude_results = (0, [])
    if not args.policy_only:
        claude_status, claude_results = run_claude_validation(claude_targets(args.target))

    policies = [validate_policy(skill) for skill in skills]
    policy_errors = sum(len(report["errors"]) for report in policies)
    report = {
        "status": "fail" if claude_status or policy_errors else "pass",
        "claude_validation": claude_results,
        "policy_validation": policies,
        "summary": {
            "skills": len(skills),
            "policy_errors": policy_errors,
            "policy_warnings": sum(len(report["warnings"]) for report in policies),
        },
    }
    print(json.dumps(report, indent=2))
    return 1 if claude_status or policy_errors else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
