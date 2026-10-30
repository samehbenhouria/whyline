#!/usr/bin/env bash
# Phase 2: bootstrap samples + verify.sh (detached, logged).
set -u
cd /workspaces/getting-started/zetaris-platform || exit 21
echo "=== BOOTSTRAP ==="
docker compose up -d bootstrap
sleep 5
docker compose ps -a
echo "=== WAIT BOOTSTRAP EXIT ==="
for i in $(seq 1 40); do
  st=$(docker compose ps -a --format '{{.Service}} {{.State}}' 2>/dev/null | grep '^bootstrap' || true)
  echo "try $i: $st"
  case "$st" in *Exited*) break;; esac
  sleep 15
done
docker compose logs --tail 20 bootstrap || true
echo "=== VERIFY ==="
./verify.sh
echo "=== PHASE2_DONE ==="
