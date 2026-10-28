"""WhyLine H-MEM engine: persistent hierarchical memory with retrieval.

Implements the Meterless H-MEM engine pattern (persistent memory and
retrieval) as the explanation backbone of the agent:

  Layer 0 - EVIDENCE: one record per fact fetched through Zetaris.
            Each record keeps its source name, the SQL that produced it,
            the retrieval time, the raw payload, and a SHA-256 hash of the
            payload so any later tampering is detectable.
  Layer 1 - FINDINGS: statements derived from one or more evidence
            records (by the Nightshift/Nemotron reasoning step). A finding
            cannot exist without at least one evidence link.
  Layer 2 - CONCLUSIONS: the final "why" answer, linked to findings.

Retrieval walks the hierarchy both ways: a conclusion can be *explained*
by reconstructing its full proof chain (conclusion -> findings ->
evidence -> source + SQL), and any memory item can be found again by
term search across layers in later investigations.

The store is a single JSON document on disk: memory survives restarts
(persistent) and is fully inspectable by judges.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


def _hash_payload(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Evidence:
    source: str            # e.g. "zetaris:edgar_company_facts"
    query: str             # the SQL (or API call) that produced the fact
    payload: dict          # the raw fact, as returned
    retrieved_at: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: _new_id("ev"))
    payload_hash: str = ""

    def __post_init__(self) -> None:
        if not self.payload_hash:
            self.payload_hash = _hash_payload(self.payload)

    def verify(self) -> bool:
        return self.payload_hash == _hash_payload(self.payload)


@dataclass
class Finding:
    statement: str
    evidence_ids: list[str]
    entity: str = ""
    id: str = field(default_factory=lambda: _new_id("find"))


@dataclass
class Conclusion:
    statement: str
    finding_ids: list[str]
    id: str = field(default_factory=lambda: _new_id("concl"))


class BrokenChainError(Exception):
    """Raised when a proof chain cannot be fully reconstructed."""


class HMem:
    """Persistent hierarchical memory (H-MEM) for one investigation space."""

    def __init__(self, path: str):
        self.path = path
        self.evidence: dict[str, Evidence] = {}
        self.findings: dict[str, Finding] = {}
        self.conclusions: dict[str, Conclusion] = {}
        if os.path.exists(path):
            self.load()

    # ---- writes ------------------------------------------------------
    def add_evidence(self, source: str, query: str, payload: dict) -> Evidence:
        ev = Evidence(source=source, query=query, payload=payload)
        self.evidence[ev.id] = ev
        return ev

    def add_finding(self, statement: str, evidence_ids: list[str], entity: str = "") -> Finding:
        if not evidence_ids:
            raise BrokenChainError("a finding must cite at least one evidence record")
        missing = [e for e in evidence_ids if e not in self.evidence]
        if missing:
            raise BrokenChainError(f"unknown evidence ids: {missing}")
        f = Finding(statement=statement, evidence_ids=list(evidence_ids), entity=entity)
        self.findings[f.id] = f
        return f

    def add_conclusion(self, statement: str, finding_ids: list[str]) -> Conclusion:
        if not finding_ids:
            raise BrokenChainError("a conclusion must cite at least one finding")
        missing = [f for f in finding_ids if f not in self.findings]
        if missing:
            raise BrokenChainError(f"unknown finding ids: {missing}")
        c = Conclusion(statement=statement, finding_ids=list(finding_ids))
        self.conclusions[c.id] = c
        return c

    # ---- persistence ---------------------------------------------------
    def save(self) -> None:
        data = {
            "evidence": [asdict(e) for e in self.evidence.values()],
            "findings": [asdict(f) for f in self.findings.values()],
            "conclusions": [asdict(c) for c in self.conclusions.values()],
        }
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def load(self) -> None:
        with open(self.path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.evidence = {d["id"]: Evidence(**d) for d in data.get("evidence", [])}
        self.findings = {d["id"]: Finding(**d) for d in data.get("findings", [])}
        self.conclusions = {d["id"]: Conclusion(**d) for d in data.get("conclusions", [])}

    # ---- retrieval -----------------------------------------------------
    def search(self, *terms: str) -> dict[str, list]:
        """Term retrieval across all three layers (case-insensitive)."""
        needles = [t.lower() for t in terms if t]
        def hit(text: str) -> bool:
            return any(n in text.lower() for n in needles)
        return {
            "evidence": [e for e in self.evidence.values()
                         if hit(e.source) or hit(json.dumps(e.payload, default=str))],
            "findings": [f for f in self.findings.values()
                         if hit(f.statement) or hit(f.entity)],
            "conclusions": [c for c in self.conclusions.values() if hit(c.statement)],
        }

    def explain(self, conclusion_id: str) -> dict:
        """Reconstruct and verify the full proof chain of a conclusion.

        Returns the chain conclusion -> findings -> evidence. Raises
        BrokenChainError if any link is missing or any evidence payload
        no longer matches its stored hash (tamper / corruption).
        """
        if conclusion_id not in self.conclusions:
            raise BrokenChainError(f"unknown conclusion: {conclusion_id}")
        concl = self.conclusions[conclusion_id]
        chain_findings = []
        for fid in concl.finding_ids:
            if fid not in self.findings:
                raise BrokenChainError(f"conclusion cites missing finding {fid}")
            f = self.findings[fid]
            evs = []
            for eid in f.evidence_ids:
                if eid not in self.evidence:
                    raise BrokenChainError(f"finding cites missing evidence {eid}")
                ev = self.evidence[eid]
                if not ev.verify():
                    raise BrokenChainError(f"evidence {eid} failed hash verification")
                evs.append({"id": ev.id, "source": ev.source, "query": ev.query,
                            "retrieved_at": ev.retrieved_at, "payload": ev.payload,
                            "payload_hash": ev.payload_hash})
            chain_findings.append({"id": f.id, "statement": f.statement,
                                   "entity": f.entity, "evidence": evs})
        return {"conclusion": {"id": concl.id, "statement": concl.statement},
                "findings": chain_findings, "verified": True}
