# generate-custom-resume

An agent skill that turns a job post into a truthful, evidence-based application package. It works in Claude Code, Cursor, Antigravity, Codex, Gemini CLI, GitHub Copilot, and any other agent that reads [Agent Skills](https://agentskills.io).

```text
/generate-custom-resume https://example.com/careers/frontend-engineer
```

The agent assesses fit and practical eligibility, researches the employer, maps each requirement to your real achievements, writes the resume plus a cover letter or outreach when appropriate, exports DOCX and PDF, and checks that nothing was lost in export. It never invents experience, metrics, or company facts, and it never submits applications or sends messages for you. It makes relevant experience easy to evaluate; it does not guarantee an interview.

## Install

Requirements: Python 3.9+. PDF export needs Chrome, Chromium, Edge, or Brave; DOCX export works without a browser. Optional: `pip install pypdf` enables PDF content and link checks, and `pip install pypdfium2 pillow` (or poppler's `pdftoppm`) enables PDF page previews.

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add RiyasaatAhmed/generate-custom-resume
/plugin install generate-custom-resume@riyasaat-skills
```

On Claude Code 2.1.275 or later this is one step: `/plugin install generate-custom-resume --marketplace RiyasaatAhmed/generate-custom-resume`. Plugin skills are namespaced, so run `/generate-custom-resume:generate-custom-resume <job post>`, or just ask Claude to tailor your resume for a job.

**Cursor**: install from the Cursor plugin marketplace, or go to *Customize → From GitHub Repository* and paste `https://github.com/RiyasaatAhmed/generate-custom-resume`.

**Antigravity, Codex, Gemini CLI, Copilot, OpenCode, and other agents** (via the [skills CLI](https://github.com/vercel-labs/skills)):

```bash
npx skills add RiyasaatAhmed/generate-custom-resume -g
```

`-g` installs for your user rather than one project; the CLI asks which agents to install for.

**From a clone** (for development, or to pin a local copy):

```bash
git clone https://github.com/RiyasaatAhmed/generate-custom-resume
cd generate-custom-resume && ./install.sh
```

`install.sh` symlinks the skill into `~/.claude/skills` (Claude Code) and `~/.agents/skills` (read by Cursor, Antigravity, Codex, Gemini CLI, and others). Use `--target claude` or `--target agents` to link only one, `--smoke` to test PDF export, and `--uninstall` to remove the links. It never replaces a skill installed by something else.

To install by hand, copy `skills/generate-custom-resume/` into your agent's skills folder. The skill is self-contained: its scripts, references, and templates live inside that folder.

## Your data

Your profile and applications live in a data folder outside the installed skill, so updates never touch them:

```text
~/resume-kit/            or $RESUME_KIT_HOME
├── profile/
│   ├── profile.json         identity, contacts, links, presentation settings
│   ├── base-resume.md       full, truthful master resume (bullet-bank comments allowed)
│   ├── candidate-notes.md   positioning, voice, and access rules the agent must follow
│   └── achievements.json    optional evidence bank
└── applications/        one folder per job
```

On first run the agent calls `scripts/init_kit.py`, which creates this folder with fictional starter files (Jane Doe) and never overwrites existing files. Replace the examples with your own details before generating a real application; the agent refuses to treat the examples as your experience. To use a different folder, set `RESUME_KIT_HOME=/path/to/folder` in your shell profile.

Keeping files local does not mean local-only processing: what your agent sends to its model provider depends on the agent and its settings.

## What each application contains

```text
applications/<company-role-date-id>/
├── application.json        preparation, events, submission history
├── job-post.md             archived source and retrieval date
├── evidence-map.json       requirements matched to direct/adjacent/missing/unknown evidence
├── research.md             sourced observations, hypotheses, changes, open questions
├── resume.md / .docx / .pdf / .html
├── qa.json                 pass/fail/skipped for each check
├── resume-pages-<hash>/    actual PDF page previews, when a renderer is available
├── upload/                 clean filenames, created only after checks pass
├── cover-letter.md         when requested or appropriate
├── outreach/               the chosen channel's draft
├── interview-prep.md       optional
└── submitted/<version>/    copies and hashes of what you confirmed you submitted
```

| Step | Decision/output |
| --- | --- |
| Fit | Compare explicit requirements and eligibility with confirmed candidate facts |
| Research | Save employer facts with sources; label hypotheses and unknowns |
| Evidence | Select defensible achievements; ask about material gaps |
| Writing | One coherent case across resume, letter, and outreach |
| Export/QA | Preserve content and links, check page count, inspect actual PDF pages |
| Records | Keep drafting, contacting, and submitting distinct |

Candidate notes govern style and access (for example, "never access LinkedIn"); they cannot make an unsupported claim true. Time-zone overlap does not establish work authorization or residence.

## Resume source format

The exporter supports a deliberate Markdown dialect, not arbitrary Markdown:

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

Sections are optional; `Work Experience` is also accepted. Unknown sections, malformed entries, tables, and code blocks fail explicitly. Each bullet is one source line. HTML comments are left out of exports, so the master resume can hold a bullet bank the agent selects from. There is no forced page count, bullet count, or number in every bullet.

Contacts come from `profile.json`. Bare `[View Project]` tokens resolve through `company_projects` and move to the company row; other bare tokens resolve through `link_labels`. Unresolved tokens fail export.

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
| `auto_bold` | Auto-emphasize metrics and skill terms; manual bold always works |
| `bold_terms`, `summary_bold_phrases` | Extra auto-bold terms and summary regexes |
| `resume_max_pages` | Default QA page budget, overridden by `--max-pages` |

Environment variables: `RESUME_KIT_HOME` (data folder), `RESUME_PROFILE` (a different profile.json), `CHROME_PATH` (a specific Chromium-based browser).

## Running the scripts yourself

The agent runs these for you. Paths below assume a clone; `S=skills/generate-custom-resume/scripts` and `A=~/resume-kit/applications/<id>`.

```bash
python3 $S/init_kit.py                                  # create/check the data folder
python3 $S/md_export.py $A/resume.md                    # DOCX + PDF (--docx-only works without Chrome)
python3 $S/qa.py $A/resume.md --max-pages 2             # writes $A/qa.json
python3 $S/md_export.py $A/cover-letter.md --cover
python3 $S/evidence.py map $A/evidence-map.json         # add --bank ~/resume-kit/profile/achievements.json
python3 $S/outreach.py check $A/outreach/recruiter.txt --channel recruiter --application $A/application.json
python3 $S/applications.py init --company "Example Co" --role "Engineer"
python3 $S/applications.py event $A ready --note "Reviewed documents and QA"
python3 $S/applications.py submit $A upload/Jane-Doe-Resume.pdf --confirm-submitted   # only after YOU submitted
python3 $S/applications.py summary --group-by role_family
```

QA compares the source with DOCX text and links, PDF text and link destinations, and the page budget. Results are pass, fail, or skipped per check; `--require-complete` makes skipped checks exit 2. Rendering pages is not visual inspection: `--visual-reviewed "notes"` is for after someone actually looked at every page. These checks do not certify any particular ATS.

`outreach.py check` flags unresolved placeholders, missing subjects, overlong messages, and "I have applied" wording without a confirmed submission. `applications.py submit` records something you already did; it never submits. Outcome rates count only submitted applications, and small samples do not prove causation.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 skills/generate-custom-resume/scripts/smoke.py   # exports fictional fixtures; needs Chrome
claude plugin validate . --strict
```

Tests use temporary folders and fictional profiles; they never touch a real profile, HOME, or send anything.

```text
.claude-plugin/          Claude Code plugin + marketplace manifests
.cursor-plugin/          Cursor plugin + marketplace manifests
skills/generate-custom-resume/
├── SKILL.md             the workflow (Agent Skills format)
├── references/          detailed guidance loaded only when a step needs it
├── scripts/             export, QA, evidence, outreach, and records helpers
└── assets/              DOCX template, fictional starter profile, example evidence map
install.sh               link a clone into local agents
tests/
```

DOCX styling comes from `assets/resume-template.docx`. A custom template must keep the 17 prototype paragraphs in the order documented by `PROTO` in `scripts/md_to_docx.py`. PDF styling is in `scripts/md_to_pdf.py`.

When releasing, bump `version` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, and `metadata.version` in `SKILL.md`.

## Research basis and limits

The writing and formatting defaults draw on these sources. Each supports a narrow point, not a universal rule:

- [CareerOneStop formatting](https://cloudfront.careeronestop.org/JobSearch/Resumes/ResumeGuide/formatting.aspx): readable layouts and one or two pages based on experience.
- [Harvard resume/letter guidance](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/): specific, factual, tailored writing and relevant examples.
- [Greenhouse parsing](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse): formatting-related extraction failures; not a universal scoring specification.
- [Greenhouse filtering](https://support.greenhouse.io/hc/en-us/articles/27104809835291-Talent-Filtering): exact keyword filtering exists; it does not establish universal ATS ranking weights.
- [MIT networking](https://capd.mit.edu/resources/using-ai-for-networking/): specific, concise messages and clear requests.
- [OPM work samples](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/work-samples-and-simulations/): job-relevant demonstrations assess competencies; unsolicited portfolio benefits remain an inference.
- [NBER writing-assistance study](https://www.nber.org/papers/w30886): an 8% relative hiring increase in one online-labor-market experiment, not a guarantee for this kit.

No actual ATS upload or application-conversion history was used to validate this kit.

## License

MIT © Riyasaat Ahmed Rahul
