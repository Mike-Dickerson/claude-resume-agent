---
name: resume
description: Build a tailored .docx resume for a specific job posting from the user's master inventory. Use when the user says /resume, pastes a job posting or job URL, or asks for a resume for a role.
argument-hint: "<job URL, pasted posting, or shortlist #>"
---

# /resume: tailored resume for one posting

## 1. Get the posting

`$ARGUMENTS` may be a URL, pasted text, a shortlist number, or a company name from `data/job-shortlist.md`. Fetch the full posting: use WebFetch for Dice and most sites, and Claude in Chrome for LinkedIn or Indeed. If you can't get it, ask the user to paste it.

## 2. Confirm before building

Tell the user, in a few lines:
- **The parsed job title.** It becomes the file name: `output/<Title_With_Underscores>_<mmddyyyy>.docx`.
- **Fit verdict:** which required items match, and the honest gaps.
- **Red flags,** if any (see `/find-jobs`).

Wait for an OK on the title. If the user already said "go" or picked the job from a shortlist, a fit that's clear is enough; note the title and proceed.

## 3. Tailor

Read `profile/master-inventory.md`, `profile/preferences.md`, and `profile/contact.md`. Follow every rule in `CLAUDE.md`, and every framing rule and note in `preferences.md`.

- **Headline:** the posting's title, then `|`, then 4–6 of its key terms that the user really has.
- **Summary** (5–7 sentences): mirror the posting's language for things the user has really done, lead the way preferences say, and include one concrete number.
- **Skills:** 6–9 rows of `[label, items]`, ordered by what the posting asks for first. Use the posting's words where they are true.
- **Experience:** newest first, and nothing before the earliest year in preferences. Choose and reword bullets from the inventory to hit the posting's requirements: a bold lead-in, then the result. Keep numbers exact. For a consultancy, use `subsections` for the clients that matter to this posting.
- **Sections:** education and certifications, plus projects and links if they help.
- Fill the length the user prefers (default 2 pages) without padding.

Never add facts that aren't in the profile. If the posting needs something you're not sure about, ask.

## 4. Build and verify

1. Write the spec JSON to `output/specs/<same name>.json`. The format is in `scripts/build_resume.py` and `examples/resume-spec.example.json`.
2. Run `python scripts/build_resume.py output/specs/<name>.json`.
3. Run `python scripts/page_count.py <output docx>`. If it's over the target length, tighten the weakest bullets and rebuild. If it's well under, add the next most relevant inventory bullets.

## 5. Report

Give the file path, the page count, a 2–3 line summary of how it was tailored, the caveats (gaps, travel, applicant count, vendor asking for PII), and an offer of `/cover-letter`. Log the job in `data/job-shortlist.md` if it isn't there yet.
