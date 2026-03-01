---
name: imagine
description: >-
  Generate or edit images via a multi-provider Image API using a bundled Python CLI.
  Supports Google Gemini (default) and OpenAI. Use when generating, creating, editing,
  inpainting, masking, removing or replacing backgrounds, creating product shots,
  concept art, covers, batch image variants, or working with transparent backgrounds.
argument-hint: "[prompt or instruction]"
---

# Image Generation Skill

Generates or edits images for the current project (e.g., website assets, game assets, UI mockups, product mockups, wireframes, logo design, photorealistic images, infographics). Defaults to **Google Gemini** (`gemini-3.1-flash-image-preview`) as the default provider, with **OpenAI** (`gpt-image-1.5`) available via `--provider openai`. Prefers the bundled CLI for deterministic, reproducible runs.

Run `python "$IMAGINE" generate --help` to see all available params for the current provider.

## CLI path setup

Set the path to the bundled CLI at the start of any image generation workflow:

```bash
export IMAGINE="$HOME/.claude/plugins/web/skills/imagine/scripts/image_gen.py"
```

All CLI invocations below assume `$IMAGINE` is set.

## When to use

- Generate a new image (concept art, product shot, cover, website hero)
- Edit an existing image (inpainting, masked edits, lighting or weather transformations, background replacement, object removal, compositing, transparent background)
- Style-guided generation or editing using a reference image (`--reference`)
- Batch runs (many prompts, or many variants across prompts)

## Decision tree (provider -> generate vs edit vs batch)

### Provider selection

- If the user needs **mask-based editing** → `--provider openai`
- If the user needs **transparent background control** (`--background transparent`) → `--provider openai`
- If the user needs **fine-grained quality/compression/fidelity control** → `--provider openai`
- Otherwise → **Google** (default, no `--provider` flag needed)

### Command selection

- If the user provides an input image (or says "edit/retouch/inpaint/mask/translate/localize/change only X") → **`generate --image`**
- If the user wants to apply a reference style → add **`--reference`** to the command
- Else if the user needs many different prompts/assets → **`generate-batch`**
- Else → **`generate`**

All image inputs (`--image`, `--mask`, `--reference`) accept both local file paths and `https://` URLs.

## Workflow

1. Decide intent: provider + command (see decision tree above).
2. Collect inputs up front: prompt(s), exact text (verbatim), constraints/avoid list, and any input image(s)/mask(s). For multi-image edits, label each input by index and role; for edits, list invariants explicitly.
3. If batch: write a temporary JSONL under the OS temp dir (one job per line), run once, then delete the JSONL.
4. Augment prompt into a short labeled spec (structure + constraints) without inventing new creative requirements.
5. Run the bundled CLI (`python "$IMAGINE" ...`) with sensible defaults (see references/cli.md).
6. For complex edits/generations, inspect outputs (open/view images) and validate: subject, style, composition, text accuracy, and invariants/avoid items.
7. Iterate: make a single targeted change (prompt or mask), re-run, re-check.
8. Save/return final outputs and note the final prompt + flags used.

## Temp and output conventions

- Use OS temp directory via `tempfile.gettempdir()/imagine/` for intermediate files (for example JSONL batches); delete when done.
- Write final artifacts under `output/imagine/` when working in this repo.
- Use `--out` or `--out-dir` to control output paths; keep filenames stable and descriptive.

## Dependencies (install if missing)

Prefer `uv` for dependency management.

### Google provider (default)

```
uv pip install google-genai pillow
```

### OpenAI provider

```
uv pip install openai pillow
```

If `uv` is unavailable:

```
python3 -m pip install google-genai pillow   # Google
python3 -m pip install openai pillow         # OpenAI
```

## Environment

- **Google (default)**: `GOOGLE_API_KEY` must be set for live API calls.
- **OpenAI**: `OPENAI_API_KEY` must be set when using `--provider openai`.

If the key is missing, give the user these steps:

1. Create an API key in the provider's platform UI:
   - Google: <https://aistudio.google.com/apikey>
   - OpenAI: <https://platform.openai.com/api-keys>
2. Set the key as an environment variable in their system.
3. Offer to guide them through setting the environment variable for their OS/shell if needed.

- Never ask the user to paste the full key in chat. Ask them to set it locally and confirm when ready.

If installation isn't possible in this environment, tell the user which dependency is missing and how to install it locally.

## Provider parameters

### Shared image input flags (all providers)

| Flag | Repeatable | Notes |
|------|-----------|-------|
| `--image` | Yes | Input image for editing (file path or URL) |
| `--mask` | No | Mask image for inpainting (file path or URL) |
| `--reference` | Yes | Style reference image (file path or URL) |

### Google Gemini (default)

| Parameter | Default | Choices | Notes |
|-----------|---------|---------|-------|
| `--model` | `gemini-3.1-flash-image-preview` | `gemini-3.1-flash-image-preview` | Google Gemini image model |
| `--aspect-ratio` | `1:1` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `1:4`, `4:1`, `1:8`, `8:1`, `21:9` | Image aspect ratio |
| `--resolution` | `1K` | `512px`, `1K`, `2K`, `4K` | Output resolution |
| `--n` | `1` | `1`-`10` | Number of images (concurrent calls) |
| `--output-format` | `png` | `png`, `jpeg`, `webp` | Output image format |

### OpenAI GPT Image (`--provider openai`)

| Parameter | Default | Choices | Notes |
|-----------|---------|---------|-------|
| `--model` | `gpt-image-1.5` | `gpt-image-1.5`, `gpt-image-1-mini` | OpenAI image model |
| `--size` | `1024x1024` | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | Output size in pixels |
| `--quality` | `auto` | `low`, `medium`, `high`, `auto` | Image quality level |
| `--background` | (unset) | `transparent`, `opaque`, `auto` | Transparent requires png/webp |
| `--output-format` | `png` | `png`, `jpeg`, `webp` | Output image format |
| `--output-compression` | (unset) | `0`-`100` | Compression (jpeg/webp only) |
| `--input-fidelity` | (unset) | `low`, `high` | Requires `--image`; strict identity/layout lock |
| `--moderation` | (unset) | `auto`, `low` | Content moderation level |
| `--n` | `1` | `1`-`10` | Number of images |

## Defaults & rules

- Use **Google Gemini** unless the user explicitly asks for OpenAI or needs OpenAI-specific features (masks, background control, compression).
- Assume the user wants a new image unless they explicitly ask for an edit.
- Require the appropriate API key before any live API call.
- Prefer the bundled CLI (`python "$IMAGINE" ...`) over writing new one-off scripts.
- Never modify `scripts/image_gen.py` or files under `scripts/providers/`. If something is missing, ask the user before doing anything else.
- If the result isn't clearly relevant or doesn't satisfy constraints, iterate with small targeted prompt changes; only ask a question if a missing detail blocks success.

## Prompt augmentation

Reformat user prompts into a structured, production-oriented spec. Only make implicit details explicit; do not invent new requirements.

## Use-case taxonomy (exact slugs)

Classify each request into one of these buckets and keep the slug consistent across prompts and references.

Generate:

- photorealistic-natural — candid/editorial lifestyle scenes with real texture and natural lighting.
- product-mockup — product/packaging shots, catalog imagery, merch concepts.
- ui-mockup — app/web interface mockups that look shippable.
- infographic-diagram — diagrams/infographics with structured layout and text.
- logo-brand — logo/mark exploration, vector-friendly.
- illustration-story — comics, children's book art, narrative scenes.
- stylized-concept — style-driven concept art, 3D/stylized renders.
- historical-scene — period-accurate/world-knowledge scenes.

Edit:

- text-localization — translate/replace in-image text, preserve layout.
- identity-preserve — try-on, person-in-scene; lock face/body/pose.
- precise-object-edit — remove/replace a specific element (incl. interior swaps).
- lighting-weather — time-of-day/season/atmosphere changes only.
- background-extraction — transparent background / clean cutout.
- style-transfer — apply reference style while changing subject/scene.
- compositing — multi-image insert/merge with matched lighting/perspective.
- sketch-to-render — drawing/line art to photoreal render.

Quick clarification (augmentation vs invention):

- If the user says "a hero image for a landing page", you may add *layout/composition constraints* that are implied by that use (e.g., "generous negative space on the right for headline text").
- Do not introduce new creative elements the user didn't ask for (e.g., adding a mascot, changing the subject, inventing brand names/logos).

Template (include only relevant lines):

```
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user's main prompt>
Scene/background: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Quality: <low/medium/high/auto>
Input fidelity (edits): <low/high>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Augmentation rules:

- Keep it short; add only details the user already implied or provided elsewhere.
- Always classify the request into a taxonomy slug above and tailor constraints/composition/quality to that bucket. Use the slug to find the matching example in `references/sample-prompts.md`.
- If the user gives a broad request (e.g., "Generate images for this website"), use judgment to propose tasteful, context-appropriate assets and map each to a taxonomy slug.
- For edits, explicitly list invariants ("change only X; keep Y unchanged").
- If any critical detail is missing and blocks success, ask a question; otherwise proceed.

## Examples

### Generation example (hero image)

```
Use case: stylized-concept
Asset type: landing page hero
Primary request: a minimal hero image of a ceramic coffee mug
Style/medium: clean product photography
Composition/framing: centered product, generous negative space on the right
Lighting/mood: soft studio lighting
Constraints: no logos, no text, no watermark
```

### Edit example (invariants)

```bash
python "$IMAGINE" generate --image input.png --prompt "Replace the background with a warm sunset gradient"
```

```
Use case: precise-object-edit
Asset type: product photo background replacement
Primary request: replace the background with a warm sunset gradient
Constraints: change only the background; keep the product and its edges unchanged; no text; no watermark
```

### Style-guided generation (--reference)

```bash
python "$IMAGINE" generate --reference style.png --prompt "A man riding a motorcycle on a white background"
```

```
Use case: style-transfer
Primary request: apply the reference image's visual style to a man riding a motorcycle on a white background
Constraints: preserve palette, texture, and brushwork; no extra elements; plain white background
```

## Prompting best practices (short list)

- Structure prompt as scene -> subject -> details -> constraints.
- Include intended use (ad, UI mock, infographic) to set the mode and polish level.
- Use camera/composition language for photorealism.
- Quote exact text and specify typography + placement.
- For tricky words, spell them letter-by-letter and require verbatim rendering.
- For multi-image inputs, reference images by index and describe how to combine them.
- For edits, repeat invariants every iteration to reduce drift.
- Iterate with single-change follow-ups.
- For latency-sensitive runs, start with quality=low; use quality=high for text-heavy or detail-critical outputs.
- For strict edits (identity/layout lock), consider input_fidelity=high (OpenAI only).
- If results feel "tacky", add a brief "Avoid:" line (stock-photo vibe; cheesy lens flare; oversaturated neon; harsh bloom; oversharpening; clutter) and specify restraint ("editorial", "premium", "subtle").
- These practices apply to both Google and OpenAI providers.

More principles: `references/prompting.md`. Copy/paste specs: `references/sample-prompts.md`.

## Guidance by asset type

Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in `references/sample-prompts.md`.

## CLI + environment notes

- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/image-api.md`

## Reference map

- **`references/cli.md`**: how to *run* image generation/edits/batches via `scripts/image_gen.py` (commands, flags, recipes).
- **`references/image-api.md`**: what knobs exist at the API level (parameters, sizes, quality, background, edit-only fields).
- **`references/prompting.md`**: prompting principles (structure, constraints/invariants, iteration patterns).
- **`references/sample-prompts.md`**: copy/paste prompt recipes (generate + edit workflows; examples only).
