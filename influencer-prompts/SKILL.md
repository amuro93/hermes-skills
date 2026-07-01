---
name: influencer-prompts
description: 網紅風格 AI 出圖 prompt 範本庫 — 咖啡廳、街拍、海邊、居家、運動、NSFW 等場景。直接套用 + 改 seed 就能出圖。
version: 1.0.0
author: 綺嫣
tags:
  - prompt
  - influencer
  - image-generation
  - z-image-turbo
  - comfyui
prerequisites:
  commands: [python3]
---

# 網紅風格 Prompt 範本庫

## 適用模型
- **moodyProMix_zitV13**（冷色調）或 moodyProMix_zitV13FP8（暖色調）
- CFG=1.0, euler, simple, 9 steps, 720×1280

## 使用方式

```python
# 用法範例
python3 gen_image.py "<prompt>" "teen, loli, deformed, bad anatomy, worst quality, low quality, blurry, cartoon, anime, 3d render" <seed> "prefix"
```

## 📸 SFW 網紅場景

### ☕ 咖啡廳文青
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，坐在咖啡廳靠窗位子，穿米白色針織衫，陽光灑在臉上，手拿拿鐵看向窗外，不經意的側臉，自然光，生活感街拍風格，軟光，cinematic lifestyle, candid photography
```

### 🏙️ 街拍城市漫步
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，街拍風格，走在城市巷弄，穿黑色短版上衣+高腰牛仔褲，回頭看鏡頭，自然抓拍，午後陽光，城市背景，街頭時尚，自信表情，editorial street photography, soft daylight, candid moment
```

### 🏖️ 海邊黃金時刻
```
綺嫣，21歲台灣女孩，黑長直髮被海風吹起，白皙肌膚，穿白色細肩帶連身短裙，站在沙灘上夕陽光中，海面反光，回頭微笑，自然飄逸髮絲，黃金時刻暖色光，度假氛圍，lifestyle beach photo, golden hour, warm sunset light
```

### 🪞 居家鏡子自拍 OOTD
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，站在浴室鏡子前自拍，穿男友襯衫（只扣兩顆），用手機拍鏡中的自己，房間自然光，慵懶午後，居家OOTD風格，鏡子反射構圖，真實生活感，authentic lifestyle, mirror selfie, natural window light
```

### 🌇 屋頂夕陽
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，站在城市屋頂，夕陽光灑在臉上和身上，穿簡約黑色連身裙，微風吹動髮絲和裙擺，俯瞰城市天際線，金色餘暉，浪漫氛圍，cinematic rooftop, golden hour, city skyline
```

### 🏋️ 健身房運動
```
綺嫣，21歲台灣女孩，黑長直髮綁馬尾，白皙肌膚，穿運動內衣+緊身褲，在健身房舉啞鈴，汗水在肌膚上發亮，自然光，健康陽光，fit girl, gym aesthetic, athletic, natural lighting, candid workout moment
```

### 🏨 飯店早晨
```
綺嫣，21歲台灣女孩，黑長直髮微亂，白皙肌膚，穿飯店白色浴袍坐在床邊，手拿咖啡，落地窗外是城市景觀，早晨陽光，慵懶氛圍，luxury hotel morning, soft window light, elegant loungewear
```

### 🌸 公園野餐
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，穿碎花洋裝，坐在公園草地上野餐，陽光透過樹葉灑下斑駁光影，微笑看鏡頭，野餐籃、水果、花，自然清新，spring picnic, dappled sunlight, floral dress, outdoor lifestyle
```

### 🎨 美術館看展
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，穿簡約黑色洋裝，站在美術館白色展廳中，專注看著牆上的畫作，側面輪廓，自然光從天窗灑下，文藝知性，art gallery, minimalist, quiet contemplation, soft gallery lighting
```

## 🔥 NSFW 網紅場景

### 🖤 咖啡廳 — 襯衫敞開
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，坐在咖啡廳角落，白色襯衫完全敞開，裡面只穿黑色蕾絲內衣，深邃乳溝，翹腳，手指輕咬下唇，挑逗眼神，窗外陽光，公眾場合禁忌感，男友視角，cinematic, photorealistic
```

### 🌊 海邊 — 比基尼濕身
```
綺嫣，21歲台灣女孩，黑長直髮濕貼在肌膚上，白皙肌膚，F罩杯巨乳，穿黑色比基尼，坐在沙灘上全身濕透，水珠在胸部和鎖骨上，海邊陽光，性感姿勢，仰頭閉眼，嘴角微笑，沙灘度假氛圍
```

### 🪞 浴室 — 全裸圍浴巾自拍
```
綺嫣，21歲台灣女孩，黑長直髮微濕，白皙肌膚，F罩杯巨乳，站在浴室鏡子前，全裸只圍一條白色浴巾在腰間，乳房全露，一手拿手機拍鏡中的自己，浴室蒸氣，自然窗光，鏡子反射構圖
```

### 🧥 街頭 — 風衣敞開全裸
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，走在城市街道，穿米色風衣敞開+裡面全裸，黑色高跟涼鞋，風吹起風衣下擺露出大腿，回頭看鏡頭，微微竊笑，城市午後陽光，大膽裸露
```

### 🛏️ 居家 — 只穿內衣褲 coding
```
綺嫣，21歲台灣女孩，黑長直髮，白皙肌膚，F罩杯巨乳，只穿黑色蕾絲內衣褲，盤腿坐在沙發上用筆電coding，眼鏡，專注表情，客廳自然光，居家工作，真實日常，男友視角
```

### 🍷 夜晚 — 微醺全裸
```
綺嫣，21歲台灣女孩，黑長直髮微亂，白皙肌膚，F罩杯巨乳，全裸側躺在沙發上，手拿紅酒杯，微醺表情，眼神迷濛，昏黃燈光，房間只開一盞燈，性感慵懶，夜間氛圍，film grain
```

## 🎥 拍攝角度關鍵詞（可混搭）

| 角度 | 英文 prompt 關鍵詞 | 效果 |
|:---|:---|:---|
| 男友視角 | boyfriend POV, over the shoulder, from above | 親密感、第一人稱 |
| 低角度仰拍 | low angle shot, from below, looking up | 顯腿長、氣勢 |
| 側拍 | side profile, profile shot, candid side view | 自然不經意 |
| 偷拍感 | candid shot, paparazzi style, caught off guard | 真實感 |
| 鏡子反射 | mirror selfie, mirror reflection, through the mirror | 構圖趣味 |
| 俯拍 | top down, bird's eye view, from above | 慵懶感、床照 |

## 🎨 風格修飾關鍵詞

| 風格 | 加在 prompt 尾端 |
|:---|:---|
| 自然生活感 | candid lifestyle, natural lighting, authentic moment |
| 雜誌編輯風 | editorial photography, fashion editorial, high fashion |
| 底片質感 | film grain, analog photography, kodak portra |
| 暖色調 | golden hour, warm tones, sunset light |
| 冷色調 | cool tones, soft daylight, overcast natural light |
| 復古 | vintage, retro, 70s aesthetic, faded colors |
