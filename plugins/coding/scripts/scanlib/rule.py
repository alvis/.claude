"""Rule dataclass describing one auto-loaded scanner."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from scanlib.predicates import source_files

type Scanner = Callable[..., None]


@dataclass(frozen=True, slots=True)
class Rule:
    """One standard-violation scanner discovered from the ``scanners`` package.

    A rule module exports either a single ``RULE`` or a ``RULES`` tuple of
    instances; the loader sorts them by ``(order, id)`` to fix output order.
    """

    id: str
    label: str
    scan: Scanner
    order: int
    applies_to: Callable[[Path], bool] = source_files
    honor_no_tests: bool = False
    # reserved traceability metadata — constitution rule IDs this scanner
    # relates to; currently carried for documentation, not read by the engine.
    rule_refs: tuple[str, ...] = ()
