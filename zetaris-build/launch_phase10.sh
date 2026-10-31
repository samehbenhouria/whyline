#!/usr/bin/env bash
# Detached launcher for phase 10 (S2a recapture only).
nohup python3 /workspaces/whyline/zetaris-build/phase10_s2a.py > /workspaces/phase10.log 2>&1 &
echo "P10_LAUNCHED pid=$!"
