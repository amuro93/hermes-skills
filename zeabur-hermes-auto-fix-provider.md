---
name: zeabur-hermes-auto-fix-provider
description: 解決 Zeabur Hermes Agent 一鍵模板每次重啟 seed config.yaml 導致 401 錯誤的問題。透過持久化 wrapper 腳本 + 直接覆蓋 config.yaml 自動修正 provider。
version: 1.0.0
author: Aina
tags: [zeabur, hermes, deployment, provider, 401, auto-fix]
---

# Zeabur Hermes Agent — Provider 自動修復

## 問題描述

Zeabur 一鍵模板的 Hermes Agent 每次重啟時，`cont-init.d/99-zeabur-llm-config` 會 seed（覆蓋）`/opt/data/config.yaml`，設回指向 Zeabur AI Hub 的預設值：

```yaml
model:
  provider: custom
  base_url: https://sfo1.aihub.zeabur.ai/v1
  default: claude-sonnet-4-5
```

加上 `AI_HUB_API_KEY` 環境變數為 `${AI_HUB_API_KEY}`（未展開的 literal 字串），導致：

```
HTTP 401: Authentication Error, LiteLLM Virtual Key expected.
Received=${AI_HUB_API_KEY}, expected to start with 'sk-'.
```

## 解決方案

在持久化目錄 `/opt/data/` 建立 wrapper 腳本，利用 Zeabur Dashboard 的 ENTRYPOINT 欄位指向它，讓它在每次重啟時**先覆蓋 config.yaml**，再啟動 Hermes。

### 踩坑紀錄

| 嘗試 | 結果 | 原因 |
|:----|:----|:-----|
| ❌ 清掉 LLM_MODEL / LLM_BASE_URL env var | 無效 | seed script 無條件執行 |
| ❌ `hermes config set` 在 wrapper 中（root 執行） | 401 仍在 | 寫入 `/opt/data/.hermes/config.yaml`，但 Hermes 讀的是 `/opt/data/config.yaml` |
| ❌ `su -s /bin/sh hermes -c "hermes config set ..."` | 寫入位置不同 | 同上 |
| ✅ 直接 `cat > /opt/data/config.yaml` 覆蓋檔案 | **成功！** | seed script 先執行 → wrapper 再蓋回去 → Hermes 讀到正確值 |

## 實作步驟

### 1. 確認服務是 Docker Image 模式（非 GitHub Repo）

Zeabur Dashboard → 服務 → Settings → 確認顯示「您的服務目前是從 Docker 映像檔執行的」

### 2. 建立 wrapper 腳本

進 **Exec** 頁籤，貼上：

```bash
cat > /opt/data/startup-wrapper.sh << 'SCRIPT'
#!/bin/sh
echo "🔧 修正 Provider..."
cat > /opt/data/config.yaml << 'CONFIG'
model:
  provider: deepseek
  default: deepseek-v4-flash
CONFIG
echo "✅ 修正完成，啟動 Hermes..."
exec /opt/hermes/docker/main-wrapper.sh "$@"
SCRIPT
chmod +x /opt/data/startup-wrapper.sh
```

> ⚠️ `provider` 和 `default` 請依實際使用的 AI 服務修改。範例使用 DeepSeek V4 Flash。

### 3. 修改 ENTRYPOINT

Zeabur Dashboard → 服務 → **Settings** → 啟動指令區：

| 欄位 | 填入值 |
|:----|:--------|
| **ENTRYPOINT** | `/init /opt/data/startup-wrapper.sh gateway` |
| **CMD** | 留空 |

> **注意**：最後的 `gateway` 是 Hermes 子指令，表示啟動 Telegram Gateway。如果是要啟動其他模式（如 `chat`），請替換。

### 4. 儲存 → 自動 Redeploy

按「儲存」，Zeabur 會自動 Redeploy。觀察日誌應看到：

```
🔧 修正 Provider...
✅ 修正完成，啟動 Hermes...
```

之後的 Telegram 訊息應正常回覆，不再 401。

## 驗證方式

對 Bot 發送訊息，正常回覆即成功。或檢查日誌中無 `AuthenticationError`。

## 其他情境

### 使用不同 Provider

修改 wrapper 中的 `config.yaml` 內容：

```yaml
model:
  provider: openrouter        # 或 gemini, xai 等
  default: anthropic/claude-sonnet-4  # 對應的 model 名稱
```

### 啟動非 Gateway 模式

修改 ENTRYPOINT 最後的參數：

| 用途 | ENTRYPOINT |
|:----|:-----------|
| Telegram Gateway | `/init /opt/data/startup-wrapper.sh gateway` |
| 純 CLI | `/init /opt/data/startup-wrapper.sh` |
| Dashboard only | `/init /opt/data/startup-wrapper.sh dashboard` |

## 原理

```
Container Start
    │
    ▼
s6-overlay init (PID 1)
    │
    ▼
cont-init.d/*          ← Zeabur 的 seed script 在此覆蓋 config.yaml
    │
    ▼
/opt/data/startup-wrapper.sh  ← 我們的自訂 wrapper，蓋回正確值
    │
    ▼
exec main-wrapper.sh gateway   ← 啟動 Hermes Gateway
    │
    ▼
Hermes 讀到正確的 config.yaml → Provider 正確 → 無 401
```
