---
name: applied
description: Log a job application the user actually sent (or update its status), so it is never suggested again and follow-ups are tracked. Use when the user says /applied, "I applied to...", "sent it", or reports a recruiter reply, interview, or rejection.
argument-hint: "<company / role> [status]"
---

# /applied: track applications

Keep `data/applications.md` as one table, newest first:

```markdown
| Date | Company / vendor | Role | Link | Resume sent | Status | Next step |
|---|---|---|---|---|---|---|
```

- **New application:** add a row with today's date. Fill the link and resume file from `data/job-shortlist.md` or `output/` when you can match them. Status: `Applied`.
- **Update** (recruiter replied, interview, rejected, offer): change that row's Status and Next step, and add a dated note under the table if there are details worth keeping.
- **No arguments:** show the table, and flag rows over 7 days old with no response as candidates for a follow-up note. Offer to draft one.

Record only what the user says actually happened. A resume being built doesn't mean it was sent.
