#!/usr/bin/env bash
# Detached launcher for phase 8 captures.
nohup python3 /workspaces/whyline/zetaris-build/phase8_capture.py > /workspaces/phase8.log 2>&1 &
echo "P8_LAUNCHED pid=$!"
