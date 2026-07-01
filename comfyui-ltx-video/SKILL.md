---
name: comfyui-ltx-video
description: LTX 2.3 image-to-video pipeline via ComfyUI. 241-frame dual-stage sampling with DualCLIP, LoRA, LatentUpscaler, audio sync.
version: 1.0.0
author: 綺嫣
tags:
  - comfyui
  - ltx
  - video-generation
  - image-to-video
prerequisites:
  commands: [python3, curl]
---

# LTX 2.3 Image-to-Video Pipeline (ComfyUI)

## Overview

Generate 10-second videos from a reference image using LTX 2.3 on ComfyUI. This is a **dual-stage pipeline** using SamplerCustomAdvanced with CFGGuider, not the simple LTXVImgToVideo direct path.

**Use for:** Explicit/NSFW content that would fail Seedance content review. Free to run on your own GPU.

## Prerequisites

| Requirement | Notes |
|:--|:--|
| ComfyUI with LTX 2.3 | LTX 2.3 model + all required nodes |
| RTX 5080 (16GB) recommended | 960×1280 at 241 frames needs ~14GB VRAM |
| RTX 4070 (12GB) possible | Lower resolution or fewer frames |
| DualCLIPLoader | For gemma_3 + text_projection CLIP |
| Required LoRAs | MysticXXX @1.0, dynamic LoRA @0.5 |

## Installation

```bash
hermes skill install amuro93/hermes-skills comfyui-ltx-video
```

## Files

| File | Purpose |
|:--|:--|
| `SKILL.md` | This file |
| `scripts/ltx_exact_gen.py` | Auto-generate the 46-node workflow JSON |
| `references/pitfalls.md` | Troubleshooting guide |

## Pipeline Architecture

```
LoadImage → LTXVPreprocess → EmptyLTXVLatentVideo
                              ↓
Stage 1: LTXVImgToVideoInplace (strength=0.7)
         → SamplerCustomAdvanced (euler_ancestral, 8 steps)
         → LTXVLatentUpscaler (x2)
                              ↓
Stage 2: LTXVImgToVideoInplace (strength=1.0)
         → SamplerCustomAdvanced (euler_cfg_pp, 4 steps)
                              ↓
         VAEDecodeTiled → CreateVideo → SaveVideo
```

### Key Parameters

| Node | Value |
|:--|:--|
| Frames | 241 (~10s @ 24fps) |
| Resolution | 960×1280 (stage 1: 480×640, upscaled) |
| CLIP | DualCLIPLoader (gemma_3_12B + text_projection) |
| LoRAs | MysticXXX @1.0, dynamic @0.5 |
| Stage 1 | euler_ancestral_cfg_pp, 8 sigmas, strength 0.7 |
| Stage 2 | euler_cfg_pp, 4 sigmas, strength 1.0 |
| VAE | VAEDecodeTiled (tile=768, temporal=4096) |

## Usage

### Step 1: Upload reference image

```bash
curl -s -X POST "https://your-comfyui/upload/image" \
  -F "image=@/tmp/ref_image.png;filename=ref.jpg" \
  -F "type=input" -F "overwrite=true" --max-time 30
```

### Step 2: Generate workflow JSON

Edit `scripts/ltx_exact_gen.py` to set:
- `image` = filename uploaded in step 1
- `text` = your prompt (English only, detailed scene description)

Then run:
```bash
python3 scripts/ltx_exact_gen.py > /tmp/ltx_payload.json
```

### Step 3: Submit to ComfyUI

```bash
curl -s -X POST "https://your-comfyui/prompt" \
  -H "Content-Type: application/json" \
  -d @/tmp/ltx_payload.json --max-time 20
```

### Step 4: Poll and download

```bash
# Check queue
curl -s "https://your-comfyui/queue"

# When done, get output filename
curl -s "https://your-comfyui/history/<PROMPT_ID>"

# Download
curl -sL -o /tmp/output.mp4 \
  "https://your-comfyui/view?filename=FILE&type=output&subfolder=video" \
  --max-time 120
```

### Step 5: Deliver

```markdown
MEDIA:/tmp/output.mp4
```

## Prompt Tips (for LTX 2.3)

LTX 2.3 uses natural language English prompts via DualCLIP:

✅ Good:
```
A beautiful young Taiwanese woman lying on a white bed, slowly turning to face the camera, soft warm lighting, natural skin texture, cinematic quality
```

✅ Include action descriptions:
```
She slowly sits up from the bed, stretches her arms above her head, then looks toward the window with morning sunlight streaming in
```

✅ Include audio cues in prompt for synced sound:
```
gentle breathing sounds, soft fabric rustling, ambient room tone
```

## Model & LoRA Reference

| Component | Recommended |
|:--|:--|
| Base model | `ltx-2.3-22b-dev-fp8.safetensors` |
| CLIP | `gemma_3_12B_it_fp8_scaled` + `ltx-2.3_text_projection_bf16` |
| LoRA 1 | `MysticXXX` @ 1.0 (quality enhancement) |
| LoRA 2 | `dynamic` @ 0.5 (motion quality) |
| Upscaler | `ltvx_upscaler_8x.safetensors` |

## Cost Comparison: LTX vs Seedance

| Factor | LTX 2.3 (Local) | Seedance (Cloud) |
|:--|:--:|:--:|
| GPU cost | Free (electricity) | $0.48-0.64/video |
| Content review | ✅ None | ❌ Blocks NSFW |
| Max duration | ~20 seconds | 8 seconds |
| Resolution | 960×1280 | 480p |
| Audio | ✅ Synced audio | ✅ Background audio |
| Speed | ~5-8 minutes | ~3-5 minutes |
| Requires | Boss's PC on | Internet only |

## Troubleshooting

| Problem | Likely Cause | Fix |
|:--|:--|:--|
| Meta tensor error | Wrong CLIP loader | Use DualCLIPLoader, not CLIPLoader |
| Ghosting/artifacts | Single-stage pipeline | Use dual-stage (SamplerCustomAdvanced) |
| Short video (<5s) | frames=49 or 73 | Set frames=241 |
| Blurry output | No LatentUpscaler | Add LTXVLatentUpscaler x2 |
| Person doesn't match ref | No LTXVPreprocess | Add with img_compression=18 |
| 403 on upload | Tunnel auth | Check ComfyUI tunnel access |
| VRAM OOM | 4070 with 960×1280 | Reduce to 720×960 or fewer frames |

## See Also

- `comfyui-image-gen` — Generate reference images for LTX
- `seedance-video` — Cloud alternative for non-explicit content
