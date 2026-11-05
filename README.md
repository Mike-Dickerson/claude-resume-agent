# Resume Agent

A job-search agent that runs in your terminal on [Claude Code](https://docs.claude.com/en/docs/claude-code). Load your resumes once. It finds jobs, screens them against your real experience, and builds tailored `.docx` resumes and cover letters, using only facts from your own documents.

```
> /find-jobs remote contract python
> /resume https://www.dice.com/job-detail/...
> /cover-letter
> /applied Acme - Senior Data Engineer
```

## What you need

- **A Claude account:** Pro or Max subscription, or an Anthropic API key.
- **Claude Code.** Install it with:
  - Windows (PowerShell): `irm https://claude.ai/install.ps1 | iex`
  - macOS / Linux: `curl -fsSL https://claude.ai/install.sh | bash`
- **Python 3.10+.** The launcher installs `python-docx` and `pypdf` for you.
- **Optional:** the [Claude in Chrome](https://claude.ai/chrome) extension, so the agent can search LinkedIn and Indeed in your logged-in browser. Dice works without it.
- **Optional:** Microsoft Word or LibreOffice, so it can check page counts.

## Start

```powershell
git clone https://github.com/Mike-Dickerson/claude-resume-agent.git
cd claude-resume-agent
.\start.ps1          # Windows
./start.sh           # macOS / Linux
```

The launcher checks Python, Claude Code, and your sign-in, then opens the agent. **On first run, it asks for your documents** (resumes, LinkedIn PDF export, project lists) and a few preferences: target roles, remote or onsite, W2 or contract, and how far back to go.

To pick up where you left off: `.\start.ps1 -Continue` (or `./start.sh --continue`).

## Commands

| Command | What it does |
|---|---|
| `/documents` | Add or update your documents and preferences. Runs automatically on first run. |
| `/login` | Check, fix, or switch your Claude sign-in. |
| `/find-jobs [keywords]` | Search Dice, LinkedIn, and Indeed; screen each posting; keep a ranked shortlist. |
| `/resume <url or posting>` | Build a tailored resume in `output/`, checked for page count. |
| `/cover-letter [email]` | Write a cover letter (and an email version) for that job. |
| `/applied <job> [status]` | Log what you sent, and track replies and follow-ups. |

You can also just talk to it: "find me 3 remote contract jobs and make resumes for the best ones."

## Your data stays local

`profile/`, `output/`, and `data/` are in `.gitignore`, so your resumes, contact details, and application log are never committed. The agent never submits applications or sends email on its own. It drafts, and you send.

## How it works

| Piece | Role |
|---|---|
| `CLAUDE.md` | The agent's standing rules: facts only from your profile, confirm the title, verify page count, and protect your personal info. |
| `.claude/skills/*/SKILL.md` | One file per slash command. Edit these to change how it behaves. |
| `.claude/settings.json` | A SessionStart hook that detects first run, plus safe default permissions. |
| `scripts/build_resume.py` | Turns a JSON spec into a formatted `.docx`. See `examples/`. |
| `scripts/build_cover_letter.py`, `extract_text.py`, `page_count.py`, `check_profile.py` | Cover letters, reading your uploads, page checks, and first-run detection. |

## License

MIT
