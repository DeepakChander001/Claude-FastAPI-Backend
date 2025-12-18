@echo off
setlocal
set "PYTHONPATH=%~dp0"
python "%~dp0src\client\cli.py" %*
endlocal
