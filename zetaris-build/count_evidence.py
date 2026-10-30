#!/usr/bin/env python3
"""Count evidence records in memory.json and pull the margin statements."""
import json

mem = json.load(open("/workspaces/whyline/out/memory.json"))
print("MEMORY_KEYS", sorted(mem.keys()))
for k, v in mem.items():
    print("KEY", k, type(v).__name__, len(v) if hasattr(v, "__len__") else "-")
ev = None
for k in ("evidence", "evidences", "records", "proofs"):
    if k in mem:
        ev = mem[k]
if isinstance(ev, dict):
    print("EVIDENCE_COUNT", len(ev))
elif isinstance(ev, list):
    print("EVIDENCE_COUNT", len(ev))
# margin statements live in findings text
chain = json.load(open("/workspaces/whyline/out/chain.json"))
for f in chain.get("findings") or []:
    s = json.dumps(f)
    if "margin" in s.lower():
        print("FINDING_MARGIN_SNIPPET", s[:220])
print("MEMCOUNT_DONE")
