# Move to the project root
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $PSScriptRoot

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
}

# Run the app from project root
Write-Host "🚀 Launching Bookmark Manager..." -ForegroundColor Cyan
python prototype/api.py
