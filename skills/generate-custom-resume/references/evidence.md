# Candidate evidence

Read the full selected base resume, including bullet-bank comments. If
`profile/achievements.json` exists, validate and use it as an additional source index:

```bash
python3 "<KIT>/scripts/evidence.py" bank "<KIT>/profile/achievements.json"
```

The fictional `profile/achievements.example.json` demonstrates the schema; never copy
its claims into the real profile. Create real records from supplied claims only. Keep
stable IDs. Empty fields stay null/unknown rather than plausible invented detail.

Each record includes `id`, `employer`, `claim`, `source`, and `status`. Record dates,
problem, personal contribution, collaborators, method, skills, metrics, artifacts,
confidentiality, open questions, and interview notes when known. Metric entries need
a name and unit, with baseline/result, period, population, measurement source, and
attribution where available. A derived metric needs its calculation. Preserve both
the original statement and the derivation; do not silently replace the original.

Statuses mean:

- `candidate-stated`: supplied in a candidate source, not independently verified.
- `context-confirmed`: include the dated answer/reference in `confirmation`.
- `artifact-supported`: identify the supporting artifacts; verify what they actually
  establish rather than treating a public link as proof of every result.
- `needs-clarification`: scope/meaning is unresolved. It cannot serve as direct proof.

Ask targeted questions about material uncertainties: personal ownership, before/after
values, period, denominator, attribution, and whether the details may be disclosed.
Do not demand public proof of private work. An unquantified delivery can be useful
evidence. Do not invent a metric to satisfy a formatting rule. Save confirmed answers
to the bank so future runs do not repeat questions.

Use `templates/evidence-map.example.json` as a structural example. Each requirement
gets a stable ID, exact requirement, posting source, importance (`required`, `preferred`,
`responsibility`), match (`direct`, `adjacent`, `missing`, `unknown`), sources, and treatment.
Sources use `{"achievement_id": "id"}` or, for legacy profiles,
`{"reference": "profile/base-resume.md: employer/bullet", "excerpt": "exact supplied claim"}`.
Include eligibility items and a reasoned recommendation. Do not generate a fit percentage.

```bash
python3 "<KIT>/scripts/evidence.py" map "<APP>/evidence-map.json" --bank "<KIT>/profile/achievements.json"
```

Omit `--bank` when all sources use references/excerpts. Validate every final resume,
letter, and outreach claim against the sources manually: this script checks structure
and source IDs, not semantic truth, dates, causation, or whether someone can defend a claim.
Record selected achievement IDs/source references and any changes in `research.md`.

Preserve measurement meaning. An increase from 20% to 30% is 10 percentage points or
50% relative growth, not a 10% relative increase. Do not assume an experiment proves
causation or a team result was achieved alone. Clarify overlapping roles before deriving
years of experience. If a claim cannot be clarified, narrow or omit it.
