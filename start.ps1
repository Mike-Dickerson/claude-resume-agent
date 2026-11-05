# Resume Agent launcher (Windows PowerShell)
# Usage:  .\start.ps1            start a new session
#         .\start.ps1 -Continue  pick up the last session
param([switch]$Continue)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Resume Agent" -ForegroundColor Cyan

# 1. Python + packages
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python 3.10+ is required: https://www.python.org/downloads/ (check 'Add to PATH')." -ForegroundColor Red
    exit 1
}
python -c "import docx, pypdf" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python packages..."
    python -m pip install --quiet -r requirements.txt
}

# 2. Claude Code
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "Claude Code is not installed. Install it with:" -ForegroundColor Yellow
    Write-Host "  irm https://claude.ai/install.ps1 | iex"
    Write-Host "then open a new terminal and run .\start.ps1 again."
    exit 1
}

# 3. Sign-in
$status = claude auth status 2>$null | Out-String
if ($status -notmatch '"loggedIn":\s*true') {
    Write-Host "You're not signed in to Claude yet. Opening sign-in..." -ForegroundColor Yellow
    claude auth login
}

# 4. Go
if ($Continue) { claude --continue } else { claude "Hi" }
