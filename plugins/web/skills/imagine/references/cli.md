# CLI reference (`scripts/image_gen.py`)

This file contains the "command catalog" for the bundled image generation CLI. Keep `SKILL.md` as overview-first; put verbose CLI details here.

## What this CLI does

- `generate`: generate or edit images from a prompt. If `--image` is provided, it's an edit; otherwise it's a generation. Add `--reference` for style-guided output.
- `generate-batch`: run many jobs from a JSONL file (one job per line)
- `edit` (hidden alias): backward-compatible alias for `generate --image`; `--image` is required.

Supports multiple providers: **Google Gemini** (default) and **OpenAI**.

Real API calls require **network access** + the appropriate API key (`GOOGLE_API_KEY` or `OPENAI_API_KEY`). `--dry-run` does not.

## Quick start (works from any repo)

Set a stable path to the skill CLI:

```
export IMAGINE="$HOME/.claude/plugins/web/skills/imagine/scripts/image_gen.py"
```

### Discover available params

```
python "$IMAGINE" generate --help                        # Shows Google params (default)
python "$IMAGINE" --provider openai generate --help      # Shows OpenAI params
```

### Dry-run (no API call; no network required)

```
python "$IMAGINE" generate --prompt "Test" --dry-run
python "$IMAGINE" --provider openai generate --prompt "Test" --dry-run
```

### Generate with Google (default)

```
uv run --with google-genai python "$IMAGINE" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --aspect-ratio 16:9 \
  --resolution 1K
```

### Generate with OpenAI

```
uv run --with openai python "$IMAGINE" --provider openai generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024
```

No `uv` installed? Use your active Python env:

```
python "$IMAGINE" generate --prompt "A cozy alpine cabin at dawn"
```

## Provider flag

Use `--provider` to select which image generation provider to use:

```
--provider google     # Default — Google Gemini (gemini-3.1-flash-image-preview)
--provider openai     # OpenAI (gpt-image-1.5)
```

The `--provider` flag must appear **before** the subcommand:

```
python "$IMAGINE" --provider openai generate --prompt "..."
```

## Guardrails (important)

- Use `python "$IMAGINE" ...` (or equivalent full path) for generations/edits/batch work.
- Do **not** create one-off runners (e.g. `gen_images.py`) unless the user explicitly asks for a custom wrapper.
- **Never modify** `scripts/image_gen.py` or files under `scripts/providers/`. If something is missing, ask the user before doing anything else.

## Defaults by provider

### Google (default)

- Model: `gemini-3.1-flash-image-preview`
- Aspect ratio: `1:1`
- Resolution: `1K`
- Output format: `png`

### OpenAI

- Model: `gpt-image-1.5`
- Size: `1024x1024`
- Quality: `auto`
- Output format: `png`
- Background: unspecified (API default). If you set `--background transparent`, also set `--output-format png` or `webp`.

## Google-specific flags

- `--aspect-ratio`: Image aspect ratio. 14 ratios supported: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `1:4`, `4:1`, `1:8`, `8:1`, `21:9`.
- `--resolution`: Output resolution: `512px`, `1K`, `2K`, `4K`.
- `--n` with Google: makes N **concurrent** API calls (Google API returns one image per call).

## OpenAI-specific flags

- `--size`: Output dimensions: `1024x1024`, `1536x1024`, `1024x1536`, `auto`.
- `--quality`: Image quality: `low`, `medium`, `high`, `auto`.
- `--background`: Background mode: `transparent`, `opaque`, `auto`.
- `--output-format`: Output format: `png`, `jpeg`, `webp`.
- `--output-compression`: Compression level `0`-`100` (jpeg/webp only).
- `--input-fidelity` (edit-only): `low` or `high` (use `high` for strict edits).
- `--moderation`: Content moderation: `auto` or `low`.

## Image input flags

All image flags accept local file paths or `https://` URLs. URLs are downloaded to a temp directory that is automatically cleaned up after the command completes.

| Flag | Repeatable | Required | Notes |
|------|-----------|----------|-------|
| `--image` | Yes | No (`generate`), Yes (`edit`) | Input image for editing |
| `--mask` | No | No | Mask image for inpainting (PNG with alpha) |
| `--reference` | Yes | No | Style reference image |

When `--image` or `--reference` is provided, the CLI uses the edit pathway (OpenAI: `images.edit()`; Google: multi-image `generate_content`).

### URL examples

```bash
# Edit an image from a URL
python "$IMAGINE" generate --image "https://example.com/photo.jpg" --prompt "Change the background"

# Style reference from a URL
python "$IMAGINE" generate --reference "https://example.com/style.png" --prompt "A landscape in this style"
```

## Quality + input fidelity (OpenAI)

- `--quality` works for `generate` and `generate-batch`: `low|medium|high|auto`.
- `--input-fidelity` requires `--image`: `low|high` (use `high` for strict edits like identity or layout lock).

Example:

```
python "$IMAGINE" --provider openai generate --image input.png --prompt "Change only the background" --quality high --input-fidelity high
```

## Style references (`--reference`)

Use `--reference` to provide one or more style guide images. The model uses the reference to guide the visual style, color palette, and texture of the output.

```bash
# Style-guided generation
python "$IMAGINE" generate --reference style.png --prompt "A man riding a motorcycle"

# Style-guided edit (apply style to an existing image)
python "$IMAGINE" generate --image photo.png --reference style.png --prompt "Apply the reference style"

# Multiple references
python "$IMAGINE" generate --reference ref1.png --reference ref2.png --prompt "Blend these styles"
```

**Provider behavior:**
- **Google**: Reference images are prepended to the `contents` list before edit images and the prompt.
- **OpenAI**: Reference images are combined with edit images and sent to the `images.edit()` endpoint. A style-reference context line is always added to the prompt.

## Masks

- **OpenAI**: Supports mask-based editing. Use a **PNG** mask; an alpha channel is strongly recommended. The mask should match the input image dimensions.
- **Google**: Does **not** support mask-based editing. If `--mask` is provided with the Google provider, a warning is printed and the mask is ignored. Use `--provider openai` for mask support.

In the edit prompt, repeat invariants (e.g., "change only the background; keep the subject unchanged") to reduce drift.

## Optional deps

Prefer `uv run --with ...` for an out-of-the-box run without changing the current project env; otherwise install into your active env:

```
uv pip install google-genai pillow   # Google provider
uv pip install openai pillow         # OpenAI provider
```

## Common recipes

### Google: generate with aspect ratio

```
uv run --with google-genai python "$IMAGINE" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --aspect-ratio 16:9 \
  --resolution 2K
```

### Google: generate + downscaled copy for web

```
uv run --with google-genai --with pillow python "$IMAGINE" generate \
  --prompt "A cozy alpine cabin at dawn" \
  --aspect-ratio 16:9 \
  --downscale-max-dim 1024
```

### OpenAI: generate + downscaled copy

```
uv run --with openai --with pillow python "$IMAGINE" --provider openai generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --downscale-max-dim 1024
```

Notes:

- Downscaling writes an extra file next to the original (default suffix `-web`, e.g. `output-web.png`).
- Downscaling requires Pillow (use `uv run --with pillow ...` or install it into your env).

### Generate with augmentation fields

```
python "$IMAGINE" generate \
  --prompt "A minimal hero image of a ceramic coffee mug" \
  --use-case "landing page hero" \
  --style "clean product photography" \
  --composition "centered product, generous negative space" \
  --constraints "no logos, no text"
```

### Batch generation (async, concurrent)

```
mkdir -p /tmp/imagine
cat > /tmp/imagine/prompts.jsonl << 'EOF'
{"prompt":"Cavernous hangar interior with a compact shuttle parked center-left, open bay door","use_case":"game concept art environment","composition":"wide-angle, low-angle, cinematic framing","lighting":"volumetric light rays through drifting fog","constraints":"no logos or trademarks; no watermark","aspect_ratio":"3:2"}
{"prompt":"Gray wolf in profile in a snowy forest, crisp fur texture","use_case":"wildlife photography print","composition":"100mm, eye-level, shallow depth of field","constraints":"no logos or trademarks; no watermark","aspect_ratio":"1:1"}
EOF

python "$IMAGINE" generate-batch --input /tmp/imagine/prompts.jsonl --out-dir out --concurrency 5

# Cleanup (recommended)
rm -f /tmp/imagine/prompts.jsonl
```

Notes:

- Use `--concurrency` to control parallelism (default `5`). Higher concurrency can hit rate limits; the CLI retries on transient errors.
- Per-job overrides are supported in JSONL (e.g., `aspect_ratio`, `resolution`, `size`, `quality`, `background`, `output_format`, `n`, and prompt-augmentation fields).
- `--n` generates multiple variants for a single prompt; `generate-batch` is for many different prompts.
- Treat the JSONL file as temporary: write it to the OS temp dir and delete it after the run (don't commit it).

### Edit (Google — no mask)

```
python "$IMAGINE" generate --image input.png --prompt "Replace the background with a warm sunset"
```

### Edit (OpenAI — with mask)

```
python "$IMAGINE" --provider openai generate --image input.png --mask mask.png --prompt "Replace the background with a warm sunset"
```

### Style-guided generation

```
python "$IMAGINE" generate --reference style.png --prompt "A cozy alpine cabin at dawn" --aspect-ratio 16:9
```

### Style-guided edit

```
python "$IMAGINE" generate --image photo.png --reference style.png --prompt "Apply the reference style to this photo"
```

## Backward compatibility

The `edit` subcommand is still supported as a hidden alias for `generate --image`. Existing scripts using `edit --image ...` will continue to work unchanged. New usage should prefer `generate --image ...`.

## CLI notes

- Google: 14 aspect ratios, 4 resolution levels. No mask support.
- OpenAI: 4 pixel sizes, 4 quality levels, background control, mask support, compression control.
- Transparent backgrounds require `--provider openai` with `output_format` set to `png` or `webp`.
- Default output is `output.png`; multiple images become `output-1.png`, `output-2.png`, etc.
- Use `--no-augment` to skip prompt augmentation (style-reference context is always included when `--reference` is used).
- All image inputs (`--image`, `--mask`, `--reference`) accept local file paths or `https://` URLs.
- Temp path is OS-agnostic (use `tempfile.gettempdir()/imagine/` for intermediate files).

## See also

- API parameter quick reference: `references/image-api.md`
- Prompt examples: `references/sample-prompts.md`
