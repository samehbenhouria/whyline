# Nightshift integration — verified record

WhyLine's reasoning path is **Meterless Nightshift** with **NVIDIA
Nemotron** connected inside it. This note records exactly what was
verified, where, and what did not work — no claim here goes beyond
a screen, a receipt, or a CLI response seen during the build
(26–27 Oct 2026).

## What the product line actually is (vendor's own words)

The Meterless homepage separates the two builds: the *free web
edition* is "try a job in your browser", while "the hotspot for
your apps runs on the Mac, Windows & DGX editions". WhyLine uses
the **Windows edition (v1.2.7)** daemon as its Nightshift.

## The web edition — configured fully, routes nothing

In the web edition (meterless.ai/Nightshift/WEB/) the team
completed the whole connection chain: an OpenRouter provider key
(free tier, no credits, no payment method) was stored, the
providers header read "2 of 16 cloud keys stored", lanes read
**5/5 ready**, and 8 OpenRouter models showed as connected —
including **Nemotron 3 Super (Free)**, **Nemotron 3 Ultra
(Free)** and **Nemotron 3.5 Lightning (Free)**. A model pin on
Nemotron 3 Ultra (Free) was confirmed by the UI.

No request ever completed a route there:

- Request 1 (default routing, no key yet): console receipt
  "No route completed — in 124 · out 0 — $0.0000".
- Request 2 (pinned to Nemotron 3 Ultra, key stored, lanes 5/5):
  receipt "No route completed — in 257 · out 0 — $0.0000"; the
  OpenRouter key's usage page still showed *Last Used: Never* —
  the request never left the in-tab router.
- Request 3 (unpinned, key stored): receipt "No route completed —
  in 303 · out 0 — $0.0000".
- The Queue/Jobs path answered in plain words:
  "tool_runtime_unavailable: this build has no tool-capable
  attempt path".
- The stored key also does not persist to a fresh tab (the web
  build's "daemon" is the original tab's session).

Conclusion recorded by the team: the web edition demonstrates
the cockpit but executes no routed request. The receipts above
are the evidence; nothing about the web edition is claimed
beyond them.

## The Windows-edition daemon — running and answering

- Installer: official `Nightshift_1.2.7_x64-setup.exe`
  (654,073,220 bytes), downloaded from the vendor's own listing;
  its **SHA-256 was verified** against the published
  `SHA256SUMS` / `APP_BUILD_INFO.txt` before installation
  (a first download whose hash did not match was discarded).
- Installed on the team's Windows machine; the app initialized
  its data directory and started `meterlessd` + the runtime;
  the engine listens on `127.0.0.1:8088`.
- The official CLI (`ns`) reports: `status → ok: true,
  engine_reachable: true, version 1.2.7, admission accepting`.
- The OpenRouter provider key was added in this daemon's
  Providers setup by the account holder (free tier; no credits,
  no payment method), bringing the Nemotron (Free) lanes up in
  the real build.
- WhyLine calls this daemon through its OpenAI-compatible
  endpoint (`whyline/nightshift_client.py`,
  `METERLESS_BASE_URL=http://127.0.0.1:8088/v1`,
  model = the Nemotron model connected in Nightshift).

<!-- NIGHTSHIFT-TEST: at freeze time, add the test request's
     answering model, its verbatim reply reference (demo video
     timestamp), and the OpenRouter key Last Used change that
     proves the request left the machine. -->
