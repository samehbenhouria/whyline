#!/usr/bin/env bash
# Detached launcher for phase 5 (onboarding).
nohup bash /workspaces/whyline/zetaris-build/phase5_onboard.sh > /workspaces/phase5.log 2>&1 &
echo "P5_LAUNCHED pid=$!"
