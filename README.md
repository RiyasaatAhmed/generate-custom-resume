# generate-custom-resume

**One command that tailors your whole application to a job post:** a rewritten resume (DOCX + PDF), a cover letter, and a LinkedIn message for the hiring manager.

```
/generate-custom-resume https://jobs.example.com/acme/senior-frontend-engineer
```

It works inside **Claude Code** or **Cursor**. You give it a job post; it researches the company, compares the post against your master resume, rewrites the resume to fit, exports it, and writes the cover letter and outreach message. Everything lands in one folder per application.

It never invents experience. Every bullet, skill, and number has to trace back to your master resume or something you confirm in chat. When the job asks for something you don't have, it asks you instead of making it up.

---

## What you get for each application

```
applications/acme-senior-frontend-engineer/
├── job-post.md              the original posting, archived (postings disappear)
├── resume.md                the tailored resume, in markdown
├── resume.docx              styled Word version
├── resume.pdf               linked, print-ready PDF
├── resume-wrap-check.png    screenshot used to verify every bullet fits on one line
├── upload/
│   ├── Jane-Doe-Resume.pdf  clean filenames to actually upload
│   └── Jane-Doe-Resume.docx
├── cover-letter.md          250-350 words, plain text, ready to paste
└── outreach.txt             LinkedIn message for the hiring manager + 3 InMail subject lines
```

Plus a running `applications/applications-log.md` table of every job you applied to.

In chat, it also posts:

- **Company Intelligence brief:** mission, product, values, tone, tech signals, and one current, verifiable "why them" detail
- **Gap report:** each resume section against what the job wants, with what to reframe and what to ask you about
- **Change log:** what moved, what was cut, which job problem each bullet answers, and where each number came from
- **Quality checklist:** about 30 checks, each ticked or called out

## How it works

| Phase | What happens |
| ----- | ------------ |
| **0. Load you** | Reads your profile, master resume, and personal rules |
| **1. Research + rewrite** | Fetches the job post, researches the company, finds the gaps, rewrites the resume (exact job title in the headline, one-line bullets with metrics, ATS keywords copied verbatim) |
| **2. Export + QA** | Builds the DOCX and PDF, checks that the text parses, checks page breaks, and screenshots the page so wrapped lines get fixed |
| **3. Cover letter** | Strategy, then draft, then a pass that removes AI-sounding writing, using three bundled skills. Bans filler like "passionate" and "excited" |
| **4. Outreach** | A short LinkedIn message (under 900 characters) to the person the role reports to, with three InMail subject lines (120 characters max) |
| **5. Interview prep** | *On request:* turns each bullet into a full STAR story |

---

## Requirements

| Need | Why | Check |
| ---- | --- | ----- |
| **macOS or Linux** (Windows works through WSL) | `setup.sh` is a bash script | |
| **Python 3.9+** | the export scripts (standard library only) | `python3 --version` |
| **Google Chrome** (or Chromium, Edge, Brave) | renders the PDF and the wrap-check screenshot | |
| **Claude Code** or **Cursor** | runs the command | `claude --version` |
| *Optional:* `pypdf` | enables the page-break check | `python3 -m pip install pypdf` |

No other packages are needed.

---

## Quick start

### 1. Get the kit

```bash
git clone <this-repo-url> generate-custom-resume
cd generate-custom-resume
```

(Or download and unzip it anywhere you like.)

### 2. Run setup

```bash
./setup.sh
```

This:

1. checks Python and Chrome
2. creates your profile files from the examples (it never overwrites existing ones)
3. installs the command and skills into this folder for Claude Code (`.claude/`) and Cursor (`.cursor/`)
4. exports a sample resume as a smoke test

**Want the command available in every folder?** Use `./setup.sh --global` instead. It also installs into `~/.claude` and `~/.cursor`. An existing `generate-custom-resume` command there gets backed up first, and a skill folder with the same name as one of the bundled skills is left untouched.

### 3. Fill in your profile

Edit the three files in `profile/`. They start as examples for a fictional "Jane Doe"; replace them with your own details. See [Your profile](#your-profile) below.

### 4. Run it

**Claude Code**

```bash
cd generate-custom-resume
claude
```

Then in the chat:

```
/generate-custom-resume https://link-to-the-job-post
```

**Cursor:** open the folder, open the agent chat, type `/generate-custom-resume` and paste the job link.

If the job site blocks fetching (LinkedIn, some ATS portals), paste the job text after the command instead of the URL.

---

## Your profile

Everything personal lives in `profile/`, which is **git-ignored** apart from the examples. Your data stays on your machine.

### `profile/base-resume.md`: your master resume

This is the **only source of truth** for your experience. Put everything true in it, even what doesn't fit on one page; the command chooses what to show for each job.

Keep this shape, because the exporter parses it:

```markdown
# Your Name

**Senior Frontend Engineer | TypeScript, React & Next.js | Design Systems**

Remote (EU / US East overlap)

🌐 yoursite.dev | 📧 you@example.com | LinkedIn | GitHub

---

## Summary

One paragraph. Use **bold** for the phrases that matter.

---

## Skills

Frontend: typescript, react, next.js
Backend & Cloud: node.js, docker, aws

---

## Experience

### Job Title

**Company Name**, City, Country (Remote) | Mar 2023 - Present

- Result-first bullet with a **metric**. [View Project]
- Another bullet.

<!-- - A true win kept off the default cut. The command can pull it in when a job calls for it. -->

---

## Education

**B.S. Computer Science** | Sep 2015 - Jun 2019
University Name, City, Country

---

## Honors & Awards

**Award Title 2019** - Where it is from
One line of detail. [View Paper]
```

Tips:

- **Bullet bank:** strong but less general wins can go in one-line HTML comments under a role (`<!-- - ... -->`). They stay off the default resume, but the command can use them when a job needs them.
- **Link tokens** like `[View Project]` at the end of a bullet are moved onto the company line and linked using `profile.json`.
- Each HTML comment has to fit on **one line**.
- Have a second version, such as a full-stack one? Save it as `profile/base-resume-fullstack.md`. The command picks the variant that fits the role and tells you which one it used.

### `profile/profile.json`: name, links, and export settings

| Key | What it does |
| --- | ------------ |
| `name` | Your full name |
| `standard_headline` | The headline on your LinkedIn. You're told when a tailored headline differs from it |
| `upload_basename` | Filename for upload copies, e.g. `Jane-Doe-Resume` |
| `contact_lines` | Contact rows under your name. Each row is a list of `{ "icon", "text", "url" }`. The text is shown, the URL is the link, and the icon is optional |
| `link_labels` | Targets for bracket tokens: `"View Paper": "https://..."` makes `[View Paper]` a link |
| `company_projects` | Where `[View Project]` points for each company (matched against the company name) |
| `company_websites` | Turns the company name into a link |
| `company_about` | Optional italic one-liner under each company ("What the company does") |
| `auto_bold` | `true` also bolds metrics and skill names automatically on export. `false` bolds only what you mark with `**` |
| `bold_terms` | Extra phrases to auto-bold |
| `summary_bold_phrases` | Regex patterns to auto-bold in the summary only, e.g. `"\\d+\\+\\s*years"` |

The resume and cover letter take contact details **from this file**, so they always match.

### `profile/candidate-notes.md`: your personal rules

Plain-English instructions the command reads before each run. **They override the command's defaults.** This is where you add:

- **Sources of truth:** your portfolio URL, extra resume variants
- **Positioning:** your strongest angle and the roles you're targeting
- **Domain rules:** e.g. "for health tech roles, lead with the clinical wins and spell out PHI and EHR"
- **Cover letter voice:** tone, and the links to include
- **Outreach voice:** the exact opening and closing lines for the LinkedIn message
- **Hard rules:** anything that must never happen ("never mention client X by name")

The example file shows each section.

---

## Running the scripts yourself

The command runs these for you, and you can also run them by hand. All of them work from any directory.

```bash
# Export resume markdown to .docx + .pdf (+ .html) next to it
python3 scripts/md_export.py applications/<slug>/resume.md

# Export a cover letter to .docx + .pdf (optional; the command keeps it as text by default)
python3 scripts/md_export.py applications/<slug>/cover-letter.md --cover

# QA: parse check, page-break report, wrap-check screenshot
python3 scripts/qa.py applications/<slug>/resume.md

# Print an existing .docx as plain text
python3 scripts/docx_text.py ~/Downloads/old-resume.docx

# LinkedIn helpers: Unicode bold headers, and length checks for the outreach file
python3 scripts/outreach.py bold "Design Systems"
python3 scripts/outreach.py check applications/<slug>/outreach.txt
```

Useful flags for `md_export.py`: `--docx-only`, `--pdf-only`, `--docx <path>`, `--pdf <path>`, `--template <file.docx>`.

Environment variables:

| Variable | Effect |
| -------- | ------ |
| `RESUME_PROFILE=/path/to/profile.json` | Use a different profile (e.g. to keep several personas) |
| `CHROME_PATH=/path/to/chrome` | Use a specific Chromium-based browser |

---

## Project structure

```
generate-custom-resume/
├── README.md
├── setup.sh                        installer (re-runnable)
├── commands/
│   └── generate-custom-resume.md   the command itself (source; setup.sh fills in paths)
├── skills/                         bundled cover-letter skills (MIT, see Credits)
│   ├── cover-letter/
│   ├── cover-letter-generator/
│   └── clarity/
├── scripts/
│   ├── md_export.py                main export entry point (resume or cover letter)
│   ├── md_to_docx.py               markdown -> styled DOCX (clones styles from the template)
│   ├── md_to_pdf.py                markdown -> HTML -> PDF through headless Chrome
│   ├── md_to_cover.py              cover letter export
│   ├── resume_links.py             link resolution + auto-bold rules
│   ├── qa.py                       post-export checks
│   ├── outreach.py                 LinkedIn bold text + length checks
│   ├── docx_text.py                .docx -> plain text
│   └── kit.py                      shared paths, profile loading, Chrome lookup
├── templates/
│   └── resume-template.docx        DOCX style source (fonts, spacing, tab stops)
├── profile/                        YOUR data (git-ignored apart from *.example.*)
└── applications/                   generated output (git-ignored)
```

### Customizing the DOCX look

`md_to_docx.py` builds the document by cloning formatted "prototype" paragraphs from `templates/resume-template.docx`, so the DOCX keeps real Word styling (embedded Arimo font, right-aligned dates on tab stops, hanging bullets). To restyle it, open the template in Word, change fonts, sizes, and colors, and save. **Keep the 17 paragraphs in the same order**; the index map is `PROTO` at the top of `md_to_docx.py`. The PDF look is set by the `CSS` block in `md_to_pdf.py`.

---

## Updating and uninstalling

- **Moved the folder?** Re-run `./setup.sh` (and `--global` if you used it). The installed command contains the folder's absolute path.
- **Edited `commands/generate-custom-resume.md`?** Re-run `./setup.sh` to update the installed copies.
- **Remove the user-level install:** `./setup.sh --uninstall-global`. It removes only files this kit created.

---

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| `Chrome/Chromium not found` | Install Google Chrome, or set `CHROME_PATH` to your browser's binary |
| `/generate-custom-resume` doesn't show up | Run `./setup.sh`, then restart Claude Code / Cursor. Without `--global`, open the kit folder itself |
| The command says your profile still has "Jane Doe" | Replace the examples in `profile/` with your own details |
| Job post won't fetch | Paste the job text after the command instead of the URL |
| `page check skipped` in QA | `python3 -m pip install pypdf` (optional) |
| `parse QA: FAILED` | Usually a resume `.md` that doesn't match the expected shape. Compare it with `profile/base-resume.example.md` |
| A link token shows as plain `[Label]` | Add the label to `link_labels`, or the company to `company_projects`, in `profile.json` |

---

## Ground rules the command follows

- **No invented experience.** Claims, skills, and metrics come from your master resume, your notes, or your confirmation in chat.
- **No LinkedIn scraping.** It never opens LinkedIn. If the hiring manager's name isn't on a public non-LinkedIn page, it leaves `[Name]` and lists the sources it checked.
- **No em dashes** and no filler ("passionate", "synergy", "results-driven") in the resume or cover letter.
- **Nothing gets committed or sent for you.** You review everything and send it yourself.

---

## Credits

The cover-letter phase uses three community skills, bundled under their MIT licenses (see the `LICENSE` in each folder):

- [`cover-letter`](https://github.com/claude-office-skills/skills) by Claude Office Skills Contributors (lightly adapted)
- [`cover-letter-generator`](https://github.com/paramchoudhary/resumeskills) by Resume Skills
- [`clarity`](https://github.com/addyosmani/clarity) by Addy Osmani (bundled: `SKILL.md`, `references/`, and the two lint scripts)

## License

[MIT](LICENSE)
