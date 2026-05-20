"""Rule discovery — auto-load every module in the scanners package."""

import importlib
import pkgutil
import sys

from scanlib.rule import Rule


def load_rules(*, package: str = "scanners") -> list[Rule]:
    """Import every non-underscore module in ``package`` and collect its rules.

    A module contributes either a single ``RULE`` or a ``RULES`` iterable.
    Discovered rules are sorted by ``(order, id)`` to fix output order.
    """
    pkg = importlib.import_module(package)
    rules: list[Rule] = []
    for info in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"{package}.{info.name}")
        except Exception as exc:  # noqa: BLE001 — advisory tool, isolate per-module failures
            print(f"warn: failed to load rule module {info.name}: {exc}", file=sys.stderr)
            continue
        found = getattr(mod, "RULES", None)
        if found is None:
            single = getattr(mod, "RULE", None)
            found = [single] if single is not None else []
        rules.extend(found)
    rules.sort(key=lambda r: (r.order, r.id))
    return rules
