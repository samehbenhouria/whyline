#!/usr/bin/env python3
"""WhyLine CLI: run one investigation and emit the proof artifacts.

Modes:
  --live            query Zetaris via whyline.zetaris_client (needs
                    ZETARIS_API_KEY / ZETARIS_ORG_ID / ZETARIS_BASE_URL)
  --replay FILE     replay recorded Zetaris responses (JSON: label ->
                    rows) instead of calling Zetaris; artifacts are
                    marked as replayed from the recorded responses.

Reasoning:
  --nightshift      also send the evidence pack to Nightshift
                    (METERLESS_* env) and store its narrative finding.
  Without it, findings are the agent's deterministic computations only.

Config: a JSON file with company, question, queries {label: SQL},
sources {label: source name}, margin_pair [label, rev, ni, fy].
Outputs: memory.json (H-MEM store), chain.json (verified proof chain),
report.html (human-readable explanation page).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whyline.agent import InvestigationConfig, run_investigation
from whyline.hmem import HMem
from whyline.report import render_html


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--replay")
    ap.add_argument("--nightshift", action="store_true")
    args = ap.parse_args()

    if args.live == bool(args.replay):
        ap.error("choose exactly one of --live or --replay FILE")

    with open(args.config, encoding="utf-8") as fh:
        cfg_raw = json.load(fh)
    cfg = InvestigationConfig(
        company=cfg_raw["company"],
        question=cfg_raw["question"],
        queries=cfg_raw["queries"],
        sources=cfg_raw.get("sources", {}),
        margin_pair=tuple(cfg_raw["margin_pair"]) if cfg_raw.get("margin_pair") else None,
    )

    recorded = {}
    if args.replay:
        with open(args.replay, encoding="utf-8") as fh:
            recorded = json.load(fh)
        sql_to_label = {v: k for k, v in cfg.queries.items()}

        def query_fn(sql: str):
            label = sql_to_label.get(sql)
            if label is None or label not in recorded:
                raise RuntimeError(f"no recorded response for query label {label!r}")
            return recorded[label]
    else:
        from whyline.zetaris_client import ZetarisClient
        client = ZetarisClient()
        query_fn = client.run_query

    reason_fn = None
    if args.nightshift:
        from whyline.nightshift_client import NightshiftClient
        ns = NightshiftClient()

        def reason_fn(prompt: str, _pack):
            return ns.chat([{"role": "user", "content": prompt}])["content"]

    os.makedirs(args.out, exist_ok=True)
    mem = HMem(os.path.join(args.out, "memory.json"))
    result = run_investigation(mem, cfg, query_fn, reason_fn)

    with open(os.path.join(args.out, "chain.json"), "w", encoding="utf-8") as fh:
        json.dump(result.chain, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(render_html(result.chain, question=cfg.question, company=cfg.company))
    print(json.dumps({"conclusion_id": result.conclusion_id,
                      "computed": result.computed,
                      "mode": "replay" if args.replay else "live",
                      "nightshift": bool(args.nightshift),
                      "out": args.out}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
