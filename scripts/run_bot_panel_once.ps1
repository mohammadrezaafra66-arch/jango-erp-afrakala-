$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$LogDir = Join-Path $ProjectRoot "logs\bot_panel_runner"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir ("run-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".log")

function Write-RunLog($Message) {
    $Line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $Line
    Add-Content -Path $LogFile -Value $Line -Encoding UTF8
}

Write-RunLog "Starting bot panel runner"
Write-RunLog "ProjectRoot=$ProjectRoot"
Write-RunLog "PythonExe=$PythonExe"

& $PythonExe manage.py check 2>&1 | ForEach-Object { Write-RunLog $_ }
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe manage.py seed_bot_panel_defaults 2>&1 | ForEach-Object { Write-RunLog $_ }
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe manage.py run_pending_bot_requests 2>&1 | ForEach-Object { Write-RunLog $_ }
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-RunLog "Bot panel runner completed successfully"
exit 0
