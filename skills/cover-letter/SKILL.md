---
# ═══════════════════════════════════════════════════════════════════════════════
# CLAUDE OFFICE SKILL - Enhanced Metadata v2.0
# ═══════════════════════════════════════════════════════════════════════════════

# Basic Information
name: cover-letter
description: ">"
version: "2.0.0"
author: Claude Office Skills Contributors
license: MIT

# Categorization
category: hr
tags:
  - cover-letter
  - job-application
  - writing
department: HR/Personal

# AI Model Compatibility
models:
  recommended:
    - claude-sonnet-4
    - claude-opus-4
  compatible:
    - claude-3-5-sonnet
    - gpt-4
    - gpt-4o

# MCP Tools Integration
mcp:
  server: office-mcp
  tools:
    - create_docx
    - docx_to_pdf

# Skill Capabilities
capabilities:
  - letter_writing
  - personalization
  - professional_tone

# Language Support
languages:
  - en
  - zh
---

# Cover Letter

## Why cover letters still matter

Cover letters are not dead. They are the first thing read 45% of the time (ResumeGenius, 625 hiring managers surveyed). 83% of hiring managers read most cover letters they receive, even when not required. But time is brutal: 36% spend under 30 seconds. An engaging one earns dramatically more: 60% spend 2+ minutes on letters that hook them early.

The stakes are binary. 49% of hiring managers say a strong cover letter can secure an interview for an otherwise weak candidate. 51% will reject strong candidates over a weak letter. A ResumeGo study found tailored cover letters received 53% more callbacks than untailored ones.

The single biggest factor: **customization**. 90% of cover letters are rejected due to lack of it. 78% of recruiters say they can easily distinguish generic from tailored submissions.

**Frame:** treat each cover letter like a short consulting proposal. You have researched their problem, you have relevant experience solving similar problems, and you are proposing an engagement. That frame naturally produces customization, specificity, and the right tone. Everything generic falls away.

---

## How to use

1. Share the job posting (URL or text)
2. Provide your resume or relevant experience
3. Mention any specific points to highlight (referral, unique angle)
4. The skill produces a tailored cover letter + key points mapping

When run via the portfolio workflow, the **Company Intelligence brief** from `frontend-job-research.mdc` Step 0.5 feeds the "why them" paragraph directly.

---

## Structure: the Problem-Solution format

The highest-performing cover letter structure, backed by meta-analysis of 80+ studies, is Problem-Solution. Stories are 22x more memorable than facts alone. This format forces specificity and positions you as a consultant solving their problem, not a supplicant asking for a job.

41% of hiring managers say the intro paragraph leaves the biggest impression.

```
[Date]

[Hiring Manager Name/Title or "Engineering Hiring Team"]
[Company Name]

Dear [Name / Hiring Manager],

PARAGRAPH 1 — ANCHOR WIN (50-75 words)
Lead with your single strongest proof point that maps to their
#1 requirement. Open with the result or the pain you solved,
not "I am writing to apply." One specific achievement with a
metric. End by connecting it to this role or company.

PARAGRAPH 2 — EVIDENCE STACK (75-100 words)
Two or three more proof points, each matching a different job
requirement. Pattern: their problem → your action → quantified
result. Show range (technical depth + collaboration, scale +
craft). Mirror language from the job post and company content.

PARAGRAPH 3 — WHY THIS COMPANY (50-75 words)
One specific, verifiable detail from your company research
(a recent launch, an engineering blog post, a value stated
in their own words). Connect it to how you work or what you
care about. No generic flattery. This paragraph proves you
chose THEM, not just any open role.

PARAGRAPH 4 — CLOSE (25-40 words)
Specific next step. Reference portfolio/GitHub if relevant.
No "I look forward to hearing from you" filler.

[Sign-off],
[Your Name]
```

**Word count:** 250-400 words total (half a page). 66% of job seekers and 49% of hiring managers prefer half-page or shorter.

**Paragraph count:** 3-4. Never exceed 4. If you can say it in 3, use 3.

---

## The opening line

The first sentence is the most-read sentence in the letter. Waste it and 36% of readers are already gone.

**Kill these openers:**
- "I am writing to apply for..." (the single most overused opening in existence)
- "I believe I would be a great fit..." (generic, tentative)
- "To Whom It May Concern" (signals laziness; 72% of hiring managers rate it negatively)
- "I'm a hard worker / team player / results-driven" (meaningless without evidence)
- Starting with your career journey or education

**What works instead:**
- Lead with a result: "Cutting build time from 45 minutes to 2 minutes on a 500K-page app taught me what frontend performance actually means at scale."
- Lead with their pain: "Your job posting describes my last two years: React interfaces for complex data workflows on Linux infrastructure."
- Lead with a specific connection: "[Referrer] suggested I reach out after I showed them the workflow manager I built at [Company]."
- Lead with a relevant anchor win + metric, then pivot to their role.

---

## The "why this company" paragraph

This paragraph separates serious candidates from mass-appliers. It must contain one specific, verifiable, recent detail that proves you chose THEM.

### Research methodology (15-20 minutes minimum per application)

When run via the portfolio workflow, pull the **Company Intelligence brief** (see `frontend-job-research.mdc` Step 0.5): fetch the company's About / Mission, Values / Culture, Blog / Engineering blog, and Product pages, plus recent news. For recruiter or "our partner" posts, resolve the real employer first; if it stays anonymous, research the named industry/domain and say so.

**Priority order for research:**
1. **Engineering blog / changelog / public repos** (strongest for tech roles: shows you understand their technical reality)
2. **Recent news, launches, funding** (last 6-12 months; proves timeliness)
3. **Product / docs / pricing** (shows you understand what they actually build)
4. **Values / culture page** (use their exact phrasing, not a paraphrase)
5. **About / mission** (weakest signal alone; strongest when combined with specifics)

### What to write

Connect a specific, current, verifiable detail to your own experience or values:

| Weak (generic flattery) | Strong (specific connection) |
|---|---|
| "I love your mission" | "Your move into [specific area] aligns with the work I did at [company] where I [result]" |
| "I admire your culture" | "Your engineering blog post on [topic] describes the exact tradeoff I navigated at [company]" |
| "I'm excited about your growth" | "Your recent [specific launch/funding/product] tells me the [workflows/systems] are getting more complex, and that's where I do my best work" |

**Never invent company facts.** If a page is missing or gated, say so or skip it. Generic flattery is worse than nothing.

---

## Tech and engineering roles

Software engineer cover letters operate differently. The 2025-2026 market is exceptionally competitive, with entry-level positions attracting 200+ applicants. Your letter must prove technical depth, not just describe it.

**Show, don't list.** Do not enumerate programming languages. Describe one specific project where you used those technologies to solve a real problem. Write like you are explaining a production change in code review: the problem, the tradeoff, your approach, the outcome.

**Link to proof strategically.** Reference GitHub or portfolio with specificity: "In [project], I built [specific thing] using [stack], which [quantified result]." Do not write "see my GitHub" as generic filler.

**Only claim what you can defend.** Do not list skills or tools you are not comfortable being interviewed on. The cover letter sets the interview agenda.

**Mirror their stack.** If the company uses React, TypeScript, and Docker (from their job post, repos, or engineering blog), name those exact tools in your letter. ATS scores this. Humans notice it.

**Show tradeoff thinking.** Engineering is about tradeoffs. Hiring managers want to know how you think through problems, not just that you solved them. "I chose [approach] over [alternative] because [reason]" reads as senior. "I used [tool]" reads as junior.

---

## ATS: what the system sees

Modern ATS platforms (Workday, Greenhouse, Lever) parse cover letters using NLP, not rigid keyword matching. Key findings:

- **ATS weights early content more heavily.** Lead with your strongest qualifications in paragraph 1, not paragraph 3.
- **Keyword stuffing is penalized.** Forced language patterns are detected. Natural keyword integration within narrative context performs better than isolated term placement.
- **Cover letters are secondary scoring signals.** A strong letter can boost a borderline resume score into the screening range, but cannot compensate for a weak resume.
- **Mention the company name and role title explicitly.** ATS systems recognize these and score applications higher.
- **Formatting matters technically.** Complex formatting, graphics, tables, headers/footers, and colored text can break ATS parsing. Stick to plain text structure, standard fonts, single column.

When the posting says "optional," submit one anyway. 72% of hiring managers still expect them when listed as optional. Submitting one when others skip it is a free edge.

---

## What kills cover letters

### Instant disqualifiers

- **Typos and formatting errors**: dealbreaker for 75%+ of hiring managers.
- **Wrong company name**: HR flags this immediately. The single fastest way to get rejected.
- **AI-generated content that sounds like AI**: 80% of hiring managers view it negatively. 74% claim they can detect it. If you use AI to draft, you must rewrite it until it sounds like a specific human, not a polished language model.

### Phrases to eliminate

| Dead phrase | Why it fails |
|---|---|
| "I am writing to apply for..." | Wastes the most-read sentence on zero information |
| "I'm a hard worker" / "team player" | Meaningless without evidence; everyone claims this |
| "I would be perfect for this role" | Arrogant without proof |
| "This position would help me grow" | Self-focused; they want to know what you contribute |
| "I think I would be a great fit" | Tentative language that undermines confidence |
| "passionate" / "excited" / "thrilled" | AI cliches; empty calories |
| "synergy" / "leverage" / "results-driven" | Corporate filler that signals nothing |

### The cardinal sin

Making the letter about your career journey and goals instead of solving their problems. Only 9% of recruiters want to learn about your motivation. They want to know what you will do for them.

### Resume repetition

The cover letter is not a prose version of your resume. Add new angles: why this company, how you think about the problem, what context the resume cannot convey. If someone could learn the same information from your resume, the sentence is wasted.

---

## Tone and voice

Write like you are emailing a respected colleague you like but do not know especially well. Not formal business correspondence. Not a text to a friend.

**Match the company's own tone.** If their job posting and website are casual, lean conversational. If they are a traditional institution, lean more formal. Read their actual content first.

**Confidence without arrogance:** State what you have done and can do, backed by evidence. Replace "I think I could contribute" (tentative) with "At [company], I [achieved X], and I would bring that same approach to [their challenge]" (confident and grounded).

**Humor is high-risk.** Unless you are certain the company culture embraces it (from their own content, blog, or social media) and your humor is self-aware and dev-relevant, avoid it. What seems funny to you might read as unprofessional.

**The AI voice trap:** The biggest tone risk right now is submitting something that sounds generically polished. Hiring managers are calibrated to detect this. Specific details, natural sentence rhythm, and genuine enthusiasm for particular aspects of the role are the antidotes.

**Read it aloud.** If it sounds like corporate jargon or a robot wrote it, rewrite it. It should sound like you would actually say this to a human.

---

## Quantify everything

Vague claims are invisible. Specific numbers are memorable.

| Vague | Specific |
|---|---|
| "Increased performance" | "Cut build time from 45 min to 2 min" |
| "Managed a team" | "Led 3-person squad across 2 time zones" |
| "Improved efficiency" | "Reduced data fetch latency 35% for 1,200+ accounts" |
| "Built features" | "Shipped PDF viewer with caching, cut load time 70%" |

Every proof point in the letter should have a number, a scope, or both. If the real number is unknown, ask the candidate; never invent one. A specific, true metric is best.

---

## Workflow integration

When called from the `generate-custom-resume` command (Phase 3), these inputs are available:

1. **Candidate notes:** `profile/candidate-notes.md` (voice, tone, extra rules)
2. **Job post:** archived in Phase 1 as `job-post.md`
3. **Tailored resume:** the Phase 1 rewrite (`resume.md`)
4. **Company Intelligence brief:** from Phase 1 Step 2

The command's own Phase 3 rules (format, length, banned words, save path) override everything in this skill.

---

## Output format

```markdown
## Cover Letter

**Position:** [Role]
**Company:** [Company]
**Tailored for:** [Specific aspects addressed]

---

[Full cover letter text]

---

## Requirement-to-proof mapping

| Job requirement | Proof point in letter |
|---|---|
| [Requirement 1] | [Which sentence addresses it + metric] |
| [Requirement 2] | [Which sentence addresses it + metric] |

## Customization notes

- [Any suggestions for further personalization]
- [Research gaps: what you could not verify]
```

---

## Example: tech role cover letter

**Input:** "Write a cover letter for a Senior Software Engineer role at Stripe. 6 years Python/Go, built payment systems, fintech domain."

**Output:**

Dear Hiring Manager,

Building payment infrastructure that processes $50M+ monthly taught me that the hard part is never the code. It is the trust. At [Current Company], I architected our core payment processing system in Python and Go, reducing transaction failures 40% and improving throughput from 1,000 to 10,000 transactions per second. That work required understanding financial regulations and user trust as deeply as the distributed systems underneath.

I led the integration with 4 payment providers and implemented fraud detection that prevented $2M in potential losses. When our compliance team flagged PCI scope creep, I redesigned our tokenization layer to isolate cardholder data, cutting our audit surface by 60%. I also mentored 2 junior engineers through their first production payment integrations, which meant teaching them to think about failure modes before happy paths.

What draws me to Stripe specifically is how your API design philosophy shows up in the developer experience. Your recent Connect platform expansion into 25 new markets tells me the payment orchestration complexity is growing, and orchestration under regulatory constraints is exactly where I have spent the last 3 years. I want to build infrastructure that millions of businesses depend on, alongside engineers who treat API ergonomics as a first-class concern.

I would love to discuss how my payment systems experience and approach to trust-critical infrastructure can contribute at Stripe. My work is at github.com/[handle].

Best regards,
[Your Name]

---

**Requirement-to-proof mapping:**

| Job requirement | Proof point |
|---|---|
| Python/Go systems | Payment system architecture, Python + Go, $50M+ throughput |
| Scale and reliability | 1K to 10K TPS, 40% failure reduction |
| Security/compliance | PCI tokenization redesign, 60% audit surface reduction |
| Payment domain | 4 provider integrations, $2M fraud prevention |
| Mentorship/seniority | 2 junior engineers mentored on production payments |
| Why Stripe | Connect platform expansion, API design philosophy, regulatory orchestration |
