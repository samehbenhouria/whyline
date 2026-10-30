#!/usr/bin/env bash
# Phase 7 v2: Playwright pinned to 1.49.1 (last release line supporting
# the codespace's Ubuntu 20.04 base) + Chromium + system deps.
set -u
python3 -m pip install --user "playwright==1.49.1" 2>&1 | tail -n 2
python3 -m playwright install chromium 2>&1 | tail -n 3
sudo -n python3 -m playwright install-deps chromium 2>&1 | tail -n 2 || echo "DEPS_SUDO_UNAVAILABLE"
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(args=['--no-sandbox']); print('CHROMIUM_OK', b.version); b.close(); p.stop()"
echo "=== PHASE7_DONE ==="
