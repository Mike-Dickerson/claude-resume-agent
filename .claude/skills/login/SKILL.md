---
name: login
description: Check, fix, or switch the Claude account this agent runs under (sign in, sign out, status, API key). Use when the user says /login, can't sign in, sees auth errors, or wants to switch accounts.
argument-hint: "[status | login | logout | switch]"
---

# /login: Claude sign-in

The agent runs on Claude Code, so it uses Claude Code's own sign-in. Sign-in is interactive (it opens a browser), so **the user runs the commands themselves**. You check the status and walk them through it.

1. Check the current status:
   ```
   claude auth status --text
   ```
   (The JSON form, `claude auth status`, shows `loggedIn`, `authMethod`, and the account email.)

2. Report it in one line: signed in or not, the method (claude.ai subscription or API key), and the account email.

3. Then, based on `$ARGUMENTS` or what they want:

   | Want | Tell them to type |
   |---|---|
   | Sign in | `/login` (works inside this session), or quit and run `claude auth login` |
   | Sign out | `/logout`, or `claude auth logout` |
   | Switch accounts | `/logout`, then `/login` |
   | Use an API key instead of a subscription | Set `ANTHROPIC_API_KEY` in their environment, then restart with `claude` |
   | Long-lived token (for scripts or CI, needs a subscription) | `claude setup-token` |

   Tip: typing `! claude auth login` runs the command from inside this session.

4. After they finish, run `claude auth status --text` again and confirm it worked.

Never ask the user to paste a password, API key, or token into the chat, and never write one into any file in this repo.

If `claude` isn't found, Claude Code isn't installed or isn't on PATH. Point them to the install steps in `README.md`.
