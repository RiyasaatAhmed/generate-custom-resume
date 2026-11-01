# Cover letters

Use the job posting, selected evidence, employer research, and candidate voice. Follow
the requested format/length. Do not generate or submit a prohibited letter. For an
optional letter, include it when it adds a meaningful argument; otherwise explain why
the resume already covers the relevant evidence. Aim for about half a page, 200–300
words; the checker fails a letter over 350. Never pad to reach a length.

Give the letter one purpose: connect the candidate's judgment and experience to this
employer's work. Use three short paragraphs:

1. **Lead with the point.** In the first two sentences, name the role and the strongest
   proof that matches the employer's top priority. Do not open with the candidate's name,
   "I am writing to apply for X, which I saw on Y", or "To whom it may concern".
2. **One achievement, with a decision.** The problem, what the candidate chose and why,
   and the result. One story told properly beats a list of metrics.
3. **Why this employer, then a specific next step.** One sourced detail about their work,
   and a concrete offer, such as walking through a named project.

Address a named person when research confirms one; otherwise use the team or company
name, never "Sir or Madam".

Use a real referral only if confirmed. Never invent motivation, a decision, or a personal
story to make the writing vivid.

The resume gives the facts; the letter can explain context and reasoning. Do not stack
every metric or repeat the resume in prose. Match reasonable formality, not a caricature
of the company's marketing voice. First person, genuine enthusiasm, and thanks are
appropriate when they serve the message. Avoid generic praise and exaggerated promises.

Since AI writing tools spread, echoing the posting's wording no longer sets a letter
apart: in one platform study the link between posting-match and callbacks fell 51%, and
employers leaned on work history instead. What still carries signal is substance a
template cannot produce: a specific decision, a verifiable result, a link to the work.
Use the posting's terms where they are true, but never as a substitute for evidence. Ask
the candidate to read the draft and change anything that does not sound like them.

Use the same gap policy as the resume and outreach: never imply an absent qualification
is held; answer required questions honestly; explain transferable evidence when material.
Do not list every optional weakness or claim a learning plan unless confirmed.

Run one editorial pass for unsupported claims, vague actors, repeated content, excessive
jargon, and generic employer rationale. If the candidate's notes name an editing skill,
follow [the editing pass](editing.md), which guards facts after the edit. Do not force a short
sentence into every paragraph or ban ordinary first-person ownership. A candidate's
explicit punctuation preferences still apply.

Save `cover-letter.md` as plain text: greeting, paragraphs, sign-off. Plain URLs can be
included if wanted. A formatted legacy `# Name` / `**headline**` / `---` header is also
accepted by the exporter. Do not leave placeholders in a submission-ready letter.

Check length and generic phrasing (warnings never block; judge them in context):

```bash
python3 "<SKILL_DIR>/scripts/outreach.py" check "<APP>/cover-letter.md" --channel cover-letter
```

By default deliver paste-ready text. If a letter attachment is requested:

```bash
python3 "<SKILL_DIR>/scripts/md_export.py" "<APP>/cover-letter.md" --cover
python3 "<SKILL_DIR>/scripts/qa.py" "<APP>/cover-letter.md" --cover --max-pages 1 --json "<APP>/cover-letter-qa.json"
```

The source-based checks validate retained text/links, not the credibility of its argument.
Recheck every claim against evidence and every company detail against its research source.

Evidence behind these defaults (each a narrow point, not a guarantee):
[ResumeGo field experiment](https://www.resumego.net/research/cover-letters/) (vendor,
7,287 applications, 2019–2020: tailored letters drew 53% more callbacks than none;
generic letters helped little); [Cui, Dias & Ye 2025](https://arxiv.org/abs/2509.25054)
and [Galdin & Silbert 2025](https://arxiv.org/abs/2511.08785) (preprints: AI tools
eroded the signal value of tailored wording); hiring-manager surveys reported by career
sites favor half a page or less (secondhand, so treated as a default, not a rule).
