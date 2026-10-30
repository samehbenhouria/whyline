#!/usr/bin/env bash
# Detached launcher for phase 6 (investigation).
nohup bash /workspaces/whyline/zetaris-build/phase6_investigation.sh > /workspaces/phase6.log 2>&1 &
echo "P6_LAUNCHED pid=$!"
