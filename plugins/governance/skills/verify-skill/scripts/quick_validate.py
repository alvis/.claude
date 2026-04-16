"""Quick structural validation for SKILL.md files.

Validates frontmatter schema, required sections, and basic content quality.
Can be run standalone: python quick_validate.py /path/to/SKILL.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from utils import (
    OPTIONAL_FRONTMATTER_FIELDS,
    REQUIRED_FRONTMATTER_FIELDS,
    REQUIRED_SECTIONS,
    VALID_CONTEXTS,
    VALID_MODELS,
    get_skill_name_from_path,
    parse_frontmatter,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def _issue(level: str, field: str, message: str) -> dict:
    return {"level": level, "field": field, "message": message}


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


def validate_frontmatter(frontmatter: dict, skill_path: str) -> list[dict]:
    """Validate frontmatter fields against the skill schema.

    Checks required fields, value constraints, naming conventions, and
    trigger-description quality.

    Args:
        frontmatter: Parsed frontmatter dict.
        skill_path: Path to the SKILL.md (used for directory-name matching).

    Returns:
        List of issue dicts with ``level``, ``field``, and ``message`` keys.
    """
    issues: list[dict] = []

    # --- Required fields ---------------------------------------------------
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in frontmatter:
            issues.append(_issue("error", field, f"Required field '{field}' is missing"))

    # --- name checks -------------------------------------------------------
    name = frontmatter.get("name")
    if name is not None:
        if not _KEBAB_RE.match(str(name)):
            issues.append(
                _issue("error", "name", f"Name '{name}' is not valid kebab-case")
            )
        expected_name = get_skill_name_from_path(skill_path)
        if str(name) != expected_name:
            issues.append(
                _issue(
                    "error",
                    "name",
                    f"Name '{name}' does not match directory name '{expected_name}'",
                )
            )

    # --- description checks ------------------------------------------------
    description = frontmatter.get("description")
    if description is not None:
        desc_str = str(description)
        if "use when" not in desc_str.lower():
            issues.append(
                _issue(
                    "warning",
                    "description",
                    "Description should contain a 'Use when' clause for trigger matching",
                )
            )

    # --- Optional field value validation -----------------------------------
    model = frontmatter.get("model")
    if model is not None and str(model) not in VALID_MODELS:
        issues.append(
            _issue(
                "error",
                "model",
                f"Invalid model '{model}'. Valid: {VALID_MODELS}",
            )
        )

    context = frontmatter.get("context")
    if context is not None and str(context) not in VALID_CONTEXTS:
        issues.append(
            _issue(
                "error",
                "context",
                f"Invalid context '{context}'. Valid: {VALID_CONTEXTS}",
            )
        )

    # Warn on unknown optional fields (fields not in either required or
    # optional lists).
    known_fields = set(REQUIRED_FRONTMATTER_FIELDS) | set(OPTIONAL_FRONTMATTER_FIELDS)
    for key in frontmatter:
        if key not in known_fields:
            issues.append(
                _issue("warning", key, f"Unknown frontmatter field '{key}'")
            )

    return issues


def validate_sections(content: str) -> list[dict]:
    """Check that all required sections exist and are ordered correctly.

    Looks for markdown headings matching ``## 1. INTRODUCTION``,
    ``## INTRODUCTION``, etc.

    Args:
        content: Full text content of the SKILL.md file.

    Returns:
        List of issue dicts.
    """
    issues: list[dict] = []

    # Build a pattern for each required section that tolerates optional
    # numbering: "## 1. INTRODUCTION" or "## INTRODUCTION".
    section_positions: dict[str, int] = {}
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+(?:\d+\.\s+)?{re.escape(section)}"
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            section_positions[section] = match.start()
        else:
            issues.append(
                _issue("error", "sections", f"Required section '{section}' not found")
            )

    # Check ordering -- each found section should appear after the previous.
    found_sections = [s for s in REQUIRED_SECTIONS if s in section_positions]
    for i in range(1, len(found_sections)):
        prev, curr = found_sections[i - 1], found_sections[i]
        if section_positions[curr] < section_positions[prev]:
            issues.append(
                _issue(
                    "error",
                    "sections",
                    f"Section '{curr}' appears before '{prev}' -- wrong order",
                )
            )

    # Warn on leftover template instruction comments.
    if "<!-- INSTRUCTION:" in content:
        issues.append(
            _issue(
                "warning",
                "sections",
                "Leftover template <!-- INSTRUCTION: --> comment(s) found",
            )
        )

    return issues


def validate_content_quality(content: str) -> list[dict]:
    """Run basic content quality checks on the skill body.

    Checks for ASCII diagrams, subagent instruction blocks, skill completion
    sections, and placeholder text.

    Args:
        content: Full text content of the SKILL.md file.

    Returns:
        List of issue dicts.
    """
    issues: list[dict] = []

    # ASCII diagram -- look for ```plaintext blocks.
    if "```plaintext" not in content:
        issues.append(
            _issue(
                "warning",
                "content",
                "No ASCII diagram found (expected a ```plaintext block)",
            )
        )

    # Subagent instruction blocks -- look for >>> / <<< delimiters.
    has_open = ">>>" in content
    has_close = "<<<" in content
    if not has_open or not has_close:
        issues.append(
            _issue(
                "warning",
                "content",
                "No subagent instruction blocks found (expected >>> and <<< delimiters)",
            )
        )

    # Skill completion section.
    if "Skill Completion" not in content and "SKILL COMPLETION" not in content.upper():
        issues.append(
            _issue("warning", "content", "No 'Skill Completion' section found")
        )

    # Placeholder text detection.
    placeholder_patterns = [
        r"\[Step Name\]",
        r"\[Description\]",
        r"\[TODO\]",
        r"\[PLACEHOLDER\]",
        r"\[INSERT ",
    ]
    for pat in placeholder_patterns:
        if re.search(pat, content, re.IGNORECASE):
            issues.append(
                _issue(
                    "warning",
                    "content",
                    f"Placeholder text detected matching pattern: {pat}",
                )
            )

    return issues


# ---------------------------------------------------------------------------
# Top-level validate
# ---------------------------------------------------------------------------


def validate(skill_path: str) -> dict:
    """Run all structural validations on a SKILL.md file.

    Args:
        skill_path: Absolute path to the SKILL.md file.

    Returns:
        A dict containing overall status, per-category results, and counts.
    """
    path = Path(skill_path)
    if not path.is_file():
        return {
            "status": "fail",
            "frontmatter": {
                "status": "fail",
                "issues": [_issue("error", "file", f"File not found: {skill_path}")],
            },
            "sections": {"status": "fail", "issues": []},
            "content_quality": {"status": "fail", "issues": []},
            "total_errors": 1,
            "total_warnings": 0,
        }

    content = path.read_text(encoding="utf-8")

    # --- Frontmatter -------------------------------------------------------
    try:
        frontmatter = parse_frontmatter(skill_path)
        fm_issues = validate_frontmatter(frontmatter, skill_path)
    except (ValueError, FileNotFoundError) as exc:
        fm_issues = [_issue("error", "frontmatter", str(exc))]

    fm_errors = [i for i in fm_issues if i["level"] == "error"]
    fm_status = "fail" if fm_errors else "pass"

    # --- Sections ----------------------------------------------------------
    sec_issues = validate_sections(content)
    sec_errors = [i for i in sec_issues if i["level"] == "error"]
    sec_status = "fail" if sec_errors else "pass"

    # --- Content quality ---------------------------------------------------
    cq_issues = validate_content_quality(content)
    cq_errors = [i for i in cq_issues if i["level"] == "error"]
    cq_status = "fail" if cq_errors else "pass"

    # --- Aggregate ---------------------------------------------------------
    all_issues = fm_issues + sec_issues + cq_issues
    total_errors = sum(1 for i in all_issues if i["level"] == "error")
    total_warnings = sum(1 for i in all_issues if i["level"] == "warning")
    overall = "fail" if total_errors > 0 else "pass"

    return {
        "status": overall,
        "frontmatter": {"status": fm_status, "issues": fm_issues},
        "sections": {"status": sec_status, "issues": sec_issues},
        "content_quality": {"status": cq_status, "issues": cq_issues},
        "total_errors": total_errors,
        "total_warnings": total_warnings,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quick structural validation for SKILL.md files."
    )
    parser.add_argument("skill_path", help="Path to the SKILL.md file to validate")
    args = parser.parse_args()

    result = validate(args.skill_path)

    print(yaml.safe_dump(result, default_flow_style=False, sort_keys=False))

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
