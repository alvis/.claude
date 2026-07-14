#!/usr/bin/env python3
"""Validate and stitch a split agent template into a Claude agent file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


AGENT_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FIXED_ROUTING_LANGUAGE = re.compile(
    r"\b(?:only|always)\s+(?:spawn|delegate|route)\b"
    r"|\bAgent` tool for one purpose\b"
    r"|\bI am the only agent who forms\b",
    re.IGNORECASE,
)
SHARED_POLICY_LANGUAGE = (
    "current `Agent` roster",
    "When I need a Dynamic Workflow",
    "For changed code, I inspect",
    "REVIEWED: source=",
    "I hold the `Agent` tool",
    "I hold `Agent`",
    "spawn target",
    "spawned by",
)
REVIEWER_DEFAULT = re.compile(
    r"[A-Z][a-z]+(?: [A-Z][a-z]+)+ \([^;\n()]+; [^)\n]+\)"
)


class AgentTemplateError(ValueError):
    """Raised when an agent source pair cannot produce a valid definition."""


def _reject_nonstandard_number(value: str) -> None:
    raise ValueError(f"non-standard JSON number: {value}")


def load_agent_frontmatter(template_directory: Path) -> dict[str, Any]:
    frontmatter_path = template_directory / "frontmatter/claude.json"
    base_path = template_directory / "base.md"
    if not frontmatter_path.is_file():
        raise AgentTemplateError(f"missing frontmatter/claude.json in {template_directory}")
    if not base_path.is_file():
        raise AgentTemplateError(f"missing base.md in {template_directory}")
    resolved_template = template_directory.resolve()
    for source_path in (frontmatter_path, base_path):
        try:
            source_path.resolve().relative_to(resolved_template)
        except ValueError as error:
            raise AgentTemplateError(
                f"template symlink or path escapes agent directory: {source_path}"
            ) from error
    try:
        frontmatter = json.loads(
            frontmatter_path.read_text(encoding="utf-8"),
            parse_constant=_reject_nonstandard_number,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise AgentTemplateError(f"invalid JSON in {frontmatter_path}: {error}") from error
    if not isinstance(frontmatter, dict):
        raise AgentTemplateError(f"frontmatter must be a JSON object: {frontmatter_path}")
    name = frontmatter.get("name")
    if not isinstance(name, str) or not AGENT_NAME.fullmatch(name):
        raise AgentTemplateError(f"invalid agent name in {frontmatter_path}: {name!r}")
    if name != template_directory.name:
        raise AgentTemplateError(
            f"frontmatter name {name!r} does not match directory {template_directory.name!r}"
        )
    return frontmatter


def _tool_names(frontmatter: dict[str, Any]) -> set[str] | None:
    tools = frontmatter.get("tools")
    if tools is None:
        return None
    if isinstance(tools, str):
        return {tool for tool in re.split(r"[\s,]+", tools) if tool}
    if isinstance(tools, list):
        return {tool for tool in tools if isinstance(tool, str)}
    return set()


def validate_agent_contract(frontmatter: dict[str, Any], body: str) -> None:
    """Reject agent definitions whose prose disagrees with their capabilities."""
    if frontmatter.get("model") == "haiku" and "effort" in frontmatter:
        raise AgentTemplateError("haiku agents must omit effort")

    routing_text = "\n".join(
        value
        for value in (
            body,
            frontmatter.get("description"),
            frontmatter.get("initialPrompt"),
        )
        if isinstance(value, str)
    )
    if FIXED_ROUTING_LANGUAGE.search(routing_text):
        raise AgentTemplateError(
            "fixed routing language conflicts with runtime discovery"
        )

    duplicated_policy = next(
        (phrase for phrase in SHARED_POLICY_LANGUAGE if phrase in body), None
    )
    if duplicated_policy:
        raise AgentTemplateError(
            f"agent body repeats shared delegation policy: {duplicated_policy}"
        )

    tools = _tool_names(frontmatter)
    if tools is not None and "SendMessage" in body and "SendMessage" not in tools:
        raise AgentTemplateError("mentions SendMessage but its tools omit it")
    if tools is not None and "SendMessage" not in tools:
        raise AgentTemplateError("explicit tools must include SendMessage")

    hooks = frontmatter.get("hooks", {})
    if isinstance(hooks, dict):
        for matcher in hooks.get("Stop", []):
            if not isinstance(matcher, dict):
                continue
            for hook in matcher.get("hooks", []):
                if not isinstance(hook, dict):
                    continue
                prompt = hook.get("prompt", "")
                if not isinstance(prompt, str) or "review-routing gate" not in prompt:
                    continue
                if (
                    len(REVIEWER_DEFAULT.findall(prompt)) < 1
                    or "proven defaults" not in prompt
                    or "better runtime specialist" not in prompt
                ):
                    raise AgentTemplateError(
                        "review-routing hook must name concrete reviewer defaults"
                    )
                if (
                    "independently inspect the changed artifact" not in prompt
                    or "return verdict ok or blocked with findings" not in prompt
                ):
                    raise AgentTemplateError(
                        "review-routing hook must state the independent review action"
                    )


def stitch_agent_definition(template_directory: Path) -> str:
    """Return one installable Markdown agent definition for a source pair."""
    template_directory = Path(template_directory)
    frontmatter = load_agent_frontmatter(template_directory)
    body = (template_directory / "base.md").read_text(encoding="utf-8").lstrip("\n")
    validate_agent_contract(frontmatter, body)
    yaml = json.dumps(frontmatter, ensure_ascii=False, indent=2, allow_nan=False)
    return f"---\n{yaml}\n---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        stitched = stitch_agent_definition(args.template)
    except AgentTemplateError as error:
        parser.error(str(error))
    if args.output:
        args.output.write_text(stitched, encoding="utf-8")
    else:
        print(stitched, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
