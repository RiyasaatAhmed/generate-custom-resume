import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import outreach


class OutreachTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "outreach.txt"

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text, **kwargs):
        self.path.write_text(text)
        with contextlib.redirect_stdout(io.StringIO()):
            return outreach.check(self.path, **kwargs)

    def test_empty_and_placeholders(self):
        self.assertEqual(self.check(""), 1)
        self.assertEqual(self.check("// ---\n// only a comment"), 1)
        self.assertEqual(self.check("Hi [Name], could we connect?"), 1)
        self.assertEqual(self.check("Hi [Name], could we connect?", draft=True), 0)

    def test_channel_subject_contract(self):
        self.assertEqual(self.check("Hi Alex, could we connect?", channel="connection"), 0)
        self.assertEqual(self.check("Hi Alex, could we connect?", channel="email"), 1)
        self.assertEqual(self.check("Frontend role\n// ---\nHi Alex, could we discuss the role?", channel="email"), 0)

    def test_submission_claim_needs_confirmation(self):
        text = "Hi Alex, I've applied for the frontend role. Could we discuss the team?"
        self.assertEqual(self.check(text), 1)
        record = self.path.with_name("application.json")
        record.write_text(json.dumps({"applied_at": "2026-11-01T10:00:00+00:00"}))
        self.assertEqual(self.check(text, application=record), 0)

    def test_custom_budget_and_unicode(self):
        self.assertEqual(self.check("Hi Zoë", limit=6), 0)
        self.assertEqual(self.check("Hi Zoë", limit=5), 1)
