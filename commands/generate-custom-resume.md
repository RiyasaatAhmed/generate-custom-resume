---
description: Tailor a resume, cover letter, and LinkedIn outreach message to one job post
argument-hint: <job post URL or pasted job text>
---

# Generate Custom Resume + Cover Letter + Outreach

End-to-end application tailoring: fetch job post, deep company research, gap analysis, resume rewrite, export `.docx` + `.pdf`, tailored cover letter, post-apply LinkedIn outreach message to the reporting manager.

**Kit root:** `{{KIT}}`
**Profile:** `{{KIT}}/profile/` (`profile.json`, `base-resume.md`, `candidate-notes.md`)
**Output dir:** `{{KIT}}/applications/<slug>/` (one folder per application)
**Slug format:** `<company-slug>-<role-slug>` (lowercase kebab-case, e.g. `stripe-senior-frontend-engineer`)

Files inside each application folder:

| File | Phase |
| ---- | ----- |
| `job-post.md` | 1 |
| `resume.md`, `resume.docx`, `resume.pdf`, `resume.html` | 1-2 |
| `upload/<upload_basename>.pdf` and `.docx` | 2 |
| `cover-letter.md` | 3 |
| `outreach.txt` | 4 |
| `interview-prep.md` | 5 (on request) |

## Input

User provides **job post URL** or pasted job text. If missing, ask once. **No rewrite until Phase 1 gate passes.**

$ARGUMENTS

---

## Phase 0 -- Load the candidate

1. Read `{{KIT}}/profile/candidate-notes.md`. It holds this candidate's personal rules: sources of truth, positioning, domain rules, voice, and hard rules. **Where it conflicts with this file, the candidate notes win.**
2. Read `{{KIT}}/profile/profile.json` for `name`, `standard_headline`, `upload_basename`, and contact links.
3. If `profile/base-resume.md` is missing, or still contains the example candidate "Jane Doe", stop and tell the user to fill in their profile (see the kit README) before continuing.

---

## Phase 1 -- Job + company research + tailored resume markdown

### Step 1: Lock inputs

1. **Job post** -- `WebFetch` on the URL; fall back to pasted text if fetch fails or content is gated. **Archive it**: save the full job text to `{{KIT}}/applications/<slug>/job-post.md` (postings get taken down; needed for interview prep and follow-ups).
2. **Base resume** -- read the master resume `{{KIT}}/profile/base-resume.md` (content source of truth). Read the **bullet bank** comments too: lines like `<!-- - Built a design system... -->` under a role are real, verified wins kept off the default cut for space. They are valid source material, selectable like any other bullet when the role calls for them. If the candidate also keeps `.docx` resumes, extract their text with:

```bash
python3 "{{KIT}}/scripts/docx_text.py" path/to/resume.docx
```

3. **Pick base** -- if `profile/` holds more than one base (`base-resume.md` plus variants such as `base-resume-fullstack.md`), default to `base-resume.md` and switch only when the role's core matches a variant (for example, backend/API/infra is core). Say which and why.
4. **Portfolio context** -- if the candidate notes list a portfolio or project source, skim it for context on the work behind each bullet.

### Step 2: Deep company research

The job post is the spec; the company is the audience. Research before rewriting.

1. **Identify the real company.** Many posts are recruiter or aggregator listings ("our partner", "a stealth startup"). Resolve the actual employer: careers page, recruiter client list, domain vocabulary, funding/news. If anonymous, research the recruiter + named domain instead and say so.
2. **Fetch their own words.** `WebFetch` or `WebSearch` in priority order:
   - About / Mission -- what they build, who for, the problem they claim to own
   - Values / Culture / Careers -- how they describe good work and good people
   - Blog / Engineering blog / Changelog -- what they ship, tech choices, tone
   - Product / Docs / Pricing -- actual surfaces, workflows, domain terms, customer type
   - Recent news / funding / launches -- a specific, current hook (last 6-12 months)
3. **Post a Company Intelligence brief** in chat:

```
Company      | real name (or "anonymous, via <recruiter>")
Mission      | one sentence in their words
Product      | what it is + who uses it
Domain       | industry + real-world workflow they digitize
Values       | 3-5 phrases they actually use
Tone         | how they write (playful / academic / terse / mission-heavy)
Tech signals | stacks, AI usage, scale, from blog/docs/post
Why-them hook| one specific, current, verifiable detail (launch, value, blog claim)
Vocabulary   | 5-10 domain/product terms to mirror in resume + CL
```

4. **Feed it forward.** The brief drives: Summary positioning, Skills ordering, domain framing of bullets, cover letter's why-them paragraph. Never invent company facts; mark unknown fields `unknown`.

### Step 3: Parse the job post

Extract and label:

| Bucket           | What to pull                                        |
| ---------------- | --------------------------------------------------- |
| Role signals     | title, seniority, team size, ownership level        |
| Must-haves       | hard requirements (years, stack, domain)            |
| Nice-to-haves    | bonus skills                                        |
| Responsibilities | day-to-day verbs (build, own, optimize, mentor...)  |
| Keywords         | tools, frameworks, methods (for ATS + human scan)   |
| Hidden problem   | one sentence: the bottleneck they did not spell out |

### Step 4: Section-by-section gap analysis

Audit every resume section:

```
Section | Current | Job wants | Gap | Fix
```

Sections (match base resume order):

1. **Header** -- name; headline (`Role | Stack | Specialty`); location/relocation line; contact. Does headline mirror the job title and seniority?
2. **Summary** -- one positioning paragraph. Does it lead with their #1 problem + strongest proof?
3. **Skills** -- grouped by category. Reorder by job priority; add every must-have and nice-to-have the post names that the candidate genuinely has.
4. **Experience** -- every role, newest first. Per role: title fit, bullet order, metric presence, keyword coverage. For each bullet: does an HR skim show this candidate already solved a problem this team has?
5. **Education** -- optional, see below. If kept, one line.
6. **Honors & Awards** -- optional, see below. If kept, only entries that reinforce the role.

**Education and Honors & Awards are not mandatory sections.** Both default to **omitted**. Include a section only when the job post gives a reason to:

| Include **Education** when | Include **Honors & Awards** when |
| -------------------------- | -------------------------------- |
| The post names a degree requirement or preference ("BS in CS or equivalent", "degree in a technical field") | An entry is direct evidence of a must-have (a published paper for an ML/research role, competitive programming for a post that tests algorithms) |
| The post is at a company or in a market that screens on credentials (consultancies, regulated industries, visa-sponsoring employers, graduate or new-grad programs) | The post names the exact thing the award proves (publications, open source, competition results, speaking) |
| The application form or ATS requires an education field | The company's own research signals they value it (research-heavy engineering blog, academic founders) |
| The candidate's degree is the only proof of a domain the post needs | The honor is recent and prestigious enough to be a differentiator on its own |

If none of the triggers fire, cut the section entirely. Do not keep a stub, a heading with one thin line under it, or `Education` purely out of habit. Space on page one is the scarcest resource on a resume: an experience bullet that answers the post's pain always outranks a degree the post never asked about.

Say in the change log which of the two were kept or cut and which trigger fired. When both are cut, check whether the resume now fits on one page and say so.

Gap types: `missing keyword`, `weak framing`, `wrong emphasis`, `missing skill`, `missing experience`, `untranslated experience`, `missing impact`, `missing metric`

Post gap table with priorities: `fix now (reframe)` / `ask user (real gap)` / `nice to have` / `already covered`.

### Step 5: Rewrite rules (non-negotiable)

**Truthful framing:**
- Never invent experience, skills, employers, scope, or metrics. Every claim must trace to the base resume, a source listed in the candidate notes, or a fact the user has confirmed in chat.
- Tailor by selection and framing, not invention: reorder bullets, translate real work into the job's vocabulary, emphasize the most relevant real wins, cut the rest.
- If the role requires something the base resume lacks, surface the closest adjacent real experience and frame it honestly. List anything still uncovered in the gap report and ask the user whether they have unlisted experience there; do not write the bullet without their answer.
- Metrics come only from the base resume (including bullet bank comments) or the user. Rounding or restating a real number is fine; inventing one is not.

**Domain rules:**
- Apply every domain rule in the candidate notes (for example, how to lead bullets for health tech or fintech posts, and which acronyms to spell out). Domain vocabulary that does not match the target post reads as noise; keep it off resumes for other domains.

**Header:**
- **Use the posting's exact job title verbatim in the headline** whenever it truthfully describes the candidate's level: 55% of recruiters search by title and ATS ranks title matches heavily. "Frontend Engineer II" in the post means "Frontend Engineer II" in the headline, not "Senior Frontend Engineer". If the exact title would overstate or understate the candidate, use the closest truthful variant.
- Headline formula: `Exact Job Title | Stack | Specialty`.
- If the tailored headline diverges from `standard_headline` in `profile.json`, tell the user in chat so they can weigh resume-vs-LinkedIn consistency. Never access LinkedIn to check.

**Summary:**
- The Summary must feel naturally aligned with the company's mission, values, and priorities, but **never copy-paste phrases from the job post or company site**. Internalize what they care about and write an original summary that makes the reader think "this person already thinks the way we do."
- Lead with their #1 problem + strongest proof.
- Assume an LLM screener will summarize this resume for the recruiter: write the Summary as the fit-thesis you want that summary to repeat, mapping plainly to the posting's top 3 requirements.

**Skills:**
- **Group by category** with each category on its own line (e.g. `Frontend: react, next.js, typescript`). Ordered by relevance to the role.
- **One line per group in the exported PDF, non-negotiable.** A skills group must never wrap to a second line. A wrapped group leaves an orphaned fragment sitting alone under a dense block, which reads as overflow and kills the scannability the grouping exists to create.
  - Budget the whole line, label included, at **110-120 characters**. The observed wrap point is ~126 characters, but the category label renders bold and therefore wider than its character count suggests, so the exact threshold shifts with how long the label is. Treat 120 as the ceiling and never ship a group you have not seen rendered.
  - Verify in the same print-width screenshot as the bullet wrap check (Phase 2 QA). Check skills groups and bullets in one pass.
  - When a group is over budget, fix it in this order: cut the item the job post never names; collapse a parenthetical to one example (`agentic coding (claude code, cursor)` to `agentic coding (claude code)`); drop a generic umbrella term that a concrete sibling already implies (`api-first design` when `rest apis` is present). **Splitting into two groups is the last resort**, since it costs a whole line on a page where an experience bullet is worth more.
  - Never shrink a group by deleting a must-have keyword from the post. If the only way to fit is dropping a required term, move that term into an experience bullet instead and cut a different skill from the line.
- Add or remove groups based on the job post (omit DevOps if pure frontend, add Design if relevant).
- **Skills must be specific tools and technologies, never vague terms.** Replace generic labels with concrete tools (e.g. "testing" -> "jest, playwright", "observability" -> "sentry", "product analytics" -> "posthog", "ci/cd" -> "github actions", "cloud deployment" -> "aws"). Pull tool names from the job post or company research first, and only list tools the candidate has actually used.
- **Copy must-have phrases verbatim.** Many ATS filters match literally: if the post says "cross-functional collaboration", that exact string must appear somewhere (skills line or bullet), not a synonym. Spell out full technology names, adding the acronym once when the post uses both forms (e.g. "Server-Side Rendering (SSR)", "PostgreSQL" not "Postgres").

**Experience:**
- **Frameworks:** bullet structure is **XYZ** (result first, measured, one line: accomplished X, measured by Y, by doing Z). Bullet selection and ordering per role is **CAR** (lead with the challenge this employer recognizes; the bullet whose problem matches the job post's pain goes first). STAR stays off the page: every bullet must have a full story behind it the candidate can expand in an interview.
- **Maximum 4 bullet points per role**, choosing only the most relevant to the target job.
- Reorder bullets so the most relevant win is first per role.
- Every bullet: their problem + your action + scope + quantified outcome.
- **One line per bullet, non-negotiable.** Each bullet must fit a single line in the exported PDF: aim for 90-105 characters. Lead with the metric, keep the mechanism to a short phrase, and cut implementation detail that does not sell (an HR reader needs the what and the result, not the how).
- **Bold what matters with `**`**: metrics and ranges (`**12s to 380ms**`, `**48%**`) and the 1-2 key technologies or standards (`**SSE**`, `**WCAG 2.2 AA**`). 2-4 bolds per bullet, never whole clauses; a bullet that is mostly bold highlights nothing.
- Plain words over jargon: "screens" not "surfaces", "time to first response" not "TTFT". A recruiter must understand every bullet without engineering context.
- Lead with their pain -- open each bullet with the business or technical bottleneck the employer cares about, using their vocabulary.
- Cut or shrink bullets that do not serve this role.
- Do not copy bullets verbatim when the job names different pains. Rewrite each so HR reads: same problem, already handled.

**General:**
- Keep `[View Project]` / `[Youtube]` style link tokens at the end of a bullet in the `.md` as usual; the exporter moves them onto the company line, right-aligned opposite the company name. Labels resolve through `profile.json` (`link_labels`, `company_projects`).
- One page unless the post explicitly asks for a longer CV. If the resume runs a few lines onto page two, cutting Education and Honors & Awards (see Step 4) is the first lever to reach, before shortening a bullet that is doing real work.
- No em dashes in written content.
- No filler: passionate, excited, synergy, results-driven.
- Keep the markdown shape of the base resume (`# Name`, bold headline, `## Section` headings, `### Job Title`, `**Company**, Location | Dates`, `- ` bullets). The exporter parses that shape. HTML comments must each sit on a single line.

**Page break rule (for two-page resumes):**
- After export, check the PDF. If an experience role is split across a page break (starts at the bottom of page one and continues on page two), push that role so it starts cleanly at the top of page two. No role should be orphaned across pages.
- A section heading alone at the foot of page one, with its content on page two, is the same defect. Either pull the whole section up or push the heading down; never leave `EDUCATION` or `HONORS & AWARDS` stranded from what it labels. `qa.py` prints where page 1 ends and page 2 starts, since a single tall screenshot will not show where the break lands.

### Step 6: Save resume

Save to: `{{KIT}}/applications/<slug>/resume.md`

File header:

```
<!-- Base: profile/base-resume.md -->
<!-- Job: [title] @ [company] -->
<!-- Hidden problem: [one sentence] -->
```

### Step 7: Post change log

Bullet list: what moved, what was cut, what was reframed (and from which base bullet), which job problems each experience bullet maps to, and confirmation that every number traces to the base resume or a user-confirmed fact.

**Gate:** `resume.md` saved with header comments + gap report + change log posted -> then Phase 2.

---

## Phase 2 -- Resume export

Run export automatically (do not tell the user to run it manually). From any directory:

```bash
python3 "{{KIT}}/scripts/md_export.py" "{{KIT}}/applications/<slug>/resume.md"
```

Add `--template <path.docx>` only if the candidate notes name a custom DOCX template.

Then run QA:

```bash
python3 "{{KIT}}/scripts/qa.py" "{{KIT}}/applications/<slug>/resume.md"
```

It does three checks. Act on each:

1. **Parse QA** -- extracts the `.docx` text and verifies the candidate's name, every contact, every job title, and every date range survive parsing. A failure means the export is broken; fix before continuing.
2. **Page check** -- page count, plus where page 1 ends and page 2 starts (needs `pypdf`; if it reports "skipped", say so and rely on the screenshot). Apply the page break rule from Phase 1 Step 5.
3. **Line-wrap check** -- writes `resume-wrap-check.png` beside the resume: the `.html` rendered at A4 print width. **Read the screenshot.** Any bullet on two lines gets shortened and re-exported until every bullet is one line. Any skills group that wraps gets trimmed to 110-120 characters using the fix order in Step 5. A trailing fragment alone on its own line is the tell to look for.

Re-run export + QA after every fix.

**Upload-ready copy** -- recruiters and parsers prefer `Firstname-Lastname-Resume.pdf`, and the slug filename leaks the tailoring workflow. Copy the exports to `{{KIT}}/applications/<slug>/upload/<upload_basename>.pdf` and `.docx`, using `upload_basename` from `profile.json`. These are the files the user actually submits.

**Gate:** `.docx` and `.pdf` exist beside the `.md`, QA passed, upload copies created -> then Phase 3.

---

## Phase 3 -- Cover letter

### Skills to invoke

Phase 3 runs three skills (bundled with this kit) as a pipeline. Each has one job. Do not let them overlap, and do not reimplement them.

| Step | Skill | Use it for | Ignore its |
| ---- | ----- | ---------- | ---------- |
| 1. Strategy | `cover-letter-generator` | Hook type selection (5 types below), gap handling, startup-vs-enterprise tone calibration | template, output format, closing advice |
| 2. Draft | `cover-letter` | Quantification table ("Managed a team" -> "Led 12-person team across 3 time zones"), value-proposition framing | template, openers, closers, header block |
| 3. Scrub | `clarity` | The authenticity pass, in **rewrite** mode: `references/edit.md` (diagnoses + rewrite check) and the Email/Marketing rows of `references/medium.md` | interview/co-write mode, `references/longform.md`, provenance note, "search aid, not a ban" leniency |

If a skill is not available in this session, read its `SKILL.md` directly from `{{KIT}}/skills/<name>/SKILL.md`.

**Precedence: this file wins every conflict** (and the candidate notes win over this file). All three skills are generic, written for a general audience. Steps 1 and 2 are scaffolding only.

**Three template skills pull toward the average.** Stacking them makes letters more generic, not less. The authenticity comes from Step 3 plus the Authenticity rules section below, not from more scaffolding. If a skill's suggestion is more generic than what you already have, discard it.

### Skill overrides (non-negotiable)

| Skill says | This file says | Winner |
| ---------- | -------------- | ------ |
| `cover-letter`: open with "I am excited to apply for the [Position] role at [Company]" | Kill that opener; "excited" is a banned word | this file |
| `cover-letter`: close with "I look forward to speaking with you" | That is filler; use a specific next step | this file |
| `cover-letter`: "Express enthusiasm for next steps" | No enthusiasm language anywhere | this file |
| `cover-letter`: header block with name, email, phone, LinkedIn, city | Date + hiring team + company only | this file |
| `cover-letter`: `## Key Points Highlighted` / `## Customization Notes` output wrapper | Plain text only, no headers | this file |
| `cover-letter`: examples use em dashes and "passionate", "resonates deeply" | No em dashes, no filler words, ever | this file |
| `cover-letter`: length options 250 / 350 / 450 words | 250-350 words | this file |
| `cover-letter`: "Cannot access actual job postings" | Phase 1 already fetched and archived it; pass it in | this file |
| `cover-letter-generator`: template opens with contact info block (name, email, phone, LinkedIn, city) | Date + hiring team + company only | this file |
| `cover-letter-generator`: closing should "express genuine enthusiasm" and "thank them" | Specific next step. No enthusiasm language, no thanks-for-your-time | this file |
| `cover-letter-generator`: hook examples use "I was excited to see", "I'm excited about" | "excited" is banned. Use the hook types, not the sample wording | this file |
| `cover-letter-generator`: output `# COVER LETTER FOR...`, `## Analysis Summary`, `## Alternative Openings`, `## Key Talking Points` | Saved file is plain text only, no headers. Alternative openings may be offered in chat, never in the file | this file |
| `cover-letter-generator`: 250-400 words | 250-350 words | this file |
| `cover-letter-generator`: ✅/❌ emoji in checklists | Never in output | this file |
| `clarity`: "unnecessary bold" is surface residue | Cover letter is plain text anyway. Never run this skill on the resume `.md`, where bold on metrics is required | this file |
| `clarity`: watch-lists are "a search aid, not a ban" | In the cover letter the banned words and em dashes below are hard bans, no context exception | this file |
| `clarity`: leave `[TK: question]` where only the author knows the answer | No `[TK]` reaches the saved file. Ask the user in chat, or cut the sentence | this file |
| `clarity`: "If the draft is hollow... offer the interview" | Don't start an interview. Name the missing anchor and ask one targeted question in chat | this file |
| `clarity`: `prose_stats.py` lint | Optional diagnostic. Do not print its output in chat | this file |

### Structure: Problem-Solution format (3-4 paragraphs)

```
[Date]

[Hiring Manager Name or "Engineering Hiring Team"]
[Company Name]

Dear [Name / Hiring Manager],

PARAGRAPH 1 -- ANCHOR WIN (50-75 words)
Lead with your single strongest proof point that maps to their
#1 requirement. Open with the result or the pain you solved,
not "I am writing to apply." One specific achievement with a
metric. End by connecting it to this role or company.

PARAGRAPH 2 -- EVIDENCE STACK (75-100 words)
Two or three more proof points, each matching a different job
requirement. Pattern: their problem -> your action -> quantified
result. Show range (technical depth + collaboration, scale +
craft). Mirror language from the job post and company content.

PARAGRAPH 3 -- WHY THIS COMPANY (50-75 words)
One specific, verifiable detail from your company research
(a recent launch, an engineering blog post, a value stated
in their own words). Connect it to how you work or what you
care about. No generic flattery. This paragraph proves you
chose THEM, not just any open role.

PARAGRAPH 4 -- CLOSE (25-40 words)
Specific next step. Reference portfolio/GitHub if relevant.
No "I look forward to hearing from you" filler.

[Sign-off],
[Your Name]
```

### Inputs
- Job post + tailored resume from Phase 1 + Company Intelligence brief + candidate notes (cover letter voice)
- Lead proof with the job's top requirement

### Tailoring
- Rewrite hook, reorder proof, mirror post keywords
- Build "why them" paragraph from the brief: cite one specific, verifiable detail and match their tone
- No generic flattery; never invent company facts

### Format (non-negotiable)
- Plain text only -- no headers, bold, links, emojis, or horizontal rules
- Metrics and URLs inline (e.g. 25%, the candidate's site and GitHub from `profile.json`)
- 250-350 words, 3-4 paragraphs, no em dashes
- Tone: technically confident, matched to the company's tone from the intelligence brief. Humor (max one light dev-relevant joke per paragraph) only when the brief shows a playful or informal voice; at formal companies, warm and direct instead
- No: passionate, excited, thrilled, synergy, results-driven

### Kill these openers
- "I am writing to apply for..."
- "I believe I would be a great fit..."
- "I'm a hard worker / team player"
- Starting with career journey or education

### What works instead
- Lead with a result + metric
- Lead with their pain matched to your experience
- Lead with a specific connection (referral, project similarity)

### Hook types (pick one, from `cover-letter-generator`)

Name the type you chose in the change log so the next letter does not reuse it.

| Type | Use when | Opens with |
| ---- | -------- | ---------- |
| Problem-Solver | The post names a pain you have already fixed. **Default for engineering roles** | The bottleneck, then your fix |
| Impressive Achievement | Your strongest metric outclasses the requirement | The number |
| Specific Company Knowledge | Research surfaced a launch, blog post, or public stack detail | Their thing, then your relevance |
| Industry Insight | You can say something true and non-obvious about their market | The observation |
| Mutual Connection | There is a real referral. Never fabricate one | The name |

**Do not start any sentence with "I"** where it can be avoided, especially the first sentence of a paragraph. Open with the problem, the number, or the company. "Taking p75 INP from 620ms to 140ms meant..." beats "I took p75 INP...".

### Gap handling (from `cover-letter-generator`)

Phase 1 Step 4 already produced the gap list. Rules for the letter:

- **Never apologize and never flag a gap the post did not ask about.** Naming an unasked gap creates a doubt that was not there.
- If the post names a **preferred** qualification the candidate lacks, do not mention it. Let the adjacent real experience do the work.
- If the post names a **required** qualification the candidate lacks, address it in one clause inside Paragraph 2, then immediately pivot to the transferable proof. Never a standalone sentence, never a standalone paragraph.
- Only claim a gap is being closed if the candidate confirmed it in chat. No "currently learning X" unless it is true.

### Authenticity rules (the point of the whole phase)

A letter reads human when it contains things a language model could not have guessed. Scaffolding cannot supply this; only the archived job post, the intelligence brief, and the base resume can.

**Every letter must contain at least two of these:**

- A number that appears nowhere in the job post and could only come from this candidate's work
- A specific, verifiable company detail from research: a named launch, a public stack choice, a community they run, a phrase from their own site
- A concrete noun from the candidate's actual work: "10,000-row scheduling grid", "chart PDF viewer", "flow cytometry workspace". Not "a complex data-heavy interface"
- An honest limit or preference stated plainly, where it is true and not disqualifying

**Rhythm.** Vary sentence length deliberately. One short sentence under 8 words per paragraph. If three consecutive sentences have similar length, break one.

**Register.** Match the intelligence brief's tone reading. Formal and mission-heavy company means warm and direct, no jokes. Playful company allows at most one light dev-relevant joke per paragraph. When unsure, warm and direct.

**The specificity test.** Read each sentence and ask: could this appear in a letter to a different company with the name swapped? If yes, it is filler. Cut it or make it specific.

### AI-tell scrub (final pass before saving)

Generic content, not AI use, is what gets letters rejected (62% of managers reject AI-flavored letters lacking personalization).

**Run `clarity` in rewrite mode over the drafted letter body**, then verify by hand. Register: Message (Email row of `references/medium.md`): the reader is a hiring manager, the outcome is a reply. Scope: the cover letter only. Never run it on the resume `.md` -- it strips bold, and Phase 1 Step 5 requires bold on every metric.

The `clarity` diagnoses (`references/edit.md`) that hit cover letters hardest:

| Diagnosis | Cover-letter form | Fix |
| --------- | ----------------- | --- |
| Importance without mechanism | "played a pivotal role in a transformative migration" | Name the actor, the mechanism, and the number from the resume |
| Specific-looking vagueness | "I once fixed a major performance issue" | Which page, which metric, what changed. If the resume doesn't say, ask; never fill it in |
| Formula carrying the argument | "This isn't just X, it's Y" / "innovation, inspiration, and industry insight" | Flatten test: state it without the cadence. If nothing specific remains, cut it |
| Prestige vocabulary | delve, leverage, robust, seamless, "furthermore", "crucial" | Rewrite the claim; don't swap in a synonym |
| Structural regularity | Every paragraph ends on a quotable zinger | Stop each paragraph on its last concrete fact |
| Generic ending | "excited for what's ahead" | Close with a concrete next step |

Plus this file's hard rule, which `clarity` does not cover: zero em dashes.

Also check by hand:

- Ban AI-vocabulary: delve, leverage, spearheaded, testament, tapestry, robust, seamless, "I am excited", "aligns with my values"
- Vary sentence lengths; uniform rhythm reads machine-made
- Verify at least two details that could only come from this candidate about this company: one real, defensible win and one verifiable company fact from the intelligence brief
- Grep the saved file to confirm: `grep -nE "delve|leverage|spearhead|testament|tapestry|robust|seamless|passionate|excited|thrilled|synergy|results-driven|—" cover-letter.md`

### Save to
`{{KIT}}/applications/<slug>/cover-letter.md`

**Do not** export the cover letter to docx/pdf unless the user asks. If they do:

```bash
python3 "{{KIT}}/scripts/md_export.py" "{{KIT}}/applications/<slug>/cover-letter.md" --cover
```

(The cover export expects `# Name`, a bold headline line, `---`, then the letter body.)

### Log the application

Append one row to `{{KIT}}/applications/applications-log.md` (create it with a table header `| Date | Company | Role | Slug | Job URL |` if missing):

`| YYYY-MM-DD | Company | Role | <slug> | job URL |`

**Gate:** `cover-letter.md` saved + log row appended -> then Phase 4.

---

## Phase 4 -- Post-apply outreach message

A LinkedIn DM to the person the role reports to, sent **after** applying. This format has converted for real applications. It is not a cover letter and not a 3-sentence cold DM. Do not substitute either.

### Who it goes to

The reporting manager named in the post ("You'll report to our Head of Engineering"). If the post names no one, address the most senior engineering leader the research surfaced.

**Never access LinkedIn to find the name** -- that is a standing hard rule, no exceptions, including "just to check the spelling". Try non-LinkedIn sources once (company About/Team page, Crunchbase, Built In, press coverage, conference talks). If the name is not public off-platform, leave `[Name]` in the draft and tell the user to fill it in. Say which sources were checked so they know it was not guesswork.

### Structure

```
Hi <Name>,

<OPENER>

<BOLD HEADER 1>:
One sentence, 100-115 characters. At least one hard metric.

<BOLD HEADER 2>:
One sentence, 100-115 characters. At least one hard metric.

<BOLD HEADER 3>:
<BOLD HEADER 4>:
<BOLD HEADER 5>:

<CLOSER>
```

`<OPENER>` and `<CLOSER>` come verbatim from the "Outreach voice" section of the candidate notes. If the notes have none, use these defaults:

- Opener: `I have applied at <Company> for the position of <exact job title>. I think I'm a strong match for this role.`
- Closer: `I've applied for the role and wanted to reach out to you personally, as I'm really excited about it.`

### Rules

- **Five blocks, chosen per role.** Derive the headers from the job post's must-haves, in the post's own priority order. Never reuse a previous application's headers by default. The last block is usually the candidate's strongest positioning (see the candidate notes).
- **One sentence per block, one hard metric minimum**, 100-115 characters. Every number must already appear in the tailored `resume.md`. No new claims here. See the length limit below: the whole message stays under 900 characters.
- **Name a gap inside its matching block** when the post marks that skill *ideal* or *preferred* rather than required: "Temporal is new to me, but the stateful multi-step job behind record retrieval isn't." Volunteering it reads as confidence and makes the rest more credible. Omit the gap when the post lists it as a hard requirement.
- **Keep the candidate's voice.** The opener and closer stay verbatim. The Phase 3 banned-word list (including "excited") **does not apply to this phase** -- that rule governs the cover letter. This wording converted; do not improve it.
- Links are optional. Include a portfolio link under a block only when it is direct proof of that block's claim, and only if the user wants links.
- No em dashes.
- Contractions are good here ("isn't", "I'd"). This should read faster and looser than the cover letter.

### Bold headers

Headers use Unicode mathematical bold. **Generate them, never hand-type them** -- transcribing the codepoints by hand produces broken glyphs:

```bash
python3 "{{KIT}}/scripts/outreach.py" bold "Design Systems"
```

Unicode bold is fine in a LinkedIn message box. Warn the user not to reuse these headers in email: screen readers announce the characters individually and some relays strip them to boxes.

### InMail subject lines

An InMail needs a subject; a connection DM does not. **Always produce three**, mark one recommended, and let the user pick. Build every one from the archived job post, never from a previous application.

**Formula:**

```
<differentiator from the post's #1 ask> + <role title as the post names it>
+ with <2-3 TECHNOLOGIES IN CAPS> experience + wants to join <Company | your team>
```

Examples (character counts shown; the 120 ceiling below is the reason one of them needs compressing):

- 90 -- `Performance-obsessed Web Developer with REACT & NEXT.JS experience wants to join your team`
- 65 -- `Next/React dev with healthtech experience wants to join Northwind`
- 121, **over the ceiling** -- `Frontend Software Engineer who goes beyond UI components, with NEXT.JS, REACT & TYPESCRIPT experience, wants to join Acme`
  - 109, compressed by dropping the third technology -- `Frontend Software Engineer who goes beyond UI components, with NEXT.JS & REACT experience, wants to join Acme`

**Rules:**

- **Third person, candidate as the grammatical subject.** It reads as a headline, not a request. Never "I am applying for" or a question.
- **Slot 1 is the whole trick.** Pull the differentiator from the single hardest thing the post asks for: the responsibility most applicants will ignore ("goes beyond UI components"), an obsession the post names ("Performance-obsessed"), or a domain match the post needs ("healthtech experience"). A generic adjective wastes the slot.
- **One differentiator, never two stacked.** If two are tempting, that is what the second and third options are for.
- **Stack in caps, 2-3 technologies, taken from the post.** Caps is what the eye catches in a crowded inbox. Pick the ones the post names first; a named nice-to-have (STORYBOOK, PLAYWRIGHT) beats a generic one when it is the post's own differentiator.
- **Role title verbatim from the post**, or the closest truthful variant, same rule as the resume headline.
- **Close with the company name** when it is public; `your team` only when the employer is anonymous or it is a recruiter listing.
- **Maximum 120 characters. Hard ceiling, target 95-110 so there is margin.** LinkedIn allows 200, but the preview truncates well before that, so front-load the differentiator. Anything over 120 gets compressed, never offered. Compress in this order: drop the third technology (2 in caps is fine), shorten the differentiator, then replace the company name with `your team`. Never cut the role title.
- **Count the subject text and nothing else**, from the first letter of the differentiator to the last letter of the company name. No label, no prefix, no quotes, no `//`. Measure with code, never by eye.
- **Store each subject alone on its own line in the outreach file, with no comment prefix**, so the stored line length IS the subject length and the user can copy the bare line. Put the label and count on the preceding `//` line:
  ```
  // RECOMMENDED (108 characters):
  Product Engineer who makes users actually trust AI, with REACT & NODE.JS experience, wants to join Northwind
  ```
  Never write `// InMail subject (105 ch): <subject>` on one line. A 28-character prefix turns a compliant 108-character subject into a 136-character line, and anyone measuring that line reads it as over the ceiling.
- Make the three options structurally distinct: one on the post's #1 responsibility, one on the candidate's strongest obsession or craft angle, one on the domain or positioning angle.

### Length limit: under 900 characters

**The whole message must come in under 900 characters.** This is a hard ceiling, not a target to drift past. A wall of text in an InMail preview does not get opened, and the five-block structure only reads as scannable when each block is one tight line.

The scaffolding is fixed at roughly 230 characters (greeting, opener, closer), which leaves about 670 for the five blocks. Budget per block:

| Part | Budget |
| ---- | ------ |
| Bold header | 2-3 words, around 18 characters |
| Body | **one sentence**, 100-115 characters, carrying the metric |
| Block total | around 135 characters |

Write to that budget on the first pass. Do not draft long and trim; the structure survives compression badly when it is an afterthought.

If the count exceeds 900, compress in this order and say what was cut:

1. Shorten the bold headers.
2. Cut filler from the body sentences: "An earlier 45-component system" becomes "A 45-component system", "to unblock a $1.2M enterprise contract" becomes "to unblock a $1.2M contract".
3. Drop the second half of a gap mention, keeping one named gap.

Never drop a block, the opener, or the closer: that structure is the format. If the user asks for a tighter budget than 900, apply the same order; if they explicitly ask for the long two-sentences-per-block version, give it and say it will not fit an InMail preview.

### Save to

`{{KIT}}/applications/<slug>/outreach.txt`, with a header comment block:

```
// Target: <name or role>, <company> (reporting manager, <job title>)
// Format: applied-first outreach template, 5 requirement blocks
// Name status: <filled in | left as [Name], sources checked: ...>
// InMail subjects. Each sits ALONE on its own line below, with no comment prefix, so the
// line length IS the subject length. Copy the bare line, never the "//" label above it.
//
// RECOMMENDED (<n> characters):
<option 1>
// ALT 1 (<n> characters):
<option 2>
// ALT 2 (<n> characters):
<option 3>
//
// Length: <n> characters
// ---
<the message>
```

**Verify before delivering:**

```bash
python3 "{{KIT}}/scripts/outreach.py" check "{{KIT}}/applications/<slug>/outreach.txt"
```

It measures every bare subject line (must be <= 120) and the message below `// ---` in codepoints (what LinkedIn counts, must be < 900) and UTF-8 bytes (each bold header character is 4 bytes, so a byte-counting field reads roughly 20% longer). Report both counts to the user. Fix and re-check until it passes.

Print the message to chat as well, so the user can copy it without opening the file.

**Gate:** `outreach.txt` saved, check passed, message printed -> then deliver.

---

## Phase 5 (on request) -- Interview prep

When the user asks for interview prep for this application, expand each tailored experience bullet into its full STAR story (Situation, Task, Action, Result, with the real numbers behind the bullet) in `{{KIT}}/applications/<slug>/interview-prep.md`. Use the archived job post to anticipate likely questions. Flag any bullet the candidate may struggle to defend so they rehearse it first.

---

## Deliverable

1. Company Intelligence brief -- table of mission, product, values, tone, tech signals, why-them hook, vocabulary
2. Gap report -- table + `fix now` / `nice to have` / `already covered`
3. Change log -- moved, cut, reframed; bullet-to-job-problem mapping; metric traceability
4. Resume outputs -- `applications/<slug>/resume.md`, `.docx`, `.pdf`, plus upload-ready `upload/<upload_basename>.pdf` and `.docx`
5. Cover letter -- `applications/<slug>/cover-letter.md`; job post archived at `job-post.md`; row appended to `applications/applications-log.md`
6. Post-apply outreach message -- `applications/<slug>/outreach.txt`, printed to chat, with three InMail subject lines (one marked recommended)
7. Quality checklist (all boxes checked or gaps called out):
   - [ ] Candidate notes read and applied; any conflict resolved in their favor
   - [ ] Company Intelligence brief posted; Summary + Skills aligned with their mission/values (no copy-paste, no generic startup-speak)
   - [ ] Every must-have and nice-to-have the candidate genuinely covers appears in Skills (as concrete tools) and is backed by an experience bullet; real gaps are listed, not papered over
   - [ ] Summary names their problem and positions the candidate as someone who already solved it
   - [ ] Top 3 job responsibilities each have a dedicated, quantified experience bullet
   - [ ] Experience bullets lead with employer pain; HR reads "perfect match"
   - [ ] Every bullet has impact: a number, percentage, or concrete scope
   - [ ] Every claim traces to the base resume, a listed source, or a user-confirmed fact; no invented experience or metrics
   - [ ] Skills grouped by category, only concrete tools, and every group confirmed on a single line in the exported PDF (no wrapped group, no orphaned trailing fragment)
   - [ ] Max 4 bullets per experience role
   - [ ] Education and Honors & Awards included only on a trigger from the job post, kept or cut decision stated in the change log; no stranded section heading in the exported PDF
   - [ ] Every bullet is a single line in the exported PDF (wrap check passed), with metrics and 1-2 key technologies bolded
   - [ ] Headline uses the posting's exact job title (or closest truthful variant, divergence from `standard_headline` flagged to the user)
   - [ ] Must-have phrases appear verbatim; technology names spelled out in full
   - [ ] `qa.py` parse QA passed; upload-ready `<upload_basename>.pdf` / `.docx` created
   - [ ] Job post archived; applications log appended
   - [ ] Cover letter ran the full pipeline: `cover-letter-generator` (strategy) -> `cover-letter` (draft) -> `clarity` (scrub, rewrite mode)
   - [ ] `clarity` was run on the cover letter only, never on the resume `.md`
   - [ ] Hook type named in the change log; no sentence opens with "I" where avoidable
   - [ ] At least two authenticity anchors present (candidate-only number, verifiable company detail, concrete noun, honest limit)
   - [ ] Specificity test passed: no sentence survives a company-name swap
   - [ ] No unasked gap was volunteered; any required-gap mention is one clause inside Paragraph 2
   - [ ] No filler, no em dashes
   - [ ] Outreach message saved to `applications/<slug>/outreach.txt` and printed to chat
   - [ ] Its five block headers derive from this post's must-haves, not a previous application's
   - [ ] Every outreach metric already appears in the tailored `resume.md`; no new claims
   - [ ] `outreach.py check` passed: message under 900 codepoints, every subject <= 120 characters; counts reported to the user
   - [ ] Bold headers generated by script, not hand-typed; email-reuse warning given
   - [ ] Three InMail subject lines offered, one recommended, each built from this post's own words via the Phase 4 formula; none reused from a previous application
   - [ ] Reporting manager's name filled in, or `[Name]` left with the non-LinkedIn sources checked named
   - [ ] LinkedIn was not accessed at any point, by any means

Do not commit unless asked.
