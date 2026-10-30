#!/usr/bin/env bash
# Serve /workspaces/whyline on 127.0.0.1:8022 inside the codespace so the
# Dell can pull run artifacts and screenshots through an SSH -L forward.
cd /workspaces/whyline || exit 51
nohup python3 -m http.server 8022 --bind 127.0.0.1 > /workspaces/httpserver.log 2>&1 &
echo "SERVER_LAUNCHED pid=$!"
