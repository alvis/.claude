#!/usr/bin/env python3
"""Create a collision-safe temporary preview with canonical shared assets."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


DISCOVER_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = DISCOVER_ROOT / "examples" / "html"
ASSETS_ROOT = DISCOVER_ROOT / "assets" / "html"


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "preview"


def render_preview(example_name: str) -> Path:
    example_slug = slug(example_name.removesuffix(".html"))
    source = EXAMPLES_ROOT / f"{example_slug}.html"
    if not source.is_file():
        raise FileNotFoundError(f"No discovery example found at {source}")

    preview_dir = Path(
        tempfile.mkdtemp(prefix=f"essential-discover-claude-{example_slug}-")
    )
    destination = preview_dir / "page.html"
    html = source.read_text(encoding="utf-8")
    shared_assets = preview_dir / "shared"
    try:
        os.symlink(ASSETS_ROOT, shared_assets, target_is_directory=True)
        stylesheet_url = "./shared/discovery.css"
        script_url = "./shared/discovery.js"
    except OSError:
        stylesheet_url = (ASSETS_ROOT / "discovery.css").as_uri()
        script_url = (ASSETS_ROOT / "discovery.js").as_uri()
    html = html.replace(
        'href="../../assets/html/discovery.css"',
        f'href="{stylesheet_url}"',
        1,
    )
    html = html.replace(
        'src="../../assets/html/discovery.js"',
        f'src="{script_url}"',
        1,
    )
    html = html.replace(
        'data-page-id="',
        f'data-page-id="{preview_dir.name}-',
        1,
    )
    destination.write_text(html, encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an OS-temp Discover HTML preview."
    )
    parser.add_argument(
        "example",
        nargs="?",
        default="domain-explainer",
        help="Example filename or action slug (default: domain-explainer)",
    )
    args = parser.parse_args()

    preview = render_preview(args.example)
    print(
        json.dumps(
            {
                "status": "created",
                "path": str(preview),
                "url": preview.as_uri(),
                "serve_root": str(preview.parent),
                "asset_mode": "canonical-symlink"
                if (preview.parent / "shared").is_symlink()
                else "file-uri",
                "disposable": True,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
