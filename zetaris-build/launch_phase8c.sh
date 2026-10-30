#!/usr/bin/env bash
# Detached launcher for phase 8c captures.
nohup python3 /workspaces/whyline/zetaris-build/phase8c_capture.py > /workspaces/phase8c.log 2>&1 &
echo "P8C_LAUNCHED pid=$!"
