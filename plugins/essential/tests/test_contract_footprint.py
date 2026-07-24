from __future__ import annotations

from pathlib import Path
import unittest


ESSENTIAL = Path(__file__).resolve().parents[1]

# The mandatory read chain a PM session pays before touching engineering
# artifacts. Growth past the budget must be a conscious review decision:
# move detail into a per-moment reference instead of growing these files.
MANDATORY_CHAIN = (
    "CLAUDE.md",
    "references/orchestration.md",
    "references/engineering-work.md",
    "references/engineering-work-state.md",
)
CHAIN_BUDGET_BYTES = 40_960


class ContractFootprintTest(unittest.TestCase):
    def test_mandatory_chain_stays_within_budget(self) -> None:
        sizes = {
            relative: (ESSENTIAL / relative).stat().st_size
            for relative in MANDATORY_CHAIN
        }
        total = sum(sizes.values())
        breakdown = ", ".join(
            f"{relative}={size}" for relative, size in sizes.items()
        )
        self.assertLessEqual(
            total,
            CHAIN_BUDGET_BYTES,
            f"mandatory read chain is {total} bytes ({breakdown}); "
            f"budget is {CHAIN_BUDGET_BYTES}. Move detail into a per-moment "
            "reference instead of growing an always-read file.",
        )

    def test_injected_entry_point_stays_within_hook_limit(self) -> None:
        self.assertLessEqual((ESSENTIAL / "CLAUDE.md").stat().st_size, 2_000)


if __name__ == "__main__":
    unittest.main()
