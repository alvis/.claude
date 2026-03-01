"""OpenAI GPT Image generation provider.

Supports ``gpt-image-1.5`` and ``gpt-image-1-mini`` via the ``openai`` SDK.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import Any

from providers import ImageProvider, register_provider


MODEL_PARAMS: dict[str, dict[str, Any]] = {
    "model": {
        "default": "gpt-image-1.5",
        "choices": ["gpt-image-1.5", "gpt-image-1-mini"],
        "help": "OpenAI image model",
    },
    "size": {
        "default": "1024x1024",
        "choices": ["1024x1024", "1536x1024", "1024x1536", "auto"],
        "help": "Output size in pixels",
    },
    "quality": {
        "default": "auto",
        "choices": ["low", "medium", "high", "auto"],
        "help": "Image quality level",
    },
    "background": {
        "default": None,
        "choices": ["transparent", "opaque", "auto"],
        "help": "Background mode (transparent requires png/webp output)",
    },
    "output_format": {
        "default": "png",
        "choices": ["png", "jpeg", "webp"],
        "help": "Output image format",
    },
    "output_compression": {
        "default": None,
        "type": "int",
        "range": [0, 100],
        "help": "Compression level 0-100 (jpeg/webp only)",
    },
    "input_fidelity": {
        "default": None,
        "choices": ["low", "high"],
        "edit_only": True,
        "help": "Edit fidelity (high=strict identity/layout lock)",
    },
    "moderation": {
        "default": None,
        "choices": ["auto", "low"],
        "help": "Content moderation level",
    },
    "n": {
        "default": 1,
        "type": "int",
        "range": [1, 10],
        "help": "Number of images to generate (1-10)",
    },
}


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def _create_client() -> Any:
    """Lazily create an OpenAI sync client."""
    try:
        from openai import OpenAI  # type: ignore[import-untyped]
    except ImportError:
        _die("openai SDK not installed. Install with `uv pip install openai`.")
    return OpenAI()


def _create_async_client() -> Any:
    """Lazily create an OpenAI async client."""
    try:
        from openai import AsyncOpenAI  # type: ignore[import-untyped]
    except ImportError:
        try:
            import openai as _openai  # noqa: F401
        except ImportError:
            _die("openai SDK not installed. Install with `uv pip install openai`.")
        _die(
            "AsyncOpenAI not available in this openai SDK version. "
            "Upgrade with `uv pip install -U openai`."
        )
    return AsyncOpenAI()


def _validate_transparency(background: str | None, output_format: str) -> None:
    if background == "transparent" and output_format not in {"png", "webp"}:
        _die("transparent background requires output-format png or webp.")


def _normalize_output_format(fmt: str | None) -> str:
    if not fmt:
        return str(MODEL_PARAMS["output_format"]["default"])
    fmt = fmt.lower()
    if fmt not in {"png", "jpeg", "jpg", "webp"}:
        _die("output-format must be png, jpeg, jpg, or webp.")
    return "jpeg" if fmt == "jpg" else fmt


class _NullContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False


class _SingleFile:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: Any = None

    def __enter__(self) -> Any:
        self._handle = self._path.open("rb")
        return self._handle

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if self._handle:
            try:
                self._handle.close()
            except Exception:
                pass
        return False


class _FileBundle:
    def __init__(self, paths: list[Path]) -> None:
        self._paths = paths
        self._handles: list[Any] = []

    def __enter__(self) -> list[Any]:
        self._handles = [p.open("rb") for p in self._paths]
        return self._handles

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        for handle in self._handles:
            try:
                handle.close()
            except Exception:
                pass
        return False


@register_provider
class GPTImageProvider(ImageProvider):
    """OpenAI GPT Image generation and editing."""

    name = "openai"
    env_var = "OPENAI_API_KEY"
    MODEL_PARAMS = MODEL_PARAMS

    def _build_payload(self, prompt: str, args: Any) -> dict[str, Any]:
        """Build an API payload dict from parsed args."""
        payload: dict[str, Any] = {
            "model": getattr(args, "model", None) or MODEL_PARAMS["model"]["default"],
            "prompt": prompt,
            "n": getattr(args, "n", 1) or 1,
            "size": getattr(args, "size", None) or MODEL_PARAMS["size"]["default"],
            "quality": getattr(args, "quality", None) or MODEL_PARAMS["quality"]["default"],
        }

        for key in ("background", "output_format", "output_compression", "moderation"):
            val = getattr(args, key, None)
            if val is not None:
                payload[key] = val

        output_format = _normalize_output_format(payload.get("output_format"))
        if "output_format" in payload:
            payload["output_format"] = output_format

        _validate_transparency(payload.get("background"), output_format)

        return {k: v for k, v in payload.items() if v is not None}

    def _build_edit_payload(self, prompt: str, args: Any) -> dict[str, Any]:
        """Build an edit API payload dict from parsed args."""
        payload = self._build_payload(prompt, args)
        input_fidelity = getattr(args, "input_fidelity", None)
        if input_fidelity is not None:
            payload["input_fidelity"] = input_fidelity
        return payload

    def generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        need_edit = bool(images or references)

        if need_edit:
            payload = self._build_edit_payload(prompt, args)
            # Combine images + references into one list for OpenAI edit endpoint
            all_image_paths = list(images or []) + list(references or [])
            if references and not images:
                print(
                    "OpenAI: using edit endpoint for style reference support.",
                    file=sys.stderr,
                )
            print(
                f"Calling OpenAI Image API (edit) with {len(all_image_paths)} image(s).",
                file=sys.stderr,
            )
            started = time.time()
            client = _create_client()

            with _FileBundle(all_image_paths) as image_files, (
                _SingleFile(mask) if mask else _NullContext()
            ) as mask_file:
                request = dict(payload)
                request["image"] = image_files if len(image_files) > 1 else image_files[0]
                if mask_file is not None:
                    request["mask"] = mask_file
                result = client.images.edit(**request)

            elapsed = time.time() - started
            print(f"Edit completed in {elapsed:.1f}s.", file=sys.stderr)
            return [item.b64_json for item in result.data]

        # Pure generation
        payload = self._build_payload(prompt, args)
        print(
            "Calling OpenAI Image API (generation). This can take up to a couple of minutes.",
            file=sys.stderr,
        )
        started = time.time()
        client = _create_client()
        result = client.images.generate(**payload)
        elapsed = time.time() - started
        print(f"Generation completed in {elapsed:.1f}s.", file=sys.stderr)
        return [item.b64_json for item in result.data]

    async def async_generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        need_edit = bool(images or references)

        if need_edit:
            payload = self._build_edit_payload(prompt, args)
            all_image_paths = list(images or []) + list(references or [])
            client = _create_async_client()

            with _FileBundle(all_image_paths) as image_files, (
                _SingleFile(mask) if mask else _NullContext()
            ) as mask_file:
                request = dict(payload)
                request["image"] = image_files if len(image_files) > 1 else image_files[0]
                if mask_file is not None:
                    request["mask"] = mask_file
                result = await client.images.edit(**request)

            return [item.b64_json for item in result.data]

        payload = self._build_payload(prompt, args)
        client = _create_async_client()
        result = await client.images.generate(**payload)
        return [item.b64_json for item in result.data]

    def dry_run_payload(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> dict[str, Any]:
        need_edit = bool(images or references)
        if need_edit:
            payload = self._build_edit_payload(prompt, args)
            payload["endpoint"] = "/v1/images/edits"
            all_image_paths = list(images or []) + list(references or [])
            payload["image"] = [str(p) for p in all_image_paths]
            if references:
                payload["references"] = [str(p) for p in references]
            if mask:
                payload["mask"] = str(mask)
        else:
            payload = self._build_payload(prompt, args)
            payload["endpoint"] = "/v1/images/generations"
        payload["provider"] = "openai"
        return payload
