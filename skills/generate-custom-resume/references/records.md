# Local records, submission history, and learning

Create a unique application directory, or reuse the explicitly selected record for edits:

```bash
python3 "<KIT>/scripts/applications.py" init --company "Example Co" --role "Frontend Engineer" --url "https://example.com/job" --requisition "REQ-123" --role-family "frontend" --geography "remote-eu" --channel "direct"
```

The printed path is `<APP>`. Initialization records `drafted`, not `applied`. Save the
posting and research there. Optional fields default to unknown; do not guess geography
or authorization. Keep explicit candidate facts in the evidence map. Unique suffixes
avoid overwriting different openings with the same company/title.

After preparing and reviewing the documents, record readiness:

```bash
python3 "<KIT>/scripts/applications.py" event "<APP>" ready --note "Reviewed evidence and QA; selected upload files prepared"
```

Only after the user says they actually submitted, record the exact files submitted:

```bash
python3 "<KIT>/scripts/applications.py" submit "<APP>" "upload/Jane-Doe-Resume.pdf" --confirm-submitted --note "User confirmed submission"
```

Replace the example filename with the actual upload filename. This command records
history; it never submits. Do not use confirmation to mean “the user approved a draft.”
It creates a fresh `submitted/<version>/` with copied artifacts and hashes; later drafts
must not modify it. Files must be inside the application folder. Use
`applications.py verify "<APP>"` to detect modified/missing snapshots. Hashes detect
accidental changes, not adversarial changes to both records and artifacts.

Record actual later events with `event <APP> contacted|replied|screening|technical-interview|final|offer|rejected|withdrawn --note ...`.
Contacts and replies may occur before an application; they never establish submission.
Events retain dates even when the current state changes. Do not infer a reply is qualified
or an interview occurred merely because the next stage seems likely. Put relevant details
in the note. Closed applications remain closed; initialize a new record for a new process.

```bash
python3 "<KIT>/scripts/applications.py" summary "<KIT>/applications"
python3 "<KIT>/scripts/applications.py" summary "<KIT>/applications" --group-by role_family
```

Summaries distinguish prepared and submitted counts. Rates use submitted records and
post-submission events; zero denominators return null. Group by role_family, geography,
or channel to compare similar situations. Dates expose elapsed time. Use event notes
and submitted versions for qualitative comparison. Compare one meaningful variable
at a time and do not claim causal effects from small nonrandom samples.

An old `applications-log.md` is historical context only: its rows may mean drafts were
generated. Do not migrate them as confirmed submissions without user evidence. Existing
application folders without a record remain untouched until explicitly selected.
