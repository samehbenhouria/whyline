#!/usr/bin/env python3
"""Phase 3 exploration: login with the platform admin credentials (read
inside the codespace from the secrets file, never printed), save the
session token to a protected file, fetch the OpenAPI spec, and print only
structural facts: login response field names, candidate org ids, and API
paths mentioning keys/orgs. No credential or token value is ever printed."""
import base64
import json
import re
import sys
import urllib.request

BASE = "http://localhost:3000"
SECRETS = "/workspaces/zetaris-secrets"

lines = [l.strip() for l in open(f"{SECRETS}/platform_admin.txt") if l.strip()]
if len(lines) < 2:
    print("ADMIN_FILE_STRUCTURE_UNEXPECTED fields=", len(lines))
    sys.exit(1)
username, password = lines[0], lines[1]
print("ADMIN_FIELDS_OK")

req = urllib.request.Request(
    f"{BASE}/api/auth/login",
    data=json.dumps({"username": username, "password": password}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        login = json.loads(r.read().decode())
except Exception as e:
    print("LOGIN_FAILED", type(e).__name__, getattr(e, "code", ""))
    sys.exit(2)
print("LOGIN_OK top_level_keys=", sorted(login.keys()) if isinstance(login, dict) else type(login))

def find_keys(obj, names, path="$"):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(n in k.lower() for n in names):
                hits.append((f"{path}.{k}", v if isinstance(v, (int,)) else type(v).__name__))
            hits += find_keys(v, names, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            hits += find_keys(v, names, f"{path}[{i}]")
    return hits

for p, v in find_keys(login, ["org", "token", "access", "expir"]):
    print("LOGIN_FIELD", p, "=", v)

token = None
if isinstance(login, dict):
    token = login.get("token") or login.get("accessToken") or login.get("access_token")
if not token:
    m = re.search(r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}", json.dumps(login))
    token = m.group(0) if m else None
if not token:
    print("NO_TOKEN_IN_LOGIN")
    sys.exit(3)
with open(f"{SECRETS}/session_token.txt", "w") as f:
    f.write(token)
print("TOKEN_SAVED len=", len(token))

# OpenAPI spec via basic auth (documented route: /redoc/docs.yaml)
cred = base64.b64encode(f"{username}:{password}".encode()).decode()
for spec_url in (f"{BASE}/redoc/docs.yaml", f"{BASE}/api/docs.yaml", f"{BASE}/openapi.json"):
    try:
        r2 = urllib.request.Request(spec_url, headers={"Authorization": f"Basic {cred}"})
        with urllib.request.urlopen(r2, timeout=30) as resp:
            spec = resp.read().decode(errors="replace")
        with open("/tmp/spec.txt", "w") as f:
            f.write(spec)
        print("SPEC_OK", spec_url, "bytes=", len(spec))
        break
    except Exception as e:
        print("SPEC_MISS", spec_url, getattr(e, "code", type(e).__name__))
else:
    spec = ""

if spec:
    paths = sorted(set(re.findall(r"(/api/[A-Za-z0-9_/{}/.\-]+)", spec)))
    print("PATHS_TOTAL", len(paths))
    for p in paths:
        if any(k in p.lower() for k in ("key", "org", "token")):
            print("PATH_OF_INTEREST", p)
print("PHASE3_EXPLORE_DONE")
