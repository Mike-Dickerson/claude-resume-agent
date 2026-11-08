"""Resume Agent web app: file lists, document manager, agent chat, MyResume.Chat signup.

Run:  python web/server.py        (opens http://127.0.0.1:8765)
Only listens on this computer (127.0.0.1).
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import webbrowser

import httpx
import uvicorn
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from extract_text import docx_text, pdf_text  # noqa: E402

AREAS = {
    "documents": ROOT / "profile" / "originals",  # incoming: the user's own documents
    "resumes": ROOT / "output",                   # outgoing: generated resumes and letters
}
SESSION_FILE = ROOT / "data" / "web_session.txt"
MRC_API = os.environ.get("MRC_API", "https://api.myresume.chat/api")
PORT = int(os.environ.get("RESUME_AGENT_PORT", "8765"))
ALLOWED_UPLOAD = {".docx", ".pdf", ".md", ".txt", ".doc"}

WEB_PROMPT = (
    "You are running behind the Resume Agent web app, not a terminal. The user types in a chat box and "
    "sees your text replies. Ask questions in plain text, one short list at a time, and wait for the next "
    "message for answers. Files the user uploads through the web app land in profile/originals/. Resumes "
    "and cover letters you build in output/ appear in the web app's Resumes list automatically. If sign-in "
    "fails, tell the user to run start.ps1 (or start.sh) once in a terminal to sign in."
)
ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch", "Skill",
                 "Bash(python scripts/*)", "Bash(python web/*)", "Bash(claude auth status*)"]

app = FastAPI(title="Resume Agent")
chat_lock = threading.Lock()


def find_claude():
    """Path to the real Claude Code executable. On Windows, npm installs a claude.cmd wrapper
    that mangles quoted arguments, so prefer the claude.exe it points to."""
    found = shutil.which("claude.exe") or shutil.which("claude")
    candidates = [pathlib.Path.home() / ".local" / "bin" / "claude.exe"]
    if found:
        p = pathlib.Path(found)
        if p.suffix.lower() in (".cmd", ".bat", ".ps1", ""):
            candidates.insert(0, p.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe")
        else:
            return str(p)
    for c in candidates:
        if c.is_file():
            return str(c)
    return found


CLAUDE = find_claude()


# --- helpers ------------------------------------------------------------------
def area_dir(area):
    if area not in AREAS:
        raise HTTPException(404, "Unknown list")
    AREAS[area].mkdir(parents=True, exist_ok=True)
    return AREAS[area]


def safe_file(area, name):
    folder = area_dir(area)
    path = (folder / pathlib.Path(name).name).resolve()
    if path.parent != folder.resolve() or not path.is_file():
        raise HTTPException(404, "File not found")
    return path


def file_text(path):
    ext = path.suffix.lower()
    if ext == ".docx":
        return docx_text(path)
    if ext == ".pdf":
        return pdf_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def profile_status():
    p = ROOT / "profile"
    have = {f: (p / f).is_file() for f in ("master-inventory.md", "preferences.md", "contact.md")}
    return {"ready": all(have.values()), "files": have}


# --- pages and status -----------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return (ROOT / "web" / "index.html").read_text(encoding="utf-8")


@app.get("/api/status")
def status():
    claude = CLAUDE
    signed_in = None
    if claude:
        try:
            out = subprocess.run([claude, "auth", "status"], capture_output=True, text=True, timeout=20)
            signed_in = bool(json.loads(out.stdout or "{}").get("loggedIn"))
        except Exception:
            signed_in = None
    return {"profile": profile_status(), "claude_installed": bool(claude), "signed_in": signed_in,
            "has_session": SESSION_FILE.is_file()}


# --- file lists -----------------------------------------------------------------
@app.get("/api/files/{area}")
def list_files(area):
    folder = area_dir(area)
    files = [f for f in folder.iterdir() if f.is_file() and not f.name.startswith(("~$", "."))]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return [{"name": f.name, "size": f.stat().st_size, "modified": f.stat().st_mtime} for f in files]


@app.get("/api/files/{area}/{name}")
def download(area, name):
    path = safe_file(area, name)
    return FileResponse(path, filename=path.name)


@app.get("/api/files/{area}/{name}/text")
def text(area, name):
    return {"text": file_text(safe_file(area, name))}


@app.post("/api/files/documents")
async def upload(files: list[UploadFile] = File(...)):
    folder = area_dir("documents")
    saved = []
    for up in files:
        name = pathlib.Path(up.filename or "").name
        if not name or pathlib.Path(name).suffix.lower() not in ALLOWED_UPLOAD:
            raise HTTPException(400, f"{name or 'file'}: only .docx, .pdf, .md, .txt, or .doc files")
        dest = folder / name
        n = 2
        while dest.exists():
            dest = folder / f"{pathlib.Path(name).stem} ({n}){pathlib.Path(name).suffix}"
            n += 1
        dest.write_bytes(await up.read())
        saved.append(dest.name)
    return {"saved": saved}


@app.delete("/api/files/documents/{name}")
def delete_document(name):
    safe_file("documents", name).unlink()
    return {"deleted": name}


# --- agent chat -----------------------------------------------------------------
def describe_tool(block):
    name, args = block.get("name", ""), block.get("input", {}) or {}
    detail = args.get("file_path") or args.get("url") or args.get("command") or args.get("skill") \
        or args.get("pattern") or args.get("query") or ""
    if isinstance(detail, str) and str(ROOT) in detail:
        detail = detail.replace(str(ROOT) + os.sep, "")
    return f"{name} {detail}".strip()


def run_agent(message):
    claude = CLAUDE
    if not claude:
        yield {"type": "error", "text": "Claude Code isn't installed. See README.md."}
        return
    cmd = [claude, "-p", message, "--output-format", "stream-json", "--verbose",
           "--append-system-prompt", WEB_PROMPT,
           "--allowedTools", *ALLOWED_TOOLS, "--disallowedTools", "AskUserQuestion"]
    if SESSION_FILE.is_file():
        cmd += ["--resume", SESSION_FILE.read_text().strip()]
    if not chat_lock.acquire(blocking=False):
        yield {"type": "error", "text": "The agent is still working on your last message."}
        return
    try:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("session_id"):
                SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
                SESSION_FILE.write_text(event["session_id"])
            if event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        yield {"type": "text", "text": block["text"]}
                    elif block.get("type") == "tool_use":
                        yield {"type": "tool", "text": describe_tool(block)}
            elif event.get("type") == "result":
                if event.get("is_error"):
                    yield {"type": "error", "text": str(event.get("result") or "The agent stopped with an error.")}
                yield {"type": "done"}
        proc.wait()
        if proc.returncode not in (0, None):
            err = proc.stderr.read().strip()
            if err:
                yield {"type": "error", "text": err[-800:]}
    finally:
        chat_lock.release()


@app.post("/api/chat")
def chat(payload: dict = Body(...)):
    message = (payload.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "Empty message")

    def stream():
        for event in run_agent(message):
            yield f"data: {json.dumps(event)}\n\n"
        yield 'data: {"type": "end"}\n\n'
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/chat/reset")
def chat_reset():
    SESSION_FILE.unlink(missing_ok=True)
    return {"reset": True}


# --- MyResume.Chat --------------------------------------------------------------
@app.post("/api/mrc/signup")
def mrc_signup(form: dict = Body(...)):
    """Create a MyResume.Chat account, then upload every document. The password is passed
    straight through to MyResume.Chat over HTTPS and never stored or logged here."""
    required = ["first_name", "last_name", "email", "password", "zip_code", "phone"]
    missing = [k for k in required if not str(form.get(k, "")).strip()]
    if missing:
        raise HTTPException(400, "Missing: " + ", ".join(missing))
    if not form.get("agree"):
        raise HTTPException(400, "Please accept the MyResume.Chat user agreement.")
    body = {k: form.get(k, "") for k in required + ["titles", "about", "profile_links"]}
    body["share_with_recruiters"] = bool(form.get("share_with_recruiters", True))

    with httpx.Client(timeout=60) as client:
        r = client.post(f"{MRC_API}/signup", json=body)
        if r.status_code >= 400:
            detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith(
                "application/json") else r.text
            raise HTTPException(r.status_code, f"MyResume.Chat: {detail}")
        token = r.json().get("session_token")

        uploads = []
        docs = [f for f in area_dir("documents").iterdir()
                if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".doc", ".docx"}][:10]
        for f in docs:
            try:
                up = client.post(f"{MRC_API}/upload-resume", headers={"Authorization": f"Bearer {token}"},
                                 data={"title": f.stem}, files={"file": (f.name, f.read_bytes())},
                                 timeout=180)  # MRC virus-scans each file
                uploads.append({"file": f.name, "ok": up.status_code < 400,
                                "detail": "" if up.status_code < 400 else up.text[:300]})
            except httpx.HTTPError as e:
                uploads.append({"file": f.name, "ok": False, "detail": str(e)})
    skipped = [f.name for f in area_dir("documents").iterdir()
               if f.is_file() and f.suffix.lower() == ".md"]
    return {"created": True, "email": body["email"], "uploads": uploads, "skipped": skipped}


if __name__ == "__main__":
    for d in AREAS.values():
        d.mkdir(parents=True, exist_ok=True)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Resume Agent web app: {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
