"""H-MEM conformance tests for WhyLine.

This is the test the hackathon asks for: it shows the implemented
Meterless engine (H-MEM — persistent memory and retrieval) working.

Run:  python3 -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from whyline.hmem import HMem, BrokenChainError


def build_sample_investigation(mem: HMem) -> str:
    """A miniature company investigation with a full proof chain."""
    rev = mem.add_evidence(
        source="zetaris:edgar_company_facts",
        query="SELECT fy, val FROM edgar.tesla_revenue WHERE fy IN (2023, 2024)",
        payload={"company": "Tesla", "metric": "Revenues", "fy": 2024, "val": 97690000000},
    )
    sic = mem.add_evidence(
        source="zetaris:edgar_company_profiles",
        query="SELECT name, sic_description FROM edgar_profiles WHERE name = 'Tesla'",
        payload={"company": "Tesla", "sic": "3711", "sic_description": "Motor Vehicles & Car Bodies"},
    )
    f1 = mem.add_finding(
        "Tesla's 2024 revenue is reported at $97.69B in its EDGAR XBRL facts.",
        [rev.id], entity="Tesla")
    f2 = mem.add_finding(
        "EDGAR classifies Tesla under SIC 3711 (Motor Vehicles & Car Bodies), "
        "so its revenue must be read against the auto industry, not tech.",
        [sic.id], entity="Tesla")
    c = mem.add_conclusion(
        "Tesla's scale is that of a large car maker: $97.69B revenue inside SIC 3711.",
        [f1.id, f2.id])
    return c.id


class TestHMem(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "memory.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_proof_chain_reconstructs(self):
        mem = HMem(self.path)
        cid = build_sample_investigation(mem)
        chain = mem.explain(cid)
        self.assertTrue(chain["verified"])
        self.assertEqual(len(chain["findings"]), 2)
        sources = {ev["source"] for f in chain["findings"] for ev in f["evidence"]}
        self.assertEqual(len(sources), 2)  # two distinct Zetaris sources cited

    def test_memory_is_persistent(self):
        mem = HMem(self.path)
        cid = build_sample_investigation(mem)
        mem.save()
        reloaded = HMem(self.path)  # new instance, reads from disk
        chain = reloaded.explain(cid)
        self.assertTrue(chain["verified"])

    def test_retrieval_across_layers(self):
        mem = HMem(self.path)
        build_sample_investigation(mem)
        hits = mem.search("Tesla")
        self.assertTrue(hits["evidence"] and hits["findings"] and hits["conclusions"])
        self.assertEqual(mem.search("NoSuchCompany")["findings"], [])

    def test_finding_without_evidence_is_refused(self):
        mem = HMem(self.path)
        with self.assertRaises(BrokenChainError):
            mem.add_finding("An unsupported claim.", [])

    def test_tampered_evidence_breaks_verification(self):
        mem = HMem(self.path)
        cid = build_sample_investigation(mem)
        victim = next(iter(mem.evidence.values()))
        victim.payload["val"] = 1  # silent edit after the fact
        with self.assertRaises(BrokenChainError):
            mem.explain(cid)


if __name__ == "__main__":
    unittest.main()
