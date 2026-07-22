@echo off
echo Iniciando Traductor Local Gemma 3...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
start pythonw -m src.main
exit
