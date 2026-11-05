"""SessionStart hook: tell Claude whether the user's profile is set up.

Prints plain text; Claude Code adds hook stdout to the session context.
"""
import os
import pathlib

ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or pathlib.Path(__file__).resolve().parent.parent)
PROFILE = ROOT / "profile"
REQUIRED = ["master-inventory.md", "preferences.md", "contact.md"]

for d in ("profile/originals", "output", "data"):
    (ROOT / d).mkdir(parents=True, exist_ok=True)

missing = [f for f in REQUIRED if not (PROFILE / f).is_file()]
originals = sorted(p.name for p in (PROFILE / "originals").iterdir() if p.is_file())

if len(missing) == len(REQUIRED):
    print("FIRST RUN: no profile documents yet. Greet the user, explain in two sentences what this "
          "agent does, then run the /documents flow to collect their resume(s) and preferences "
          "before anything else.")
elif missing:
    print(f"PROFILE INCOMPLETE: missing {', '.join('profile/' + m for m in missing)}. "
          "Offer to finish setup with /documents.")
else:
    print("Profile ready: profile/master-inventory.md, preferences.md, contact.md.")
if originals:
    print("Original documents on file: " + ", ".join(originals))
