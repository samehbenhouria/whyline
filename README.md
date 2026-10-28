# WhyLine — The Agent That Can Explain Why

**Open Agent Hackathon 2026 · Track 02 · Team Idris (solo: Sameh Ben Houria)**

WhyLine investigates a complex question about a company across several
fragmented sources and answers with a *proof chain*, not just a
paragraph: every claim in the final answer links back to the finding
behind it, the evidence row behind that, and the exact SQL and source
that produced the row. If a link is missing or an evidence payload was
altered, the chain refuses to verify — the agent cannot explain what
it cannot prove.

**The frozen investigation** (see `investigation.json` and
`sql/investigation_selects.sql`): *Why is Apple's net margin what it
is, and why must that margin be read inside Apple's SIC industry
frame (3571, Electronic Computers) before any comparison with other
companies?*

## How it works

1. **Investigate (Zetaris).** All data comes through a Zetaris
   platform run by the team (the official local package, in Docker):
   federated SQL over SEC EDGAR XBRL company facts, EDGAR company
   profiles, and the company_dns SIC hierarchy — sources created with
   the official getting-started scripts 01 / 12 / 11, plus one derived
   table (Apple NetIncomeLoss, mirroring script 01, which creates
   Revenue only). The agent queries them through the Zetaris
   run-query endpoint (`whyline/zetaris_client.py`, same contract as
   the official client). Nothing is copied into a local warehouse by
   hand; each fetched row is stored as evidence *with its source and
   its exact SQL*.
2. **Compute (the agent itself).** The arithmetic a proof must not
   delegate — per-year net margin = net income / revenue on
   same-period 10-K rows — is computed deterministically by the
   agent from the evidence, never by the language model.
3. **Reason (Meterless Nightshift + NVIDIA Nemotron).** Narrative
   findings are produced through Meterless Nightshift as the primary
   AI provider (the real Windows-edition daemon, an
   OpenAI-compatible endpoint), with NVIDIA Nemotron connected
   inside Nightshift as the reasoning model. The model receives
   only the evidence pack and must cite the evidence it uses.
   See `docs/NIGHTSHIFT_NOTES.md` for the verified integration
   record — including what the free *web* edition could not do.
4. **Explain (Meterless Engine: H-MEM).** The engine implemented in
   a working feature is **H-MEM — persistent memory and retrieval**
   (`whyline/hmem.py`). Investigations live in a three-layer
   persistent memory (evidence → findings → conclusions, JSON on
   disk, SHA-256 per evidence payload). Retrieval works across
   layers, and `explain()` reconstructs and verifies the complete
   proof chain of any conclusion. The deliverable page
   (`whyline/report.py`) renders that chain: conclusion, findings,
   and for every finding the evidence rows with source, SQL,
   retrieval time and hash.

## Run it

```
# Tests — one command, standard library only:
python3 -m unittest discover -s tests -v        # 9 tests

# Live investigation (needs a running Zetaris platform + .env.local
# with ZETARIS_API_KEY / ZETARIS_ORG_ID / ZETARIS_BASE_URL):
python3 run_investigation.py --config investigation.json --out out --live

# Add the Nightshift narrative finding (METERLESS_* env set):
python3 run_investigation.py --config investigation.json --out out --live --nightshift

# Reproduce from recorded Zetaris responses (marked as replay):
python3 run_investigation.py --config investigation.json --out out --replay responses.json
```

Outputs: `out/memory.json` (the H-MEM store), `out/chain.json`
(the verified proof chain), `out/report.html` (the explanation
page). If any frozen query returns no rows, the run stops with an
explicit error instead of filling the gap.

## Verified results of the frozen investigation

From the live run of 27 Oct 2026 against the team's Zetaris
platform (full artifacts in `examples/`: `chain.json`,
`memory.json`, `report.html` — conclusion `concl_036811d88433`,
**chain verified**, 13 findings, 138 evidence records):

Net margins computed by the agent from same-period EDGAR pairs
(annual = period span ≥ 300 days — the extract labels every row
with its XBRL frame year, so the agent keys on periods, never on
the source's fiscal labels):

| Period | Revenue ($) | Net income ($) | Net margin |
|---|---|---|---|
| 2015-09-27 → 2016-09-24 | 215,639,000,000 | 45,687,000,000 | **21.19 %** |
| 2016-09-25 → 2017-09-30 | 229,234,000,000 | 48,351,000,000 | **21.09 %** |
| 2017-10-01 → 2018-09-29 | 265,595,000,000 | 59,531,000,000 | **22.41 %** |

Quarterly pairs in the same run ranged from 19.20 % to 22.83 % —
the seasonal swing an annual-only reading would hide. The SIC
frame evidence: Apple Inc., CIK 0000320193, **SIC 3571 Electronic
Computers** (Division D Manufacturing, major group 35, industry
group 357); the contrast source places Walmart (SIC 5331 Variety
Stores, revenue 408,214,000,000 $ on its labeled FY2009 row) in a
different industry frame — the reason the question forbids a raw
cross-company margin comparison.

## Tests that show the engine works

Nine tests, all passing: proof-chain reconstruction, persistence
across a reload, retrieval across all three layers, refusal of a
finding with no evidence, tamper detection (an edited payload
breaks verification), the full agent pipeline with margin
computation, the reasoning step linked to *all* evidence, refusal
on empty evidence, and the rendered report carrying the chain's
ids and hashes. (`tests/test_hmem.py`, `tests/test_agent.py`.)

## Sponsor technology — what is unique here

- **Zetaris** is not a logo on a slide: it is the *only* data path.
  The proof chain stores the Zetaris source name and the federated
  SQL for every single fact, so a judge can re-run the exact query
  against the platform and land on the exact row the answer cites.
  The platform itself was installed and verified by the team
  (its own `verify.sh`: 9/9 checks, including a full
  ui → api → driver → spark query; the official preflight: READY).
- **Meterless Nightshift / NVIDIA Nemotron** is the *only*
  reasoning path: narrative findings are generated through
  Nightshift with a Nemotron model connected inside it, and the
  demo video shows a real request passing through Nightshift.
- **H-MEM** is the explanation itself: the "why" is not generated
  after the fact — it is the memory structure of the
  investigation: persistent, retrievable, and verifiable.
- **Cursor** was not used in this build; the code was written by
  the team with its own tooling. Stated plainly, per the rules.

## Layout

- `whyline/hmem.py` — the H-MEM engine (persistent hierarchical memory)
- `whyline/zetaris_client.py` — Zetaris run-query client
- `whyline/nightshift_client.py` — Nightshift (OpenAI-compatible) client
- `whyline/agent.py` — the investigation pipeline
- `whyline/report.py` — the proof-chain HTML page
- `run_investigation.py` — CLI (`--live` / `--replay`, `--nightshift`)
- `investigation.json` — the frozen investigation (question + SQL)
- `sql/` — the frozen investigation SELECTs, with provenance notes
- `tests/` — engine + pipeline tests (9)
- `docs/` — submission texts, slide outline, Nightshift notes
- `examples/` — the verified live run: proof chain, memory store,
  rendered explanation page

*Built for the 27 Oct 2026 23:45 UTC deadline. Every claim in this
README is tied to a verified artifact of the build.*
