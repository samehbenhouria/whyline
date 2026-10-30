#!/usr/bin/env python3
"""Extract finding/evidence counts and every margin figure from chain.json."""
import json

chain = json.load(open("/workspaces/whyline/out/chain.json"))
findings = chain.get("findings") or []
print("FINDINGS_COUNT", len(findings))
concl = chain.get("conclusion")
print("CONCLUSION_TYPE", type(concl).__name__)
if isinstance(concl, dict):
    print("CONCLUSION_KEYS", sorted(concl.keys()))
    print("CONCLUSION_ID", concl.get("id") or concl.get("conclusion_id"))
ev = 0
margins = []
def walk(o):
    global ev
    if isinstance(o, dict):
        if "sha256" in o or "hash" in o:
            ev += 1
        if "net_margin" in o:
            margins.append((o.get("period") or o.get("label") or o.get("span") or "?", o["net_margin"], o.get("kind")))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
walk(chain)
print("EVIDENCE_HASH_NODES", ev)
for p, m, k in margins:
    print("MARGIN", p, round(m * 100, 2), k)
print("EXTRACT_DONE")
