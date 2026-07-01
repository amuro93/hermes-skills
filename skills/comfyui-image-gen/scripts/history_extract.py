#!/usr/bin/env python3
"""Extract first image info from ComfyUI history JSON.
Outputs: filename, subfolder, type (one per line)"""
import sys, json

with open(sys.argv[1]) as f:
    data = json.load(f)

for pid, info in data.items():
    for node_id, node_out in info.get("outputs", {}).items():
        for img in node_out.get("images", []):
            print(img["filename"])
            print(img.get("subfolder", ""))
            print(img.get("type", "output"))
            sys.exit(0)
# No images found
sys.exit(1)
