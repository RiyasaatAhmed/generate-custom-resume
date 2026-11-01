import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import applications


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.app = applications.initialize(self.root, "Example", "Engineer")

    def tearDown(self):
        self.tmp.cleanup()

    def test_initialization_and_contact_do_not_imply_submission(self):
        other = applications.initialize(self.root, "Example", "Engineer")
        self.assertNotEqual(other, self.app)
        record = applications.event(self.app, "contacted")
        self.assertIsNone(record["applied_at"])
        report = applications.summarize(self.root)["groups"]["all"]
        self.assertEqual(report["prepared"], 2)
        self.assertEqual(report["submitted"], 0)
        self.assertIsNone(report["rates_among_submitted"]["offer"])

    def test_confirmation_and_snapshots(self):
        artifact = self.app / "resume.pdf"
        artifact.write_bytes(b"fictional artifact")
        with self.assertRaises(ValueError):
            applications.submit(self.app, [Path("resume.pdf")])
        with self.assertRaises(ValueError):
            applications.event(self.app, "applied")
        record = applications.submit(self.app, [Path("resume.pdf")], confirmed=True)
        self.assertIsNotNone(record["applied_at"])
        artifact.write_bytes(b"a later draft")
        self.assertEqual(applications.verify_snapshots(self.app), [])
        snapshot = self.app / record["submissions"][0]["snapshot"] / "resume.pdf"
        snapshot.write_bytes(b"tampering")
        self.assertTrue(applications.verify_snapshots(self.app))

    def test_outside_files_and_unsubmitted_interview_are_rejected(self):
        outside = self.root / "private.txt"
        outside.write_text("not an application artifact")
        with self.assertRaises(ValueError):
            applications.submit(self.app, [outside], confirmed=True)
        with self.assertRaises(ValueError):
            applications.event(self.app, "screening")

    def test_summary_counts_applications_not_duplicate_events(self):
        (self.app / "resume.md").write_text("Fictional resume")
        applications.submit(self.app, [Path("resume.md")], confirmed=True)
        applications.event(self.app, "replied")
        applications.event(self.app, "replied")
        applications.event(self.app, "screening")
        report = applications.summarize(self.root)["groups"]["all"]
        self.assertEqual(report["counts_among_submitted"]["replied"], 1)
        self.assertEqual(report["rates_among_submitted"]["screening"], 1.0)

    def test_closed_application_rejects_further_changes(self):
        (self.app / "resume.pdf").write_bytes(b"fictional")
        applications.submit(self.app, [Path("resume.pdf")], confirmed=True)
        applications.event(self.app, "rejected", note="Fictional rejection")
        with self.assertRaises(ValueError):
            applications.event(self.app, "screening")
        with self.assertRaises(ValueError):
            applications.submit(self.app, [Path("resume.pdf")], confirmed=True)
        states = [e["state"] for e in applications.load(self.app)["events"]]
        self.assertEqual(states, ["drafted", "applied", "rejected"])

    def test_pre_application_reply_is_not_an_outcome(self):
        applications.event(self.app, "contacted")
        applications.event(self.app, "replied")
        (self.app / "resume.pdf").write_bytes(b"fictional")
        applications.submit(self.app, [Path("resume.pdf")], confirmed=True)
        report = applications.summarize(self.root)["groups"]["all"]
        self.assertEqual(report["submitted"], 1)
        self.assertEqual(report["counts_among_submitted"]["replied"], 0)

    def test_resubmission_keeps_first_date_and_both_snapshots(self):
        artifact = self.app / "resume.pdf"
        artifact.write_bytes(b"version one")
        first = applications.submit(self.app, [Path("resume.pdf")], confirmed=True)["applied_at"]
        artifact.write_bytes(b"version two")
        record = applications.submit(self.app, [Path("resume.pdf")], confirmed=True)
        self.assertEqual(record["applied_at"], first)
        self.assertEqual(len(record["submissions"]), 2)
        self.assertNotEqual(*[s["sha256"]["resume.pdf"] for s in record["submissions"]])
        self.assertEqual(applications.verify_snapshots(self.app), [])

    def test_summary_groups_and_reports_malformed_records(self):
        applications.initialize(self.root, "Other", "Engineer", role_family="frontend")
        broken = self.root / "broken"
        broken.mkdir()
        (broken / "application.json").write_text('{"schema_version": 1, "state": "maybe", "events": []}')
        report = applications.summarize(self.root, "role_family")
        self.assertEqual(report["groups"]["frontend"]["prepared"], 1)
        self.assertEqual(report["groups"]["unknown"]["prepared"], 1)
        self.assertEqual(len(report["errors"]), 1)

    def test_cli_requires_confirmation(self):
        (self.app / "resume.pdf").write_bytes(b"fictional")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(applications.main(["submit", str(self.app), "resume.pdf"]), 1)
        self.assertIsNone(applications.load(self.app)["applied_at"])
