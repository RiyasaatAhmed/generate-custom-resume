# generate-custom-resume

Create a truthful, evidence-based application package from a job posting in **Claude Code** or **Cursor**:

```text
/generate-custom-resume https://example.com/careers/frontend-engineer
```

The workflow assesses fit and practical eligibility, researches the employer, maps requirements to real achievements, writes the resume and appropriate cover letter/outreach, and validates exports. It helps make relevant experience easy to evaluate; it does not guarantee an interview or an offer.

## Setup

Core scripts require Python 3.9+. PDF export requires Chrome/Chromium (Edge or Brave also work). DOCX export uses the standard library. Optional `pypdf` enables PDF content, link, and page checks; `pypdfium2` plus Pillow or the `pdftoppm` program enables actual PDF page previews.

```bash
./setup.sh
# Install without a browser smoke test:
./setup.sh --skip-smoke
# Optional user-level installation, only if wanted:
./setup.sh --global --skip-smoke
```

Setup creates missing profile files from fictional examples and installs project-local command/skill links. It never overwrites an existing profile or an unrelated skill link, and it does not create `profile/achievements.json` (the bank is optional and must hold only your real claims). Setup also reports whether pypdf and a PDF page renderer are available. Global command collisions are backed up. The command loads this kit's explicit skill path even when another skill has the same name. Missing Chrome does not prevent DOCX-only use.

Replace the example profile before generating a real application:

- `profile/base-resume.md`: full, truthful experience and optional bullet-bank comments.
- `profile/profile.json`: identity, contact details, links, and presentation settings.
- `profile/candidate-notes.md`: positioning, access restrictions, and voice preferences.
- Optional `profile/achievements.json`: reusable evidence; see `achievements.example.json` for the schema. Do not copy fictional claims into your real bank. An empty bank can start as `{"schema_version": 1, "achievements": []}`.

Personal profile files and generated applications are Git-ignored by default. This does not guarantee local-only processing: what the assistant sends to its provider or tools depends on the chosen application and configuration. Do not place private candidate data in tracked examples or tests.

Open this folder in Claude Code or Cursor, then invoke the command. If a site blocks retrieval, paste the job text. Existing applications can be revised by supplying their folder. Re-run setup after moving the kit or changing the command. Broken links left by the old location are repointed; links to other existing skills are reported and left alone.

## What each application contains

```text
applications/<company-role-requisition-date-unique-id>/
├── application.json        preparation, events, submission history
├── job-post.md             archived source and retrieval date
├── evidence-map.json       requirements and direct/adjacent/missing/unknown evidence
├── research.md             sourced observations, hypotheses, changes, open questions
├── resume.md
├── resume.docx
├── resume.pdf
├── resume.html
├── qa.json                 pass/fail/skipped for each check
├── resume-pages-<hash>/     actual PDF previews, when a renderer is available
├── upload/                 clean filenames selected for submission
├── cover-letter.md         when requested/appropriate
├── outreach/               selected channel drafts
├── interview-prep.md       optional evidence-based interview preparation
└── submitted/<version>/    copies and hashes of confirmed submissions
```

The workflow follows this sequence:

| Step | Decision/output |
| --- | --- |
| Fit | Compare explicit requirements and eligibility with confirmed candidate facts |
| Research | Save employer facts with sources; distinguish hypotheses and unknowns |
| Evidence | Select defensible achievements and identify material questions |
| Writing | Build one coherent case across resume, letter, and outreach |
| Export/QA | Preserve content and links, check pages, inspect actual PDF previews |
| Records | Keep drafting, contacting, and submitting distinct |
| Learning | Track submitted applications and later outcomes with clear denominators |

No invented skills, experience, metrics, referrals, or company facts. No automatic messages, applications, publishing, or commits. Candidate preferences govern style and access; they cannot make an unsupported claim true. Time-zone overlap does not establish work authorization or residence.

## Resume source format

The renderer supports a deliberate Markdown dialect, not arbitrary Markdown:

```markdown
# Your Name
**Truthful Role | Relevant Specialty**
Location / availability
email@example.com | Portfolio

## Summary
A relevant, factual positioning paragraph.

## Skills
Frontend: TypeScript, React

## Experience
### Actual Job Title
**Company Name**, City, Country (Remote) | Mar 2023 - Present
- A specific action, mechanism, and supported outcome. [View Project]

## Education
**B.S. Computer Science** | 2015 - 2019
University Name
**M.S. Computing** | 2019 - 2021
Another University

## Projects
### Relevant Project
- A real contribution. [Demo](https://example.com/demo)

## Certifications
**Credential** | 2024
Issuer

## Publications
[Paper title](https://example.com/paper)

## Honors & Awards
**Award** - Issuer
Relevant detail.
```

Sections are optional; omit empty headings. `Work Experience` is also accepted. Unknown sections, malformed experience entries, tables, and code blocks fail explicitly. Each source bullet is one Markdown line, though it may wrap naturally in the output. Additional education entries begin with a bold degree or `###` heading. HTML comments are omitted from exports; the agent can select true achievements from bullet-bank comments.

Use readable one- or two-page output according to relevance and employer instructions. There is no forced single-line bullet, fixed bullet count per role, or requirement to invent a number for every achievement. Preserve the actual job titles and dates.

Contacts come from `profile.json` when provided. Bare `[View Project]` tokens resolve through `company_projects` and move from experience bullets to the company row. Other bare tokens resolve through `link_labels`. Standard `[label](url)` links are supported. Unresolved tokens fail export.

## Profile settings

| Key | Purpose |
| --- | --- |
| `name` | Candidate identity; also used for plain-text letter exports |
| `standard_headline` | Baseline for reporting a tailored headline change |
| `upload_basename` | Clean filename stem, e.g. `Jane-Doe-Resume`; not a path |
| `contact_lines` | Rows of `{ "text", "url", "icon" }` contacts; icon optional |
| `link_labels` | Bare link token destinations |
| `company_projects` | Project links by employer name |
| `company_websites` | Employer name links |
| `company_about` | Optional factual employer context |
| `auto_bold` | Auto-emphasize supported metrics/skill terms; manual bold always works |
| `bold_terms`, `summary_bold_phrases` | Additional auto-bold terms/summary regexes |
| `resume_max_pages` | Default QA page budget, overridden by `--max-pages` |

`RESUME_PROFILE=/path/to/profile.json` selects a different profile. `CHROME_PATH=/path/to/browser` selects a Chromium-based browser. Scripts resolve their own dependencies independently of the current working directory.

## Export and check

```bash
python3 scripts/md_export.py applications/<id>/resume.md
python3 scripts/qa.py applications/<id>/resume.md --max-pages 2

# DOCX-only export without Chrome:
python3 scripts/md_export.py applications/<id>/resume.md --docx-only

# Plain-text or legacy-header letter, when an attachment is needed:
python3 scripts/md_export.py applications/<id>/cover-letter.md --cover
python3 scripts/qa.py applications/<id>/cover-letter.md --cover --max-pages 1 --json applications/<id>/cover-letter-qa.json
```

Other export options: `--pdf-only`, `--docx <path>`, `--pdf <path>`, `--template <path>`. `--docx-only` and `--pdf-only` are mutually exclusive. The main QA command expects sibling DOCX/PDF files; a DOCX-only export performs its own source-content/link checks but is not a complete PDF validation.

A letter can be plain greeting/body/sign-off, or use the old `# Name`, optional bold headline, `---`, body format. Empty bodies fail before export.

QA checks retained text from raw source, DOCX label/URL relationships, PDF URI destinations, and a configured page limit. It writes `qa.json`. Results are `passed`, `failed`, or `incomplete`. Exit 1 means failure; with `--require-complete`, exit 2 means skipped checks. Without that flag, incomplete optional checks exit 0 but are still reported as incomplete. These checks do not certify any particular ATS.

Actual PDF previews need `pdftoppm` or `pypdfium2` + Pillow. Rendering is not visual inspection. Inspect every page, then use `--visual-reviewed "reviewer and observations"` only if that inspection occurred. The report includes the current PDF hash. `--no-screenshot` skips rendering; `--html-preview` provides a separate HTML preview, not a pagination check. Missing tools are reported honestly. Do not claim an incomplete QA run is fully verified.

## Evidence validation

```bash
python3 scripts/evidence.py bank profile/achievements.json
python3 scripts/evidence.py map applications/<id>/evidence-map.json --bank profile/achievements.json
```

See [the evidence guide](skills/generate-custom-resume/references/evidence.md) and [the fictional map](templates/evidence-map.example.json). Legacy profiles can use source references and excerpts instead of achievement IDs; omit `--bank` in that case. The validators check structure and references, not real-world truth or whether a number is causally attributable to the candidate.

## Outreach

```bash
python3 scripts/outreach.py check applications/<id>/outreach/hiring-manager.txt --channel hiring-manager --application applications/<id>/application.json
python3 scripts/outreach.py check applications/<id>/outreach/connection.txt --channel connection --draft
python3 scripts/outreach.py bold "Design Systems"
```

Channels: `connection`, `recruiter`, `hiring-manager`, `inmail`, `email`, `referral`, `follow-up`, `legacy`. The existing five-block style remains optional. Email/InMail subjects go above a `// ---` separator, each bare subject on its own line. Other channels can contain just the body. Empty bodies fail. `--draft` permits unresolved placeholders but does not make a draft send-ready. `--limit N` changes the editorial budget. Local codepoint/byte counts are not claims about current platform limits.

Post-application wording requires a record with confirmed `applied_at`. Prefer truthful pre-application wording until then. The checker is a guard for common phrases, not a semantic truth detector; review all wording before use.

## Application history

```bash
python3 scripts/applications.py init --company "Example Co" --role "Engineer" --requisition "REQ-123"
python3 scripts/applications.py event applications/<id> ready --note "Reviewed documents and QA"
# Only AFTER the user actually submitted these files:
python3 scripts/applications.py submit applications/<id> upload/Jane-Doe-Resume.pdf --confirm-submitted
python3 scripts/applications.py event applications/<id> contacted --note "User confirmed recruiter contact"
python3 scripts/applications.py event applications/<id> screening --note "Screen scheduled"
python3 scripts/applications.py verify applications/<id>
python3 scripts/applications.py summary applications --group-by role_family
```

`submit` records an action already taken; it never submits anything. It copies the exact named files into a fresh snapshot with hashes. Revisions leave those snapshots alone. `verify` detects accidental missing/modified artifacts and manifests. Contact before application is valid and does not imply submission. The old Markdown log is historical context, not proof of submission; it is not automatically migrated.

Reports retain prepared/submitted counts and post-submission outcomes. Rates with no submitted applications are null. Small nonrandom samples do not establish that a template caused a hire.

## Tests and maintenance

```bash
python3 -m unittest discover -s tests -v
bash -n setup.sh
python3 scripts/smoke.py
```

Unit tests use temporary directories and fictional profiles. `smoke.py` exports fictional base and extended resumes plus a plain-text letter, retains artifacts in a new temp folder, and reports skipped visual checks. Optional `--output <empty-dir>` selects where to inspect outputs. Browser failures may require the host's execution permission. No tests should modify a real candidate profile or send messages.

The main workflow is [skills/generate-custom-resume/SKILL.md](skills/generate-custom-resume/SKILL.md); focused references contain the detailed guidance. `commands/generate-custom-resume.md` is a small host entrypoint. The two cover-letter skill names are compatibility entrypoints to one shared guide. Clarity remains available as an optional editing aid.

DOCX styling still comes from `templates/resume-template.docx`. Custom templates must retain the 17 prototype paragraphs in the order documented by `PROTO` in `scripts/md_to_docx.py`. PDF styling is in `scripts/md_to_pdf.py`. Keep content and styling changes separate when troubleshooting.

`./setup.sh --uninstall-global` removes matching kit-owned global links/commands. It does not delete candidate data or project-local files.

## Credits and license

MIT. Bundled compatibility skills retain their original licenses: Claude Office Skills Contributors (`cover-letter`), Resume Skills (`cover-letter-generator`), and Addy Osmani (`clarity`).

## Research basis and limits

The workflow's writing and formatting defaults draw on these sources. Each supports a narrow point, not a universal rule:

- [CareerOneStop formatting](https://cloudfront.careeronestop.org/JobSearch/Resumes/ResumeGuide/formatting.aspx): readable layouts and one or two pages based on experience.
- [Harvard resume/letter guidance](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/): specific, factual, tailored writing and relevant examples.
- [Greenhouse parsing](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse): formatting-related extraction failures; not a universal scoring specification.
- [Greenhouse filtering](https://support.greenhouse.io/hc/en-us/articles/27104809835291-Talent-Filtering): exact keyword filtering exists; it does not establish universal ATS ranking weights.
- [MIT networking](https://capd.mit.edu/resources/using-ai-for-networking/): specific, concise messages and clear requests.
- [OPM work samples](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/work-samples-and-simulations/): job-relevant demonstrations assess competencies; unsolicited portfolio benefits remain an inference.
- [NBER writing-assistance study](https://www.nber.org/papers/w30886): an 8% relative hiring increase in one online-labor-market experiment, not a guarantee for this kit.

No actual ATS upload or application-conversion history was used to validate this kit. Local QA confirms that content and links survive export; it does not certify any particular ATS.
