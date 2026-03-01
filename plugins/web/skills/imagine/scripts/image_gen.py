#!/usr/bin/env python3
"""Generate or edit images via a multi-provider Image API.

Defaults to Google Gemini (gemini-3.1-flash-image-preview) for generation.
Use ``--provider openai`` for OpenAI gpt-image-1.5.

Run ``python image_gen.py generate --help`` to see all available params for
the active provider.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import urllib.request
import urllib.error
from contextlib import contextmanager
from io import BytesIO
from typing import Any, Dict, Generator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Ensure the ``providers`` package is importable when running as a script.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from providers import get_provider, PROVIDER_REGISTRY  # noqa: E402
import providers.google  # noqa: E402, F401  — registers NanoBananaProvider
import providers.openai  # noqa: E402, F401  — registers GPTImageProvider

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

DEFAULT_PROVIDER = "google"
DEFAULT_CONCURRENCY = 5
DEFAULT_DOWNSCALE_SUFFIX = "-web"

MAX_IMAGE_BYTES = 50 * 1024 * 1024
MAX_BATCH_JOBS = 500


# ======================================================================
# Shared utilities (provider-agnostic)
# ======================================================================

def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

def _read_prompt(prompt: Optional[str], prompt_file: Optional[str]) -> str:
    if prompt and prompt_file:
        _die("Use --prompt or --prompt-file, not both.")
    if prompt_file:
        path = Path(prompt_file)
        if not path.exists():
            _die(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    if prompt:
        return prompt.strip()
    _die("Missing prompt. Use --prompt or --prompt-file.")
    return ""  # unreachable


def _augment_prompt(
    args: argparse.Namespace,
    prompt: str,
    *,
    references: Optional[List[Path]] = None,
) -> str:
    fields = _fields_from_args(args)
    return _augment_prompt_fields(args.augment, prompt, fields, references=references)


def _augment_prompt_fields(
    augment: bool,
    prompt: str,
    fields: Dict[str, Optional[str]],
    *,
    references: Optional[List[Path]] = None,
) -> str:
    sections: List[str] = []

    # Always prepend style-reference context when references are present,
    # even under --no-augment, so the model understands the extra images.
    if references:
        sections.append(
            "Style reference: use the provided reference image(s) to guide "
            "the visual style, color palette, and texture of the output."
        )

    if not augment:
        sections.append(prompt)
        return "\n".join(sections)

    if fields.get("use_case"):
        sections.append(f"Use case: {fields['use_case']}")
    sections.append(f"Primary request: {prompt}")
    if fields.get("scene"):
        sections.append(f"Scene/background: {fields['scene']}")
    if fields.get("subject"):
        sections.append(f"Subject: {fields['subject']}")
    if fields.get("style"):
        sections.append(f"Style/medium: {fields['style']}")
    if fields.get("composition"):
        sections.append(f"Composition/framing: {fields['composition']}")
    if fields.get("lighting"):
        sections.append(f"Lighting/mood: {fields['lighting']}")
    if fields.get("palette"):
        sections.append(f"Color palette: {fields['palette']}")
    if fields.get("materials"):
        sections.append(f"Materials/textures: {fields['materials']}")
    if fields.get("text"):
        sections.append(f"Text (verbatim): \"{fields['text']}\"")
    if fields.get("constraints"):
        sections.append(f"Constraints: {fields['constraints']}")
    if fields.get("negative"):
        sections.append(f"Avoid: {fields['negative']}")

    return "\n".join(sections)


def _fields_from_args(args: argparse.Namespace) -> Dict[str, Optional[str]]:
    return {
        "use_case": getattr(args, "use_case", None),
        "scene": getattr(args, "scene", None),
        "subject": getattr(args, "subject", None),
        "style": getattr(args, "style", None),
        "composition": getattr(args, "composition", None),
        "lighting": getattr(args, "lighting", None),
        "palette": getattr(args, "palette", None),
        "materials": getattr(args, "materials", None),
        "text": getattr(args, "text", None),
        "constraints": getattr(args, "constraints", None),
        "negative": getattr(args, "negative", None),
    }


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def _normalize_output_format(fmt: Optional[str]) -> str:
    if not fmt:
        return "png"
    fmt = fmt.lower()
    if fmt not in {"png", "jpeg", "jpg", "webp"}:
        _die("output-format must be png, jpeg, jpg, or webp.")
    return "jpeg" if fmt == "jpg" else fmt


def _build_output_paths(
    out: str,
    output_format: str,
    count: int,
    out_dir: Optional[str],
) -> List[Path]:
    ext = "." + output_format

    if out_dir:
        out_base = Path(out_dir)
        out_base.mkdir(parents=True, exist_ok=True)
        return [out_base / f"image_{i}{ext}" for i in range(1, count + 1)]

    out_path = Path(out)
    if out_path.exists() and out_path.is_dir():
        out_path.mkdir(parents=True, exist_ok=True)
        return [out_path / f"image_{i}{ext}" for i in range(1, count + 1)]

    if out_path.suffix == "":
        out_path = out_path.with_suffix(ext)
    elif output_format and out_path.suffix.lstrip(".").lower() != output_format:
        _warn(
            f"Output extension {out_path.suffix} does not match output-format {output_format}."
        )

    if count == 1:
        return [out_path]

    return [
        out_path.with_name(f"{out_path.stem}-{i}{out_path.suffix}")
        for i in range(1, count + 1)
    ]


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:60] if value else "job"


def _job_output_paths(
    *,
    out_dir: Path,
    output_format: str,
    idx: int,
    prompt: str,
    n: int,
    explicit_out: Optional[str],
) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "." + output_format

    if explicit_out:
        base = Path(explicit_out)
        if base.suffix == "":
            base = base.with_suffix(ext)
        elif base.suffix.lstrip(".").lower() != output_format:
            _warn(
                f"Job {idx}: output extension {base.suffix} does not match output-format {output_format}."
            )
        base = out_dir / base.name
    else:
        slug = _slugify(prompt[:80])
        base = out_dir / f"{idx:03d}-{slug}{ext}"

    if n == 1:
        return [base]
    return [
        base.with_name(f"{base.stem}-{i}{base.suffix}")
        for i in range(1, n + 1)
    ]


# ---------------------------------------------------------------------------
# Image file / URL helpers
# ---------------------------------------------------------------------------

def _is_url(value: str) -> bool:
    """Return True if *value* looks like an HTTP(S) URL."""
    return value.startswith("http://") or value.startswith("https://")


def _download_to_temp(url: str, temp_dir: str) -> Path:
    """Download *url* into *temp_dir* and return the local path."""
    print(f"Downloading {url} ...", file=sys.stderr)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "imagine-cli/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            # Derive a filename from the URL (fallback to "download")
            url_path = url.split("?")[0].split("#")[0]
            name = Path(url_path).name or "download"
            dest = Path(temp_dir) / name
            # Avoid collisions
            counter = 0
            while dest.exists():
                counter += 1
                dest = Path(temp_dir) / f"{dest.stem}_{counter}{dest.suffix}"
            with dest.open("wb") as fout:
                shutil.copyfileobj(resp, fout)
    except (urllib.error.URLError, OSError) as exc:
        _die(f"Failed to download {url}: {exc}")
    if dest.stat().st_size > MAX_IMAGE_BYTES:
        _warn(f"Downloaded image exceeds 50MB limit: {url}")
    print(f"Downloaded to {dest}", file=sys.stderr)
    return dest


@contextmanager
def _temp_download_context() -> Generator[str, None, None]:
    """Create a temporary directory for URL downloads; clean up on exit."""
    tmp = tempfile.mkdtemp(prefix="imagine_dl_")
    try:
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _resolve_paths(
    raw_values: Optional[List[str]],
    temp_dir: str,
    *,
    dry_run: bool = False,
    label: str = "image",
) -> Optional[List[Path]]:
    """Resolve a list of strings (file paths or URLs) to local Paths.

    On *dry_run* URLs produce placeholder paths without downloading.
    """
    if not raw_values:
        return None
    resolved: List[Path] = []
    for raw in raw_values:
        if _is_url(raw):
            if dry_run:
                resolved.append(Path(f"<{label}:{raw}>"))
            else:
                resolved.append(_download_to_temp(raw, temp_dir))
        else:
            path = Path(raw)
            if not dry_run and not path.exists():
                _die(f"{label.capitalize()} file not found: {path}")
            if not dry_run and path.stat().st_size > MAX_IMAGE_BYTES:
                _warn(f"{label.capitalize()} exceeds 50MB limit: {path}")
            resolved.append(path)
    return resolved


def _resolve_single_path(
    raw_value: Optional[str],
    temp_dir: str,
    *,
    dry_run: bool = False,
    label: str = "image",
) -> Optional[Path]:
    """Single-value variant of ``_resolve_paths``."""
    if raw_value is None:
        return None
    result = _resolve_paths([raw_value], temp_dir, dry_run=dry_run, label=label)
    return result[0] if result else None


# ---------------------------------------------------------------------------
# Decode / write / downscale helpers
# ---------------------------------------------------------------------------

def _derive_downscale_path(path: Path, suffix: str) -> Path:
    if suffix and not suffix.startswith("-") and not suffix.startswith("_"):
        suffix = "-" + suffix
    return path.with_name(f"{path.stem}{suffix}{path.suffix}")


def _downscale_image_bytes(image_bytes: bytes, *, max_dim: int, output_format: str) -> bytes:
    try:
        from PIL import Image
    except Exception:
        _die(
            "Downscaling requires Pillow. Install with `uv pip install pillow` (then re-run)."
        )

    if max_dim < 1:
        _die("--downscale-max-dim must be >= 1")

    with Image.open(BytesIO(image_bytes)) as img:
        img.load()
        w, h = img.size
        scale = min(1.0, float(max_dim) / float(max(w, h)))
        target = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))

        resized = img if target == (w, h) else img.resize(target, Image.Resampling.LANCZOS)

        fmt = output_format.lower()
        if fmt == "jpg":
            fmt = "jpeg"

        if fmt == "jpeg":
            if resized.mode in ("RGBA", "LA") or ("transparency" in getattr(resized, "info", {})):
                bg = Image.new("RGB", resized.size, (255, 255, 255))
                bg.paste(resized.convert("RGBA"), mask=resized.convert("RGBA").split()[-1])
                resized = bg
            else:
                resized = resized.convert("RGB")

        out = BytesIO()
        resized.save(out, format=fmt.upper())
        return out.getvalue()


def _decode_write_and_downscale(
    images: List[str],
    outputs: List[Path],
    *,
    force: bool,
    downscale_max_dim: Optional[int],
    downscale_suffix: str,
    output_format: str,
) -> None:
    for idx, image_b64 in enumerate(images):
        if idx >= len(outputs):
            break
        out_path = outputs[idx]
        if out_path.exists() and not force:
            _die(f"Output already exists: {out_path} (use --force to overwrite)")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        raw = base64.b64decode(image_b64)
        out_path.write_bytes(raw)
        print(f"Wrote {out_path}")

        if downscale_max_dim is None:
            continue

        derived = _derive_downscale_path(out_path, downscale_suffix)
        if derived.exists() and not force:
            _die(f"Output already exists: {derived} (use --force to overwrite)")
        derived.parent.mkdir(parents=True, exist_ok=True)
        resized = _downscale_image_bytes(raw, max_dim=downscale_max_dim, output_format=output_format)
        derived.write_bytes(resized)
        print(f"Wrote {derived}")


# ---------------------------------------------------------------------------
# Input parsing helpers (JSONL batch)
# ---------------------------------------------------------------------------

def _print_request(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _normalize_job(job: Any, idx: int) -> Dict[str, Any]:
    if isinstance(job, str):
        prompt = job.strip()
        if not prompt:
            _die(f"Empty prompt at job {idx}")
        return {"prompt": prompt}
    if isinstance(job, dict):
        if "prompt" not in job or not str(job["prompt"]).strip():
            _die(f"Missing prompt for job {idx}")
        return job
    _die(f"Invalid job at index {idx}: expected string or object.")
    return {}  # unreachable


def _read_jobs_jsonl(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        _die(f"Input file not found: {p}")
    jobs: List[Dict[str, Any]] = []
    for line_no, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            item: Any
            if line.startswith("{"):
                item = json.loads(line)
            else:
                item = line
            jobs.append(_normalize_job(item, idx=line_no))
        except json.JSONDecodeError as exc:
            _die(f"Invalid JSON on line {line_no}: {exc}")
    if not jobs:
        _die("No jobs found in input file.")
    if len(jobs) > MAX_BATCH_JOBS:
        _die(f"Too many jobs ({len(jobs)}). Max is {MAX_BATCH_JOBS}.")
    return jobs


def _merge_non_null(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(dst)
    for k, v in src.items():
        if v is not None:
            merged[k] = v
    return merged


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

def _extract_retry_after_seconds(exc: Exception) -> Optional[float]:
    for attr in ("retry_after", "retry_after_seconds"):
        val = getattr(exc, attr, None)
        if isinstance(val, (int, float)) and val >= 0:
            return float(val)
    msg = str(exc)
    m = re.search(r"retry[- ]after[:= ]+([0-9]+(?:\\.[0-9]+)?)", msg, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    return None


def _is_rate_limit_error(exc: Exception) -> bool:
    name = exc.__class__.__name__.lower()
    if "ratelimit" in name or "rate_limit" in name:
        return True
    msg = str(exc).lower()
    return "429" in msg or "rate limit" in msg or "too many requests" in msg


def _is_transient_error(exc: Exception) -> bool:
    if _is_rate_limit_error(exc):
        return True
    name = exc.__class__.__name__.lower()
    if "timeout" in name or "timedout" in name or "tempor" in name:
        return True
    msg = str(exc).lower()
    return "timeout" in msg or "timed out" in msg or "connection reset" in msg


async def _generate_one_with_retries(
    provider: Any,
    prompt: str,
    args: argparse.Namespace,
    *,
    attempts: int,
    job_label: str,
    images: Optional[List[Path]] = None,
    mask: Optional[Path] = None,
    references: Optional[List[Path]] = None,
) -> List[str]:
    """Call provider.async_generate with retry logic for transient errors."""
    last_exc: Optional[Exception] = None
    for attempt in range(1, attempts + 1):
        try:
            return await provider.async_generate(
                prompt, args, images=images, mask=mask, references=references,
            )
        except Exception as exc:
            last_exc = exc
            if not _is_transient_error(exc):
                raise
            if attempt == attempts:
                raise
            sleep_s = _extract_retry_after_seconds(exc)
            if sleep_s is None:
                sleep_s = min(60.0, 2.0**attempt)
            print(
                f"{job_label} attempt {attempt}/{attempts} failed ({exc.__class__.__name__}); retrying in {sleep_s:.1f}s",
                file=sys.stderr,
            )
            await asyncio.sleep(sleep_s)
    raise last_exc or RuntimeError("unknown error")


# ======================================================================
# Command handlers
# ======================================================================

def _generate(args: argparse.Namespace, provider: Any) -> None:
    prompt = _read_prompt(args.prompt, args.prompt_file)

    raw_images = getattr(args, "image", None)
    raw_mask = getattr(args, "mask", None)
    raw_references = getattr(args, "reference", None)

    with _temp_download_context() as temp_dir:
        image_paths = _resolve_paths(raw_images, temp_dir, dry_run=args.dry_run, label="image")
        mask_path = _resolve_single_path(raw_mask, temp_dir, dry_run=args.dry_run, label="mask")
        reference_paths = _resolve_paths(raw_references, temp_dir, dry_run=args.dry_run, label="reference")

        # Validate mask format
        if mask_path and not args.dry_run:
            if mask_path.suffix.lower() != ".png":
                _warn(f"Mask should be a PNG with an alpha channel: {mask_path}")

        prompt = _augment_prompt(args, prompt, references=reference_paths)

        output_format = _normalize_output_format(getattr(args, "output_format", None))
        n = getattr(args, "n", 1) or 1
        output_paths = _build_output_paths(args.out, output_format, n, args.out_dir)

        if args.dry_run:
            payload = provider.dry_run_payload(
                prompt, args,
                images=image_paths, mask=mask_path, references=reference_paths,
            )
            payload["outputs"] = [str(p) for p in output_paths]
            _print_request(payload)
            return

        images = provider.generate(
            prompt, args,
            images=image_paths, mask=mask_path, references=reference_paths,
        )
        _decode_write_and_downscale(
            images,
            output_paths,
            force=args.force,
            downscale_max_dim=args.downscale_max_dim,
            downscale_suffix=args.downscale_suffix,
            output_format=output_format,
        )


def _job_image_list(job: Dict[str, Any], key: str) -> Optional[List[str]]:
    """Extract an image list from a JSONL job, accepting singular or plural key."""
    plural = key + "s" if not key.endswith("s") else key
    singular = key.rstrip("s") if key.endswith("s") else key
    val = job.get(plural) or job.get(singular)
    if val is None:
        return None
    if isinstance(val, str):
        return [val]
    if isinstance(val, list):
        return [str(v) for v in val]
    return None


async def _run_generate_batch(args: argparse.Namespace, provider: Any) -> int:
    jobs = _read_jobs_jsonl(args.input)
    out_dir = Path(args.out_dir)

    base_fields = _fields_from_args(args)

    with _temp_download_context() as temp_dir:
        if args.dry_run:
            for i, job in enumerate(jobs, start=1):
                prompt_text = str(job["prompt"]).strip()
                fields = _merge_non_null(base_fields, job.get("fields", {}))
                fields = _merge_non_null(fields, {k: job.get(k) for k in base_fields.keys()})

                # Resolve per-job image inputs
                raw_images = _job_image_list(job, "image")
                raw_mask_val = job.get("mask")
                raw_refs = _job_image_list(job, "reference")

                image_paths = _resolve_paths(raw_images, temp_dir, dry_run=True, label="image")
                mask_path = _resolve_single_path(raw_mask_val, temp_dir, dry_run=True, label="mask") if raw_mask_val else None
                reference_paths = _resolve_paths(raw_refs, temp_dir, dry_run=True, label="reference")

                augmented = _augment_prompt_fields(
                    args.augment, prompt_text, fields, references=reference_paths,
                )

                # Build a job-level args namespace with per-job overrides
                job_args = argparse.Namespace(**vars(args))
                for key in ("model", "n", "size", "quality", "background",
                            "output_format", "output_compression", "moderation",
                            "aspect_ratio", "resolution"):
                    if key in job:
                        setattr(job_args, key, job[key])

                payload = provider.dry_run_payload(
                    augmented, job_args,
                    images=image_paths, mask=mask_path, references=reference_paths,
                )

                effective_output_format = _normalize_output_format(
                    getattr(job_args, "output_format", None)
                )
                n = getattr(job_args, "n", 1) or 1
                outputs = _job_output_paths(
                    out_dir=out_dir,
                    output_format=effective_output_format,
                    idx=i,
                    prompt=prompt_text,
                    n=n,
                    explicit_out=job.get("out"),
                )
                downscaled = None
                if args.downscale_max_dim is not None:
                    downscaled = [
                        str(_derive_downscale_path(p, args.downscale_suffix)) for p in outputs
                    ]
                payload["job"] = i
                payload["outputs"] = [str(p) for p in outputs]
                payload["outputs_downscaled"] = downscaled
                _print_request(payload)
            return 0

        sem = asyncio.Semaphore(args.concurrency)
        any_failed = False

        async def run_job(i: int, job: Dict[str, Any]) -> Tuple[int, Optional[str]]:
            nonlocal any_failed
            prompt_text = str(job["prompt"]).strip()
            job_label = f"[job {i}/{len(jobs)}]"

            fields = _merge_non_null(base_fields, job.get("fields", {}))
            fields = _merge_non_null(fields, {k: job.get(k) for k in base_fields.keys()})

            # Resolve per-job image inputs
            raw_images = _job_image_list(job, "image")
            raw_mask_val = job.get("mask")
            raw_refs = _job_image_list(job, "reference")

            image_paths = _resolve_paths(raw_images, temp_dir, dry_run=False, label="image")
            mask_path = _resolve_single_path(raw_mask_val, temp_dir, dry_run=False, label="mask") if raw_mask_val else None
            reference_paths = _resolve_paths(raw_refs, temp_dir, dry_run=False, label="reference")

            augmented = _augment_prompt_fields(
                args.augment, prompt_text, fields, references=reference_paths,
            )

            job_args = argparse.Namespace(**vars(args))
            for key in ("model", "n", "size", "quality", "background",
                        "output_format", "output_compression", "moderation",
                        "aspect_ratio", "resolution"):
                if key in job:
                    setattr(job_args, key, job[key])

            n = getattr(job_args, "n", 1) or 1
            effective_output_format = _normalize_output_format(
                getattr(job_args, "output_format", None)
            )
            outputs = _job_output_paths(
                out_dir=out_dir,
                output_format=effective_output_format,
                idx=i,
                prompt=prompt_text,
                n=n,
                explicit_out=job.get("out"),
            )
            try:
                async with sem:
                    print(f"{job_label} starting", file=sys.stderr)
                    started = time.time()
                    images = await _generate_one_with_retries(
                        provider,
                        augmented,
                        job_args,
                        attempts=args.max_attempts,
                        job_label=job_label,
                        images=image_paths,
                        mask=mask_path,
                        references=reference_paths,
                    )
                    elapsed = time.time() - started
                    print(f"{job_label} completed in {elapsed:.1f}s", file=sys.stderr)
                _decode_write_and_downscale(
                    images,
                    outputs,
                    force=args.force,
                    downscale_max_dim=args.downscale_max_dim,
                    downscale_suffix=args.downscale_suffix,
                    output_format=effective_output_format,
                )
                return i, None
            except Exception as exc:
                any_failed = True
                print(f"{job_label} failed: {exc}", file=sys.stderr)
                if args.fail_fast:
                    raise
                return i, str(exc)

        tasks = [asyncio.create_task(run_job(i, job)) for i, job in enumerate(jobs, start=1)]

        try:
            await asyncio.gather(*tasks)
        except Exception:
            for t in tasks:
                if not t.done():
                    t.cancel()
            raise

        return 1 if any_failed else 0


def _generate_batch(args: argparse.Namespace, provider: Any) -> None:
    exit_code = asyncio.run(_run_generate_batch(args, provider))
    if exit_code:
        raise SystemExit(exit_code)


# ======================================================================
# CLI entry point
# ======================================================================

def _add_shared_args(parser: argparse.ArgumentParser) -> None:
    """Add provider-agnostic arguments shared across all subcommands."""
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--out", default="output.png")
    parser.add_argument("--out-dir")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--augment", dest="augment", action="store_true")
    parser.add_argument("--no-augment", dest="augment", action="store_false")
    parser.set_defaults(augment=True)

    # Prompt augmentation hints
    parser.add_argument("--use-case")
    parser.add_argument("--scene")
    parser.add_argument("--subject")
    parser.add_argument("--style")
    parser.add_argument("--composition")
    parser.add_argument("--lighting")
    parser.add_argument("--palette")
    parser.add_argument("--materials")
    parser.add_argument("--text")
    parser.add_argument("--constraints")
    parser.add_argument("--negative")

    # Post-processing
    parser.add_argument("--downscale-max-dim", type=int)
    parser.add_argument("--downscale-suffix", default=DEFAULT_DOWNSCALE_SUFFIX)


def main() -> int:
    # --- Phase 1: Parse --provider early so we can load the right provider ---
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=sorted(PROVIDER_REGISTRY.keys()),
        help=f"Image generation provider (default: {DEFAULT_PROVIDER})",
    )
    pre_args, remaining = pre_parser.parse_known_args()

    provider = get_provider(pre_args.provider)

    # --- Phase 2: Build the full parser with provider-specific args ---
    parser = argparse.ArgumentParser(
        description="Generate or edit images via the Image API",
        parents=[pre_parser],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate or edit images")
    _add_shared_args(gen_parser)
    provider.register_args(gen_parser)
    gen_parser.add_argument(
        "--image", action="append", default=None,
        help="Input image for editing (repeatable; file path or URL)",
    )
    gen_parser.add_argument(
        "--mask", default=None,
        help="Mask image for inpainting (file path or URL)",
    )
    gen_parser.add_argument(
        "--reference", action="append", default=None,
        help="Style reference image (repeatable; file path or URL)",
    )
    gen_parser.set_defaults(func=_generate)

    batch_parser = subparsers.add_parser(
        "generate-batch",
        help="Generate multiple prompts concurrently (JSONL input)",
    )
    _add_shared_args(batch_parser)
    provider.register_args(batch_parser)
    batch_parser.add_argument("--input", required=True, help="Path to JSONL file (one job per line)")
    batch_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    batch_parser.add_argument("--max-attempts", type=int, default=3)
    batch_parser.add_argument("--fail-fast", action="store_true")
    batch_parser.set_defaults(func=_generate_batch)

    # Hidden backward-compat alias — routes to the same unified handler
    edit_parser = subparsers.add_parser("edit", help=argparse.SUPPRESS)
    _add_shared_args(edit_parser)
    provider.register_args(edit_parser)
    edit_parser.add_argument("--image", action="append", required=True)
    edit_parser.add_argument("--mask", default=None)
    edit_parser.add_argument("--reference", action="append", default=None)
    edit_parser.set_defaults(func=_generate)

    args = parser.parse_args()

    # --- Phase 3: Validate common constraints ---
    n = getattr(args, "n", 1) or 1
    if n < 1 or n > 10:
        _die("--n must be between 1 and 10")
    if getattr(args, "concurrency", 1) < 1 or getattr(args, "concurrency", 1) > 25:
        _die("--concurrency must be between 1 and 25")
    if getattr(args, "max_attempts", 3) < 1 or getattr(args, "max_attempts", 3) > 10:
        _die("--max-attempts must be between 1 and 10")
    oc = getattr(args, "output_compression", None)
    if oc is not None and not (0 <= oc <= 100):
        _die("--output-compression must be between 0 and 100")
    if args.command == "generate-batch" and not args.out_dir:
        _die("generate-batch requires --out-dir")
    if getattr(args, "downscale_max_dim", None) is not None and args.downscale_max_dim < 1:
        _die("--downscale-max-dim must be >= 1")

    # Provider-level validation (checks MODEL_PARAMS constraints)
    provider.validate(args)
    provider.ensure_api_key(args.dry_run)

    # --- Phase 4: Dispatch ---
    args.func(args, provider)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
