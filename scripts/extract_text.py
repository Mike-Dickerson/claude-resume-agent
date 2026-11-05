"""Print the text of a .docx, .pdf, .md, or .txt file so Claude can read it.

Usage: python scripts/extract_text.py <file> [<file> ...]
"""
import pathlib
import sys


def docx_text(path):
    import docx
    doc = docx.Document(path)
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            cells = []
            for c in row.cells:
                if c.text not in cells:  # merged cells repeat
                    cells.append(c.text)
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def pdf_text(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("pypdf is not installed: run  pip install -r requirements.txt")
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def main(paths):
    if not paths:
        sys.exit(__doc__)
    for raw in paths:
        path = pathlib.Path(raw)
        ext = path.suffix.lower()
        if ext == ".docx":
            text = docx_text(path)
        elif ext == ".pdf":
            text = pdf_text(path)
        elif ext in (".md", ".txt", ""):
            text = path.read_text(encoding="utf-8", errors="replace")
        else:
            text = f"(unsupported file type {ext}; ask the user for .docx, .pdf, .md, or .txt)"
        print(f"===== {path.name} =====\n{text.strip()}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
