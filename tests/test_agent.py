"""Tests for the WhyLine agent pipeline (fake query/reason functions).

Covers: evidence-only flow, deterministic margin computation, refusal
on empty evidence, the narrative finding linked to ALL evidence, the
context finding that keeps every source reachable from the conclusion,
and the rendered report carrying ids + hashes of the verified chain.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from whyline.agent import InvestigationConfig, InvestigationError, run_investigation
from whyline.hmem import HMem
from whyline.report import render_html

ROWS = {
    "margins": [{"period_start": "2023-10-01", "period_end": "2024-09-30",
                 "revenue": 200.0, "net_income": 50.0}],
    "profile": [{"name": "Acme", "sic": "3571", "sic_description": "Electronic Computers"}],
}


def _cfg():
    return InvestigationConfig(
        company="Acme",
        question="Why is Acme's margin what it is?",
        queries={"margins": "SELECT ... margins", "profile": "SELECT ... profile"},
        sources={"margins": "zetaris:edgar_company_facts",
                 "profile": "zetaris:edgar_profiles_sic"},
        margin_pair=("margins", "revenue", "net_income", "period_start", "period_end"),
    )


def _query(sql):
    return ROWS["margins"] if "margins" in sql else ROWS["profile"]


class TestAgentPipeline(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.mem = HMem(os.path.join(self._tmp.name, "mem.json"))

    def tearDown(self):
        self._tmp.cleanup()

    def test_pipeline_margin_and_chain(self):
        res = run_investigation(self.mem, _cfg(), _query)
        key = "2023-10-01..2024-09-30"
        self.assertEqual(res.computed[key]["net_margin"], 0.25)
        self.assertEqual(res.computed[key]["kind"], "annual")
        self.assertTrue(res.chain["verified"])
        findings = res.chain["findings"]
        self.assertTrue(any("net margin = 0.2500" in f["statement"] for f in findings))
        ev = findings[0]["evidence"][0]
        self.assertEqual(ev["source"], "zetaris:edgar_company_facts")
        self.assertTrue(ev["payload_hash"])

    def test_pipeline_with_reasoning(self):
        seen = {}

        def reason(prompt, pack):
            seen["pack"] = pack
            return "Narrative: margins reflect the SIC frame."

        res = run_investigation(self.mem, _cfg(), _query, reason_fn=reason)
        self.assertEqual(len(seen["pack"]), 2)  # both evidence rows packed
        narrative = [f for f in res.chain["findings"] if "Narrative" in f["statement"]]
        self.assertTrue(narrative)
        self.assertEqual(len(narrative[0]["evidence"]), 2)

    def test_pipeline_refuses_empty_evidence(self):
        with self.assertRaises(InvestigationError):
            run_investigation(self.mem, _cfg(), lambda sql: [])

    def test_report_renders_chain(self):
        res = run_investigation(self.mem, _cfg(), _query)
        page = render_html(res.chain, question=_cfg().question, company="Acme")
        self.assertIn("SHA-256", page)
        self.assertIn("Electronic Computers", page)


if __name__ == "__main__":
    unittest.main()
