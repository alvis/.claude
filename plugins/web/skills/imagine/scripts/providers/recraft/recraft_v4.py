"""Recraft image generation provider.

Supports Recraft V4, V4 Pro, V3, and V2 models (including vector variants)
via the OpenAI-compatible API at ``external.api.recraft.ai``.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any

from providers import ImageProvider, register_provider


# ======================================================================
# Size maps
# ======================================================================

V4_SIZES: dict[str, str] = {
    "1:1": "1024x1024",
    "2:1": "1536x768",
    "1:2": "768x1536",
    "3:2": "1280x832",
    "2:3": "832x1280",
    "4:3": "1216x896",
    "3:4": "896x1216",
    "5:4": "1152x896",
    "4:5": "896x1152",
    "16:9": "1344x768",
    "9:16": "768x1344",
    "6:10": "832x1344",
    "14:10": "1280x896",
    "10:14": "896x1280",
}

V4_PRO_SIZES: dict[str, str] = {
    "1:1": "2048x2048",
    "2:1": "3072x1536",
    "1:2": "1536x3072",
    "3:2": "2560x1664",
    "2:3": "1664x2560",
    "4:3": "2432x1792",
    "3:4": "1792x2432",
    "16:9": "2688x1536",
    "9:16": "1536x2688",
}

V3_V2_SIZES: set[str] = {
    "1024x1024",
    "1365x1024",
    "1024x1365",
    "1536x1024",
    "1024x1536",
    "1820x1024",
    "1024x1820",
    "1024x2048",
    "2048x1024",
    "1434x1024",
    "1024x1434",
    "1024x1280",
    "1280x1024",
    "1024x1707",
    "1707x1024",
}

# ======================================================================
# Named styles (V2/V3 only)
# ======================================================================

V3_STYLES: list[str] = [
    "any",
    "realistic_image",
    "digital_illustration",
    "vector_illustration",
    "icon",
]

V2_STYLES: list[str] = [
    "realistic_image",
    "digital_illustration",
    "vector_illustration",
    "icon",
    "realistic_image/b_and_w",
    "realistic_image/hard_flash",
    "realistic_image/hdr",
    "realistic_image/natural_light",
    "realistic_image/studio_portrait",
    "realistic_image/enterprise",
    "realistic_image/motion_blur",
    "digital_illustration/pixel_art",
    "digital_illustration/hand_drawn",
    "digital_illustration/grain",
    "digital_illustration/infantile_sketch",
    "digital_illustration/2d_art_poster",
    "digital_illustration/handmade_3d",
    "digital_illustration/hand_drawn_outline",
    "digital_illustration/engraving_color",
    "digital_illustration/2d_art_poster_2",
]

ALL_NAMED_STYLES: list[str] = sorted(set(V3_STYLES + V2_STYLES))

# ======================================================================
# Model lists
# ======================================================================

ALL_MODELS: list[str] = [
    "recraftv4",
    "recraftv4_vector",
    "recraftv4_pro",
    "recraftv4_pro_vector",
    "recraftv3",
    "recraftv3_vector",
    "recraftv2",
    "recraftv2_vector",
]

V4_MODELS: set[str] = {
    "recraftv4",
    "recraftv4_vector",
    "recraftv4_pro",
    "recraftv4_pro_vector",
}

V4_PRO_MODELS: set[str] = {
    "recraftv4_pro",
    "recraftv4_pro_vector",
}

V3_MODELS: set[str] = {
    "recraftv3",
    "recraftv3_vector",
}

V2_MODELS: set[str] = {
    "recraftv2",
    "recraftv2_vector",
}

V3_V2_MODELS: set[str] = V3_MODELS | V2_MODELS

VECTOR_MODELS: set[str] = {m for m in ALL_MODELS if "_vector" in m}

# ======================================================================
# MODEL_PARAMS
# ======================================================================

MODEL_PARAMS: dict[str, dict[str, Any]] = {
    "model": {
        "default": "recraftv4",
        "choices": ALL_MODELS,
        "help": "Recraft model variant",
    },
    "size": {
        "default": "1024x1024",
        "help": "Output size as WxH or aspect ratio (e.g. 16:9)",
    },
    "n": {
        "default": 1,
        "type": "int",
        "range": [1, 6],
        "help": "Number of images to generate (1-6)",
    },
    "output_format": {
        "default": None,
        "choices": ["png", "jpeg", "webp", "svg"],
        "help": "Output image format (auto: svg for vector models, png otherwise)",
    },
    "recraft_style": {
        "default": None,
        "choices": ALL_NAMED_STYLES,
        "help": "Named style preset (V2/V3 only; mutually exclusive with --style-id)",
    },
    "style_id": {
        "default": None,
        "help": "Custom style UUID",
    },
    "strength": {
        "default": None,
        "edit_only": True,
        "help": "Image-to-image strength 0-1",
    },
    "negative_prompt": {
        "default": None,
        "help": "Negative prompt (V2/V3 only)",
    },
}


# ======================================================================
# Helpers
# ======================================================================

def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def _is_aspect_ratio(value: str) -> bool:
    """Return True if *value* looks like an aspect ratio (e.g. ``16:9``)."""
    parts = value.split(":")
    return len(parts) == 2 and all(p.isdigit() for p in parts)


def _resolve_size(size_str: str, model: str) -> str:
    """Resolve an aspect-ratio shorthand or WxH string to a valid WxH value."""
    if model in V4_PRO_MODELS:
        size_map = V4_PRO_SIZES
        valid_wxh = set(V4_PRO_SIZES.values())
        label = "V4 Pro"
    elif model in V4_MODELS:
        size_map = V4_SIZES
        valid_wxh = set(V4_SIZES.values())
        label = "V4"
    else:
        size_map = {}
        valid_wxh = V3_V2_SIZES
        label = "V3/V2"

    if _is_aspect_ratio(size_str):
        resolved = size_map.get(size_str)
        if resolved is None:
            allowed = ", ".join(sorted(size_map.keys())) if size_map else "(none)"
            _die(
                f"Aspect ratio '{size_str}' is not valid for {label} models. "
                f"Allowed ratios: {allowed}"
            )
        return resolved

    if size_str not in valid_wxh:
        allowed = ", ".join(sorted(valid_wxh))
        _die(
            f"Size '{size_str}' is not valid for {label} models. "
            f"Allowed sizes: {allowed}"
        )
    return size_str


def _create_client() -> Any:
    """Lazily create a sync OpenAI client pointed at Recraft."""
    try:
        from openai import OpenAI  # type: ignore[import-untyped]
    except ImportError:
        _die("openai SDK not installed. Install with `uv pip install openai`.")
    return OpenAI(
        base_url="https://external.api.recraft.ai/v1",
        api_key=os.getenv("RECRAFT_API_TOKEN"),
    )


def _create_async_client() -> Any:
    """Lazily create an async OpenAI client pointed at Recraft."""
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
    return AsyncOpenAI(
        base_url="https://external.api.recraft.ai/v1",
        api_key=os.getenv("RECRAFT_API_TOKEN"),
    )


# ======================================================================
# Provider implementation
# ======================================================================

@register_provider
class RecraftProvider(ImageProvider):
    """Recraft image generation and editing via the OpenAI-compatible API."""

    name = "recraft"
    env_var = "RECRAFT_API_TOKEN"
    MODEL_PARAMS = MODEL_PARAMS

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, args: argparse.Namespace) -> None:
        """Validate Recraft-specific constraints on top of base validation."""
        super().validate(args)

        model = getattr(args, "model", None) or MODEL_PARAMS["model"]["default"]
        recraft_style = getattr(args, "recraft_style", None)
        style_id = getattr(args, "style_id", None)
        negative_prompt = getattr(args, "negative_prompt", None)

        if recraft_style and style_id:
            _die("--recraft-style and --style-id are mutually exclusive.")

        if recraft_style and model in V4_MODELS:
            _die(
                f"--recraft-style is only supported with V2/V3 models, "
                f"not '{model}'."
            )

        if negative_prompt and model in V4_MODELS:
            _die(
                f"--negative-prompt is only supported with V2/V3 models, "
                f"not '{model}'."
            )

        # Validate the style value against model-specific lists
        if recraft_style:
            if model in V3_MODELS and recraft_style not in V3_STYLES:
                allowed = ", ".join(V3_STYLES)
                _die(
                    f"--recraft-style '{recraft_style}' is not valid for V3 models. "
                    f"Allowed: {allowed}"
                )
            if model in V2_MODELS and recraft_style not in V2_STYLES:
                allowed = ", ".join(V2_STYLES)
                _die(
                    f"--recraft-style '{recraft_style}' is not valid for V2 models. "
                    f"Allowed: {allowed}"
                )

        # Validate size (resolve will _die on invalid)
        size = getattr(args, "size", None) or MODEL_PARAMS["size"]["default"]
        _resolve_size(size, model)

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------

    def _get_model(self, args: Any) -> str:
        return getattr(args, "model", None) or MODEL_PARAMS["model"]["default"]

    def _get_output_format(self, args: Any) -> str:
        model = self._get_model(args)
        fmt = getattr(args, "output_format", None)
        if fmt is None and model in VECTOR_MODELS:
            return "svg"
        return fmt or "png"

    def _build_extra_body(self, args: Any) -> dict[str, Any]:
        """Build the ``extra_body`` dict for Recraft-specific API params."""
        extra: dict[str, Any] = {}

        recraft_style = getattr(args, "recraft_style", None)
        if recraft_style:
            extra["style"] = recraft_style

        style_id = getattr(args, "style_id", None)
        if style_id:
            extra["style_id"] = style_id

        negative_prompt = getattr(args, "negative_prompt", None)
        if negative_prompt:
            extra["negative_prompt"] = negative_prompt

        return extra

    def _build_payload(self, prompt: str, args: Any) -> dict[str, Any]:
        """Build a generation API payload dict from parsed args."""
        model = self._get_model(args)
        size = getattr(args, "size", None) or MODEL_PARAMS["size"]["default"]
        resolved_size = _resolve_size(size, model)

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "n": getattr(args, "n", 1) or 1,
            "size": resolved_size,
            "response_format": "b64_json",
        }

        extra_body = self._build_extra_body(args)
        if extra_body:
            payload["extra_body"] = extra_body

        return payload

    # ------------------------------------------------------------------
    # Custom style creation (V3 only)
    # ------------------------------------------------------------------

    def _create_custom_style(
        self,
        client: Any,
        references: list[Path],
        base_style: str = "digital_illustration",
    ) -> str:
        """Upload reference images and create a custom style (V3 only)."""
        files = [
            ("file", (ref.name, ref.open("rb"), "image/png"))
            for ref in references
        ]
        response = client.post(
            "/styles",
            cast_to=object,
            body={"style": base_style},
            files=files,
        )
        return response["id"]

    # ------------------------------------------------------------------
    # Sync generation
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        model = self._get_model(args)
        output_format = self._get_output_format(args)
        client = _create_client()

        # --image + --mask => inpainting
        if images and mask:
            return self._inpaint_sync(client, prompt, args, images[0], mask)

        # --image => image-to-image
        if images:
            return self._image_to_image_sync(client, prompt, args, images[0])

        # --reference => custom style transfer (V3 only)
        if references:
            if model in V4_MODELS:
                _die(
                    "Custom style references are only supported with V3 models. "
                    f"Current model: {model}"
                )
            recraft_style = getattr(args, "recraft_style", None) or "digital_illustration"
            print(
                f"Creating custom style from {len(references)} reference image(s)...",
                file=sys.stderr,
            )
            style_id = self._create_custom_style(client, references, base_style=recraft_style)
            print(f"Custom style created: {style_id}", file=sys.stderr)

            payload = self._build_payload(prompt, args)
            # Override extra_body to use the new style_id
            extra = payload.get("extra_body", {})
            extra.pop("style", None)
            extra["style_id"] = style_id
            payload["extra_body"] = extra

            print(
                "Calling Recraft API (generation with custom style).",
                file=sys.stderr,
            )
            started = time.time()
            result = client.images.generate(**payload)
            elapsed = time.time() - started
            print(f"Generation completed in {elapsed:.1f}s.", file=sys.stderr)
            return [item.b64_json for item in result.data]

        # Pure generation
        payload = self._build_payload(prompt, args)
        print(
            "Calling Recraft API (generation). This can take up to a minute.",
            file=sys.stderr,
        )
        started = time.time()
        result = client.images.generate(**payload)
        elapsed = time.time() - started
        print(f"Generation completed in {elapsed:.1f}s.", file=sys.stderr)
        return [item.b64_json for item in result.data]

    def _image_to_image_sync(
        self,
        client: Any,
        prompt: str,
        args: Any,
        image: Path,
    ) -> list[str]:
        """Perform image-to-image editing via the non-standard endpoint."""
        model = self._get_model(args)
        size = getattr(args, "size", None) or MODEL_PARAMS["size"]["default"]
        resolved_size = _resolve_size(size, model)
        n = getattr(args, "n", 1) or 1
        strength = getattr(args, "strength", None)

        extra = self._build_extra_body(args)

        print(
            "Calling Recraft API (image-to-image).",
            file=sys.stderr,
        )
        started = time.time()

        files: dict[str, Any] = {
            "image": (image.name, image.open("rb"), "image/png"),
        }
        data: dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "n": str(n),
            "response_format": "b64_json",
            "size": resolved_size,
        }
        if strength is not None:
            data["strength"] = str(strength)
        if extra.get("style"):
            data["style"] = extra["style"]
        if extra.get("style_id"):
            data["style_id"] = extra["style_id"]

        response = client.post(
            "/images/imageToImage",
            cast_to=object,
            body=data,
            files=files,
        )
        elapsed = time.time() - started
        print(f"Image-to-image completed in {elapsed:.1f}s.", file=sys.stderr)
        return [item["b64_json"] for item in response["data"]]

    def _inpaint_sync(
        self,
        client: Any,
        prompt: str,
        args: Any,
        image: Path,
        mask: Path,
    ) -> list[str]:
        """Perform inpainting via the non-standard endpoint."""
        model = self._get_model(args)
        size = getattr(args, "size", None) or MODEL_PARAMS["size"]["default"]
        resolved_size = _resolve_size(size, model)
        n = getattr(args, "n", 1) or 1

        extra = self._build_extra_body(args)

        print(
            "Calling Recraft API (inpainting).",
            file=sys.stderr,
        )
        started = time.time()

        files: dict[str, Any] = {
            "image": (image.name, image.open("rb"), "image/png"),
            "mask": (mask.name, mask.open("rb"), "image/png"),
        }
        data: dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "n": str(n),
            "response_format": "b64_json",
            "size": resolved_size,
        }
        if extra.get("style"):
            data["style"] = extra["style"]
        if extra.get("style_id"):
            data["style_id"] = extra["style_id"]

        response = client.post(
            "/images/inpaint",
            cast_to=object,
            body=data,
            files=files,
        )
        elapsed = time.time() - started
        print(f"Inpainting completed in {elapsed:.1f}s.", file=sys.stderr)
        return [item["b64_json"] for item in response["data"]]

    # ------------------------------------------------------------------
    # Async generation
    # ------------------------------------------------------------------

    async def async_generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        model = self._get_model(args)

        # Non-standard endpoints use asyncio.to_thread wrapping sync calls
        if images and mask:
            client = _create_client()
            return await asyncio.to_thread(
                self._inpaint_sync, client, prompt, args, images[0], mask,
            )

        if images:
            client = _create_client()
            return await asyncio.to_thread(
                self._image_to_image_sync, client, prompt, args, images[0],
            )

        if references:
            if model in V4_MODELS:
                _die(
                    "Custom style references are only supported with V3 models. "
                    f"Current model: {model}"
                )
            # Style creation + generation via sync client in a thread
            client = _create_client()

            recraft_style = getattr(args, "recraft_style", None) or "digital_illustration"
            style_id = await asyncio.to_thread(
                self._create_custom_style, client, references, recraft_style,
            )

            payload = self._build_payload(prompt, args)
            extra = payload.get("extra_body", {})
            extra.pop("style", None)
            extra["style_id"] = style_id
            payload["extra_body"] = extra

            async_client = _create_async_client()
            result = await async_client.images.generate(**payload)
            return [item.b64_json for item in result.data]

        # Pure generation
        payload = self._build_payload(prompt, args)
        async_client = _create_async_client()
        result = await async_client.images.generate(**payload)
        return [item.b64_json for item in result.data]

    # ------------------------------------------------------------------
    # Dry run
    # ------------------------------------------------------------------

    def dry_run_payload(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> dict[str, Any]:
        model = self._get_model(args)
        size = getattr(args, "size", None) or MODEL_PARAMS["size"]["default"]
        output_format = self._get_output_format(args)

        # Resolve size without dying on dry run (already validated if applicable)
        try:
            resolved_size = _resolve_size(size, model)
        except SystemExit:
            resolved_size = size

        payload: dict[str, Any] = {
            "provider": "recraft",
            "model": model,
            "prompt": prompt,
            "n": getattr(args, "n", 1) or 1,
            "size": resolved_size,
            "output_format": output_format,
        }

        recraft_style = getattr(args, "recraft_style", None)
        if recraft_style:
            payload["recraft_style"] = recraft_style

        style_id = getattr(args, "style_id", None)
        if style_id:
            payload["style_id"] = style_id

        negative_prompt = getattr(args, "negative_prompt", None)
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if images and mask:
            payload["endpoint"] = "/v1/images/inpaint"
            payload["image"] = [str(p) for p in images]
            payload["mask"] = str(mask)
        elif images:
            payload["endpoint"] = "/v1/images/imageToImage"
            payload["image"] = [str(p) for p in images]
            strength = getattr(args, "strength", None)
            if strength:
                payload["strength"] = strength
        else:
            payload["endpoint"] = "/v1/images/generations"

        if references:
            payload["references"] = [str(p) for p in references]

        return payload
