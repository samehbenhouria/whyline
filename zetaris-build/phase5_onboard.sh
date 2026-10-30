#!/usr/bin/env bash
# Phase 5: onboard the source chain for the WhyLine investigation
# (company_dns -> edgar_facts -> edgar_profiles -> sic_edgar_usl).
set -u
cd /workspaces/getting-started || exit 31
echo "=== ONBOARD sic_edgar_usl ==="
python3 scripts/onboard.py run sic_edgar_usl 2>&1
echo "ONBOARD_EXIT=$?"
echo "=== CHECK ==="
python3 scripts/onboard.py --check 2>&1 | head -n 20
echo "=== PHASE5_DONE ==="
