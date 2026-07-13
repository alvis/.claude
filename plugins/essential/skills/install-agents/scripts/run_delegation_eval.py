#!/usr/bin/env python3
"""Opt-in live check that runtime agent discovery beats a fixed collaborator list."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from typing import Any, List


SYNTHETIC_REVIEWER = "synthetic-runtime-reviewer"


def extract_agent_targets(lines: Iterable[str]) -> List[str]:
    """Return subagent types from actual Agent tool calls in stream-json output."""
    targets: List[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("type") == "tool_use" and value.get("name") == "Agent":
                target = value.get("input", {}).get("subagent_type")
                if isinstance(target, str):
                    targets.append(target)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for line in lines:
        try:
            visit(json.loads(line))
        except json.JSONDecodeError:
            continue
    return targets


def build_command(
    agents: dict[str, Any], budget: str = "0.30", model: str | None = None
) -> List[str]:
    """Build a Claude CLI command isolated from user/project configuration."""
    command = [
        "claude",
        "-p",
        "--bare",
        "Delegate this task: review fr-FR ICU message changes for placeholder parity and fallback safety.",
        "--agent",
        "runtime-aware-router",
        "--agents",
        json.dumps(agents, separators=(",", ":")),
        "--setting-sources",
        "",
        "--disable-slash-commands",
        "--no-chrome",
        "--mcp-config",
        "{}",
        "--strict-mcp-config",
        "--tools",
        "Agent",
        "--allowedTools",
        "Agent",
        "--permission-mode",
        "dontAsk",
        "--output-format",
        "stream-json",
        "--no-session-persistence",
        "--max-budget-usd",
        budget,
    ]
    if model:
        command.extend(("--model", model))
    return command


def main() -> int:
    if os.environ.get("RUN_LIVE_AGENT_EVAL") != "1":
        print("SKIP: set RUN_LIVE_AGENT_EVAL=1 to run the paid Claude CLI delegation eval")
        return 0

    agents = {
        "runtime-aware-router": {
            "description": "Delegation router; inspects runtime agents and assigns work to the best fit.",
            "prompt": (
                "Inspect the current Agent roster before delegating. Named collaborators are "
                "defaults, not limits. For the user's request, call Agent exactly once with the "
                "best available specialist; do not perform the review yourself."
            ),
            "tools": ["Agent"],
        },
        "known-general-reviewer": {
            "description": "General code reviewer; checks maintainability and correctness.",
            "prompt": "Review code generally and return concise findings.",
            "tools": [],
        },
        SYNTHETIC_REVIEWER: {
            "description": (
                "Localization review specialist; reviews ICU message changes for placeholder "
                "parity, locale correctness, and fallback safety."
            ),
            "prompt": "Review localization changes for ICU placeholder and fallback defects.",
            "tools": [],
        },
    }
    command = build_command(
        agents,
        budget=os.environ.get("DELEGATION_EVAL_BUDGET_USD", "0.30"),
        model=os.environ.get("DELEGATION_EVAL_MODEL"),
    )

    with tempfile.TemporaryDirectory(prefix="delegation-eval-") as workdir:
        completed = subprocess.run(
            command,
            cwd=workdir,
            text=True,
            capture_output=True,
            check=False,
        )

    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        return completed.returncode

    targets = extract_agent_targets(completed.stdout.splitlines())
    if targets != [SYNTHETIC_REVIEWER]:
        print(
            f"FAIL: expected one Agent call to {SYNTHETIC_REVIEWER}, observed {targets}",
            file=sys.stderr,
        )
        return 1

    print(f"PASS: runtime router delegated to {SYNTHETIC_REVIEWER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
