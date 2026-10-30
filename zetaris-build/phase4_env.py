#!/usr/bin/env python3
"""Phase 4: write /workspaces/getting-started/.env.local from the secrets
file + a fresh login session token. Values are never printed; only field
names and success markers."""
import json
import shlex
import urllib.request

BASE = "http://localhost:3000"
SECRETS = "/workspaces/zetaris-secrets"
lines = [l.strip() for l in open(f"{SECRETS}/platform_admin.txt") if l.strip()]
username, password = lines[0], lines[1]

req = urllib.request.Request(
    f"{BASE}/api/auth/login",
    data=json.dumps({"username": username, "password": password}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as r:
    login = json.loads(r.read().decode())
token = login["idToken"]
org = login["orgId"]
print("LOGIN_OK org=", org)

env = {
    "ZETARIS_BASE_URL": "http://localhost:3000",
    "ZETARIS_ORG_ID": str(org),
    "ZETARIS_USERNAME": username,
    "ZETARIS_PASSWORD": password,
    "ZETARIS_API_KEY": token,
    "ZETARIS_USER_AGENT": "whyline samehbenhouria@gmail.com",
    "ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
    "ZETARIS_JDBC_URL": "jdbc:zetaris:lightning@localhost:10000",
    "ZETARIS_QUERY_LIMIT": "1000",
}
out = "/workspaces/getting-started/.env.local"
with open(out, "w") as f:
    for k, v in env.items():
        f.write(f"{k}={shlex.quote(v)}\n")
import os
os.chmod(out, 0o600)
print("ENV_WRITTEN fields=", ",".join(sorted(env.keys())))
print("PHASE4_DONE")
