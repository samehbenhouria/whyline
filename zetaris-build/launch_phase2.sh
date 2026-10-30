#!/usr/bin/env bash
# Detached launcher for phase 2 (bootstrap + verify).
nohup bash /workspaces/whyline/zetaris-build/phase2_bootstrap_verify.sh > /workspaces/phase2.log 2>&1 &
echo "P2_LAUNCHED pid=$!"
