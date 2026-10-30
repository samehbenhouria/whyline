#!/usr/bin/env bash
# Detached launcher for phase 7 (playwright install).
nohup bash /workspaces/whyline/zetaris-build/phase7_playwright.sh > /workspaces/phase7.log 2>&1 &
echo "P7_LAUNCHED pid=$!"
