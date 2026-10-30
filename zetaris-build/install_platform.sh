#!/usr/bin/env bash
# Zetaris platform install inside the whyline-build codespace.
# Assumes: /workspaces/getting-started/zetaris-platform.zip present,
#          docker registry login ALREADY done,
#          /workspaces/zetaris-secrets/platform_admin.txt present.
# Logs progress markers; safe to read the log at any time.
set -u
GS=/workspaces/getting-started
PF=$GS/zetaris-platform
GUI=https://whyline-build-jw69qg5prv4h57w9-3000.app.github.dev
step() { echo "=== STEP $1 $2 ==="; }

step 1 "unzip platform"
cd "$GS" || exit 11
if [ ! -d "$PF" ]; then unzip -q zetaris-platform.zip || exit 12; fi
cd "$PF" || exit 13
chmod +x preflight.sh verify.sh 2>/dev/null
find init initdb -type f -name '*.sh' -exec chmod +x {} + 2>/dev/null
ls

step 2 "env GUI_URL"
grep -E '^(GUI_URL|ALLOWED_ORIGINS|UI_PORT)=' .env || true
sed -i "s|^GUI_URL=.*|GUI_URL=$GUI|" .env
sed -i "s|^ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=$GUI|" .env
grep -E '^(GUI_URL|ALLOWED_ORIGINS|UI_PORT)=' .env

step 3 "preflight"
./preflight.sh || echo "PREFLIGHT_NONZERO (continuing to pull; recheck after)"

step 4 "compose pull"
docker compose config --quiet || exit 14
docker compose pull || exit 15

step 5 "compose up core"
docker compose up -d postgres driver api ui || exit 16
sleep 20
docker compose ps -a

step 6 "driver db probe"
docker compose exec -T driver bash -c 'getent hosts postgres; timeout 4 bash -c "</dev/tcp/postgres/5432"; echo TCP_EXIT=$?'
docker compose exec -T postgres pg_isready -h postgres -U zetaris -d metastore || true

echo "=== INSTALL_PHASE1_DONE ==="
