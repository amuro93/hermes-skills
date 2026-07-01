#!/usr/bin/env python3
"""Extract a field from a JSON file. Usage: json_extract.py <file> <key1.key2...>"""
import sys, json

with open(sys.argv[1]) as f:
    data = json.load(f)

keys = sys.argv[2].split(".")
val = data
for k in keys:
    if isinstance(val, dict):
        val = val.get(k, "")
    elif isinstance(val, list):
        try:
            val = val[int(k)]
        except:
            val = ""
    else:
        val = ""
print(val)
