
# One-Click Installer for Claude Code CLI (Windows)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://raw.githubusercontent.com/DeepakChander001/Claude-FastAPI-Backend/main"
$InstallDir = "$env:USERPROFILE\.claude-client"
$ClientScript = "$InstallDir\cli.py"
$VenvDir = "$InstallDir\venv"
$PythonExe = "$VenvDir\Scripts\python.exe"

Write-Host "Installing Claude Code CLI..." -ForegroundColor Cyan

# 1. Create Directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
    Write-Host "Created installation directory: $InstallDir"
}

# 2. Download cli.py
Write-Host "Downloading client..."
try {
    Invoke-WebRequest -Uri "$RepoUrl/src/client/cli.py" -OutFile $ClientScript
} catch {
    Write-Error "Failed to download client script. Please check your internet connection."
}

# 3. Create Virtual Environment (Isolated)
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
}

# 4. Install Dependencies
Write-Host "Installing dependencies (requests)..."
& $PythonExe -m pip install requests --quiet

# 5. Create 'nexus' command (Shim)
$ShimPath = "$InstallDir\nexus.cmd"
$ShimContent = "@echo off`r`n`"$PythonExe`" `"$ClientScript`" %*"
Set-Content -Path $ShimPath -Value $ShimContent

Write-Host "`n✅ Installation Complete!" -ForegroundColor Green
Write-Host "You can now run 'nexus' from this folder."
Write-Host "To run it from ANYWHERE, add this folder to your PATH:"
Write-Host "  $InstallDir" -ForegroundColor Yellow

# Optional: Attempt to modify User PATH (Requires restart to take effect)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$InstallDir", "User")
Write-Host "NOTE: You may need to restart your terminal for the 'nexus' command to work globally." -ForegroundColor Yellow
