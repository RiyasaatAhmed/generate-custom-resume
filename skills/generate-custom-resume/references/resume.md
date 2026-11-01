# Resume writing and supported format

Choose one clear fit argument. Lead with relevant evidence of the work this employer
needs; retain ownership and a useful mechanism. Preserve actual employment titles,
employers, dates, scope, and metric meaning. A target headline can use the posting's
title only when it truthfully describes the candidate; flag divergence from the profile's
standard headline without accessing LinkedIn.

Prefer concise bullets, often one or two lines. Give recent/relevant work more space
and compress older work. Use a measured outcome when supported; concrete delivery,
scope, or responsibility is also valid. Do not force every bullet to open with a number
or imply every past project solved the target company's exact problem.

Use a readable one- or two-page resume according to relevant experience, market, and
employer instructions. Keep useful education compact. Do not cut proof merely to make
all lines equal. Avoid stranded headings, clipped text, or a role title separated from
its company and first bullet. A long role may continue logically onto another page.

Group supported tools and methods by relevance. Include exact job terminology when
truthful and natural; spell out unfamiliar acronyms when useful. Demonstrate collaboration
through real work rather than a disconnected adjective. Never add a tool from company
research unless the candidate has actually used it.

Preserve candidate writing preferences. Otherwise use plain language, modest emphasis,
and a clear mechanism. Punctuation and individual words are not evidence of authorship.
Manual bold is supported; profile auto-bold remains optional.

The exporter accepts this Markdown dialect:

```markdown
# Full Name
**Truthful headline**
Location / availability
email@example.com | Portfolio

## Summary
Relevant positioning supported by the candidate's facts.

## Skills
Frontend: TypeScript, React

## Experience
### Actual Job Title
**Employer**, Location | Jan 2023 - Present
Optional single company-context line before bullets.
- A specific contribution and supported outcome. [View Project]

## Education
**B.S. Computer Science** | 2018 - 2022
Example University
**M.S. Computing** | 2022 - 2024
Another University

## Projects
### Relevant Project
- A truthful contribution. [Demo](https://example.com/demo)

## Certifications
**Credential Name** | Year
Issuer and relevant details.

## Publications
[Publication title](https://example.com/paper)

## Honors & Awards
**Award** - Issuer
Relevant detail.
```

Sections are optional and retain source order except the summary, which follows the
header. Omit empty sections. `Work Experience` aliases `Experience`; honors heading
aliases are accepted. Unsupported headings/tables/code blocks fail explicitly. Each
experience bullet is one Markdown source line, even when it wraps in the PDF. Each
education entry starts with a bold degree or `###` heading. Do not nest bullets.

Contacts render from `profile.json` when present. Keep source contacts consistent with
that profile. Inline Markdown links are supported. Bare tokens resolve through
`link_labels`/`company_projects`; unresolved tokens fail export. Bare experience links
move to the company row. HTML comments are excluded from output; selected bullet-bank
claims must become real bullets. Use the parser's supported structure, not arbitrary Markdown.
