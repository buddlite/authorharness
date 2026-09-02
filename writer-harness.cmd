@echo off
setlocal EnableExtensions

rem Run from the repository directory so this file also works when double-clicked.
pushd "%~dp0"

where uv >nul 2>nul
if not errorlevel 1 (
    uv run --locked writer %*
    set "exit_code=%ERRORLEVEL%"
    popd
    exit /b %exit_code%
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m writer_harness %*
    set "exit_code=%ERRORLEVEL%"
    popd
    exit /b %exit_code%
)

echo Writer Harness requires uv, or an existing .venv. 1>&2
echo Install uv from https://docs.astral.sh/uv/getting-started/installation/ 1>&2
echo Then run this file again. 1>&2
popd
exit /b 1
