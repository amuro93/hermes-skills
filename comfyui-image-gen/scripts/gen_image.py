#!/usr/bin/env python3
"""One-shot Z-Image Turbo image generation via ComfyUI.

For 凌霏: set COMFYUI_URL to Boss's 5080 tunnel.
Uses primary host with optional fallback via COMFYUI_URL_2 env var.

Usage:
  python3 gen_image.py "positive prompt" "negative prompt" SEED "prefix"

Environment variables:
  COMFYUI_URL       Primary host (default: https://comfyui.drizzt-studio.com)
  COMFYUI_URL_2     Fallback host (default: https://4070.drizzt-studio.com)
  OUTPUT_DIR        Output directory (default: ./media/images)
  TEMPLATE_PATH     Workflow template path (default: ./templates/zimage-turbo.json)

Output:
  - Downloads image to OUTPUT_DIR/{prefix}_001.png
  - Prints the file path on success
"""

import sys, os, json, time, urllib.request, urllib.parse, urllib.error

HOSTS = [
    os.environ.get("COMFYUI_URL", "https://comfyui.drizzt-studio.com"),
]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(SCRIPT_DIR, "..", "media", "images"))
TEMPLATE = os.environ.get("TEMPLATE_PATH",
    os.path.join(SCRIPT_DIR, "..", "templates", "zimage-turbo.json"))


def try_host(host: str, data: str, prefix: str) -> str | None:
    """Try to generate on one ComfyUI host. Returns output path or None."""
    try:
        # Step 2: Submit
        req = urllib.request.Request(
            f"{host}/prompt", data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            return None
        print(f"  Submitted to {host}: {prompt_id}", file=sys.stderr)

        # Step 3: Poll queue
        while True:
            qreq = urllib.request.Request(f"{host}/queue")
            qresp = urllib.request.urlopen(qreq, timeout=10)
            queue = json.loads(qresp.read())
            running = queue.get("queue_running", [])
            pending = queue.get("queue_pending", [])
            if len(running) == 0 and len(pending) == 0:
                break
            time.sleep(3)

        # Step 4: Get filename
        hreq = urllib.request.Request(f"{host}/history/{prompt_id}")
        hresp = urllib.request.urlopen(hreq, timeout=10)
        history = json.loads(hresp.read())
        images = []
        for pid, info in history.items():
            for node_id, node_out in info.get("outputs", {}).items():
                for img in node_out.get("images", []):
                    images.append(img)
        if not images:
            return None

        img = images[0]
        filename = img["filename"]
        subfolder = img.get("subfolder", "")
        img_type = img.get("type", "output")

        # Step 5: Download
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"{prefix}_001.png")
        dl_url = f"{host}/view?filename={urllib.parse.quote(filename)}&subfolder={urllib.parse.quote(subfolder)}&type={img_type}"
        dl_req = urllib.request.Request(dl_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": f"{host}/"
        })
        with urllib.request.urlopen(dl_req, timeout=60) as resp_dl:
            with open(out_path, "wb") as f:
                f.write(resp_dl.read())

        return out_path

    except (urllib.error.URLError, urllib.error.HTTPError,
            OSError, json.JSONDecodeError) as e:
        print(f"  {host} failed: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 5:
        print("Usage: gen_image.py <pos> <neg> <seed> <prefix>", file=sys.stderr)
        sys.exit(1)

    pos = sys.argv[1]
    neg = sys.argv[2]
    seed = int(sys.argv[3])
    prefix = sys.argv[4]

    # Step 1: Generate workflow from template
    with open(TEMPLATE, "r") as f:
        tmpl = f.read()
    out = tmpl.replace("__POSITIVE__", pos)
    out = out.replace("__NEGATIVE__", neg)
    out = out.replace("__SEED__", str(seed))
    out = out.replace("__PREFIX__", prefix)
    json.loads(out)  # validate
    data = out.encode("utf-8")

    # Try hosts in order
    last_error = None
    for host in HOSTS:
        print(f"  Trying {host}...", file=sys.stderr)
        result = try_host(host, data, prefix)
        if result:
            size = os.path.getsize(result)
            print(f"OK: {result} ({size} bytes)")
            return
        last_error = f"All hosts failed"

    print(f"ERROR: {last_error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
