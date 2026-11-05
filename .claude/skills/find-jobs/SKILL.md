---
name: find-jobs
description: Search job boards (Dice, LinkedIn, Indeed) for roles that fit the user's profile and preferences, screen each one, and keep a ranked shortlist. Use when the user says /find-jobs or asks to find, search for, or look for jobs.
argument-hint: "[keywords, or 'contract', 'today', etc.]"
---

# /find-jobs: search, screen, shortlist

Before searching, read `profile/preferences.md` (targets, location, work types, rate floor), `profile/master-inventory.md`, `data/job-shortlist.md`, and `data/applications.md`. Skip anything already applied to or already on the shortlist.

## 1. Search

Build 3–6 queries from the target roles plus the user's strongest skills. Use `$ARGUMENTS` if given. Default to postings from the **last 3 days**.

| Board | How | Notes |
|---|---|---|
| **Dice** | WebFetch `https://www.dice.com/jobs?q=<kw>&filters.workplaceTypes=Remote&filters.employmentType=CONTRACTS&filters.postedDate=THREE` | Works without a browser. Drop the employment filter for full-time. Open each job's detail URL before judging it. |
| **LinkedIn** | Needs **Claude in Chrome** (the user's logged-in browser). `https://www.linkedin.com/jobs/search/?keywords=<kw>&f_WT=2&f_TPR=r259200` | The newer search may drop the contract filter, so put "contract" in the keywords. Read a job at `/jobs/view/<id>/`. |
| **Indeed** | Needs **Claude in Chrome**. `https://www.indeed.com/jobs?q=<kw>&l=Remote&sc=0kf%3Ajt%28contract%29%3B&fromage=3` | Plain fetches get blocked (403). Wait for the security check page to pass, then re-read the tab. |

If the Chrome tools aren't available, say that LinkedIn and Indeed need the Claude in Chrome extension and a restart with `claude --continue`, and search Dice meanwhile. In the browser, only read pages. Never click Apply, submit forms, or accept terms without the user's explicit yes.

## 2. Screen each candidate

Open the full posting, not just the search card. Give each one a verdict:

- **Hard filters** (from preferences): location and remote status, work type, rate floor, citizenship or clearance, required years.
- **Fit:** count the *required* items the inventory actually covers. Name the gaps honestly. A gap in a "preferred" item is fine; a gap in a "required" item lowers the rank.
- **Red flags:** asks for SSN, DOB, or bank info up front; pay to apply; vague "data entry" posts; the same post from many vendors (keep the one with the best rate or the most direct client).
- **Signal:** how recent the post is, the applicant count, a named end client, and a direct recruiter email.

## 3. Report

Show a ranked table: **#, role and company (linked), pay and type, why it fits, gaps and caveats**. Lead with the top 3. Keep it short.

Then append a dated section to `data/job-shortlist.md` with the same rows plus a "skipped" list with one-line reasons. That keeps the next search from re-screening them.

Offer: "Want resumes for the top N?" Then run `/resume` for each one the user picks.
