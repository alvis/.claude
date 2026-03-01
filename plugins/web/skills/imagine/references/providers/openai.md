# OpenAI GPT Image — API reference

## Endpoints

- Generate: `POST /v1/images/generations` (`client.images.generate(...)`)
- Edit: `POST /v1/images/edits` (`client.images.edit(...)`)

## Models

- Default: `gpt-image-1.5`
- Alternative: `gpt-image-1-mini` (faster, lower-cost generation)

## Core parameters (generate + edit)

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

## Edit-specific parameters

| Parameter | Default | Values | Notes |
|-----------|---------|--------|-------|
| `image` | (required) | file(s) | One or more input images |
| `mask` | (optional) | file | Mask image (same size, alpha channel required) |
| `input_fidelity` | (unset) | `low`, `high` | High = strict identity/layout lock |

## Style references

- OpenAI has no native style-reference parameter. Reference images are combined with edit images and sent to the `images.edit()` endpoint.
- The CLI adds a style-reference context line to the prompt so the model knows which images are style guides.
- When only `--reference` is provided (no `--image`), the edit endpoint is used with the reference as the input image.

## Output

- `data[]` list with `b64_json` per image

## Limits

- Input images/masks < 50 MB
- Masking is prompt-guided
- Large sizes/high quality increase latency
- Start with `quality=low` for fast iteration
- `input_fidelity=high` for strict edits
