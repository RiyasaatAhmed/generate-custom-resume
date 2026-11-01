import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.bank = json.loads((ROOT / "profile/achievements.example.json").read_text())
        self.mapping = json.loads((ROOT / "templates/evidence-map.example.json").read_text())

    def test_examples(self):
        self.assertEqual(evidence.bank_errors(self.bank), [])
        self.assertEqual(evidence.map_errors(self.mapping, self.bank), [])

    def test_unknown_and_unresolved_sources(self):
        self.assertTrue(evidence.map_errors(self.mapping))
        self.bank["achievements"][0]["status"] = "needs-clarification"
        self.assertTrue(evidence.map_errors(self.mapping, self.bank))

    def test_elevated_status_needs_reference(self):
        for status in ("context-confirmed", "artifact-supported"):
            self.bank["achievements"][0]["status"] = status
            self.assertTrue(evidence.bank_errors(self.bank))

    def test_duplicate_id_and_derived_metric(self):
        self.bank["achievements"].append(copy.deepcopy(self.bank["achievements"][0]))
        self.assertTrue(evidence.bank_errors(self.bank))
        self.bank["achievements"].pop()
        self.bank["achievements"][0]["metrics"][0]["derived"] = True
        self.assertTrue(evidence.bank_errors(self.bank))

    def test_legacy_sources_and_unknown_eligibility(self):
        self.mapping["requirements"][0]["sources"] = [{"reference": "profile/base-resume.md: Northwind", "excerpt": "Built a clinical editor"}]
        self.assertEqual(evidence.map_errors(self.mapping), [])
        self.mapping["eligibility"][0]["candidate_status"] = "met"
        self.assertTrue(evidence.map_errors(self.mapping))

    def test_evidence_gaps(self):
        gap = self.mapping["requirements"][1]
        for match in ("missing", "unknown"):
            gap["match"] = match
            self.assertEqual(evidence.map_errors(self.mapping, self.bank), [], match)
        for match in ("direct", "adjacent"):
            gap["match"] = match
            self.assertTrue(evidence.map_errors(self.mapping, self.bank), match)
        gap["match"] = "missing"
        self.mapping["recommendation"] = {"decision": "pursue", "reasons": []}
        self.assertTrue(evidence.map_errors(self.mapping, self.bank))
        self.mapping["recommendation"] = {"decision": "auto-reject", "reasons": ["x"]}
        self.assertTrue(evidence.map_errors(self.mapping, self.bank))

    def test_metric_without_unit_fails(self):
        del self.bank["achievements"][0]["metrics"][0]["unit"]
        self.assertTrue(evidence.bank_errors(self.bank))

    def test_known_eligibility_needs_candidate_source(self):
        item = self.mapping["eligibility"][0]
        item.update(candidate_status="met", candidate_source="Candidate answer, 2026-11-01")
        self.assertEqual(evidence.map_errors(self.mapping, self.bank), [])
