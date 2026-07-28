from __future__ import annotations

from pathlib import Path

from contract_footprint import check_plugin

PLUGIN = Path(__file__).resolve().parents[1]

# This plugin owns both lists: what it injects at hook time, and what a session
# must read before acting in its domain.
PAYLOADS = ("AGENTS.md", "MAINAGENT.md", "SUBAGENT.md")
CHAIN = (
    "AGENTS.md",
    "references/orchestration.md",
    "references/engineering-work.md",
    "references/engineering-work-state.md",
)


def test_contract_footprint_stays_within_budget() -> None:
    assert check_plugin(PLUGIN, PAYLOADS, CHAIN) == []
