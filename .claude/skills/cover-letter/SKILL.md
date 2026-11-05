---
name: cover-letter
description: Write a one-page .docx cover letter (or a short application email) for a job, matched to the tailored resume. Use when the user says /cover-letter, or asks for a cover letter or application email.
argument-hint: "[job / resume name] [email]"
---

# /cover-letter

1. **Find the target.** Use the job and resume from this session, or the one named in `$ARGUMENTS`; spec files are in `output/specs/`. If it's unclear which job, ask.
2. **Write about 250–350 words, in 3–4 paragraphs:**
   - The role, and the single strongest match in one sentence.
   - Two or three proofs taken straight from the resume and inventory, with real numbers, each tied to a stated requirement.
   - How the user works: the work type and availability from preferences, plus remote setup if relevant.
   - A short close asking for a conversation.

   Plain, confident language. No "I am writing to express my interest." Don't repeat the resume line for line. Same facts rules as resumes: nothing that isn't in the profile, and no claims about citizenship or work authorization unless `preferences.md` states them.
3. **Build it.** Write the spec to `output/specs/<Title>_CoverLetter_<mmddyyyy>.json` (format in `scripts/build_cover_letter.py`), then run `python scripts/build_cover_letter.py <spec>`. The name and contact come from `profile/contact.md`.
4. **Email variant.** If the user is applying by email (`$ARGUMENTS` contains "email", or the posting gives a recruiter address), also write a shorter version (120–180 words) with a subject line to `output/<Title>_Email_<mmddyyyy>.md`. **Don't send it.** The user sends it themselves, unless they explicitly ask you to and a mail tool is connected.
5. Report the path(s). If the posting asked for extras such as a rate, availability, or a skills matrix, draft those answers in the reply only (see `CLAUDE.md` rule 3).
