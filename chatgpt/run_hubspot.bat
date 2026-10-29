@echo off
setlocal
set "HUBSPOT_EXAMPLE_DIR=%~dp0"
powershell.exe -NoProfile -Command "$python = Join-Path $env:HUBSPOT_EXAMPLE_DIR '.venv\Scripts\python.exe'; $client = Join-Path $env:HUBSPOT_EXAMPLE_DIR 'client.py'; if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { [Console]::Error.WriteLine('Python environment not found. Follow the setup instructions in chatgpt\README.md.'); exit 1 }; & $python $client; exit $LASTEXITCODE"
exit /b %ERRORLEVEL%
