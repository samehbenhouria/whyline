"""Nightshift (Meterless) reasoning client for WhyLine.

Nightshift exposes an OpenAI-compatible runtime. WhyLine sends it ONLY
the evidence pack built from Zetaris results (facts + source + SQL) and
asks for narrative findings; the model must cite the evidence ids it
uses and must not invent numbers. The deterministic arithmetic (e.g.
margins) is computed by the agent itself, never delegated.

Configuration (environment):
  METERLESS_BASE_URL      e.g. http://127.0.0.1:8088/v1
  METERLESS_RUNTIME_TOKEN runtime token from the Nightshift Console
  METERLESS_MODEL         e.g. nvidia/nemotron-3-super-120b-a12b
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class NightshiftError(RuntimeError):
    pass


class NightshiftClient:
    def __init__(self, base_url: str | None = None, token: str | None = None,
                 model: str | None = None, timeout: int = 300):
        self.base_url = (base_url or os.environ.get("METERLESS_BASE_URL", "")).rstrip("/")
        self.token = token or os.environ.get("METERLESS_RUNTIME_TOKEN", "")
        self.model = model or os.environ.get("METERLESS_MODEL", "meterless/auto")
        self.timeout = timeout
        if not self.base_url:
            raise NightshiftError("METERLESS_BASE_URL is not set.")

    def chat(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        body = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(f"{self.base_url}/chat/completions",
                      data=json.dumps(body).encode("utf-8"),
                      headers=headers, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            detail = e.read(500).decode("utf-8", errors="replace")
            raise NightshiftError(f"Nightshift request failed: HTTP {e.code} {detail}") from e
        except (URLError, OSError, TimeoutError) as e:
            raise NightshiftError(f"Cannot reach Nightshift at {self.base_url}: {e}") from e
        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise NightshiftError(f"Unexpected Nightshift response shape: {str(raw)[:300]}") from e
        return {"model": raw.get("model", self.model), "content": content, "raw": raw}
