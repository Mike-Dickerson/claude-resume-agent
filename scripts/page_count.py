"""Report the page count of .docx files.

Uses Microsoft Word on Windows when available, otherwise LibreOffice (soffice) to
convert to PDF and count pages. Prints "unknown" when neither is installed.

Usage: python scripts/page_count.py <file.docx> [...]
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def word_count(path):
    ps = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        f"$d = $w.Documents.Open('{path}', $false, $true); "
        "$n = $d.ComputeStatistics(2); $d.Close($false); $w.Quit(); Write-Output $n"
    )
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=120)
    return int(out.stdout.strip().splitlines()[-1])


def soffice_count(path):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        raise RuntimeError("no soffice")
    from pypdf import PdfReader
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(path)],
                       capture_output=True, timeout=120, check=True)
        return len(PdfReader(pathlib.Path(tmp) / (path.stem + ".pdf")).pages)


def count(path):
    path = pathlib.Path(path).resolve()
    methods = [word_count, soffice_count] if os.name == "nt" else [soffice_count]
    for m in methods:
        try:
            return m(path)
        except Exception:
            continue
    return "unknown (install Microsoft Word or LibreOffice to check)"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for f in sys.argv[1:]:
        print(f"{pathlib.Path(f).name}: {count(f)} pages")
