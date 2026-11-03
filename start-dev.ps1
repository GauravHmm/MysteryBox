# Start both local services. Close their process windows to stop them.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
if (-not (Test-Path (Join-Path $backend '.venv\Scripts\python.exe'))) { throw 'Backend virtual environment is missing. Follow README.md first.' }
Start-Process -FilePath (Join-Path $backend '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','app.main:app','--reload','--port','8000' -WorkingDirectory $backend
Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory $frontend
Write-Host 'MysteryBox is starting: http://localhost:5173 (frontend), http://localhost:8000 (API).'
