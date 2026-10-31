#!/usr/bin/env bash
# Detached launcher for phase 9 captures (jury pass-1 corrections).
nohup python3 /workspaces/whyline/zetaris-build/phase9_capture.py > /workspaces/phase9.log 2>&1 &
echo "P9_LAUNCHED pid=$!"
