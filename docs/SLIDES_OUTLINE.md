# Pitch deck outline (§6.2 — 9 required contents, 10 slides)

1. Title — WhyLine, Track 02, Team Idris. "An agent that can explain why — and prove it."
2. Problem & target users — unauditable AI answers; fragmented company
   data (filings / profiles / industry classifications that don't join).
   Users: analysts, investors, compliance.
3. Solution — investigate → reason → prove; the proof chain as product.
4. Live investigation (visual) — the demo question, the result page,
   one chain expanded down to source + SQL.
5. Agent workflow / architecture — diagram: user question → Zetaris
   federated SQL → evidence → Nightshift/Nemotron findings → H-MEM
   conclusion → cited answer.
6. Technical stack — Python, Zetaris REST/SQL, Nightshift, H-MEM JSON
   store with SHA-256 evidence hashes, tests.
7. Zetaris & Meterless use — sources created (EDGAR facts, profiles,
   SIC), Nightshift as sole reasoning path, H-MEM as the engine.
8. What is unique — the explanation is the memory structure itself;
   tamper-evident; a claim without evidence is refused by construction.
9. Product visuals — screenshots: result page, chain view, test run 5/5.
10. Future enhancements — more Zetaris sources (NACE EU, Japan),
    World Model shared state, filing-watch monitoring mode.

[All claims on these slides must match the frozen build — Règle nº 1.
No metric appears here that the build did not actually produce.]
