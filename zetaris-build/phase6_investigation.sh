#!/usr/bin/env bash
# Phase 6: derived net-income table + the live WhyLine investigation.
set -u
echo "=== REFRESH ENV ==="
python3 /workspaces/whyline/zetaris-build/phase4_env.py || exit 41
echo "=== CREATE NETINCOME TABLE ==="
cd /workspaces/getting-started || exit 42
python3 scripts/run_sql.py /workspaces/whyline/zetaris-build/apple_netincome_create.sql --skip-exists 2>&1 | tail -n 8
echo "=== RUN INVESTIGATION LIVE ==="
set -a
. /workspaces/getting-started/.env.local
set +a
cd /workspaces/whyline || exit 43
python3 run_investigation.py --live --config investigation.json --out out 2>&1 | tail -n 30
echo "RUN_EXIT=$?"
ls -la out/
grep -a -o "Chain verified: [A-Za-z]*" out/report.html | head -n 2
echo "=== PHASE6_DONE ==="
