"""Build a formatted .docx resume from a JSON spec.

Usage: python scripts/build_resume.py <spec.json>

Spec (see examples/resume-spec.example.json):
{
  "output": "output/Senior_Data_Engineer_11052026.docx",
  "name": "Jordan Example",
  "contact": "City, ST (Remote) | email | phone | linkedin | github",
  "headline": "Senior Data Engineer | Python · SQL · Snowflake",
  "summary": "Paragraph...",
  "skills": [["Languages", "Python, SQL"], ...],
  "experience": [
    {"title": "Company - Role", "dates": "2019 - Present", "location": "Remote",
     "intro": "optional paragraph",
     "bullets": [["Bold lead-in:", "rest of bullet"], ["", "bullet with no lead-in"]],
     "subsections": [{"title": "Client: Acme", "dates": "2021 - 2023", "bullets": [...]}]}
  ],
  "sections": [
    {"heading": "EDUCATION & CERTIFICATIONS", "paragraphs": ["..."]},
    {"heading": "PROJECTS", "bullets": [["Name:", "description"]]}
  ],
  "accent": "1E5E53"          (optional hex color for headings)
}
"""
import json
import pathlib
import sys

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

GRAY = RGBColor(0x5A, 0x5A, 0x5A)
FONT = "Calibri"
MARGIN = 0.6  # inches


class Resume:
    def __init__(self, accent="1E5E53"):
        self.accent_hex = accent
        self.accent = RGBColor.from_string(accent.upper())
        self.doc = docx.Document()
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, side, Inches(MARGIN))
        self.text_width = Inches(8.5 - 2 * MARGIN)
        normal = self.doc.styles["Normal"]
        normal.font.name = FONT
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        normal.font.size = Pt(10.5)
        normal.paragraph_format.space_after = Pt(0)
        normal.paragraph_format.line_spacing = 1.0

    # --- primitives -----------------------------------------------------------
    @staticmethod
    def _space(p, before=0, after=0):
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)

    @staticmethod
    def _run(p, text, bold=False, size=None, color=None, italic=False):
        r = p.add_run(text)
        r.bold = bold or None
        r.italic = italic or None
        if size:
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color
        return r

    def para(self, text, after=3, size=None, color=None, align=None, bold=False):
        p = self.doc.add_paragraph()
        self._space(p, 0, after)
        if align:
            p.alignment = align
        self._run(p, text, bold=bold, size=size, color=color)
        return p

    def heading(self, text):
        p = self.doc.add_paragraph()
        self._space(p, 9, 3)
        p.paragraph_format.keep_with_next = True
        bdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "2"), ("w:color", self.accent_hex)):
            bottom.set(qn(k), v)
        bdr.append(bottom)
        p._p.get_or_add_pPr().append(bdr)
        self._run(p, text.upper(), bold=True, size=11.5, color=self.accent)

    def dated_line(self, title, dates="", size=11, bold=True, color=None, before=4):
        p = self.doc.add_paragraph()
        self._space(p, before, 1)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.tab_stops.add_tab_stop(self.text_width, WD_TAB_ALIGNMENT.RIGHT)
        self._run(p, title, bold=bold, size=size, color=color)
        if dates:
            self._run(p, "\t" + dates, size=9.5, color=GRAY)

    def bullet(self, lead, text):
        p = self.doc.add_paragraph(style="List Bullet")
        self._space(p, 0, 2)
        if lead:
            self._run(p, lead.rstrip() + " ", bold=True)
        self._run(p, text)

    def skills(self, rows):
        t = self.doc.add_table(rows=len(rows), cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.autofit = False
        widths = (Inches(1.55), self.text_width - Inches(1.55))
        for row, (label, text) in zip(t.rows, rows):
            for cell, width, value, bold in zip(row.cells, widths, (label, text), (True, False)):
                cell.width = width
                p = cell.paragraphs[0]
                self._space(p, 1, 1)
                self._run(p, value, bold=bold, size=10, color=self.accent if bold else None)

    # --- document -------------------------------------------------------------
    def build(self, spec):
        self.para(spec["name"], after=0, size=20, color=self.accent, bold=True,
                  align=WD_ALIGN_PARAGRAPH.CENTER)
        if spec.get("contact"):
            self.para(spec["contact"], after=2, size=9.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER)
        if spec.get("headline"):
            self.para(spec["headline"], after=2, size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

        if spec.get("summary"):
            self.heading(spec.get("summary_heading", "Professional Summary"))
            self.para(spec["summary"], after=2)
        if spec.get("skills"):
            self.heading(spec.get("skills_heading", "Core Skills"))
            self.skills(spec["skills"])
        if spec.get("experience"):
            self.heading(spec.get("experience_heading", "Professional Experience"))
            for job in spec["experience"]:
                dates = job.get("dates", "")
                if job.get("location"):
                    dates = f"{job['location']}  |  {dates}" if dates else job["location"]
                self.dated_line(job["title"], dates)
                if job.get("intro"):
                    self.para(job["intro"], after=2)
                for lead, text in job.get("bullets", []):
                    self.bullet(lead, text)
                for sub in job.get("subsections", []):
                    self.dated_line(sub["title"], sub.get("dates", ""), size=10.5, color=self.accent, before=3)
                    if sub.get("intro"):
                        self.para(sub["intro"], after=2)
                    for lead, text in sub.get("bullets", []):
                        self.bullet(lead, text)
        for section in spec.get("sections", []):
            self.heading(section["heading"])
            for text in section.get("paragraphs", []):
                self.para(text, after=2)
            for lead, text in section.get("bullets", []):
                self.bullet(lead, text)
        return self.doc


def main(spec_path):
    spec_path = pathlib.Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = pathlib.Path(spec["output"])
    if not out.is_absolute():
        out = pathlib.Path(__file__).resolve().parent.parent / out
    out.parent.mkdir(parents=True, exist_ok=True)
    Resume(spec.get("accent", "1E5E53")).build(spec).save(out)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
