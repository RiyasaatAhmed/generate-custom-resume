# Cover letters

Use the job posting, selected evidence, employer research, and candidate voice. Follow
the requested format/length. Do not generate or submit a prohibited letter. For an
optional letter, include it when it adds a meaningful argument; otherwise explain why
the resume already covers the relevant evidence. A focused letter is usually roughly
200–350 words, but do not pad to reach a quota.

Give the letter one purpose: connect the candidate's judgment and experience to this
employer's work. A useful shape is a relevant opening, one achievement including an
actual decision/tradeoff, a sourced reason for this employer, and a natural next step.
Use a real referral only if confirmed. Never invent motivation, a decision, or a personal
story to make the writing vivid.

The resume gives the facts; the letter can explain context and reasoning. Do not stack
every metric or repeat the resume in prose. Match reasonable formality, not a caricature
of the company's marketing voice. First person, genuine enthusiasm, and thanks are
appropriate when they serve the message. Avoid generic praise and exaggerated promises.

Use the same gap policy as the resume and outreach: never imply an absent qualification
is held; answer required questions honestly; explain transferable evidence when material.
Do not list every optional weakness or claim a learning plan unless confirmed.

Run one editorial pass for unsupported claims, vague actors, repeated content, excessive
jargon, and generic employer rationale. Clarity may assist using its rewrite guidance,
but is optional; preserve its factual and formatting safeguards. Do not force a short
sentence into every paragraph or ban ordinary first-person ownership. A candidate's
explicit punctuation preferences still apply.

Save `cover-letter.md` as plain text: greeting, paragraphs, sign-off. Plain URLs can be
included if wanted. A formatted legacy `# Name` / `**headline**` / `---` header is also
accepted by the exporter. Do not leave placeholders in a submission-ready letter.

By default deliver paste-ready text. If a letter attachment is requested:

```bash
python3 "<SKILL_DIR>/scripts/md_export.py" "<APP>/cover-letter.md" --cover
python3 "<SKILL_DIR>/scripts/qa.py" "<APP>/cover-letter.md" --cover --max-pages 1 --json "<APP>/cover-letter-qa.json"
```

The source-based checks validate retained text/links, not the credibility of its argument.
Recheck every claim against evidence and every company detail against its research source.
