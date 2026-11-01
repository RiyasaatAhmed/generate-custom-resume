import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/generate-custom-resume/scripts"))
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

    def run_check(self, text, **kwargs):
        self.path.write_text(text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = outreach.check(self.path, **kwargs)
        return code, out.getvalue()

    def test_direct_message_budgets_follow_linkedin_length_data(self):
        # LinkedIn: under 400 characters replied to most; over 800 below average.
        message = "Hi Alex, " + "I built accessible scheduling tools for clinics. " * 17
        self.assertGreater(len(message), 800)
        for channel in ("recruiter", "hiring-manager", "inmail", "referral"):
            with self.subTest(channel=channel):
                code, _ = self.run_check(("Role\n// ---\n" if channel == "inmail" else "") + message, channel=channel)
                self.assertEqual(code, 1)

    def test_generic_phrases_and_stacked_asks_warn_without_failing(self):
        text = ("I hope this message finds you well. I am a results-driven engineer passionate about health. "
                "Could we talk? Could you refer me? Could you share the salary?")
        code, out = self.run_check(text, channel="recruiter")
        self.assertEqual(code, 0)
        for phrase in ("i hope this message finds you well", "results-driven", "passionate about", "3 questions"):
            self.assertIn(phrase, out.lower())

    def test_specific_message_has_no_warnings(self):
        code, out = self.run_check("Hi Alex, I shipped the HIPAA de-identification service at Martlet.ai "
                                   "and saw your clinical-tools role. Could we talk for 15 minutes this week?",
                                   channel="recruiter")
        self.assertEqual(code, 0)
        self.assertNotIn("warning", out.lower())

    def test_cover_letter_channel(self):
        letter = ("Dear Ms. Rivera,\n\nI rebuilt clinic scheduling at Northwind and cut charting time 35%.\n\n"
                  "Thank you for considering my application.\n\nBest,\nSam Rivera")
        code, out = self.run_check(letter, channel="cover-letter")
        self.assertEqual(code, 0, out)  # "my application" is normal in a letter, not a submission claim
        self.assertIn("words", out)
        code, out = self.run_check("To whom it may concern,\n\nI am writing to apply for the role I saw on Indeed.",
                                   channel="cover-letter")
        self.assertIn("to whom it may concern", out.lower())
        self.assertIn("i am writing to apply", out.lower())
        self.assertEqual(self.run_check("word " * 420, channel="cover-letter")[0], 1)

    def test_custom_budget_and_unicode(self):
        self.assertEqual(self.check("Hi Zoë", limit=6), 0)
        self.assertEqual(self.check("Hi Zoë", limit=5), 1)
