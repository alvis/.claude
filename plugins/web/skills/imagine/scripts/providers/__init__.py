"""Base provider class, registry, and parameter system for image generation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any


class ImageProvider:
    """Base class for image generation providers.

    Subclasses must define ``name``, ``env_var``, and ``MODEL_PARAMS`` at the
    class level and implement the generation/editing hooks.

    ``MODEL_PARAMS`` is a dict of parameter definitions used to:
    - Register CLI arguments via ``register_args``
    - Validate user-supplied values via ``validate``
    - Power ``--help`` output for each provider
    """

    name: str
    env_var: str
    MODEL_PARAMS: dict[str, dict[str, Any]]

    # ------------------------------------------------------------------
    # API key helpers
    # ------------------------------------------------------------------

    def ensure_api_key(self, dry_run: bool) -> None:
        key = os.getenv(self.env_var)
        if key:
            print(f"{self.env_var} is set.", file=sys.stderr)
            return
        if dry_run:
            print(f"Warning: {self.env_var} is not set; dry-run only.", file=sys.stderr)
            return
        print(f"Error: {self.env_var} is not set. Export it before running.", file=sys.stderr)
        raise SystemExit(1)

    # ------------------------------------------------------------------
    # Argument registration (drives ``--help``)
    # ------------------------------------------------------------------

    def register_args(self, parser: argparse.ArgumentParser) -> None:
        """Add model-specific arguments to *parser* from ``MODEL_PARAMS``."""
        for param_name, spec in self.MODEL_PARAMS.items():
            flag = f"--{param_name.replace('_', '-')}"

            # Skip if the parser already knows this flag (shared args).
            if any(flag in action.option_strings for action in parser._actions):
                continue

            kwargs: dict[str, Any] = {}
            kwargs["help"] = spec.get("help", "")
            kwargs["default"] = spec.get("default")

            if "choices" in spec:
                kwargs["choices"] = spec["choices"]

            if spec.get("type") == "int":
                kwargs["type"] = int

            if spec.get("edit_only"):
                kwargs["help"] += " (requires --image)"

            parser.add_argument(flag, **kwargs)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, args: argparse.Namespace) -> None:
        """Validate parsed *args* against ``MODEL_PARAMS``."""
        for param_name, spec in self.MODEL_PARAMS.items():
            value = getattr(args, param_name, None)
            if value is None:
                continue

            if "choices" in spec and value not in spec["choices"]:
                allowed = ", ".join(str(c) for c in spec["choices"])
                _die(f"--{param_name.replace('_', '-')} must be one of: {allowed}")

            if spec.get("type") == "int" and "range" in spec:
                lo, hi = spec["range"]
                try:
                    int_val = int(value)
                except (TypeError, ValueError):
                    _die(f"--{param_name.replace('_', '-')} must be an integer")
                    return  # unreachable
                if int_val < lo or int_val > hi:
                    _die(f"--{param_name.replace('_', '-')} must be between {lo} and {hi}")

    # ------------------------------------------------------------------
    # Provider hooks (subclasses must implement)
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        args: argparse.Namespace,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        """Generate or edit images and return a list of base64-encoded strings.

        If *images* are provided the call is treated as an edit.  *references*
        supply style-guide images that influence visual output.
        """
        raise NotImplementedError

    async def async_generate(
        self,
        prompt: str,
        args: argparse.Namespace,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        """Async variant of ``generate`` for batch/concurrent use."""
        raise NotImplementedError

    def dry_run_payload(
        self,
        prompt: str,
        args: argparse.Namespace,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> dict[str, Any]:
        """Return a dict representing the API call (for ``--dry-run``)."""
        raise NotImplementedError


# ======================================================================
# Provider registry
# ======================================================================

PROVIDER_REGISTRY: dict[str, type[ImageProvider]] = {}


def register_provider(cls: type[ImageProvider]) -> type[ImageProvider]:
    """Class decorator that registers a provider by its ``name``."""
    PROVIDER_REGISTRY[cls.name] = cls
    return cls


def get_provider(name: str) -> ImageProvider:
    """Instantiate and return the provider for *name*."""
    cls = PROVIDER_REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY)) or "(none)"
        _die(f"Unknown provider '{name}'. Available: {available}")
        raise SystemExit(1)  # unreachable – keeps mypy happy
    return cls()


# ======================================================================
# Shared helpers
# ======================================================================

def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)
