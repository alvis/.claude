"""Google Gemini Nano Banana 2 image generation provider.

Uses ``gemini-3.1-flash-image-preview`` via the ``google-genai`` SDK.
"""

from __future__ import annotations

import asyncio
import base64
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from providers import ImageProvider, register_provider


MODEL_PARAMS: dict[str, dict[str, Any]] = {
    "model": {
        "default": "gemini-3.1-flash-image-preview",
        "choices": ["gemini-3.1-flash-image-preview"],
        "help": "Google Gemini image model",
    },
    "aspect_ratio": {
        "default": "1:1",
        "choices": [
            "1:1",    # Square - logos, icons, social media, product shots
            "2:3",    # Portrait - mobile screens, book covers, posters
            "3:2",    # Landscape - blog headers, feature images
            "3:4",    # Tall portrait - social stories, Pinterest pins
            "4:3",    # Standard landscape - presentations, UI mockups
            "4:5",    # Near-square portrait - Instagram posts
            "5:4",    # Near-square landscape - photo prints
            "9:16",   # Vertical - mobile wallpapers, stories, reels
            "16:9",   # Widescreen - hero images, YouTube thumbnails
            "1:4",    # Ultra-tall - vertical banners
            "4:1",    # Ultra-wide - horizontal banners
            "1:8",    # Extreme vertical strip
            "8:1",    # Extreme horizontal strip
            "21:9",   # Ultra-widescreen - cinematic panoramas
        ],
        "help": "Image aspect ratio",
    },
    "resolution": {
        "default": "1K",
        "choices": ["512px", "1K", "2K", "4K"],
        "help": "Output resolution (512px/1K/2K/4K)",
    },
    "n": {
        "default": 1,
        "type": "int",
        "range": [1, 10],
        "help": "Number of images to generate (1-10)",
    },
    "output_format": {
        "default": "png",
        "choices": ["png", "jpeg", "webp"],
        "help": "Output image format",
    },
}

# OpenAI-style size -> Google aspect_ratio + resolution mapping
SIZE_MAP: dict[str, tuple[str, str]] = {
    "1024x1024": ("1:1", "1K"),
    "1536x1024": ("3:2", "1K"),
    "1024x1536": ("2:3", "1K"),
    "auto": ("1:1", "1K"),
}


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def _create_client() -> Any:
    """Lazily create a Google GenAI client."""
    try:
        import os

        from google import genai  # type: ignore[import-untyped]
    except ImportError:
        _die(
            "google-genai SDK not installed. "
            "Install with `uv pip install google-genai` (then re-run)."
        )
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def _image_to_pil(path: Path) -> Any:
    """Load an image file as a PIL Image."""
    try:
        from PIL import Image  # type: ignore[import-untyped]
    except ImportError:
        _die("Pillow is required for image editing. Install with `uv pip install pillow`.")
    return Image.open(path)


def _convert_format(image_bytes: bytes, target_format: str) -> bytes:
    """Convert image bytes to the requested format via PIL."""
    if target_format == "png":
        return image_bytes  # Google returns PNG natively

    try:
        from PIL import Image  # type: ignore[import-untyped]
    except ImportError:
        _die("Pillow is required for format conversion. Install with `uv pip install pillow`.")

    with Image.open(BytesIO(image_bytes)) as img:
        img.load()
        fmt = target_format.upper()
        if fmt == "JPEG" and img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
            img = bg
        elif fmt == "JPEG":
            img = img.convert("RGB")
        out = BytesIO()
        img.save(out, format=fmt)
        return out.getvalue()


def _extract_images_from_response(response: Any, output_format: str) -> list[str]:
    """Extract base64-encoded image strings from a Gemini response."""
    images: list[str] = []
    if not hasattr(response, "candidates") or not response.candidates:
        _die("No candidates in Google API response.")
    for candidate in response.candidates:
        if not hasattr(candidate, "content") or not candidate.content:
            continue
        for part in candidate.content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                raw_bytes = part.inline_data.data
                converted = _convert_format(raw_bytes, output_format)
                images.append(base64.b64encode(converted).decode("ascii"))
    return images


@register_provider
class NanoBananaProvider(ImageProvider):
    """Google Gemini image generation via Nano Banana 2."""

    name = "google"
    env_var = "GOOGLE_API_KEY"
    MODEL_PARAMS = MODEL_PARAMS

    def _build_config(self, args: Any) -> Any:
        """Build a ``GenerateContentConfig`` from parsed args."""
        from google.genai import types  # type: ignore[import-untyped]

        aspect_ratio = getattr(args, "aspect_ratio", None) or MODEL_PARAMS["aspect_ratio"]["default"]
        resolution = getattr(args, "resolution", None) or MODEL_PARAMS["resolution"]["default"]

        # Map OpenAI-style --size to aspect_ratio + resolution if present
        size = getattr(args, "size", None)
        if size and size in SIZE_MAP:
            aspect_ratio, resolution = SIZE_MAP[size]

        image_config = types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=resolution,
        )
        return types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=image_config,
        )

    def _build_contents(
        self,
        prompt: str,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[Any]:
        """Build the ``contents`` list for ``generate_content``.

        Order: [reference_images..., edit_images..., prompt].
        """
        if mask:
            _warn(
                "Google provider does not support mask-based editing. "
                "Use --provider openai for mask support. Proceeding without mask."
            )

        contents: list[Any] = []
        if references:
            for ref in references:
                contents.append(_image_to_pil(ref))
        if images:
            for img_path in images:
                contents.append(_image_to_pil(img_path))
        contents.append(prompt)
        return contents

    def generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        client = _create_client()
        model = getattr(args, "model", None) or MODEL_PARAMS["model"]["default"]
        config = self._build_config(args)
        output_format = getattr(args, "output_format", None) or MODEL_PARAMS["output_format"]["default"]
        n = getattr(args, "n", 1) or 1

        if n == 1:
            contents = self._build_contents(
                prompt, images=images, mask=mask, references=references,
            )
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            return _extract_images_from_response(response, output_format)

        # n > 1: make N concurrent calls via asyncio.to_thread.
        # Each call builds its own contents to avoid sharing PIL Image
        # objects across threads (PIL Images are not thread-safe).
        build = self._build_contents

        async def _concurrent_generate() -> list[str]:
            async def _one() -> list[str]:
                thread_contents = build(
                    prompt, images=images, mask=mask, references=references,
                )
                resp = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model,
                    contents=thread_contents,
                    config=config,
                )
                return _extract_images_from_response(resp, output_format)

            tasks = [asyncio.create_task(_one()) for _ in range(n)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            all_images: list[str] = []
            for i, result in enumerate(results):
                if isinstance(result, BaseException):
                    _warn(f"Concurrent call {i + 1}/{n} failed: {result}")
                else:
                    all_images.extend(result)
            if not all_images:
                _die("All concurrent generation calls failed.")
            return all_images

        return asyncio.run(_concurrent_generate())

    async def async_generate(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> list[str]:
        client = _create_client()
        model = getattr(args, "model", None) or MODEL_PARAMS["model"]["default"]
        config = self._build_config(args)
        output_format = getattr(args, "output_format", None) or MODEL_PARAMS["output_format"]["default"]

        contents = self._build_contents(
            prompt, images=images, mask=mask, references=references,
        )

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=contents,
            config=config,
        )
        return _extract_images_from_response(response, output_format)

    def dry_run_payload(
        self,
        prompt: str,
        args: Any,
        *,
        images: list[Path] | None = None,
        mask: Path | None = None,
        references: list[Path] | None = None,
    ) -> dict[str, Any]:
        model = getattr(args, "model", None) or MODEL_PARAMS["model"]["default"]
        aspect_ratio = getattr(args, "aspect_ratio", None) or MODEL_PARAMS["aspect_ratio"]["default"]
        resolution = getattr(args, "resolution", None) or MODEL_PARAMS["resolution"]["default"]

        size = getattr(args, "size", None)
        if size and size in SIZE_MAP:
            aspect_ratio, resolution = SIZE_MAP[size]

        payload: dict[str, Any] = {
            "provider": "google",
            "endpoint": "models.generate_content",
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "response_modalities": ["IMAGE"],
        }
        if references:
            payload["references"] = [str(p) for p in references]
        if images:
            payload["images"] = [str(p) for p in images]
        if mask:
            payload["mask"] = str(mask)
            payload["mask_warning"] = "Google provider does not support masks; ignored"
        n = getattr(args, "n", 1) or 1
        if n > 1:
            payload["n"] = n
            payload["note"] = f"Will make {n} concurrent API calls"
        return payload
