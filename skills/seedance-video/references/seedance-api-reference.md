# Seedance 2.0 Fast API Reference (RunningHub)

> 原始來源：`drizzt-comfyui-gallery/references/seedance-video-api.md`
> 最後更新：2026-06-28（整合 hermes-skill-runninghub + 專用提交腳本 + 帳戶查詢 + 定價資料）

---

## 推薦用法：專用腳本

`scripts/seedance_submit.py` 封裝了完整提交 + 輪詢 + 下載 + 帳戶查詢流程：

```bash
python3 scripts/seedance_submit.py --check    # 先查餘額
python3 scripts/seedance_submit.py \
  --image "https://comfyui.drizzt-studio.com/view?filename=xxx.png&type=output" \
  --prompt "@Image 1 @Image 2 真人美女寫實風格" \
  --output /tmp/seedance_$(date +%s).mp4
```

腳本自動處理：API Key 讀取、Node 3+4 相同圖片、參數設定、10 秒輪詢（最長 5 分鐘）、下載、ffprobe 驗證。

---

## 帳戶查詢端點

用於查詢 RunningHub 帳戶餘額和配額，支援雙站備援：

| 站點 | 端點 | 認證 |
|:---|:---|:---|
| 中國站 | `POST https://www.runninghub.cn/uc/openapi/accountStatus` | `Authorization: Bearer <apiKey>` |
| 國際站 | `POST https://www.runninghub.ai/uc/openapi/accountStatus` | `Authorization: Bearer <apiKey>` |

### 請求範例
```bash
curl -s -X POST "https://www.runninghub.cn/uc/openapi/accountStatus" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <KEY>" \
  -d '{"apikey":"<KEY>"}'
```

### 回應範例
```json
{
  "code": 0, "msg": "success",
  "data": {
    "remainCoins": "3769",
    "currentTaskCounts": "0",
    "remainMoney": "14.580",
    "currency": "USD",
    "apiType": "NORMAL"
  }
}
```

---

## 實測定價資料（2026-06-28）

| Duration | 費用 | Coins | 生成時間 | 可用？ |
|:---:|:---:|:---:|:---:|:---:|
| 6 秒 | $0.48 | 6 | ~296 秒 | ✅ |
| **8 秒** | **$0.64** | **5** | **~247 秒** | ✅ **CP 最高** |
| 10 秒 | ❌ | ❌ | ❌ | ❌ 帳戶層級限制 |

500 秒以上任務失敗的錯誤追蹤：
```
"exception_type": "prompt_outputs_failed_validation",
"node_name": "RH_RhartVideoSparkvideo20FastImageToVideo",
"traceback": "[\"duration - Your API balance is insufficient, please recharge and use it\"]"
```
實測後確認**並非餘額不足**（帳戶有 $14.58），而是 Seedance 2.0 Fast 在 NORMAL 帳戶層級的限制。

---

## 完整 API 交易範例（手動版）

### 提交任務

```python
import requests, json, random, time

API_HOST = 'https://www.runninghub.ai'
API_KEY = '<KEY>'
WEBAPP_ID = '2037048115194236930'
headers = {'Content-Type': 'application/json'}

# 1. Get node list (可選：用現有 workflow 的 nodeInfoList 直接改)
r = requests.get(
    f'{API_HOST}/api/webapp/apiCallDemo?apiKey={API_KEY}&webappId={WEBAPP_ID}',
    headers=headers, timeout=15
)
nodes = r.json()['data']['nodeInfoList']

# 2. 覆寫參數
for node in nodes:
    nid, fname = str(node['nodeId']), node['fieldName']
    if nid == '6' and fname == 'text':
        node['fieldValue'] = '@Image 1 @Image 2 <prompt>'
    elif nid == '3' and fname == 'seed':
        node['fieldValue'] = random.randint(1, 999999999999999)
    elif nid == '13' and fname == 'width':
        node['fieldValue'] = 720
    elif nid == '13' and fname == 'height':
        node['fieldValue'] = 1280

# 3. 提交
r = requests.post(
    f'{API_HOST}/task/openapi/ai-app/run',
    headers=headers,
    json={'webappId': WEBAPP_ID, 'apiKey': API_KEY, 'nodeInfoList': nodes},
    timeout=30
)
task_id = r.json()['data']['taskId']
```

### 輪詢結果

```python
# 輪詢（30 次 × 3 秒 = 最長 90 秒）
for i in range(30):
    time.sleep(3)
    r = requests.post(
        f'{API_HOST}/task/openapi/outputs',
        headers=headers,
        json={'apiKey': API_KEY, 'taskId': task_id},
        timeout=15
    )
    d = r.json()
    if d.get('code') == 0 and d.get('data'):
        # 下載影片
        video_data = requests.get(d['data'][0]['fileUrl'], timeout=30)
        with open('/tmp/seedance_out.mp4', 'wb') as f:
            f.write(video_data.content)
        print(f'✅ 完成：{len(video_data.content)} bytes')
        break
```

---

## 已測試端點狀態

| Endpoint | 狀態 | 備註 |
|:---|:---:|:---|
| `POST /task/openapi/ai-app/run` | ✅ **可用** | Seedance 2.0 Fast 主端點 |
| `POST /openapi/v2/run/ai-app/{id}` | ❌ error 1101 | Payload 格式不符 |
| `POST /openapi/v2/run/workflow/{id}` | ✅ 可用 | 用於 Z-Image-Turbo 雲端管線 |
| `POST /openapi/v2/file/upload` | ❌ error 1000 | 一致「未知錯誤」 |
| `POST /openapi/v1/file/upload` | ❌ 回傳 HTML | 非 JSON |
| `POST /openapi/v2/rhart-video/sparkvideo-2.0/multimodal-video` | ❌ error 806 | APIKEY_USER_NOT_FOUND |
| `POST /openapi/v2/bytedance/seedance-2.0-global-mini/multimodal-video` | ❌ error 1014 | 需 Enterprise-Shared API Key |

---

## 檔案上傳 Dead End

RunningHub 的檔案上傳 API (`/openapi/v2/file/upload`) 一致失敗（errorCode 1000）。  
**解法：** 使用 ComfyUI Tunnel 的公開 URL 直接作為 image 來源：

```json
{"nodeId": "3", "fieldName": "image",
 "fieldValue": "https://comfyui.drizzt-studio.com/view?filename=qiyan_gallery_00001_.png&type=output"}
```

---

## 圖片 URL vs Hash

| 格式 | 範例 | 用法 |
|:---|:---|:---|
| 公開 URL | `https://comfyui.drizzt-studio.com/view?filename=...png&type=output` | 不需上傳，直接填 |
| 檔案 hash | `f931d961...e78cfe.png` | 需先透過 RunningHub web UI 上傳 |

**一律用公開 URL 方式，跳過 RunningHub 的上傳環節。**

---

## 單圖 vs 雙圖效果對照

| 方式 | 結果 | 使用時機 |
|:---|:---|:---|
| 2 張相同圖（Node 3+4 同一張） | ✅ 最寫實 | **預設場景** |
| 2 張同服裝不同角度 | 穩定，微變化 | 同一場景第二角度 |
| 1 張圖（只填 Node 3） | ⚠️ 半動漫 | 僅用於變身/轉換場景 |
| 2 張不同服裝 | ❌ 服裝中途變形 | 避免 |
| 純文字（無圖） | 動漫風 | 創作/奇幻類 |
| 1 張圖 + 轉換 prompt | 適合 morph/transform | 單角色變化 |

---

## Timeout 預期（6 秒影片）

| 配置 | 預期時間 |
|:---|:---:|
| 純文字（無圖） | ~1-2 min |
| 1 圖 + 簡單 prompt | ~2-3 min |
| 1 圖 + 轉換 prompt | ~2.5-4 min |
| 2 圖 | ~2.5-5 min |

---

## 前置圖生成（ComfyUI Z-Image-Turbo）

Seedance 的參考圖通常先用 Boss 的 ComfyUI 生成：

1. 用 `drizzt-comfyui-gallery` skill 的標準流程出圖
2. 圖片必須保守（全衣物）
3. 圖片構圖 = 影片起始動作
4. 透過 tunnel URL 傳給 Seedance

### prompt 特別注意

moodyProMix 對性感描述極敏感。要生成「保守但好看」的參考圖：

```text
positive: 端莊套裝、襯衫扣好、長褲、專業形象
negative: nsfw, exposed nipple, see-through, cleavage, bare skin, sexy, seductive
```

---

## Cost 參考

Boss 配額約可生成 **15+ 部 6s/480p 影片** / 週期。  \
提交前一定要先問 Boss。

## 實測記錄

### 2026-06-28 — 首次完整流水線測試 ✅

| 項目 | 值 |
|:--|:--|
| 參考圖 | 咖啡廳女生（全衣物毛衣+襯衫，通過審查 ✅） |
| 提交方式 | `scripts/seedance_submit.py` |
| 任務 ID | `2071097850904924162` |
| 耗時 | ~5 分鐘（296 秒） |
| 費用 | **6 coins（¥0.48）** |
| 解析度 | 496×864（9:16 比例） |
| 長度 | 6.08 秒 |
| 大小 | 1.75 MB |
| 編碼 | H.264 + AAC 音軌 |
| ffprobe 驗證 | ✅ 通過 |
| Boss 滿意度 | ✅ 「還不錯耶」 |

**關鍵經驗：**
- Polling 間隔 10 秒 × 30 次 = 5 分鐘限時足夠
- 腳本 timeout 300s 剛好卡在邊緣（實際 296s），建議下次調高到 600s
- Media 傳送：`MEDIA:/path` 正常運作 ✅
---

## 2026-06-28 實測數據

首次完整實測（咖啡廳女生圖 → 6秒影片）：

| 項目 | 數據 |
|:---|:---:|
| **參考圖** | ComfyUI Z-Image-Turbo, moodyProMix, 12步, 720×1280 |
| **圖片審查** | ✅ 全部衣物，順利通過 |
| **提交方式** | ComfyUI Tunnel URL 直連（`/view?filename=...&type=output`） |
| **提交端點** | `POST /task/openapi/ai-app/run` |
| **總耗時** | **296 秒（~5 分鐘）** |
| **費用** | **6 coins（¥0.48）** |
| **解析度** | 496×864（9:16，略低於標稱 480p） |
| **長度** | 6.08 秒（設定 6 秒） |
| **FPS** | 24 |
| **音軌** | ✅ H.264 video + AAC audio（有背景環境音） |
| **檔案大小** | 1.75 MB |
| **輪詢間隔** | 10 秒 × 30 次 = 最長 5 分鐘 |
| **Task ID** | 2071097850904924162 |

### 實測關鍵結論

1. **ComfyUI Tunnel URL 作為圖片來源 ✅ 可行** — RunningHub 端可以正常讀取 Cloudflare Tunnel 後的 `/view` 端點
2. **實際耗時約 5 分鐘** — 比之前預估的 2-3 分鐘長，但仍在可接受範圍
3. **費用約 6 coins / 部** — ¥0.48 左右
4. **端點一致穩定** — 同一組端點自 2026-06-27 起持續可用
5. **12 步出圖品質良好** — 咖啡廳場景的手部和臉部都無明顯瑕疵
