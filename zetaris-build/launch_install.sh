#!/usr/bin/env bash
# Detached launcher for the platform install (avoids shell metacharacters
# on the relay path: the install runs in background, logging to a file).
nohup bash /workspaces/whyline/zetaris-build/install_platform.sh > /workspaces/install.log 2>&1 &
echo "LAUNCHED pid=$!"
