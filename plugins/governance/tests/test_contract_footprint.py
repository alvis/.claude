from __future__ import annotations

from pathlib import Path

from contract_footprint import check_plugin

PLUGIN = Path(__file__).resolve().parents[1]

# This plugin owns both lists: what it injects at hook time, and what a session
# must read before acting in its domain.
PAYLOADS = ("CLAUDE.md",)
CHAIN = ("CLAUDE.md", "references/WORKFLOW.md", "references/ROUTING.md")


def test_contract_footprint_stays_within_budget() -> None:
    assert check_plugin(PLUGIN, PAYLOADS, CHAIN) == []
