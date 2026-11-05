"""Build a one-page .docx cover letter from a JSON spec.

Usage: python scripts/build_cover_letter.py <spec.json>

Spec (see examples/cover-letter-spec.example.json):
{
  "output": "output/Senior_Data_Engineer_CoverLetter_11052026.docx",
  "name": "Jordan Example",
  "contact": "City, ST | email | phone",
  "date": "November 5, 2026",
  "recipient": ["Hiring Team", "Acme Corp"],
  "greeting": "Dear Hiring Team,",
  "paragraphs": ["...", "...", "..."],
  "closing": "Sincerely,",
  "accent": "1E5E53"
}
"""
import json
import pathlib
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_resume import GRAY, Resume  # noqa: E402


def main(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    r = Resume(spec.get("accent", "1E5E53"))
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(r.doc.sections[0], side, Inches(1))
    r.doc.styles["Normal"].font.size = Pt(11)
    r.para(spec["name"], after=0, size=18, color=r.accent, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    if spec.get("contact"):
        r.para(spec["contact"], after=14, size=9.5, color=GRAY)
    if spec.get("date"):
        r.para(spec["date"], after=10)
    for i, line in enumerate(spec.get("recipient", [])):
        r.para(line, after=10 if i == len(spec["recipient"]) - 1 else 0)
    r.para(spec.get("greeting", "Dear Hiring Team,"), after=8)
    for text in spec["paragraphs"]:
        r.para(text, after=8)
    r.para(spec.get("closing", "Sincerely,"), after=24)
    r.para(spec["name"], after=0)

    out = pathlib.Path(spec["output"])
    if not out.is_absolute():
        out = pathlib.Path(__file__).resolve().parent.parent / out
    out.parent.mkdir(parents=True, exist_ok=True)
    r.doc.save(out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
