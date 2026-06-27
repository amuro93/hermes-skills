---
name: hermes-agent-zeabur-deployment
description: "Deploy Hermes Agent to Zeabur cloud platform using the official one-click template, including env var setup, SOUL.md configuration, and Telegram integration."
version: 1.1.0
author: Aina
tags: [hermes, zeabur, deployment, cloud, telegram]
---

# Hermes Agent → Zeabur 雲端部署

將 Hermes Agent 部署到 Zeabur 雲端平台，實現 24/7 在線。

## 官方一鍵模板

Zeabur 官方模板頁面：https://zeabur.com/templates/RTWI4O

模板包含：
- Docker 容器化（~1.3GB image）
- 持久化儲存 `/opt/data/`（SOUL.md、config.yaml、.env）
- 內建 Web Dashboard（port 9119）
- OpenAI-compatible API（port 5000）
- 多平台 messaging 支援

## 部署前準備

### 最低規格
- **2 vCPU / 4 GB RAM**（純 chat + coding 可）
- **4 vCPU / 8 GB RAM**（若會用 browser tools / vision）

### 需要的 API Keys / Token

| 項目 | 來源 | 必填 |
|:---|:---|:---:|
| Telegram Bot Token | `@BotFather` 開新 Bot | ✅ 必填 |
| Telegram User ID | `@userinfobot` 查 | ✅ 必填 |
| LLM API Key | OpenRouter/DeepSeek/Grok/Gemini | ✅ 至少一個 |
| OpenRouter Key（備用） | OpenRouter 後台 | ⏳ 可選 |

⚠️ **需要開一支新的 Telegram Bot**，不要用已在其他 Hermes instance 上運作的 Token — 兩邊會搶訊息。

## 環境變數設定

### 模板預設變數

| 變數 | 建議值 | 說明 |
|:---|:---|:---|
| `HERMES_DASHBOARD` | `true` | 開 Dashboard |
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | `admin` | 登入帳號 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | 自設 | Dashboard 登入密碼 |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | 隨機字串 | 安全 secret |
| `PASSWORD` | 同上 | 服務密碼 |
| `API_SERVER_ENABLED` | `false` | 初期關閉，之後再開 |

### 必須手動新增的變數

| 變數 | 建議值 | 說明 |
|:---|:---|:---|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | 新 Bot 的 Token |
| `TELEGRAM_ALLOWED_USERS` | `1084814634` | 你的 Telegram User ID |
| `LLM_MODEL` | `deepseek/deepseek-v4-flash` | 主力模型 |
| `LLM_BASE_URL` | `https://api.deepseek.com` | API endpoint |

### 設定步驟
1. Zeabur 服務頁面 → Environment 頁籤
2. 填寫上面表格的變數
3. 點 Redeploy 重啟服務

## 部署後設定

### 1. 登入 Dashboard
- 打開 Zeabur 給你的 Dashboard Domain
- Username: `admin` / Password: 你設的密碼

### 2. 編輯 SOUL.md（靈魂檔案）
路徑：服務 → Files → `/opt/data/SOUL.md`

SOUL.md 決定 Hermes 的人格、行為準則、回應風格。範例結構：
```markdown
你是 [角色名]，一個 [描述] 的 AI 助理。
核心原則：
- 原則 A
- 原則 B
回應風格：[風格描述]
開發習慣：[開發流程偏好]
```

編輯後重啟服務生效。

### 3. 設定 Telegram Gateway
- 若已設 `TELEGRAM_BOT_TOKEN` 環境變數，重啟後 Telegram 自動上線
- 或用 Exec 頁籤執行 `hermes gateway setup`

### 4. 驗證連線
在 Telegram 對 Bot 發送：
- `/whoami` → 應顯示 admin
- `/status` → 查看狀態

## 常用管理指令（Exec 頁籤執行）

```bash
hermes status          # 整體狀態
hermes model           # 切換模型
hermes skills          # 管理 skills
hermes sessions list   # 查看 session
hermes gateway restart # 重啟 Telegram
```

## 環境變數注意事項（雷區 🚨）

### 🚨 LLM_MODEL 和 LLM_BASE_URL

模板的 `/opt/data/config.yaml` 預設 `provider: custom` 指向 Zeabur AI Hub：

```yaml
# ❌ 模板預設 — 會導致 401 錯誤
provider: custom
base_url: https://sfo1.aihub.zeabur.ai/v1
api_key: ${AI_HUB_API_KEY}
```

**根因分析**：Zeabur 模板的 s6-overlay cont-init 腳本 **無條件 seed** config.yaml（不檢查 LLM_MODEL/LLM_BASE_URL env var）。2026-06-27 實戰驗證：即使完全不留這兩個 env var，重啟後 config.yaml 仍被覆蓋回預設。

**典型錯誤訊息（AI Hub 卡住時）：**
```
ERROR agent.conversation_loop: API call failed (attempt 1/3) ...
provider=custom base_url=https://sfo1.aihub.zeabur.ai/v1 model=claude-sonnet-4-5
summary=HTTP 401: Authentication Error, LiteLLM Virtual Key expected.
Received=${AI_HUB_API_KEY}, expected to start with 'sk-'.
```

### 已知解法

#### 第一步（最簡單）：Exec 跑一次修正
進 Zeabur Dashboard → 服務 → Exec 頁籤，執行：

```bash
s6-setuidgid hermes hermes config set model.provider deepseek
s6-setuidgid hermes hermes config set model.default deepseek-v4-flash
s6-setuidgid hermes hermes config set model.base_url ""
s6-setuidgid hermes hermes config set model.api_key ""
s6-setuidgid hermes hermes gateway restart
```

⚠️ **關鍵：必須用 `s6-setuidgid hermes` 前綴！** 因為 `hermes config set` 預設寫入 root 的家目錄，但 Hermes 實際運行在 `hermes` 用戶下。不加前綴的話修正看似成功但重啟後失效。

#### 方案 A（推薦長期）：GitHub repo + Custom Dockerfile
建立一個 repo 繼承官方 image，在 entrypoint.sh 中加入 provider 修正：
```dockerfile
FROM nousresearch/hermes-agent:v2026.6.19
COPY entrypoint.sh /usr/local/bin/hermes-entrypoint.sh
RUN chmod +x /usr/local/bin/hermes-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/hermes-entrypoint.sh"]
```
entrypoint.sh 內容：
```bash
#!/bin/sh
set -e
hermes config set model.provider deepseek
hermes config set model.default deepseek-v4-flash
hermes config set model.base_url ""
hermes config set model.api_key ""
exec "$@"
```
優點：版本控制、可複製部署、不受模板 seed 影響。缺點：需手動追官方 image 更新。

#### 方案 B（⛔ 不推薦）：ENTRYPOINT/CMD hack
曾嘗試：ENTRYPOINT 設為 `/bin/sh -c`，CMD 放修正指令 + `exec /init /opt/hermes/docker/main-wrapper.sh`。
**結果：失敗。** s6 作為 PID 1，容器內無法再次 `exec /init`，導致「Welcome to Hermes Agent... Goodbye!」後容器 BackOff。

#### 方案 C（已知問題）：/opt/data/startup-wrapper.sh
建立 `/opt/data/startup-wrapper.sh`，內容包含 `hermes config set ... && exec /opt/hermes/docker/main-wrapper.sh "$@"`，然後將 ENTRYPOINT 指向 `/init /opt/data/startup-wrapper.sh gateway`。
**結果：腳本有被執行但修正無效。** 因為 startup-wrapper.sh 以 root 權限執行，`hermes config set` 寫入 root 的設定檔而非 hermes 用戶的。解法是腳本內用 `s6-setuidgid hermes` 前綴。

```bash
#!/bin/sh
echo "🔧 Fixing provider..."
s6-setuidgid hermes hermes config set model.provider deepseek
s6-setuidgid hermes hermes config set model.default deepseek-v4-flash
s6-setuidgid hermes hermes config set model.base_url ""
s6-setuidgid hermes hermes config set model.api_key ""
echo "✅ Done, starting Hermes..."
exec /opt/hermes/docker/main-wrapper.sh "$@"
```
⚠️ **注意**：經 `/opt/data/startup-wrapper.sh gateway` 啟動時，`"$@"` 會帶入 `gateway`。但此方案尚未完全驗證通過。

### 🚨 關鍵：Files 頁籤編輯 config.yaml 不可靠（反覆驗證）

實戰多次驗證：**Files 頁籤改 config.yaml 後，Redeploy 時幾乎一定會被覆蓋**（Docker container 重建壓掉變更）。

**實際現象**（多次驗證）：
1. ❌ Files 頁籤改 model.provider → Save → Redeploy → 還是 AI Hub（401 錯誤）
2. ❌ 再試一次 Files → 再次被覆蓋
3. ✅ Exec → `s6-setuidgid hermes hermes config set model.provider deepseek` → `s6-setuidgid hermes hermes gateway restart` → 成功

**永遠優先使用 Exec 頁籤的 `s6-setuidgid hermes hermes config set` 指令**，不要靠 Files 頁籤改 config.yaml。這是目前唯一可靠且跨重啟 persist 的解法。

## 部署身份策略：雲端新角色 vs 本機分身

### 核心原則：不要搬運本機 Hermes 的全部設定

Zeabur 的 Hermes 建議給一個 **不同的身份/角色**，原因：

| 面向 | ❌ 直接複製本機 | ✅ 建立新角色 |
|:---|:---|:---|
| SOUL.md | 一樣的人格，兩邊同時跟你聊會混淆 | 新角色，分工明確 |
| Skills | 40+ 技能很多是 Windows 限定，搬了也沒用 | 只安裝雲端通用的 skills |
| 記憶 | Hermes 內部記憶搬運複雜 | 從零開始學，或只搬文字檔 |
| 目標 | 本機開發 + 雲端 24/7 一樣的人格 | ☁️ 秘書/開發助理 + 🖥️ 開發主力 |

### 🚨 命名陷阱：雲端角色名不能跟既有 Bot 同名

Zeabur agent 的**名字必須跟本機既有 Bot 不同**，否則角色自己會 confused：

| ❌ 錯誤示範 | ✅ 正確做法 |
|:---|:---|
| 本機有 SecretaryBot「曉晴」，雲端也取名「曉晴」 | 雲端改名為「蘇綺嫣」，公務稱「蘇秘書」 |
| 角色讀 PROJECTS.md 寫「SecretaryBot = 曉晴本人」，搞不清自己是誰 | 明確區分：舊 Bot = 曉晴，雲端 = 綺嫣 |

命名建議：雲端角色用不同的姓/名，但可保留相同的稱呼模式（如綺秘書/綺嫣/騷老婆/小性奴）。

### SOUL.md 寫法重點

- 不需要寫入好感度/玩具/NSFW 系統（Hermes 非設計給 NSFW 用）
- 把「人格設定 + 開發習慣 + 記憶偏好」寫進 SOUL.md 即可
- 範例：自己用的角色直接設定「對 Boss 好感度爆表」，不需要好感度分數
- 完整模板與撰寫原則：`references/soulmd-character-template.md`

### 🔴 鐵律：SOUL.md 不要出現「AI」「Hermes Agent」字眼

SOUL.md 是角色的人格設定，如果出現「你是 AI 助理」「你是 Hermes Agent」等字眼，會破壞角色沉浸感，讓 LLM 跳出角色。

❌ 錯誤：「你是用戶最信任的 AI 秘書」
✅ 正確：「你是用戶最信任的秘書」

這條適用於所有用 SOUL.md 驅動的角色，不只是雲端版。

### 雲端開發專屬：專案知識庫（PROJECTS.md）

為雲端 agent 建立一份**專屬的專案知識庫**，與「愛奈的個人記憶」分開：

```
/opt/data/
├── SOUL.md              ← 角色人格
├── config.yaml
├── .env
└── projects/            ← 專案參考資料（跟 agent 個人記憶分離）
    ├── PROJECTS.md       ← 專案總覽、開發鐵律、使用者偏好
    ├── 踩坑紀錄.md       ← 跨專案踩坑經驗
    └── secretarybot.md   ← 舊系統架構參考
```

**優點**：
- agent 看到的是「專案參考文件」不是「別人的記憶」
- 不會混淆「我是誰」和「我知道什麼」
- 可獨立更新，不影響角色人格設定

**SOUL.md 開局指引**：在 Communication Style 章節加上：
```
- **開局第一件事：讀取 `/opt/data/projects/PROJECTS.md` 和 `/opt/data/projects/踩坑紀錄.md`**
```

## Auxiliary 服務卡住：切換 Provider 後需設 Auxiliaries

DeepSeek 沒有 vision 能力，所以輔助服務需要分開設定：

```bash
# 這些可以用 deepseek（沒問題）
hermes config set auxiliary.compression.provider deepseek
hermes config set auxiliary.compression.model deepseek-v4-flash
hermes config set auxiliary.session_search.provider deepseek
hermes config set auxiliary.session_search.model deepseek-v4-flash

# Vision 需要支援 vision 的 provider
# 選項 A：用 Gemini（需有 GEMINI_API_KEY 或 GOOGLE_API_KEY）
hermes config set auxiliary.vision.provider gemini
hermes config set auxiliary.vision.model gemini-3.5-flash
# ⚠️ GOOGLE_API_KEY = GEMINI_API_KEY 別名，設其中之一即可
# 或 hermes config set auxiliary.vision.provider openrouter
```

不設也不影響主聊天，只是 log 會出現無害的警告。

## 架構注意事項

- Zeabur 模板建立的是 **獨立的新服務**，不是裝在既有伺服器上
- 如需連回本機電腦開發，選項：
  - **Git 工作流**（最安全）：雲端改 code → push → 本機 pull review
  - **Cloudflare Tunnel + 本機 Tool Server**（進階）：即時操作本機檔案
- 詳見參考檔案：`references/deployment-troubleshooting.md`（完整故障排除 + 環境變數清單）
