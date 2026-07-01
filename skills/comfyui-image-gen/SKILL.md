---
name: comfyui-image-gen
description: One-shot Z-Image Turbo image generation via ComfyUI. Submit prompt → poll queue → download image. Cross-platform Python script.
version: 1.0.0
author: 綺嫣
tags:
  - comfyui
  - image-generation
  - z-image-turbo
  - ai-art
prerequisites:
  commands: [python3, curl]
---

# ComfyUI Image Generation (Z-Image Turbo)

## Overview

Generate high-quality AI images on any ComfyUI instance with Z-Image Turbo models. This skill provides a complete Python pipeline:

1. Fill workflow template with your prompt + seed
2. Submit to ComfyUI via REST API
3. Poll queue until done
4. Download image to local directory

Works on **Linux, macOS, and Windows** (anywhere Python 3 runs).

## Prerequisites

| Dependency | Version | Notes |
|:--|:--:|:--|
| Python 3 | 3.8+ | Standard library only (urllib, json) |
| ComfyUI | Any | With Z-Image Turbo workflow loaded |
| Tunnel/Network | — | Accessible from your Hermes agent |

## Installation

Run in your Hermes terminal:

```bash
hermes skill install amuro93/hermes-skills comfyui-image-gen
```

Then set your ComfyUI URL:

```bash
# Linux/macOS
export COMFYUI_URL="https://comfyui.example.com"

# Or edit gen_image.py directly
hermes skill edit comfyui-image-gen --file scripts/gen_image.py
# Change COMFYUI_URL on line 17
```

## Files

| File | Purpose |
|:--|:--|
| `SKILL.md` | This file — documentation & usage |
| `scripts/gen_image.py` | Main Python script — one-shot generation |
| `templates/zimage-turbo.json` | Workflow template with `__POSITIVE__`, `__NEGATIVE__`, `__SEED__`, `__PREFIX__` placeholders |

## Usage

### Basic (from Hermes agent)

When the agent is loaded with this skill, it can generate images by running:

```bash
python3 /path/to/skills/comfyui-image-gen/scripts/gen_image.py \
  "綺嫣，21歲台灣女孩，甜美可愛" \
  "teen, loli, deformed, bad anatomy" \
  12345 "my_image"
```

### From your prompt (agent-level)

When using this skill in a conversation, the agent will:

1. Read this SKILL.md for instructions
2. Call `gen_image.py` with your prompt
3. Deliver the image via MEDIA

You can say things like:
- 「出一張綺嫣穿黑色蕾絲的照片」
- 「生一張側躺床上的性感圖」
- 「用 moodyProMix 出一張粉紅色洋裝的圖，seed 88888」

### Command Reference

```bash
python3 scripts/gen_image.py "<positive>" "<negative>" <seed> "<prefix>"
```

| Argument | Required | Example |
|:--|:--:|:--|
| Positive prompt | ✅ | `綺嫣，21歲，黑長直髮，白色洋裝，微笑` |
| Negative prompt | ✅ | `teen, loli, deformed, bad anatomy, worst quality` |
| Seed | ✅ | `12345` (use `-1` for random) |
| Prefix | ✅ | `qiyan_gallery` (used in filename) |

### Output

- Image saved to `./media/images/{prefix}_001.png` (relative to script)
- Script prints: `OK: ./media/images/{prefix}_001.png (file size bytes)`
- Agent should deliver via `MEDIA:/path/to/image.png`

## Customising the Model

Edit `templates/zimage-turbo.json` to change:

- **Model**: Change `model_name` in node `"1"` (e.g. `moodyProMix_zitV13.safetensors`)
- **Resolution**: Change `width`/`height` in node `"4"`
- **Steps/CFG**: Change `steps`/`cfg` in node `"5"`
- **LoRA**: Add `Lora Loader Stack` nodes between model and CLIP

## Recommended Models

| Model | Vibe | Speed |
|:--|:--|:--:|
| `moodyProMix_zitV13.safetensors` | 🏆 甜美冷色調，21歲感 | Fast |
| `moodyProMix_zitV13FP8.safetensors` | 暖色調，稍幼 | Faster |
| `moodyPornMix_zitV7.safetensors` | 冷豔成熟，22-24歲 | Fast |
| `pornmasterZImage_turboV3.safetensors` | 暖色寫實，4070推薦 | Medium |

## Prompt Tips

Z-Image-Turbo is a **DiT model** from Alibaba's Tongyi Lab. Use **natural language sentences**, not SD-style comma keyword lists.

✅ Good:
```
綺嫣，21歲台灣女孩，黑長直髮披肩，白皙肌膚，身穿白色蕾絲睡衣，坐在床邊微笑，柔和暖黃燈光，cinematic lighting
```

❌ Bad:
```
1girl, 21yo, black hair, white skin, white lace nightgown, sitting, smile, warm light
```

## Troubleshooting

| Problem | Likely Cause | Fix |
|:--|:--|:--|
| `Connection refused` | ComfyUI not running or tunnel down | Check `COMFYUI_URL` in script |
| `HTTP 500` after submit | Invalid workflow JSON | Check template placeholders filled correctly |
| Queue never empties | ComfyUI busy with another task | Wait or check ComfyUI console |
| `No output images` | Gen failed or timeout | Check ComfyUI history for errors |
| Image has bad hands | Seed/model limitation | Change seed, add hand-specific negatives |

## See Also

- `comfyui-ltx-video` — LTX 2.3 video generation pipeline
- `seedance-video` — RunningHub Seedance cloud video generation
