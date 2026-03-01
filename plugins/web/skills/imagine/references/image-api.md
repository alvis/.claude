# Image API quick reference

## Providers

This skill supports two image generation providers:

- **Google Gemini** (default): `gemini-3.1-flash-image-preview` via `google-genai` SDK
- **OpenAI**: `gpt-image-1.5` / `gpt-image-1-mini` via `openai` SDK

---

## Google Gemini

### Endpoint

- `client.models.generate_content(model, contents, config)` via `google-genai` SDK

### Models

- Default: `gemini-3.1-flash-image-preview` (Nano Banana 2)

### Parameters

| Parameter | Default | Values | Notes |
|-----------|---------|--------|-------|
| `aspect_ratio` | `1:1` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `1:4`, `4:1`, `1:8`, `8:1`, `21:9` | Aspect ratio of generated image |
| `resolution` | `1K` | `512px`, `1K`, `2K`, `4K` | Output resolution |
| `n` | `1` | `1`-`10` | Number of images (concurrent calls) |
| `output_format` | `png` | `png`, `jpeg`, `webp` | Output format (conversion via PIL) |

### Edit behavior

- Edit uses the same `generate_content` endpoint with `contents=[PIL_Image, prompt]`
- **No mask support** — Google API does not accept mask images. Use `--provider openai` for mask-based editing.
- For best results, describe the desired change precisely in the prompt with invariants.

### Style references

- Reference images are prepended to the `contents` list before edit images: `contents=[ref_images..., edit_images..., prompt]`
- The model interprets earlier images as style context and later images as edit targets
- A style-reference context line is automatically added to the prompt

### Response format

- `response.candidates[].content.parts[].inline_data.data` — raw image bytes (PNG)
- Images are converted to the requested output format via PIL if needed

### OpenAI size mapping

When `--size` is passed with the Google provider, it maps automatically:

| OpenAI size | Google aspect_ratio | Google resolution |
|-------------|-------------------|------------------|
| `1024x1024` | `1:1` | `1K` |
| `1536x1024` | `3:2` | `1K` |
| `1024x1536` | `2:3` | `1K` |
| `auto` | `1:1` | `1K` |

---

## OpenAI

### Endpoints

- Generate: `POST /v1/images/generations` (`client.images.generate(...)`)
- Edit: `POST /v1/images/edits` (`client.images.edit(...)`)

### Models

- Default: `gpt-image-1.5`
- Alternative: `gpt-image-1-mini` (faster, lower-cost generation)

### Core parameters (generate + edit)

| Parameter | Default | Values | Notes |
|-----------|---------|--------|-------|
| `model` | `gpt-image-1.5` | `gpt-image-1.5`, `gpt-image-1-mini` | Image model |
| `prompt` | (required) | text | Text prompt |
| `n` | `1` | `1`-`10` | Number of images |
| `size` | `1024x1024` | `1024x1024`, `1536x1024`, `1024x1536`, `auto` | Output size |
| `quality` | `auto` | `low`, `medium`, `high`, `auto` | Quality level |
| `background` | (unset) | `transparent`, `opaque`, `auto` | Transparent requires png/webp |
| `output_format` | `png` | `png`, `jpeg`, `webp` | Output format |
| `output_compression` | (unset) | `0`-`100` | Compression (jpeg/webp only) |
| `moderation` | (unset) | `auto`, `low` | Content moderation level |

### Edit-specific parameters

| Parameter | Default | Values | Notes |
|-----------|---------|--------|-------|
| `image` | (required) | file(s) | One or more input images |
| `mask` | (optional) | file | Mask image (same size, alpha channel required) |
| `input_fidelity` | (unset) | `low`, `high` | High = strict identity/layout lock |

### Style references

- OpenAI has no native style-reference parameter. Reference images are combined with edit images and sent to the `images.edit()` endpoint.
- The CLI adds a style-reference context line to the prompt so the model knows which images are style guides.
- When only `--reference` is provided (no `--image`), the edit endpoint is used with the reference as the input image.

### Output

- `data[]` list with `b64_json` per image

---

## Limits & notes

- Input images and masks must be under 50MB.
- Use edits endpoint when the user requests changes to an existing image.
- Masking is prompt-guided; exact shapes are not guaranteed (OpenAI).
- Google does not support masks; describe edits precisely in the prompt.
- Large sizes and high quality increase latency and cost.
- For fast iteration or latency-sensitive runs, start with `quality=low` (OpenAI) or `resolution=512px` (Google); raise for detail-critical outputs.
- Use `input_fidelity=high` for strict edits (identity preservation, layout lock, or precise compositing) — OpenAI only.
- Google `n > 1` makes N concurrent API calls (one image per call).
