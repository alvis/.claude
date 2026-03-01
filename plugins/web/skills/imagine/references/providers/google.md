# Google Gemini — API reference

## Endpoint

- `client.models.generate_content(model, contents, config)` via `google-genai` SDK

## Models

- Default: `gemini-3.1-flash-image-preview` (Nano Banana 2)

## Parameters

| Parameter | Default | Values | Notes |
|-----------|---------|--------|-------|
| `aspect_ratio` | `1:1` | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `1:4`, `4:1`, `1:8`, `8:1`, `21:9` | Aspect ratio of generated image |
| `resolution` | `1K` | `512px`, `1K`, `2K`, `4K` | Output resolution |
| `n` | `1` | `1`-`10` | Number of images (concurrent calls) |
| `output_format` | `png` | `png`, `jpeg`, `webp` | Output format (conversion via PIL) |

## Edit behavior

- Edit uses the same `generate_content` endpoint with `contents=[PIL_Image, prompt]`
- **No mask support** — Google API does not accept mask images. Use `--provider openai` for mask-based editing.
- For best results, describe the desired change precisely in the prompt with invariants.

## Style references

- Reference images are prepended to the `contents` list before edit images: `contents=[ref_images..., edit_images..., prompt]`
- The model interprets earlier images as style context and later images as edit targets
- A style-reference context line is automatically added to the prompt

## Response format

- `response.candidates[].content.parts[].inline_data.data` — raw image bytes (PNG)
- Images are converted to the requested output format via PIL if needed

## OpenAI size mapping

When `--size` is passed with the Google provider, it maps automatically:

| OpenAI size | Google aspect_ratio | Google resolution |
|-------------|-------------------|------------------|
| `1024x1024` | `1:1` | `1K` |
| `1536x1024` | `3:2` | `1K` |
| `1024x1536` | `2:3` | `1K` |
| `auto` | `1:1` | `1K` |

## Limits

- Input images/masks < 50 MB
- No mask support
- `n > 1` = N concurrent calls
- Start with `resolution=512px` for fast iteration
