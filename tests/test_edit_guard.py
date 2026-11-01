"""The edit guard must flag fact drift from a style edit and stay quiet on pure rewording."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/generate-custom-resume/scripts"
sys.path.insert(0, str(SCRIPTS))
import edit_guard

BEFORE = """Dear Hiring Team,

At Martlet.ai I lifted AI suggestion adoption from **22% to 71%** and removed ~18 hours a week
of manual review. See [my portfolio](https://riyasaat.dev) or email riyasaat@example.com.
The team called it "the first score coders trusted".

I think myself to be a strong match for this role.
"""


class EditGuardTests(unittest.TestCase):
    def changed(self, after: str, protect=()):
        return edit_guard.compare(BEFORE, after, list(protect))

    def test_pure_rewording_reports_nothing(self):
        after = """Dear Hiring Team,

I raised AI suggestion adoption at Martlet.ai from 22% to 71%, and the workflow removed ~18 hours a
week of manual review. My portfolio is at https://riyasaat.dev, and my email is riyasaat@example.com.
The team called it "the first score coders trusted".

I think myself to be a strong match for this role.
"""
        report = self.changed(after, ["I think myself to be a strong match for this role."])
        self.assertTrue(report["ok"], report)

    def test_changed_metric_is_flagged(self):
        report = self.changed(BEFORE.replace("71%", "75%"))
        self.assertFalse(report["ok"])
        self.assertEqual(report["numbers"], {"removed": ["71%"], "added": ["75%"]})

    def test_changed_unit_is_flagged(self):
        report = self.changed(BEFORE.replace("18 hours", "18 days"))
        self.assertEqual(report["numbers"], {"removed": ["18 hours"], "added": ["18 days"]})

    def test_invented_name_is_flagged(self):
        report = self.changed(BEFORE.replace("At Martlet.ai I", "At Martlet.ai, alongside Stripe, I"))
        self.assertEqual(report["names"]["added"], ["Stripe"])

    def test_lost_link_email_and_quote_are_flagged(self):
        after = (BEFORE.replace("[my portfolio](https://riyasaat.dev)", "my portfolio")
                 .replace("riyasaat@example.com", "me@example.com")
                 .replace('"the first score coders trusted"', '"a score coders finally trusted"'))
        report = self.changed(after)
        self.assertEqual(report["urls"]["removed"], ["https://riyasaat.dev"])
        self.assertEqual(report["emails"], {"removed": ["riyasaat@example.com"], "added": ["me@example.com"]})
        self.assertEqual(report["quotes"]["removed"], ["the first score coders trusted"])

    def test_protected_line_must_survive_verbatim(self):
        line = "I think myself to be a strong match for this role."
        report = self.changed(BEFORE.replace(line, "I believe I am a strong match for this role."), [line])
        self.assertEqual(report["protected"], [line])
        self.assertFalse(report["ok"])

    def test_cli_exit_codes_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            before, after = Path(tmp) / "before.md", Path(tmp) / "after.md"
            before.write_text(BEFORE)
            after.write_text(BEFORE)
            run = lambda *extra: subprocess.run([sys.executable, str(SCRIPTS / "edit_guard.py"), str(before), str(after), *extra],
                                                capture_output=True, text=True)
            self.assertEqual(run().returncode, 0)
            after.write_text(BEFORE.replace("22%", "20%"))
            result = run("--json")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["numbers"]["removed"], ["22%"])


if __name__ == "__main__":
    unittest.main()
