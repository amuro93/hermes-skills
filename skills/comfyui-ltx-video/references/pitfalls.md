# LTX 2.3 I2V — 踩坑紀錄

> 2026-06-29 實測彙整

## ⚠️ 節點設定陷阱

### ResizeImageMaskNode 動態欄位

當 `resize_type = "scale dimensions"` 時，寬高和裁切欄位**必須加前綴**：
```json
{
  "resize_type": "scale dimensions",
  "scale_method": "lanczos",
  "resize_type.crop": "center",
  "resize_type.width": ["314", 0],
  "resize_type.height": ["299", 0]
}
```
❌ 錯誤：`"crop": "center"` — 無前綴，會報 `required_input_missing`
✅ 正確：`"resize_type.crop": "center"`

### API 提交格式

ComfyUI API 接受**兩種格式**：
1. 包裝格式（標準）：`{"prompt": {節點dict}}`
2. 裸格式（某些自訂版本）：直接 `{節點dict}`

如果收到 `"No prompt provided"` 錯誤，就是沒包 `prompt` 層。

### LTX 模型不含 CLIP

`ltx-2.3-22b-dev-fp8.safetensors` 是純影片模型，**不包含文字編碼器**。
必須用 `DualCLIPLoader` 或 `CLIPLoader(type="ltxv")` 分開載入。
可用選項：
- `DualCLIPLoader` (clip_name1=gemma, clip_name2=text_projection, type=ltxv)
- `CLIPLoader` (clip_name=gemma, type=ltxv)
- `LTXVGemmaCLIPModelLoader` (但需要 tokenizer 檔案存在)

### ManualSigmas 格式

Comma-separated string，**不可有空格**（或要有統一格式）：
```
✅ "0.85, 0.7250, 0.4219, 0.0"
✅ "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"
```

## 🐛 錯誤代碼速查

| 錯誤訊息 | 原因 | 解法 |
|:---|:---|:---|
| `Tensors must have same number of dimensions: got 4 and 3` | LTXVAddGuide + 非AV模型不支援 | 改用 LTXVImgToVideoInplace |
| `clip input is invalid: None` | 忘了載 CLIP | 加 CLIPLoader/DualCLIPLoader |
| `Cannot copy out of meta tensor` | CLIP 模型載入失敗 | 換 Gemma/Qwen CLIP 或 DualCLIP |
| `No files matching pattern 'tokenizer.model'` | LTXVGemmaCLIPModelLoader 缺 tokenizer | 改用 CLIPLoader type=ltxv |
| `No prompt provided` | API 沒包 `prompt` 層 | 加 `{"prompt": {...}}` |
| `required_input_missing: crop` | ResizeImageMaskNode 缺前綴 | 加 `resize_type.crop` |

## ✅ 確認可用的模型

| 模型 | 用途 | 備註 |
|:---|:---|:---|
| `ltx-2.3-22b-dev-fp8.safetensors` | 主力影片生成 | 需另載 CLIP |
| `ltx2310eros_beta.safetensors` | 社群微調版 | 可用，但 MysticXXX LoRA 更穩 |
| `ltx-2-19b-distilled-fp8.safetensors` | 舊版 v2 | 相容但較慢 |
| `gemma_3_12B_it_fp8_scaled.safetensors` | 文字編碼 | DualCLIP 用 |
| `ltx-2.3_text_projection_bf16.safetensors` | 文字投影層 | DualCLIP 用 |
| `LTX23_video_vae_bf16.safetensors` | 專用 VAE | VAELoader 用（非必要） |

## ✅ 確認可用的 LoRA

| LoRA | 路徑 | 強度 |
|:---|:---|:---:|
| MysticXXX | `LTX2\\LTX2.3-MysticXXX.safetensors` | 1.0 |
| dynamic | `LTX2\\ltx-2.3-22b-distilled-lora-dynamic_fro09_avg_rank_105_bf16.safetensors` | 0.5 |

## ✅ 確認可用的 Upscaler

| 模型 | 用途 |
|:---|:---|
| `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | 空間放大 x2（目前使用） |
| `ltx-2.3-spatial-upscaler-x1.5-1.0.safetensors` | 空間放大 x1.5 |
| `ltx-2.3-temporal-upscaler-x2-1.0.safetensors` | 時間放大 x2（插幀） |
| `ltx-2-spatial-upscaler-x2-1.0.safetensors` | 舊版 v2 放大 |
