"""Thin Zetaris client for WhyLine.

Mirrors the official getting-started client contract:
  POST {ZETARIS_BASE_URL}/api/proxy/sql-editor/sqls/run-query
  headers: Authorization: Bearer <ZETARIS_API_KEY>, X-Org-ID: <numeric>,
           X-Request-ID: <uuid>
  body: {"sql": ..., "limit": ...}

Zetaris is the ONLY data path of the agent: every fact the agent uses
was returned by this client (or replayed from a recorded response of
this client, marked as such).
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ZetarisError(RuntimeError):
    pass


class ZetarisClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 org_id: str | None = None, timeout: int = 120):
        self.base_url = (base_url or os.environ.get("ZETARIS_BASE_URL", "http://localhost:3000")).rstrip("/")
        self.api_key = api_key or os.environ.get("ZETARIS_API_KEY", "")
        self.org_id = org_id or os.environ.get("ZETARIS_ORG_ID", "")
        self.timeout = timeout
        if not self.api_key:
            raise ZetarisError("ZETARIS_API_KEY is not set (create it in the Zetaris GUI).")
        if not self.org_id:
            raise ZetarisError("ZETARIS_ORG_ID is not set.")

    def run_query(self, sql: str, limit: int = 1000) -> list[dict[str, Any]]:
        """Run one SQL statement; return rows as a list of dicts."""
        body = {"sql": sql, "limit": limit}
        engine_id = os.environ.get("ZETARIS_ENGINE_ID")
        if engine_id:
            body["engineId"] = engine_id
        req = Request(
            f"{self.base_url}/api/proxy/sql-editor/sqls/run-query",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Org-ID": self.org_id,
                "X-Request-ID": str(uuid.uuid4()),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            detail = e.read(500).decode("utf-8", errors="replace")
            raise ZetarisError(f"Zetaris query failed: HTTP {e.code} {detail}") from e
        except (URLError, OSError, TimeoutError) as e:
            raise ZetarisError(f"Cannot reach Zetaris at {self.base_url}: {e}") from e
        return self._rows(raw)

    @staticmethod
    def _rows(raw: Any) -> list[dict[str, Any]]:
        """Normalize the several shapes a run-query result can take.

        The platform answers with rows as JSON arrays plus a column
        list — but the two do not always sit at the same level of the
        response object. This walks the response (one container deep)
        pairing each row array with the column names found beside it,
        so evidence payloads are dicts keyed by column name.
        """
        def pair(rows: list, cols: list[str] | None) -> list[dict[str, Any]]:
            out = []
            for r in rows:
                if isinstance(r, dict):
                    out.append(r)
                elif isinstance(r, list) and cols:
                    out.append(dict(zip(cols, r)))
                else:
                    out.append({"value": r})
            return out

        def scan(node: Any) -> list[dict[str, Any]] | None:
            if isinstance(node, dict):
                cols = None
                for ck in ("columns", "fields", "columnNames", "headers"):
                    v = node.get(ck)
                    if isinstance(v, list) and v:
                        cols = [str(c.get("name", c)) if isinstance(c, dict) else str(c)
                                for c in v]
                        break
                for rk in ("rows", "data", "records", "result"):
                    v = node.get(rk)
                    if isinstance(v, list):
                        return pair(v, cols)
                for v in node.values():
                    got = scan(v)
                    if got is not None:
                        return got
            elif isinstance(node, list):
                return pair(node, None)
            return None

        if raw is None:
            return []
        return scan(raw) or []
