#!/usr/bin/env python3
"""Project the authoritative Claude marketplace into Codex's catalog shape."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".claude-plugin" / "marketplace.json"
TARGET = ROOT / ".agents" / "plugins" / "marketplace.json"


def project_marketplace(source: dict[str, object]) -> dict[str, object]:
    owner = source.get("owner")
    owner_name = (
        owner.get("name")
        if isinstance(owner, dict) and isinstance(owner.get("name"), str)
        else source["name"]
    )
    plugins = source["plugins"]
    assert isinstance(plugins, list)
    return {
        "name": source["name"],
        "interface": {"displayName": owner_name},
        "plugins": [
            {
                "name": plugin["name"],
                "source": {
                    "source": "local",
                    "path": plugin["source"],
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": plugin["category"],
            }
            for plugin in plugins
            if isinstance(plugin, dict)
        ],
    }


def render_projection() -> str:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    return json.dumps(project_marketplace(source), indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the committed Codex projection is stale.",
    )
    args = parser.parse_args()
    rendered = render_projection()
    if args.check:
        if not TARGET.is_file() or TARGET.read_text(encoding="utf-8") != rendered:
            parser.error(
                "Codex marketplace projection is stale; rerun this script"
            )
        return 0
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
