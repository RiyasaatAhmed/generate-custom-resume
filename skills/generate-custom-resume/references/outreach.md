# Outreach

Choose the channel and reader before drafting. Produce the requested format, not a
bundle of every possible message. Prefer the named hiring contact or relevant team
leader over the highest executive. If identity is uncertain, record the sources checked
and leave a draft placeholder. Never invent a referral, relationship, address, or name.
Respect the candidate's no-LinkedIn-access preference when present.

| Channel | Purpose | Useful content |
| --- | --- | --- |
| connection | Establish a relevant connection | Context and one reason to connect |
| recruiter | Make fit and logistics easy to evaluate | Role/requisition, relevant experience, accurate availability, one question |
| hiring-manager | Show relevant problem-solving | Employer priority, one supported achievement, one clear ask |
| inmail | Start a relevant conversation | Brief subject and focused body |
| email | Direct professional introduction | Subject, relevance, one proof point, natural next step |
| referral | Ask an existing connection for appropriate help | Real relationship, role, evidence they can judge; no assumed endorsement |
| follow-up | Add useful context or ask for an update | Previous contact, new relevant detail if any, low-pressure request |
| legacy | Honor an explicit five-block preference | Candidate-approved opener/closer and role-specific evidence blocks |

The legacy structure may have worked for this candidate; that does not prove universal
superiority. Preserve requested wording except where it would make a false factual claim.
If an opener says “I have applied” but no submission is confirmed, use a truthful
pre-application opener or label it an unsendable post-application draft. Explain the change.

Use plain text by default. Unicode mathematical bold is an optional legacy style, not
required; avoid it when accessibility or the destination makes it unsuitable. Generate
it with `outreach.py bold` if requested. Do not impose a metric in every sentence.
Never introduce a new unsupported claim simply because the outreach is shorter.
If the notes name an editing skill, follow [the editing pass](editing.md); the candidate's
verbatim opener and closer are protected lines it must not touch.

Store a message in `outreach/<channel>.txt`. For email/InMail, put bare subject options
above the `// ---` separator; comments beginning `//` may label the recommended option.
For messages without a subject, save just the body. Replace placeholders before sending.

```bash
python3 "<SKILL_DIR>/scripts/outreach.py" check "<APP>/outreach/hiring-manager.txt" --channel hiring-manager --application "<APP>/application.json"
```

Use `--draft` only for unfinished drafts. `--limit N` overrides the editorial message
budget. The script reports codepoints and bytes, not a guarantee of a platform's current
counting method. Verify the actual destination's limit before sending. Connection notes,
DMs, and InMail are different channels. No automated sending is part of this workflow.

If follow-up planning is requested, a starting policy is one useful follow-up after
five to seven business days and at most one later final follow-up. Label this as a
configurable convention. Respect the employer's timeline, stop on refusal, and never
manufacture urgency or contact multiple people repeatedly to pressure a decision.

After actual contact is confirmed, record it with `applications.py event ... contacted`.
Keep contact provenance (source URL/date/confidence) and channel in `research.md` and
the event note. Contacting is separate from submitting an application.
