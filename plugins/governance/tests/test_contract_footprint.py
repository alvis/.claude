from __future__ import annotations

from pathlib import Path
import sys
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN.parents[1] / "scripts"))

from contract_footprint import check_plugin  # noqa: E402


# This plugin owns both lists: what it injects at hook time, and what a session
# must read before acting in its domain.
PAYLOADS = ("CLAUDE.md",)
CHAIN = ("CLAUDE.md", "references/ROUTING.md")


class ContractFootprintTest(unittest.TestCase):
    def test_contract_footprint_stays_within_budget(self) -> None:
        self.assertEqual(check_plugin(PLUGIN, PAYLOADS, CHAIN), [])


if __name__ == "__main__":
    unittest.main()
