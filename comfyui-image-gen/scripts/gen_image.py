#!/usr/bin/env python3
"""One-shot Z-Image Turbo image generation via 5080 ComfyUI.

Usage:
  python3 gen_image.py "positive prompt" "negative prompt" SEED "prefix"

Example:
  python3 gen_image.py "1girl, blowjob, kneeling" "bad hands" 12345 "qiyan_erotic"

Output:
  - Downloads image to /opt/data/media/images/{prefix}_001.png
  - Prints the file path on success
"""

import sys, os, json, time, urllib.request, urllib.parse

import os
COMFYUI_URL = os.environ.get("COMFYUI_URL", "https://comfyui.drizzt-studio.com")
OUTPUT_DIR = "/opt/data/media/images"
SCRIPT_DIR = "/opt/data/scripts"
TEMPLATE = "/opt/data/workflows/zimage-turbo.json"

def main():
    if len(sys.argv) < 5:
        print("Usage: gen_image.py <pos> <neg> <seed> <prefix>", file=sys.stderr)
        sys.exit(1)

    pos = sys.argv[1]
    neg = sys.argv[2]
    seed = int(sys.argv[3])
    prefix = sys.argv[4]

    # --- Step 1: Generate workflow from template ---
    with open(TEMPLATE, "r") as f:
        tmpl = f.read()
    out = tmpl.replace("__POSITIVE__", pos)
    out = out.replace("__NEGATIVE__", neg)
    out = out.replace("__SEED__", str(seed))
    out = out.replace("__PREFIX__", prefix)
    import json as _json
    _json.loads(out)  # validate

    # --- Step 2: Submit to ComfyUI ---
    data = out.encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        print(f"ERROR: No prompt_id in response: {result}", file=sys.stderr)
        sys.exit(1)
    print(f"Submitted: {prompt_id}")

    # --- Step 3: Poll queue until done ---
    while True:
        req2 = urllib.request.Request(f"{COMFYUI_URL}/queue")
        resp2 = urllib.request.urlopen(req2)
        queue = json.loads(resp2.read())
        running = queue.get("queue_running", [])
        pending = queue.get("queue_pending", [])
        if len(running) == 0 and len(pending) == 0:
            break
        time.sleep(3)

    # --- Step 4: Get output filename ---
    req3 = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
    resp3 = urllib.request.urlopen(req3)
    history = json.loads(resp3.read())
    images = []
    for pid, info in history.items():
        for node_id, node_out in info.get("outputs", {}).items():
            for img in node_out.get("images", []):
                images.append(img)

    if not images:
        print(f"ERROR: No output images in history: {history}", file=sys.stderr)
        sys.exit(1)

    img = images[0]
    filename = img["filename"]
    subfolder = img.get("subfolder", "")
    img_type = img.get("type", "output")

    # --- Step 5: Download ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{prefix}_001.png")
    dl_url = f"{COMFYUI_URL}/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(subfolder)}&type={img_type}"
    dl_req = urllib.request.Request(dl_url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": f"{COMFYUI_URL}/"
    })
    with urllib.request.urlopen(dl_req) as resp_dl:
        with open(out_path, "wb") as f:
            f.write(resp_dl.read())

    print(f"OK: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    main()
