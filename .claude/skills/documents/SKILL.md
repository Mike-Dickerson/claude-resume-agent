---
name: documents
description: Add or update the user's profile documents (resumes, preferences, contact info) that every resume is built from. Runs automatically on first run. Use when the user says /documents, uploads a resume, or wants to add or change a skill, job, client, certification, or preference.
argument-hint: "[file path(s) or what to change]"
---

# /documents: set up or update the profile

Everything this agent writes comes from three files in `profile/` (git-ignored, never committed):

- `profile/master-inventory.md`: the **source of truth**. Every job, client, project, skill, number, certification, and education entry, written as full facts with dates.
- `profile/preferences.md`: how the user wants to be presented and what jobs they want.
- `profile/contact.md`: name and the contact line for the resume header.

Originals go in `profile/originals/`.

## Decide the mode

- **First run** (no `master-inventory.md`): run **Setup** below.
- **Files given** (`$ARGUMENTS` has paths, or the user drags files in): run **Import**.
- **A change described in words** ("add that I'm AWS certified", "I left Acme in March"): run **Update**.
- **No arguments, profile exists**: show a short summary (counts of jobs, skills, and last updated date) and ask what to add or change.

## Setup (first run)

1. Explain in one or two sentences: "I build tailored resumes only from your own documents, so let's load them first."
2. Ask for documents. Accepted: `.docx`, `.pdf`, `.md`, `.txt`. Good inputs include current and older resumes, LinkedIn profile PDF exports, project lists, and certification lists. The user can give file paths, drag files into the terminal, or paste text. More is better: older resumes often hold details the newest one cut.
3. Run **Import** on what they give.
4. Ask the preference questions with the AskUserQuestion tool where they fit, in one or two rounds (not one by one):
   - Target roles and titles
   - Location; remote, hybrid, or onsite
   - Work types: W2 full-time, W2 contract, 1099, or C2C (and the company name if they have one)
   - Rate or salary floor
   - Earliest year to show on a resume, and how to state total experience (for example "15+ years")
   - What to lead with: newest skills, or deepest experience
   - Anything that must appear on every resume
   - Anything that must never appear
   - Resume length (default 2 pages)
5. Write `preferences.md` and `contact.md`, then show the user a short summary and ask them to correct anything.
6. Suggest a next step: `/find-jobs` or `/resume <posting>`.

## Import

1. Copy each file into `profile/originals/`. Keep the name; if one exists, add a date suffix.
2. Read it: `python scripts/extract_text.py profile/originals/<file>`. For images or scanned PDFs, read the file directly.
3. Merge the facts into `master-inventory.md`:
   - One section per employer or self-employed business. Under a consultancy, give each client its own sub-section.
   - Keep the most detailed version of every bullet. Never drop a fact because a newer resume cut it; old details are the point of this file.
   - Keep real numbers exactly as written ($ figures, %, user counts). Don't round or inflate them.
   - When two documents disagree (dates, titles), **ask** which is right. Don't pick one.
   - Add a `Skills index` at the end: each technology with the jobs where it was used and the years.
4. Report what was added and what was in conflict.

## Update

1. Apply the change the user described, in the right section of the right file.
2. Edit only what they asked. Don't restyle or rewrite neighboring entries.
3. Say exactly what changed, quoting the new line.

## File formats

`contact.md`:
```markdown
# Contact
name: Jordan Example
line: City, ST (Remote)  |  jordan@example.com  |  (555) 555-0100  |  linkedin.com/in/jordan  |  github.com/jordan
```

`preferences.md`:
```markdown
# Preferences
## Targets
- Roles: ...
- Location: ... | Remote only? yes/no
- Work types: W2 contract, C2C via <Company LLC>, full-time ...
- Rate/salary floor: ...
## Framing
- Total experience phrase: "15+ years"
- Earliest year shown: 2008 (nothing earlier, except undated "background" notes the user approves)
- Lead with: ...
- Always include: ...
- Never include: ...
- Length: 2 pages
## Notes
- (lessons learned while working together: phrasing to avoid, how to describe a custom tool, etc.)
```

When the user corrects how you present them during any session, add the lesson under `## Notes` in `preferences.md` so it sticks. Tell them you did.
