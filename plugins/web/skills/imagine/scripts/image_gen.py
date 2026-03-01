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
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Ensure the ``providers`` package is importable when running as a script.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from providers import get_provider, PROVIDER_REGISTRY  # noqa: E402
import providers.google  # noqa: E402, F401  — registers NanoBananaProvider
import providers.openai  # noqa: E402, F401  — registers GPTImageProvider
import providers.recraft  # noqa: E402, F401  — registers RecraftProvider

from helpers import (  # noqa: E402
    _die, _warn, DEFAULT_DOWNSCALE_SUFFIX, MAX_IMAGE_BYTES, MAX_BATCH_JOBS,
    _normalize_output_format, _build_output_paths, _slugify, _job_output_paths,
    _is_url, _download_to_temp, _temp_download_context, _resolve_paths, _resolve_single_path,
    _derive_downscale_path, _downscale_image_bytes, _decode_write_and_downscale,
    _print_request, _normalize_job, _read_jobs_jsonl, _merge_non_null,
    _extract_retry_after_seconds, _is_rate_limit_error, _is_transient_error,
    _generate_one_with_retries,
)
from prompt import _read_prompt, _augment_prompt, _augment_prompt_fields, _fields_from_args  # noqa: E402

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

DEFAULT_PROVIDER = "google"
DEFAULT_CONCURRENCY = 5


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
                            "aspect_ratio", "resolution",
                            "recraft_style", "style_id", "strength"):
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
