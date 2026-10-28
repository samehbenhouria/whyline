# Submission texts — frozen investigation (27 Oct 2026)

## HackOS Description field (150–2000 characters)

<!-- DESC-BEGIN -->
WhyLine is an agent that answers a hard question about a company — and
proves its answer. The frozen demo investigation asks why Apple's net
margin is what it is, and why that margin must be read inside Apple's
SIC industry frame (3571, Electronic Computers) before any comparison
with other companies. WhyLine investigates across fragmented sources
instead of guessing: SEC EDGAR XBRL company facts, EDGAR company
profiles, and the company_dns SIC hierarchy, all queried live through
a Zetaris platform the team installed and verified, as federated SQL.
Every fetched row becomes evidence that keeps its source and its exact
query. The margins are computed by the agent itself, deterministically,
from same-period 10-K rows — never delegated to the model. Narrative
reasoning runs through Meterless Nightshift with NVIDIA Nemotron
connected inside it, over an evidence pack the model must cite. The
answer is built on the Meterless H-MEM engine (persistent memory and
retrieval): findings and the conclusion live in a three-layer
persistent memory, and the "why" is delivered as a verifiable proof
chain — conclusion, the findings behind it, the evidence rows behind
them, down to the SQL a judge can re-run. A claim with no evidence is
refused by construction; an altered fact breaks the chain's hash
verification. Nine automated tests cover the engine and the pipeline.
Built for analysts, investors and compliance reviewers who cannot act
on an answer they cannot audit. Team Idris (solo), Track 02: The Agent
That Can Explain Why.
<!-- DESC-END -->

## One-page summary (Academy checklist)

1. **Problem.** AI answers about companies are fluent and
   unauditable; the data behind them is fragmented across filings,
   registries and classification systems that do not join up.
2. **Users.** Analysts, investors, compliance reviewers.
3. **Solution.** WhyLine: investigate → compute → reason → prove.
   The product surface is the proof-chain page: question,
   conclusion, findings, and every evidence row with source, SQL,
   retrieval time and SHA-256 hash.
4. **Architecture.** Zetaris (only data path — federated SQL over
   EDGAR facts, EDGAR profiles, company_dns SIC) · Nightshift +
   Nemotron (only reasoning path) · H-MEM (explanation memory:
   evidence → findings → conclusions, persistent JSON store).
5. **What is unique.** The explanation is not generated after the
   fact; it *is* the memory structure. A finding cannot exist
   without evidence; tampered evidence fails verification;
   arithmetic is deterministic and re-checkable.
6. **Evidence of work.** Live Zetaris platform verified 9/9 by its
   own `verify.sh`, official preflight READY; sources created with
   the official scripts (01/12/11) + one documented derived
   table; 9 automated tests passing; a real Nightshift request in
   the demo video (see `docs/NIGHTSHIFT_NOTES.md` for the full
   verified record, including the web edition's limits).
7. **Future.** More Zetaris sources (EU NACE, Japan
   classifications are already in the catalogue), the World
   Model engine for shared multi-agent state, and a filing-watch
   mode that re-investigates when new filings land.

## Sponsor explanation (§6.4) — in README + pitch deck

Full text: README, "Sponsor technology — what is unique here",
plus `docs/NIGHTSHIFT_NOTES.md`. Frozen facts to state:
- **Zetaris**: team-run platform (official local package), sources
  01 EDGAR facts / 12 company_dns SIC / 11 EDGAR profiles + the
  derived Apple NetIncomeLoss table (script 01 creates Revenue
  only — the derivation is documented in `sql/`). The agent uses
  the run-query endpoint, same contract as the official client.
- **Meterless**: H-MEM engine implemented in `whyline/hmem.py`,
  demonstrated by 9 tests; Nightshift (Windows edition daemon)
  is the sole reasoning path; Nemotron connected inside
  Nightshift via its Providers setup.
- **NVIDIA**: the Nemotron models connected in Nightshift
  (OpenRouter free lanes: Nemotron 3 Super / Ultra / 3.5
  Lightning). The exact model that answered the demo request is
  named in `docs/NIGHTSHIFT_NOTES.md` at freeze time.
- **Cursor**: not used in this build — stated plainly.
- **Originality**: the proof chain is the product; sponsor tech
  is load-bearing (data path, reasoning path, memory), not
  decoration.
