#!/usr/bin/env python3
"""Verify the live run artifacts: chain verification flag, counts, and
the annual margins (must match the frozen results 21.19 / 21.09 / 22.41)."""
import json
import re

OUT = "/workspaces/whyline/out"
chain = json.load(open(f"{OUT}/chain.json"))
print("CHAIN_KEYS", sorted(chain.keys())[:12])
print("VERIFIED_FIELD", chain.get("verified"))
mem = json.load(open(f"{OUT}/memory.json"))
print("MEMORY_TYPE", type(mem).__name__, "LEN", len(mem) if hasattr(mem, "__len__") else "-")
html = open(f"{OUT}/report.html", encoding="utf-8", errors="replace").read()
m = re.search(r"[Cc]hain verified[^<]{0,40}", html)
print("REPORT_CHAIN_LINE", m.group(0) if m else "NOT_FOUND")
text = json.dumps(chain)
for y, pct in (("2016", "21.19"), ("2017", "21.09"), ("2018", "22.41")):
    print("MARGIN_HINT", y, pct, pct in text)
# annual margins from findings if present
def walk(o, path="$"):
    if isinstance(o, dict):
        if o.get("kind") == "annual" and "net_margin" in o:
            print("ANNUAL", path, round(o["net_margin"] * 100, 2))
        for k, v in o.items():
            walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f"{path}[{i}]")
walk(chain)
print("VERIFY_RUN_DONE")
