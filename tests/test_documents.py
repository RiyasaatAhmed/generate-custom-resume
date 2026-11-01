"""Regression coverage uses fictional profiles and isolated outputs."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "skills/generate-custom-resume"
sys.path.insert(0, str(ROOT / "scripts"))
import kit
import md_to_cover
import qa
import md_to_docx
import md_to_pdf
import resume_links
import resume_model
import document_checks


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"RESUME_PROFILE": str(ROOT / "assets/profile/profile.example.json")})
        self.env.start()
        kit.load_profile.cache_clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()
        self.env.stop()
        kit.load_profile.cache_clear()

    def test_plain_cover_survives_cli_export(self):
        source = self.path / "cover-letter.md"
        source.write_text("Dear Team,\n\nI built an accessible scheduling interface.\n\nBest,\nJane Doe\n")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/md_export.py"), str(source),
                                 "--cover", "--docx-only"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("I built an accessible scheduling interface.", qa.docx_text(source.with_suffix(".docx")))
        self.assertEqual(md_to_cover.parse_cover(source.read_text())["name"], "Jane Doe")

    def test_legacy_cover_preserved(self):
        parsed = md_to_cover.parse_cover("# Example Person\n**Engineer**\n\n---\n\nDear Team,\n\nMy evidence.\n")
        self.assertEqual(parsed["name"], "Example Person")
        self.assertEqual(parsed["headline"], "Engineer")
        self.assertEqual(parsed["blocks"][-1], ["My evidence."])

    def test_empty_and_malformed_covers_fail_without_output(self):
        for content in ["", " \n", "<!-- comment -->", "# Jane Doe\n**Engineer**", "# Jane Doe\n---\n"]:
            with self.subTest(content=content):
                source = self.path / "empty.md"
                source.write_text(content)
                with self.assertRaises(ValueError):
                    md_to_cover.convert_docx(kit.DEFAULT_TEMPLATE, source, source.with_suffix(".docx"))
                self.assertFalse(source.with_suffix(".docx").exists())

    def test_extended_sections_survive_both_renderers(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        base = base.replace("University of Lisbon, Lisbon, Portugal", "University of Lisbon, Lisbon, Portugal\n\n**M.S. Computing** | 2020 - 2022\nExample University")
        source = self.path / "resume.md"
        source.write_text(base + "\n## Projects\n### Scheduling Tool\n- Built accessible calendars.\n\n## Certifications\n**Example Credential** | 2024\n\n## Publications\n[Sample Paper](https://example.org/paper)\n")
        data = md_to_docx.parse_md(source.read_text())
        self.assertEqual(len(data["education"]), 2)
        md_to_docx.convert(kit.DEFAULT_TEMPLATE, source, source.with_suffix(".docx"))
        docx = qa.docx_text(source.with_suffix(".docx"))
        html = md_to_pdf.render_html(data, resume_links, md_to_docx.parse_honor)
        for phrase in ["M.S. Computing", "Example University", "Scheduling Tool", "accessible calendars", "Example Credential", "Sample Paper"]:
            self.assertIn(phrase, docx)
            self.assertIn(phrase, html)
        self.assertEqual(qa.parse_qa(source, source.with_suffix(".docx")), [])

    def test_bad_resume_structure_fails(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        for text in [base + "\n## Unexpected\nImportant evidence", base.replace("## Experience", "## Employment"),
                     base.replace("### Senior Frontend Engineer", "Senior Frontend Engineer"),
                     base.replace("**Northwind Health**, Berlin, Germany (Remote) | Mar 2023 - Present", "Northwind"),
                     base + "\n## Skills\nDuplicated section", "No name or sections"]:
            with self.subTest(text=text[-50:]), self.assertRaises(ValueError):
                resume_model.parse(text)

    def test_example_and_unicode_resume_parse(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text().replace("Jane Doe", "Zoë García 李")
        parsed = md_to_docx.parse_md(base)
        self.assertEqual(parsed["name"], "Zoë García 李")
        self.assertEqual(len(parsed["roles"]), 3)
        self.assertEqual(len(parsed["roles"][0]["bullets"]), 4)

    def test_unicode_resume_survives_docx_export_and_qa(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        base = base.replace("Jane Doe", "Zoë García 李").replace(
            "## Experience", "## Experience\n### Ingeniera de Interfaz — Café Systems\n"
            "**Café Systems**, São Paulo, Brazil | Jan 2014 – Dec 2014\n"
            "- Localized the scheduling UI into 日本語 and Ελληνικά with naïve fallbacks and 5 % fewer errors.\n", 1)
        source = self.path / "resume.md"
        source.write_text(base, encoding="utf-8")
        md_to_docx.convert(kit.DEFAULT_TEMPLATE, source, source.with_suffix(".docx"))
        text = qa.docx_text(source.with_suffix(".docx"))
        for phrase in ("Zoë García 李", "São Paulo", "日本語 and Ελληνικά", "Jan 2014 – Dec 2014"):
            self.assertIn(phrase, text)
        self.assertEqual(qa.parse_qa(source, source.with_suffix(".docx")), [])

    def test_long_content_is_retained(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        bullets = "\n".join(f"- Delivered fictional scenario {i} covering validation, recovery states, keyboard access, "
                            f"and screen-reader announcements across the appointment flow, measured in test {i}."
                            for i in range(1, 31))
        source = self.path / "resume.md"
        source.write_text(base + f"\n## Projects\n### Long Project\n{bullets}\n")
        md_to_docx.convert(kit.DEFAULT_TEMPLATE, source, source.with_suffix(".docx"))
        text = qa.docx_text(source.with_suffix(".docx"))
        self.assertIn("measured in test 30.", text)
        self.assertEqual(qa.parse_qa(source, source.with_suffix(".docx")), [])

    def test_more_malformed_resumes_fail(self):
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        cases = {
            "unclosed comment": base + "\n<!-- forgotten",
            "table": base + "\n## Projects\n| a | b |",
            "code block": base + "\n## Projects\n```js\nx\n```",
            "empty bullet": base.replace("## Education", "-   \n\n## Education", 1),
            "bullet before title": base.replace("## Experience\n", "## Experience\n- Orphan bullet\n", 1),
            "empty section": base + "\n## Publications\n",
            "missing headline": base.replace("**", "", 2),
        }
        for name, text in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                resume_model.parse(text)

    def test_unresolved_link_token_fails_export(self):
        source = self.path / "resume.md"
        source.write_text((ROOT / "assets/profile/base-resume.example.md").read_text().replace(
            "## Education", "## Publications\n[Unknown Label]\n\n## Education", 1))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/md_export.py"), str(source), "--docx-only"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Unknown Label", result.stderr)
        self.assertFalse(source.with_suffix(".docx").exists())

    def make_resume(self):
        source = self.path / "resume.md"
        source.write_text((ROOT / "assets/profile/base-resume.example.md").read_text())
        md_to_docx.convert(kit.DEFAULT_TEMPLATE, source, source.with_suffix(".docx"))
        return source

    def mutate_docx(self, source, name, mutate):
        path = source.with_suffix(".docx")
        with zipfile.ZipFile(path) as z:
            files = {n: z.read(n) for n in z.namelist()}
        root = ET.fromstring(files[name])
        mutate(root)
        files[name] = ET.tostring(root)
        with zipfile.ZipFile(path, "w") as z:
            for key, value in files.items():
                z.writestr(key, value)

    def test_all_bullets_missing_fails_qa(self):
        source = self.make_resume()
        self.assertEqual(qa.parse_qa(source, source.with_suffix(".docx")), [])
        def remove_bullets(root):
            for parent in root.iter():
                for child in list(parent):
                    if child.tag == qa.NS + "p" and ''.join(n.text or '' for n in child.iter(qa.NS + 't')).startswith('•'):
                        parent.remove(child)
        self.mutate_docx(source, "word/document.xml", remove_bullets)
        problems = qa.parse_qa(source, source.with_suffix(".docx"))
        self.assertTrue(any("charting" in p for p in problems), problems)

    def test_wrong_link_destination_fails(self):
        source = self.make_resume()
        def wrong_url(root):
            for rel in root:
                if rel.get("Target") == "https://janedoe.dev":
                    rel.set("Target", "https://wrong.example")
        self.mutate_docx(source, "word/_rels/document.xml.rels", wrong_url)
        self.assertTrue(any("janedoe.dev" in p for p in qa.parse_qa(source, source.with_suffix(".docx"))))

    def test_missing_pdf_is_failure(self):
        report = qa.run(self.make_resume(), render=False)
        self.assertEqual(report["overall"], "failed")
        self.assertEqual(report["checks"]["visual_review"]["status"], "skipped")

    def test_ligature_normalization_does_not_change_numbers(self):
        self.assertEqual(document_checks.missing_content(["workflow 35%"], "workﬂow 35%"), [])
        self.assertTrue(document_checks.missing_content(["35%"], "53%"))

    def test_pdf_spacing_inside_words_is_not_missing_content(self):
        # pypdf extracts some bold digits with a stray space ("9 2%") although the page shows "92%".
        expected = ["design system covering 92% of screens."]
        extracted = "design system covering 9 2% of\nscreens."
        self.assertEqual(document_checks.missing_content(expected, extracted, ignore_spaces=True), [])
        self.assertTrue(document_checks.missing_content(expected, extracted))  # DOCX comparison stays exact
        for actual in ("covering 9 3% of screens.", "design covering 92% of screens.", ""):
            with self.subTest(actual=actual):
                self.assertTrue(document_checks.missing_content(expected, actual, ignore_spaces=True))

    def test_bold_percentages_pass_pdf_content_check(self):
        try:
            import pypdf  # noqa: F401
            kit.find_chrome()
        except (ImportError, FileNotFoundError, RuntimeError):
            self.skipTest("needs pypdf and Chrome")
        base = (ROOT / "assets/profile/base-resume.example.md").read_text()
        source = self.path / "resume.md"
        source.write_text(base.replace(
            "- Built a **50-component** design system with **Storybook** docs used by **3 squads**.",
            "- Built a design system covering **92%** of screens with **97%** adoption."), encoding="utf-8")
        md_to_pdf.convert(source, source.with_suffix(".pdf"))
        report = qa.pdf_checks(source, source.with_suffix(".pdf"), max_pages=2)
        self.assertEqual(report["pdf_content"]["status"], "pass", report["pdf_content"])

    def test_pdf_url_equivalence_is_narrow(self):
        self.assertEqual(qa.same_url("https://janedoe.dev"), qa.same_url("https://janedoe.dev/"))
        self.assertEqual(qa.same_url("HTTPS://Example.COM/a"), qa.same_url("https://example.com/a"))
        self.assertNotEqual(qa.same_url("https://example.com/a"), qa.same_url("https://example.com/b"))
        self.assertNotEqual(qa.same_url("https://example.com/Path"), qa.same_url("https://example.com/path"))
        self.assertEqual(qa.same_url("mailto:Jane@example.com"), "mailto:Jane@example.com")

    def test_chrome_timeout_reports_failure(self):
        output = self.path / "timed-out.pdf"
        with patch.object(kit, "find_chrome", return_value="chrome"), patch.object(kit.subprocess, "run", side_effect=subprocess.TimeoutExpired("chrome", 60)):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                kit.run_chrome(output=output)

    def test_page_policy_and_missing_pdf_text(self):
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest("pypdf not installed")
        source = self.make_resume()
        writer = PdfWriter()
        for _ in range(3):
            writer.add_blank_page(width=595, height=842)
        with source.with_suffix(".pdf").open("wb") as handle:
            writer.write(handle)
        report = qa.run(source, max_pages=2, render=False)
        self.assertEqual(report["checks"]["pages"]["status"], "fail")
        self.assertEqual(report["checks"]["pdf_content"]["status"], "fail")

    def test_missing_optional_checks_remain_incomplete(self):
        source = self.make_resume()
        source.with_suffix(".pdf").write_bytes(b"mock rendering input")
        successful_pdf = {key: qa.result([]) for key in ("pdf_content", "pdf_links", "pages")}
        with patch.object(qa, "pdf_checks", return_value=successful_pdf), patch.object(qa, "render_pdf", return_value=[]):
            report = qa.run(source)
        self.assertEqual(report["overall"], "incomplete")
        self.assertEqual(report["checks"]["pdf_render"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
