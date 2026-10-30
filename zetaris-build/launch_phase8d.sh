#!/usr/bin/env bash
# Detached launcher for phase 8d captures.
nohup python3 /workspaces/whyline/zetaris-build/phase8d_capture.py > /workspaces/phase8d.log 2>&1 &
echo "P8D_LAUNCHED pid=$!"
