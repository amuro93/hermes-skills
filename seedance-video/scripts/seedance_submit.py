#!/usr/bin/env python3
"""
Seedance 2.0 Fast — RunningHub 圖生影片提交腳本

用法：
  python3 seedance_submit.py --check                       查詢帳戶餘額
  python3 seedance_submit.py \\
    --image "https://comfyui.drizzt-studio.com/view?filename=xxx.png&type=output" \\
    --prompt "@Image 1 @Image 2 description" \\
    --output /tmp/seedance_result.mp4

依賴：python3 stdlib + curl
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── 設定 ──────────────────────────────────────────────────────────────────
API_HOST = "https://www.runninghub.cn"
API_HOST_INTL = "https://www.runninghub.ai"            # 備援國際站
ACCOUNT_STATUS_PATH = "/uc/openapi/accountStatus"       # 帳戶查詢端點
WEBAPP_ID = "2037048115194236930"
SUBMIT_PATH = "/task/openapi/ai-app/run"
POLL_PATH = "/task/openapi/outputs"

DEFAULT_DURATION = 6
DEFAULT_RESOLUTION = "480p"
DEFAULT_RATIO = "9:16"
MAX_POLL_ATTEMPTS = 30
POLL_INTERVAL = 10  # seconds


# ── 工具函式 ──────────────────────────────────────────────────────────────

def require_api_key(provided: str | None) -> str:
    """依序從參數、環境變數、嘗試讀取 .env_keys.sh 取得 API Key"""
    if provided:
        return provided

    key = os.environ.get("RUNNINGHUB_API_KEY")
    if key:
        return key

    # 嘗試從 .env_keys.sh 讀取
    candidates = [
        Path.home() / ".env_keys.sh",
        Path("/opt/data/.env_keys.sh"),
        Path(os.environ.get("HERMES_HOME", "~/.hermes")) / ".env",
    ]
    for p in candidates:
        p = Path(p).expanduser()
        if p.exists():
            content = p.read_text()
            for line in content.splitlines():
                if "RUNNINGHUB_API_KEY" in line and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val

    print(json.dumps({"error": "NO_API_KEY",
                       "message": "RUNNINGHUB_API_KEY 未設定。請用 --api-key 傳入或設為環境變數。"},
                      ensure_ascii=False))
    sys.exit(1)


def curl_post_json(url: str, payload: dict, headers: dict | None = None,
                   timeout: int = 60) -> dict:
    """用 curl POST JSON，回傳 parsed dict"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_path = f.name
    try:
        cmd = [
            "curl", "-s", "-S", "--fail-with-body", "-X", "POST", url,
            "--max-time", str(timeout),
            "-H", "Content-Type: application/json",
        ]
        if headers:
            for k, v in headers.items():
                cmd += ["-H", f"{k}: {v}"]
        cmd += ["-d", f"@{tmp_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.unlink(tmp_path)

    body = result.stdout or result.stderr
    if result.returncode != 0:
        try:
            err = json.loads(body)
            msg = err.get("msg", err.get("message", body[:300]))
        except (json.JSONDecodeError, TypeError):
            msg = body[:300]
        print(json.dumps({"error": "HTTP_ERROR", "message": msg}, ensure_ascii=False))
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"error": "PARSE_ERROR",
                          "message": f"無效 JSON 回應: {result.stdout[:300]}"},
                         ensure_ascii=False))
        sys.exit(1)


def check_ffprobe(file_path: str) -> bool:
    """用 ffprobe 檢查影片是否有效"""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", file_path],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            return False
        info = json.loads(r.stdout)
        streams = info.get("streams", [])
        return any(s.get("codec_type") == "video" for s in streams)
    except Exception:
        return False


# ── 帳戶查詢 ──────────────────────────────────────────────────────────────

def fetch_account_status(api_key: str) -> dict:
    """查詢 RunningHub 帳戶餘額、coins、進行中任務數"""
    host = API_HOST  # 優先中國站
    url = f"{host}{ACCOUNT_STATUS_PATH}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    result = curl_post_json(url, {"apikey": api_key}, headers, timeout=15)

    if result.get("code") != 0:
        # 中國站失敗，嘗試國際站備援
        host = API_HOST_INTL
        url = f"{host}{ACCOUNT_STATUS_PATH}"
        result = curl_post_json(url, {"apikey": api_key}, headers, timeout=15)

    if result.get("code") != 0:
        return {
            "status": "error",
            "message": result.get("msg", "查詢帳戶失敗"),
        }

    data = result.get("data", {})
    balance = data.get("remainMoney", "unknown")
    coins = data.get("remainCoins", "unknown")
    running = data.get("currentTaskCounts", "unknown")

    # 判斷帳戶狀態
    try:
        balance_num = float(balance) if balance not in (None, "unknown") else 0
        coins_num = float(coins) if coins not in (None, "unknown") else 0
    except (ValueError, TypeError):
        balance_num = 0
        coins_num = 0

    if balance_num <= 0 and coins_num <= 0:
        status = "no_balance"
    elif balance_num <= 1.0:  # 餘額低於 $1 提醒
        status = "low_balance"
    else:
        status = "ready"

    return {
        "status": status,
        "host": host,
        "balance": f"${balance}",
        "currency": data.get("currency", "USD"),
        "coins": coins,
        "running_tasks": running,
        "api_type": data.get("apiType", "unknown"),
    }


def cmd_check(api_key: str):
    """執行帳戶查詢並顯示結果"""
    info = fetch_account_status(api_key)

    if info["status"] == "error":
        print(json.dumps({
            "status": "error",
            "message": f"查詢失敗: {info.get('message', '未知錯誤')}",
        }, ensure_ascii=False))
        sys.exit(1)

    print(f"✅ 連線成功（{info['host']}）", file=sys.stderr)
    print(f"💰 餘額:        {info['balance']} {info['currency']}", file=sys.stderr)
    print(f"🪙 點數 (Coins): {info['coins']}", file=sys.stderr)
    print(f"⚡ 進行中任務:   {info['running_tasks']}", file=sys.stderr)
    print(f"🔑 API 類型:    {info['api_type']}", file=sys.stderr)

    if info["status"] == "no_balance":
        print(f"⚠️  餘額和點數都為零，無法執行任務！", file=sys.stderr)
    elif info["status"] == "low_balance":
        print(f"⚠️  餘額偏低，建議補充後再跑任務", file=sys.stderr)
    else:
        print(f"✅ 帳戶正常，可執行任務", file=sys.stderr)

    # 輸出 JSON（供 Hermes agent 解析）
    print(json.dumps(info, ensure_ascii=False))


# ── 核心流程 ──────────────────────────────────────────────────────────────

def submit_task(api_key: str, image_url: str, prompt: str,
                duration: int, resolution: str, ratio: str,
                seed: int) -> str:
    """提交 Seedance 任務，回傳 task_id"""

    payload = {
        "webappId": WEBAPP_ID,
        "apiKey": api_key,
        "nodeInfoList": [
            {"nodeId": "3", "fieldName": "image", "fieldValue": image_url},
            {"nodeId": "4", "fieldName": "image", "fieldValue": image_url},
            {"nodeId": "1", "fieldName": "real_person_mode", "fieldValue": "true"},
            {"nodeId": "1", "fieldName": "duration", "fieldValue": str(duration)},
            {"nodeId": "1", "fieldName": "ratio", "fieldValue": ratio},
            {"nodeId": "1", "fieldName": "resolution", "fieldValue": resolution},
            {"nodeId": "1", "fieldName": "prompt", "fieldValue": prompt},
            {"nodeId": "1", "fieldName": "seed", "fieldValue": str(seed)},
        ],
    }

    url = f"{API_HOST}{SUBMIT_PATH}"
    print(f"📤 提交任務至 Seedance 2.0 Fast...", file=sys.stderr)
    print(f"   圖片: {image_url}", file=sys.stderr)
    print(f"   提示: {prompt[:80]}...", file=sys.stderr)
    print(f"   參數: {duration}s, {resolution}, {ratio}", file=sys.stderr)

    resp = curl_post_json(url, payload)

    task_id = None

    # 嘗試從不同格式取出 task_id
    if "taskId" in resp:
        task_id = resp["taskId"]
    elif resp.get("data") and isinstance(resp["data"], dict):
        task_id = resp["data"].get("taskId")

    if not task_id:
        error_msg = resp.get("msg", resp.get("message", json.dumps(resp, ensure_ascii=False)[:200]))
        print(json.dumps({"error": "SUBMIT_FAILED",
                          "message": f"提交失敗: {error_msg}"},
                         ensure_ascii=False))
        sys.exit(1)

    print(f"✅ 任務已提交: {task_id}", file=sys.stderr)
    return task_id


def poll_result(api_key: str, task_id: str, output_path: str, verbose: bool = False) -> dict:
    """輪詢任務結果，下載影片，回傳結果 dict"""

    poll_payload = {"apiKey": api_key, "taskId": task_id}
    url = f"{API_HOST}{POLL_PATH}"

    print(f"⏳ 等待生成中（最多 {MAX_POLL_ATTEMPTS * POLL_INTERVAL // 60} 分鐘）...", file=sys.stderr)

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        if verbose:
            print(f"   輪詢 #{attempt}...", file=sys.stderr)

        resp = curl_post_json(url, poll_payload)

        code = resp.get("code")
        data = resp.get("data")

        # code=0 + data 有內容 = 完成
        if code == 0 and data and isinstance(data, list) and len(data) > 0:
            file_url = data[0].get("fileUrl")
            if not file_url:
                print(json.dumps({"error": "NO_FILE_URL",
                                  "message": "任務完成但無 fileUrl"},
                                 ensure_ascii=False))
                sys.exit(1)

            print(f"✅ 生成完成！下載中...", file=sys.stderr)
            dl_cmd = ["curl", "-s", "-S", "-L", "-o", output_path,
                      "--max-time", "120", file_url]
            dl_result = subprocess.run(dl_cmd, capture_output=True, text=True)

            if dl_result.returncode != 0:
                print(json.dumps({"error": "DOWNLOAD_FAILED",
                                  "message": f"下載失敗: {dl_result.stderr[:200]}"},
                                 ensure_ascii=False))
                sys.exit(1)

            file_size = Path(output_path).stat().st_size
            print(f"📦 下載完成: {file_size:,} bytes", file=sys.stderr)

            # ffprobe 驗證
            if check_ffprobe(output_path):
                print(f"✅ ffprobe 驗證通過", file=sys.stderr)
            else:
                print(f"⚠️  ffprobe 驗證失敗（可能檔案有問題）", file=sys.stderr)

            result = {
                "status": "success",
                "task_id": task_id,
                "output_file": str(Path(output_path).resolve()),
                "file_size": file_size,
                "attempts": attempt,
            }

            # 試著抓出計費資訊
            billing = resp.get("billing", data[0].get("billing", {}))
            if billing:
                result["billing"] = billing
                cost = billing.get("cost") or billing.get("amount") or billing.get("coins")
                if cost:
                    result["cost"] = cost

            return result

        # code=804 = 仍在處理中
        if code == 804 or resp.get("taskStatus") == "RUNNING":
            if verbose:
                print(f"   仍在處理中...", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        # code=805 或其他 = 失敗
        if code == 805 or code == 500:
            msg = resp.get("msg", resp.get("message", "未知錯誤"))
            print(json.dumps({"error": "TASK_FAILED",
                              "message": f"任務失敗 (code={code}): {msg}"},
                             ensure_ascii=False))
            sys.exit(1)

        # 其他情況，繼續輪詢
        if verbose:
            print(f"   狀態 code={code}，繼續等待...", file=sys.stderr)
        time.sleep(POLL_INTERVAL)

    # 超時
    print(json.dumps({"error": "TIMEOUT",
                      "message": f"任務 {task_id} 超過 {MAX_POLL_ATTEMPTS * POLL_INTERVAL // 60} 分鐘仍未完成"},
                     ensure_ascii=False))
    sys.exit(1)


# ── 主程式 ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Seedance 2.0 Fast — RunningHub 圖生影片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "範例:\n"
            "  python3 seedance_submit.py --check              # 查詢餘額\n"
            "  python3 seedance_submit.py \\\n"
            "    --image \"https://comfyui.drizzt-studio.com/view?filename=x.png&type=output\" \\\n"
            "    --prompt \"@Image 1 @Image 2 真人美女在辦公室打字，寫實風格\" \\\n"
            "    --output /tmp/seedance_result.mp4\n"
        ),
    )
    parser.add_argument("--api-key", help="RunningHub API Key（預設從環境變數讀取）")
    parser.add_argument("--check", action="store_true",
                        help="查詢帳戶餘額和配額（不執行生成）")
    parser.add_argument("--image", help="參考圖 URL（Node 3+4 共用同一張）")
    parser.add_argument("--prompt", help="提示詞（含 @Image 1 @Image 2）")
    parser.add_argument("--output", "-o", help="輸出 MP4 路徑")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                        help=f"影片秒數（4-15，預設 {DEFAULT_DURATION}）")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                        choices=["480p", "720p"],
                        help=f"解析度（預設 {DEFAULT_RESOLUTION}）")
    parser.add_argument("--ratio", default=DEFAULT_RATIO,
                        choices=["9:16", "16:9", "1:1", "4:3", "3:4", "adaptive"],
                        help=f"畫面比例（預設 {DEFAULT_RATIO}）")
    parser.add_argument("--seed", type=int, default=-1, help="隨機種子（-1=隨機）")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細輸出")
    parser.add_argument("--no-validate", action="store_true",
                        help="跳過 ffprobe 驗證")

    args = parser.parse_args()
    api_key = require_api_key(args.api_key)

    # ── 若只是查餘額 ──
    if args.check:
        cmd_check(api_key)
        return

    # ── 否則需要 image + prompt + output ──
    if not args.image or not args.prompt or not args.output:
        parser.print_help()
        print("\n❌ 請提供 --image、--prompt 和 --output 參數（或使用 --check 查詢餘額）")
        sys.exit(1)

    # 確保輸出路徑的目錄存在
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # 提交任務
    task_id = submit_task(
        api_key=api_key,
        image_url=args.image,
        prompt=args.prompt,
        duration=args.duration,
        resolution=args.resolution,
        ratio=args.ratio,
        seed=args.seed if args.seed != -1 else random.randint(1, 999999999999999),
    )

    # 輪詢 + 下載
    result = poll_result(
        api_key=api_key,
        task_id=task_id,
        output_path=args.output,
        verbose=args.verbose,
    )

    # 輸出結果 (JSON 格式，方便 Hermes agent 解析)
    output = {
        "status": result["status"],
        "task_id": result["task_id"],
        "output_file": result["output_file"],
        "file_size": result["file_size"],
        "attempts": result["attempts"],
    }
    if "cost" in result:
        output["cost"] = result["cost"]

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
