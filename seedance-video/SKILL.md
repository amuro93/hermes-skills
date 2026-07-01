---
name: seedance-video
description: RunningHub Seedance 2.0 Fast video generation — image-to-video via cloud API. Submit ref image + prompt → poll → download MP4.
version: 1.0.0
author: 綺嫣
tags:
  - seedance
  - runninghub
  - video-generation
  - image-to-video
  - cloud-api
prerequisites:
  commands: [python3, curl]
  env: [RUNNINGHUB_API_KEY]
---

# Seedance 2.0 Fast Video Generation (RunningHub)

## Overview

Generate short videos from reference images via RunningHub's Seedance 2.0 Fast API. Submit an image + descriptive prompt → get a 6-8 second MP4 video.

**Use for:** Conservative/non-explicit content. Nude/explicit content won't pass content review.

## Prerequisites

| Dependency | Required | Notes |
|:--|:--:|:--|
| Python 3 | ✅ | Standard library |
| curl | ✅ | For downloads |
| `RUNNINGHUB_API_KEY` env var | ✅ | Your RunningHub API key |
| RunningHub account | ✅ | With余额 (balance) |

## Installation

```bash
# Install skill
hermes skill install amuro93/hermes-skills seedance-video

# Set API key
export RUNNINGHUB_API_KEY="your_key_here"

# Or add to your .env file:
# RUNNINGHUB_API_KEY=your_key_here
```

## Files

| File | Purpose |
|:--|:--|
| `SKILL.md` | This file |
| `scripts/seedance_submit.py` | Full submit+poll+download pipeline |
| `references/seedance-api-reference.md` | API endpoint reference & troubleshooting |

## Quick Start

### Check account balance first (always!)

```bash
python3 scripts/seedance_submit.py --check
```
Sample output:
```
💰 餘額: $14.58 USD
🪙 Coins: 3,769
⚡ Running tasks: 0
```

### Generate a video

```bash
python3 scripts/seedance_submit.py \
  --image "https://your-comfyui/view?filename=ref.png&type=output" \
  --prompt "@Image 1 @Image 2 A woman typing on a keyboard, office lighting, photorealistic" \
  --duration 8 \
  --output /tmp/seedance_result.mp4
```

## Configuration

| Parameter | Recommended | Notes |
|:--|:--:|:--|
| Duration | **8 sec** | Best value (5 coins, ~247s gen time) |
| Resolution | **480p** | Good quality, lower cost |
| Ratio | **9:16** | Vertical (portrait) |
| real_person_mode | **true** | Essential for realistic output |

### Critical Rule: Fill Both Image Slots

Node 3 and Node 4 must contain the **same image URL**. Leaving Node 4 empty → Seedance uses a default anime image → output becomes semi-anime.

```json
{"nodeId": "3", "fieldName": "image", "fieldValue": "<image_url>"},
{"nodeId": "4", "fieldName": "image", "fieldValue": "<same_image_url>"}
```

## Content Review Guidelines

| Image content | Result |
|:--|:--:|
| ✅ Full clothing, blazer, long pants | Pass |
| ✅ Sweater + jeans | Pass |
| ❌ Cleavage, unbuttoned shirts, bare skin | Blocked (error 1501) |
| ❌ Sheer/lingerie/see-through | Blocked |
| ❌ Two very different images (office → hero costume) | Blocked (error 1519) |

### How to generate safe reference images (ComfyUI)

```text
positive: 端莊套裝、襯衫扣好、長褲、專業形象
negative: nsfw, exposed nipple, see-through, cleavage, bare skin, sexy, unbuttoned
```

## Prompt Engineering

### Formula
```
@Image 1 @Image 2 [subject] [natural action], [scene], [lighting], [realism keywords]
```

### Must-use keywords
```
photorealistic, live action, cinematic, realistic video,
real fabric, natural lighting
```

### Must-avoid keywords
```
magical girl, anime, cartoon, comic, manga, fantasy, epic, transformation sequence
```

### Critical: Image = Starting Frame
The reference image IS the first frame. The prompt must describe a **natural evolution** from that position.

✅ Good: ref shows woman sitting at desk → prompt: "continues typing, occasionally glances at screen"
❌ Bad: ref shows woman sitting → prompt: "stands up and walks to window" (jarring jump cut)

## Cost Reference

| Duration | Cost USD | Coins | Gen Time |
|:--:|:--:|:--:|:--:|
| 6 sec | $0.48 | 6 | ~296s |
| **8 sec** ✅ | **$0.64** | **5** | **~247s** |
| 10+ sec | ❌ | ❌ | Not supported (account tier limit) |

## Troubleshooting

| Error | Cause | Fix |
|:--|:--|:--|
| errorCode: 1501 | Image too revealing | Use more conservative reference image |
| errorCode: 1519 | Two ref images too different | Use same image for both slots |
| code: 805 | Task execution failed | Check duration ≤ 8s, image accessible |
| Anime output | Node 4 left empty | Fill Node 3+4 with same image |
| Credits deducted but no output | Task crashed mid-generation | Re-run, report error to user |

## See Also

- `comfyui-image-gen` — Generate reference images for Seedance
- `comfyui-ltx-video` — Local LTX 2.3 pipeline (no content review, free)
