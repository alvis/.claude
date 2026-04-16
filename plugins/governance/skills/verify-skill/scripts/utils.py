"""Shared utilities for verify-skill scripts.

Provides YAML frontmatter parsing, file path helpers, and common constants.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FRONTMATTER_FIELDS: list[str] = ["name", "description"]

OPTIONAL_FRONTMATTER_FIELDS: list[str] = [
    "model",
    "context",
    "agent",
    "allowed-tools",
]

VALID_MODELS: list[str] = ["opus", "sonnet", "haiku"]
VALID_CONTEXTS: list[str] = ["fork", "none"]

REQUIRED_SECTIONS: list[str] = [
    "INTRODUCTION",
    "SKILL OVERVIEW",
    "SKILL IMPLEMENTATION",
]

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def parse_frontmatter(skill_path: str) -> dict:
    """Parse YAML frontmatter from a SKILL.md file.

    Frontmatter is the content between the first pair of ``---`` delimiters at
    the top of the file.

    Args:
        skill_path: Absolute path to a SKILL.md file.

    Returns:
        A dict of parsed frontmatter fields.

    Raises:
        ValueError: If no valid frontmatter block is found.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(skill_path)
    if not path.is_file():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Frontmatter must start with --- on the very first line.
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"No YAML frontmatter found in {skill_path}")

    end_index: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        raise ValueError(f"Unclosed YAML frontmatter in {skill_path}")

    frontmatter_text = "\n".join(lines[1:end_index])
    parsed = yaml.safe_load(frontmatter_text)

    if not isinstance(parsed, dict):
        raise ValueError(f"Frontmatter did not parse as a mapping in {skill_path}")

    return parsed


def load_evals(skill_dir: str) -> dict | None:
    """Load evals/evals.yaml from a skill directory.

    Args:
        skill_dir: Absolute path to the skill directory (parent of SKILL.md).

    Returns:
        Parsed YAML dict, or ``None`` if the file does not exist.
    """
    evals_path = Path(skill_dir) / "evals" / "evals.yaml"
    if not evals_path.is_file():
        return None
    return yaml.safe_load(evals_path.read_text(encoding="utf-8"))


def get_skill_dir(skill_path: str) -> str:
    """Get the parent directory of a SKILL.md file.

    Args:
        skill_path: Absolute path to a SKILL.md file.

    Returns:
        The parent directory as a string.
    """
    return str(Path(skill_path).parent)


def write_yaml_report(data: dict, output_path: str) -> None:
    """Write a dict as YAML to a file.

    Args:
        data: The data to serialise.
        output_path: Destination file path.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def read_yaml(path: str) -> dict:
    """Read and parse a YAML file.

    Args:
        path: Absolute path to the YAML file.

    Returns:
        Parsed YAML as a dict.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"YAML file not found: {path}")
    result = yaml.safe_load(p.read_text(encoding="utf-8"))
    if result is None:
        return {}
    return result


def get_skill_name_from_path(skill_path: str) -> str:
    """Extract the skill name from its file path.

    The skill name is the immediate parent directory of the SKILL.md file.
    For example ``/path/to/my-skill/SKILL.md`` yields ``my-skill``.

    Args:
        skill_path: Absolute path to a SKILL.md file.

    Returns:
        The skill name string.
    """
    return Path(skill_path).parent.name
