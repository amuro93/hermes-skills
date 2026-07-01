#!/usr/bin/env python3
"""Check if ComfyUI queue is empty. Returns 0 if empty, 1 if busy."""
import sys, json

with open(sys.argv[1]) as f:
    data = json.load(f)

running = data.get("queue_running", [])
pending = data.get("queue_pending", [])
if len(running) == 0 and len(pending) == 0:
    sys.exit(0)  # empty
else:
    sys.exit(1)  # busy
