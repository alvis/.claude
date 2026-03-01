---
name: imagine
description: >-
  Generate or edit images via a multi-provider Image API using a bundled Python CLI, or craft
  structured image prompts and analyze visual styles from reference images.
  Supports Google Gemini (default), OpenAI, and Recraft. Use when generating, creating, editing,
  inpainting, masking, removing or replacing backgrounds, creating product shots,
  concept art, covers, batch image variants, working with transparent backgrounds,
  vector/SVG output, named artistic styles, crafting image prompts,
  analyzing image styles, extracting visual styles from references,
  or prompt-only generation without producing images.
argument-hint: "[prompt, instruction, or reference image for style analysis]"
---

# Image Generation Skill

Generates or edits images for the current project (e.g., website assets, game assets, UI mockups, product mockups, wireframes, logo design, photorealistic images, infographics). Defaults to **Google Gemini** (`gemini-3.1-flash-image-preview`) as the default provider, with **OpenAI** (`gpt-image-1.5`) available via `--provider openai` and **Recraft** (`recraftv4`) available via `--provider recraft`. Prefers the bundled CLI for deterministic, reproducible runs.

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
- Craft, refine, or generate a structured image prompt without producing an image
- Analyze the visual style of a reference image (palette, texture, composition)
- Extract a reusable style from a reference image for consistent application across assets

## Reference image & style extraction

At the start of every generation workflow, **ask the user whether they have a reference image** they want to match stylistically. Do not skip this step.

If a reference image is provided:

1. **Determine the intended model first.** Use the provider selection decision tree (below) to identify which provider and model the final generation will use. The style extraction method depends on this choice.

   > **Default-path note:** The default Recraft model is V4, not V3. Unless the user explicitly requests V3 or `recraftv3`/`recraftv3_vector`, style references follow Path B (style prompt analysis). When using the default Recraft model, omit `--model` (it already defaults to the latest).

2. **Branch by model:**

   **Path A — Recraft V3 models** (`recraftv3`, `recraftv3_vector`):
   - Use `mcp__recraft__create_style` to extract a reusable style from the reference image.
   - Pass the returned `styleID` via `generate_image` MCP tool or `--style-id` CLI flag.

   **Path B — All other models** (Google Gemini, OpenAI, Recraft V4/V2):
   - Visually analyze the reference image yourself and produce a **style prompt** — a structured text description that captures the visual identity of the reference.
   - The style prompt must cover these dimensions (include only those that are distinctive/non-default):
     - **Medium/technique**: e.g., watercolor, digital illustration, oil painting, 3D render, vector flat
     - **Color palette**: dominant hues, saturation level, temperature (warm/cool), contrast
     - **Texture/surface**: smooth, grainy, painterly brushstrokes, halftone, noise
     - **Lighting**: direction, quality (soft/hard), color temperature, rim light, ambient
     - **Composition style**: symmetrical, rule-of-thirds, cinematic widescreen, centered
     - **Mood/atmosphere**: serene, dramatic, whimsical, gritty, ethereal
     - **Line quality**: clean/sketchy, thick/thin, visible outlines or not
     - **Rendering detail level**: minimal/stylized vs hyperdetailed/photorealistic
   - Present the style prompt to the user for confirmation.
   - Weave the confirmed style prompt into the structured prompt spec (under `Style/medium:`, `Lighting:`, `Color palette:`, `Materials/textures:`, `Vibe/mood:` fields).

3. Regardless of path, describe the extracted/analyzed style attributes back to the user (palette, texture, composition, mood) before proceeding.

If no reference image is provided, proceed directly to prompt crafting.

## Decision tree (provider -> generate vs edit vs batch)

### Provider selection

- If the user needs **mask-based editing** → `--provider openai`
- If the user needs **transparent background control** (`--background transparent`) → `--provider openai`
- If the user needs **fine-grained quality/compression/fidelity control** → `--provider openai`
- If the user needs **named artistic styles** (Illustration, Pop Art, etc.) → `--provider recraft`
- If the user needs **custom style ID from reference images** → `--provider recraft` with explicit V3 model (`recraftv3` or `recraftv3_vector`) — this is opt-in, not the default Recraft path
- If the user needs **style-matched generation from reference images with other providers** → analyze reference visually and encode as style prompt constraints
- If the user needs **vector/SVG output** → `--provider recraft` with a `_vector` model
- If the user needs **specific exact pixel dimensions** → `--provider recraft` (supports 14+ size presets)
- Otherwise → **Google** (default, no `--provider` flag needed)

### Command selection

- If the user provides an input image (or says "edit/retouch/inpaint/mask/translate/localize/change only X") → **`generate --image`**
- If the user wants to apply a reference style → add **`--reference`** to the command
- Else if the user needs many different prompts/assets → **`generate-batch`**
- Else → **`generate`**

All image inputs (`--image`, `--mask`, `--reference`) accept both local file paths and `https://` URLs.

## Workflow

1. **Ask for reference image** — Before anything else, ask whether the user has a reference image or style to match. Do not skip this step.
2. **Extract style** — If a reference is provided, determine the intended model first (step 3 may inform this). For Recraft V3: use `mcp__recraft__create_style` to get a `styleID`. For all other models: visually analyze the reference and produce a style prompt covering medium, palette, texture, lighting, mood, and line quality. Describe the extracted/analyzed style back to the user.
3. **Decide provider + command** — Use the decision tree to select provider and command based on the user's needs.
4. **Collect inputs** — Gather prompt(s), exact text (verbatim), constraints/avoid list, and any input image(s)/mask(s). For multi-image edits, label each input by index and role; for edits, list invariants explicitly.
5. **Craft structured prompt** — This is the **primary deliverable**. Augment the user's intent into a structured prompt spec (see Prompt augmentation section). Only make implicit details explicit; do not invent new requirements.
6. **Present prompt for review** — Show the structured prompt to the user for approval. If the request is **prompt-only** (no image generation needed), stop here and deliver the prompt.
7. **Execute generation** — Run the bundled CLI (`python "$IMAGINE" ...`) or Recraft MCP tools with sensible defaults. For batch runs, write a temporary JSONL, run once, then delete.
8. **Inspect & iterate** — For complex edits/generations, inspect outputs and validate: subject, style, composition, text accuracy, and invariants/avoid items. Make a single targeted change per iteration.
9. **Deliver** — Save/return final outputs and note the final prompt + flags used.

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

### Recraft provider

```
uv pip install openai pillow
```

(Same deps as OpenAI — uses openai SDK with custom base_url)

If `uv` is unavailable:

```
python3 -m pip install google-genai pillow   # Google
python3 -m pip install openai pillow         # OpenAI
```

## Environment

- **Google (default)**: `GOOGLE_API_KEY` must be set for live API calls.
- **OpenAI**: `OPENAI_API_KEY` must be set when using `--provider openai`.
- **Recraft**: `RECRAFT_API_TOKEN` must be set when using `--provider recraft`. Create at https://app.recraft.ai/profile/api

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

### Recraft (`--provider recraft`)

| Parameter | Default | Choices | Notes |
|-----------|---------|---------|-------|
| `--model` | `recraftv4` | `recraftv4`, `recraftv4_vector`, `recraftv4_pro`, `recraftv4_pro_vector`, `recraftv3`, `recraftv3_vector`, `recraftv2`, `recraftv2_vector` | Recraft model |
| `--size` | `1024x1024` | Model-dependent (see references/providers/recraft.md) | WxH or aspect ratio (e.g., `16:9`) |
| `--recraft-style` | (unset) | Named styles (V2/V3 only) | Mutually exclusive with `--style-id` |
| `--style-id` | (unset) | UUID | Custom style ID |
| `--strength` | (unset) | `0.0`-`1.0` | Image-to-image strength (requires `--image`) |
| `--negative-prompt` | (unset) | text | Undesired elements (V2/V3 only) |
| `--output-format` | `png` | `png`, `jpeg`, `webp`, `svg` | SVG auto-selected for vector models |
| `--n` | `1` | `1`-`6` | Number of images (max 6 for Recraft) |

## Defaults & rules

- Use **Google Gemini** unless the user explicitly asks for OpenAI or needs OpenAI-specific features (masks, background control, compression).
- Use **Recraft** when the user needs named styles, custom style references, vector/SVG output, or specific pixel-level size control.
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
Lighting: <direction, quality, color temperature>
Vibe/mood: <emotional tone — nostalgic, dramatic, serene, ethereal, etc.>
Color palette: <palette notes>
Materials/textures: <surface details>
Quality: <low/medium/high/auto>
Input fidelity (edits): <low/high>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Either combined `Lighting/mood:` or separate `Lighting:` + `Vibe/mood:` lines are accepted.

Augmentation rules:

- Keep it short; add only details the user already implied or provided elsewhere.
- Order the prompt spec from global to local: scene/environment first, then subject framing, then fine details (lighting, camera, materials), then constraints/avoid. This reduces randomness in outputs.
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
- For exploration/concept sketching, use short prompts (2-3 elements); for production-ready results, use structured prompts (all 7 elements: Subject, Composition, Context, Medium, Style, Vibe, Attributes).
- If the result feels random, add spatial anchors (placement, depth layers), lighting direction, or mood — not more detail.
- Use format-specific cheat sheets in `references/prompting.md` for photorealism, illustration, vector/logo, graphic design, and 3D.

More principles: `references/prompting.md`. Copy/paste specs: `references/sample-prompts.md`.

## Guidance by asset type

Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in `references/sample-prompts.md`.

## CLI + environment notes

- CLI commands + examples: `references/cli.md`
- API parameter quick reference: `references/providers/google.md`, `references/providers/openai.md`, `references/providers/recraft.md`

## Recraft MCP tools

When the Recraft MCP server is available, prefer MCP tools over CLI for Recraft operations:

| MCP Tool | Purpose | When to use |
|----------|---------|-------------|
| `mcp__recraft__create_style` | Extract reusable style from reference image(s) | Use ONLY when generating with Recraft V3 models (`recraftv3`, `recraftv3_vector`) and user provides a reference image |
| `mcp__recraft__generate_image` | Generate image with optional style | Recraft generation with extracted `styleID` |
| `mcp__recraft__image_to_image` | Transform existing image | Style transfer, image-to-image with Recraft |
| `mcp__recraft__remove_background` | Remove image background | Background extraction tasks |
| `mcp__recraft__replace_background` | Replace image background | Background replacement tasks |
| `mcp__recraft__vectorize_image` | Convert raster to vector | SVG/vector conversion |
| `mcp__recraft__creative_upscale` | Upscale with creative enhancement | Quality enhancement with artistic interpretation |
| `mcp__recraft__crisp_upscale` | Upscale with detail preservation | Quality enhancement preserving original details |

**MCP vs CLI decision**: Use MCP tools when working within Recraft's ecosystem (style extraction + generation). Use CLI (`python "$IMAGINE" --provider recraft`) when you need cross-provider batch runs, custom output paths, or flags not exposed by MCP.

## Reference map

- **`references/cli.md`**: how to *run* image generation/edits/batches via `scripts/image_gen.py` (commands, flags, recipes).
- **`references/providers/google.md`** — Google Gemini API reference
- **`references/providers/openai.md`** — OpenAI GPT Image API reference
- **`references/providers/recraft.md`** — Recraft API reference
- **`references/prompting.md`**: prompting principles (structure, constraints/invariants, iteration patterns).
- **`references/sample-prompts.md`**: copy/paste prompt recipes (generate + edit workflows; examples only).
