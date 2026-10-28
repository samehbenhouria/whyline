"""WhyLine investigation agent.

Pipeline (one question, one company, three federated sources):

  1. FETCH   - run the investigation SQL through Zetaris only. Every
               returned row becomes an H-MEM evidence record with its
               source, the exact SQL and a SHA-256 payload hash.
  2. COMPUTE - deterministic findings (arithmetic the agent does
               itself, e.g. net margin = net income / revenue) are
               derived from evidence and stored as H-MEM findings.
  3. REASON  - the evidence pack is sent to Nightshift (Nemotron) which
               returns narrative findings; they enter H-MEM linked to
               the evidence ids they cite.
  4. EXPLAIN - the conclusion is stored, and H-MEM reconstructs and
               verifies the whole proof chain for the report.

No statement enters the chain without evidence. If a fetch returns no
rows, the investigation stops with an explicit error instead of
filling the gap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable

from .hmem import HMem


def _parse_date(value: Any) -> date:
    return date.fromisoformat(str(value)[:10])


@dataclass
class InvestigationConfig:
    company: str
    question: str
    queries: dict[str, str]          # label -> SQL (federated, via Zetaris)
    sources: dict[str, str]          # label -> H-MEM source name
    margin_pair: tuple[str, str, str, str, str] | None = None
    # (query label, revenue key, net income key, period-start key,
    #  period-end key). Annual pairs are identified by their period
    #  span (>= 300 days), never by the source's fiscal-period label:
    #  the EDGAR extract used here labels every row with its frame
    #  year, so labels cannot be trusted to separate years/quarters.


@dataclass
class InvestigationResult:
    conclusion_id: str
    chain: dict
    computed: dict[str, Any] = field(default_factory=dict)


class InvestigationError(RuntimeError):
    pass


def run_investigation(
    mem: HMem,
    cfg: InvestigationConfig,
    query_fn: Callable[[str], list[dict[str, Any]]],
    reason_fn: Callable[[str, list[dict]], str] | None = None,
) -> InvestigationResult:
    """query_fn(sql) -> rows; reason_fn(prompt, evidence_pack) -> text."""
    evidence_by_label: dict[str, list[str]] = {}
    evidence_pack: list[dict] = []

    seen_rows: set[str] = set()
    for label, sql in cfg.queries.items():
        rows = query_fn(sql)
        if not rows:
            raise InvestigationError(f"query '{label}' returned no rows; refusing to guess.")
        ids = []
        for row in rows:
            # Joins over filing extracts can repeat a row (original +
            # restated filings of the same period). Identical rows are
            # stored once; the chain stays free of duplicate evidence.
            fingerprint = sql + json.dumps(row, sort_keys=True, default=str)
            if fingerprint in seen_rows:
                continue
            seen_rows.add(fingerprint)
            ev = mem.add_evidence(source=cfg.sources.get(label, label), query=sql, payload=row)
            ids.append(ev.id)
            evidence_pack.append({"evidence_id": ev.id, "source": ev.source, "row": row})
        evidence_by_label[label] = ids

    finding_ids: list[str] = []
    computed: dict[str, Any] = {}

    if cfg.margin_pair:
        label, rev_key, ni_key, start_key, end_key = cfg.margin_pair
        rows_by_id = {p["evidence_id"]: p["row"] for p in evidence_pack}
        computed_pairs = 0
        for eid in evidence_by_label.get(label, []):
            row = rows_by_id[eid]
            try:
                revenue = float(row[rev_key])
                net_income = float(row[ni_key])
                start = _parse_date(row[start_key])
                end = _parse_date(row[end_key])
            except (KeyError, TypeError, ValueError):
                continue
            if revenue == 0:
                continue
            span_days = (end - start).days
            annual = span_days >= 300
            margin = net_income / revenue
            period = f"{start.isoformat()}..{end.isoformat()}"
            computed[period] = {"revenue": revenue, "net_income": net_income,
                                "net_margin": margin, "span_days": span_days,
                                "kind": "annual" if annual else "quarterly"}
            computed_pairs += 1
            f = mem.add_finding(
                statement=(
                    f"{cfg.company} {period} ({'full-year' if annual else 'quarterly'} "
                    f"period, {span_days} days): net margin = {margin:.4f} "
                    f"(net income {net_income:,.0f} / revenue {revenue:,.0f}), "
                    f"computed by the agent from Zetaris evidence."
                ),
                evidence_ids=[eid], entity=cfg.company)
            finding_ids.append(f.id)
        if computed_pairs == 0:
            raise InvestigationError(
                f"query '{label}' returned rows but no revenue/net-income pair "
                "could be computed from them; refusing to continue silently.")

    # Every fetched source must be reachable from the conclusion, even
    # without an LLM narrative: add a deterministic context finding per
    # query that no computation consumed. It restates evidence only.
    consumed = {cfg.margin_pair[0]} if cfg.margin_pair else set()
    rows_by_id = {p["evidence_id"]: p["row"] for p in evidence_pack}
    for label, ids in evidence_by_label.items():
        if label in consumed:
            continue
        summary = json.dumps([rows_by_id[i] for i in ids[:3]],
                             ensure_ascii=False, default=str)[:600]
        f = mem.add_finding(
            statement=(f"Context from {cfg.sources.get(label, label)}: {summary}"),
            evidence_ids=list(ids), entity=cfg.company)
        finding_ids.append(f.id)

    if reason_fn is not None:
        prompt = (
            f"Investigation question: {cfg.question}\n"
            f"Company: {cfg.company}\n\n"
            "Evidence pack (the ONLY facts you may use; cite evidence_id for "
            "every claim; do not invent numbers):\n"
            f"{json.dumps(evidence_pack, ensure_ascii=False, indent=2)}\n\n"
            "Write the explanation in at most three short paragraphs: what "
            "the facts show, why the industry (SIC) frame matters for the "
            "comparison, and what the numbers do NOT prove."
        )
        narrative = reason_fn(prompt, evidence_pack)
        all_ids = [eid for ids in evidence_by_label.values() for eid in ids]
        f = mem.add_finding(statement=narrative, evidence_ids=all_ids,
                            entity=cfg.company)
        finding_ids.append(f.id)

    if not finding_ids:
        raise InvestigationError("no finding could be derived from the evidence.")

    concl = mem.add_conclusion(
        statement=f"WhyLine answer for {cfg.company}: {cfg.question}",
        finding_ids=finding_ids)
    mem.save()
    chain = mem.explain(concl.id)
    return InvestigationResult(conclusion_id=concl.id, chain=chain, computed=computed)
