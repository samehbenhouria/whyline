#!/usr/bin/env bash
# Phase 7: install Playwright + Chromium inside the codespace for the
# S2 screenshots (detached, logged).
set -u
python3 -m pip install --user playwright 2>&1 | tail -n 2
python3 -m playwright install chromium 2>&1 | tail -n 3
python3 -m playwright install-deps chromium 2>&1 | tail -n 2 || true
echo "=== PHASE7_DONE ==="
