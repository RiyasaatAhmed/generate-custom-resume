# generate-custom-resume

An agent skill that turns a job post into a truthful, evidence-based application. It
works in Claude Code, Cursor, Antigravity, Codex, Gemini CLI, GitHub Copilot, and any
other agent that reads [Agent Skills](https://agentskills.io).

```text
/generate-custom-resume https://example.com/careers/frontend-engineer
```

Give it a job post and the agent:

1. checks your fit and practical eligibility, such as location and work authorization;
2. researches the employer;
3. matches each requirement to a real achievement from your resume;
4. writes a tailored resume, plus a cover letter or recruiter message when one fits;
5. exports DOCX and PDF, then checks that nothing was lost in export.

It never invents experience, metrics, or company facts, and it never submits an
application or sends a message for you. It makes your relevant experience easy to
evaluate; it cannot guarantee an interview.

## Install

You need Python 3.9 or later. PDF export also needs Chrome, Chromium, Edge, or Brave;
DOCX export works without a browser. Two optional extras turn on more checks:
`pip install pypdf` checks the text and links inside the PDF, and
`pip install pypdfium2 pillow` (or poppler's `pdftoppm`) renders the PDF pages so they
can be reviewed.

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add RiyasaatAhmed/generate-custom-resume
/plugin install generate-custom-resume@riyasaat-skills
```

On Claude Code 2.1.275 or later you can do it in one step:
`/plugin install generate-custom-resume --marketplace RiyasaatAhmed/generate-custom-resume`.
Claude Code prefixes plugin skills with the plugin name, so the command is
`/generate-custom-resume:generate-custom-resume <job post>`. Asking Claude to tailor your
resume for a job also works.

**Cursor**: install from the Cursor plugin marketplace, or open *Customize → From GitHub
Repository* and paste `https://github.com/RiyasaatAhmed/generate-custom-resume`.

**Antigravity, Codex, Gemini CLI, Copilot, OpenCode, and other agents**, using the
[skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add RiyasaatAhmed/generate-custom-resume -g
```

`-g` installs the skill for your user account instead of a single project. The CLI asks
which agents to install it for.

**From a clone**, for development or to keep a local copy:

```bash
git clone https://github.com/RiyasaatAhmed/generate-custom-resume
cd generate-custom-resume && ./install.sh
```

`install.sh` symlinks the skill into `~/.claude/skills` for Claude Code and into
`~/.agents/skills`, which Cursor, Antigravity, Codex, Gemini CLI, and others read. Pass
`--target claude` or `--target agents` to link only one, `--smoke` to test PDF export,
or `--uninstall` to remove the links. It never replaces a skill that something else
installed.

To install by hand, copy `skills/generate-custom-resume/` into your agent's skills
folder. The folder is self-contained: its scripts, references, and templates all live
inside it.

## Your data

Your profile and applications live in a data folder outside the installed skill, so
updating the skill never touches them:

```text
~/resume-kit/            or $RESUME_KIT_HOME
├── profile/
│   ├── profile.json         identity, contacts, links, presentation settings
│   ├── base-resume.md       full, truthful master resume (bullet-bank comments allowed)
│   ├── candidate-notes.md   positioning, voice, and access rules the agent must follow
│   └── achievements.json    optional evidence bank
└── applications/        one folder per job
```

On the first run the agent calls `scripts/init_kit.py`. It creates this folder with
fictional starter files for "Jane Doe" and never overwrites a file that already exists.
Replace the examples with your own details before you generate a real application; the
agent will not treat the examples as your experience. To keep your data somewhere else,
set `RESUME_KIT_HOME=/path/to/folder` in your shell profile.

Local files do not mean local-only processing. What your agent sends to its model
provider depends on the agent and its settings.

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

Your candidate notes control style and access. For example, a "never access LinkedIn"
rule tells the agent to stay off LinkedIn even when looking up a contact; it is an
instruction to the agent, not a technical block. Notes cannot make an unsupported claim
true. Overlapping with an employer's time zone does not establish where you live or
whether you can legally work there.

## Resume source format

The exporter accepts a specific Markdown dialect, not arbitrary Markdown:

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

Every section is optional, and `Work Experience` works in place of `Experience`. An
unknown section, a malformed entry, a table, or a code block fails with an error rather
than disappearing from the export. Write each bullet on one source line. HTML comments
never reach the export, so your master resume can keep a bullet bank in comments for the
agent to choose from. Nothing forces a page count, a bullet count, or a number in every
bullet.

Contact details come from `profile.json`. A bare `[View Project]` token resolves through
`company_projects` and moves to the company row; other bare tokens resolve through
`link_labels`. A token with no matching link fails the export.

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

Environment variables: `RESUME_KIT_HOME` sets the data folder, `RESUME_PROFILE` points to
a different `profile.json`, and `CHROME_PATH` picks a specific Chromium-based browser.

## Running the scripts yourself

The agent runs these for you. The commands assume a clone, with two shell variables:
`S=skills/generate-custom-resume/scripts` for the scripts and
`A=~/resume-kit/applications/<id>` for one application folder.

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

QA compares the source with the DOCX text and links, the PDF text and link destinations,
and the page budget, and reports each check as pass, fail, or skipped. With
`--require-complete`, a skipped check exits with code 2. Rendering the pages is not the
same as reviewing them: use `--visual-reviewed "notes"` only after someone has looked at
every page. None of these checks certifies how a particular ATS will read the resume.

`outreach.py check` catches unresolved placeholders, missing subject lines, messages over
the length budget, and "I have applied" wording before a submission is confirmed.
`applications.py submit` records a submission you already made; it never submits
anything. Outcome rates count only submitted applications, and a handful of applications
cannot show what caused a result.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 skills/generate-custom-resume/scripts/smoke.py   # exports fictional fixtures; needs Chrome
claude plugin validate . --strict
```

The tests use temporary folders and fictional profiles. They never touch a real profile
or your home folder, and they never send anything.

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

DOCX styling comes from `assets/resume-template.docx`. A custom template must keep the
17 prototype paragraphs in the order listed in `PROTO` in `scripts/md_to_docx.py`. PDF
styling lives in `scripts/md_to_pdf.py`.

For a release, bump the version in four places: `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, `.cursor-plugin/plugin.json`, and `metadata.version` in
`SKILL.md`.

## Research basis and limits

The writing and formatting defaults draw on these sources. Each supports one narrow
point, not a universal rule:

- [CareerOneStop formatting](https://cloudfront.careeronestop.org/JobSearch/Resumes/ResumeGuide/formatting.aspx): readable layouts and one or two pages based on experience.
- [Harvard resume/letter guidance](https://careerservices.fas.harvard.edu/resources/create-a-strong-resume/): specific, factual, tailored writing and relevant examples.
- [Greenhouse parsing](https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse): formatting-related extraction failures; not a universal scoring specification.
- [Greenhouse filtering](https://support.greenhouse.io/hc/en-us/articles/27104809835291-Talent-Filtering): exact keyword filtering exists; it does not establish universal ATS ranking weights.
- [MIT networking](https://capd.mit.edu/resources/using-ai-for-networking/): specific, concise messages and clear requests.
- [OPM work samples](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/work-samples-and-simulations/): job-relevant demonstrations assess competencies; unsolicited portfolio benefits remain an inference.
- [NBER writing-assistance study](https://www.nber.org/papers/w30886): an 8% relative hiring increase in one online-labor-market experiment, not a guarantee for this kit.

The kit has not been validated against real ATS uploads or real application outcomes.

## License

MIT © Riyasaat Ahmed Rahul
