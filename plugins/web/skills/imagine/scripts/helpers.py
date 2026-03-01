"""Shared helper utilities for the imagine skill (provider-agnostic).

This module contains error helpers, constants, output-path builders,
image/URL resolution, decode/write/downscale logic, batch-parsing helpers,
and retry utilities.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.request
import urllib.error
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple


# ======================================================================
# Error helpers
# ======================================================================

def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


# ======================================================================
# Constants
# ======================================================================

DEFAULT_DOWNSCALE_SUFFIX = "-web"

MAX_IMAGE_BYTES = 50 * 1024 * 1024
MAX_BATCH_JOBS = 500


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def _normalize_output_format(fmt: Optional[str]) -> str:
    if not fmt:
        return "png"
    fmt = fmt.lower()
    if fmt not in {"png", "jpeg", "jpg", "webp", "svg"}:
        _die("output-format must be png, jpeg, jpg, webp, or svg.")
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

        if output_format == "svg":
            continue  # SVG cannot be downscaled via PIL

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
