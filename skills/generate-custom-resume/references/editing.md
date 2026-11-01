# Optional editing pass

The goal is specific prose in the candidate's own voice. Do not try to beat AI detectors,
and never insert typos, slang, or fake casualness to look human.

Look for an `## Editing` section in `<DATA>/profile/candidate-notes.md`. It may name an
editing skill (for example `clarity`), the documents it applies to, and lines that must
stay verbatim.

- **No section:** do the built-in pass described in the cover-letter guide. Do not invoke
  an editing skill on your own.
- **Skill named but not installed in this agent:** say so when delivering, and do the
  built-in pass instead.
- **Skill named and installed:** load its instructions (invoke it as a skill where the
  agent supports that; otherwise read its SKILL.md) and run its rewrite mode on each
  covered draft. Tell it the reader and purpose, that every fact, number, title, date,
  link, and quotation must survive, and that it may not add experience, enthusiasm, or
  anecdotes. Keep protected lines out of its reach.

Unless the notes say otherwise, the pass covers the cover letter and outreach. On the
resume it may touch only the summary, and only when the notes list it; never bullets,
titles, dates, or the skills list.

Guard every edit:

1. Before editing, copy the draft to `<APP>/edits/<name>.before.md`.
2. After editing, compare the two, passing each verbatim line from the notes:

   ```bash
   python3 "<SKILL_DIR>/scripts/edit_guard.py" "<APP>/edits/cover-letter.before.md" "<APP>/cover-letter.md" --protect "exact verbatim line"
   ```

3. Check every reported change against the evidence map. Keep it only if the sources
   support it; otherwise restore the original wording and run the guard again. Exit 0
   does not prove the meaning held: read the edit for shifts in ownership ("led" to
   "helped"), scope, and certainty.
4. Re-run the checks for each changed file: `outreach.py check` for outreach, and export
   plus QA for a letter attachment or the resume.
5. Record in `research.md`, and in the delivery, which skill ran on which files, what the
   guard reported, and what you reverted.
