# Exports and quality checks

Run exports from the selected profile. `RESUME_PROFILE` can select a different profile.

```bash
python3 "<KIT>/scripts/md_export.py" "<APP>/resume.md"
python3 "<KIT>/scripts/qa.py" "<APP>/resume.md" --max-pages 2
```

Choose a page budget consistent with the candidate, market, and posting. `--docx-only`
and `--pdf-only` support focused exports. Unknown resume sections, malformed structure,
unresolved link tokens, and empty cover letters fail explicitly. Fix source problems;
do not bypass checks to make a broken artifact appear complete.

QA writes `qa.json` with separate DOCX text/link, PDF text/link, page-count, rendering,
and visual-review results. Each is pass/fail/skipped. `overall: incomplete` means at
least one check was skipped. Exit 1 indicates failure; add `--require-complete` for
exit 2 on incomplete checks. A normal exit 0 without that flag is not an all-checks pass.
Use `--json` to keep separate reports for resume and letter.

DOCX checks compare raw source content and actual label/destination relationships.
PDF checks need pypdf and compare extracted content and actual URI destinations. These
do not prove that every ATS will parse the resume or that links are reachable online.
Review semantic accuracy separately: facts, attribution, units, dates, claims, and sources.

Actual PDF previews use `pdftoppm` or `pypdfium2` plus Pillow when installed. Inspect
every page for clipped text, awkward splits, readability, and stray template content.
Fix meaningful problems, re-export, and recheck. Rendering is not visual inspection.
After actually inspecting the current PDF, record observations:

```bash
python3 "<KIT>/scripts/qa.py" "<APP>/resume.md" --max-pages 2 --visual-reviewed "Reviewer: inspected all pages; no clipping or stranded headings"
```

The report binds the review to the current PDF hash. Never supply that flag without
inspection. If no renderer is available, clearly report the skipped check and retain
an incomplete result. `--no-screenshot` intentionally skips rendering. Optional
`--html-preview` produces an HTML screenshot, not evidence of PDF page breaks.

When automatic content/link checks pass, copy the selected PDF/DOCX into `upload/`
using `upload_basename` from the profile. Validate the basename is a filename, not a
path. Preserve file bytes. Recreate upload copies after changes, and check their hashes
match the checked outputs. Do not copy an older export left by a failed run.

Use a fresh dated application version for a new opening; never overwrite `submitted/`.
Deliver any incomplete checks explicitly rather than claiming the package is verified.
Do not label a package ready until unresolved material facts and required checks are
handled. A user can review a provisional draft while a dependency is unavailable.
