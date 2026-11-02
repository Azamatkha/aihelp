@echo off
rem Admin panel: http://127.0.0.1:8000/admin/
cd /d "%~dp0.."
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
if not exist logs mkdir logs
venv\Scripts\python.exe manage.py collectstatic --noinput >> logs\panel.log 2>&1

:loop
echo [%date% %time%] Panel ishga tushmoqda >> logs\panel.log
venv\Scripts\python.exe -m waitress --listen=127.0.0.1:8000 config.wsgi:application >> logs\panel.log 2>&1
ping -n 11 127.0.0.1 > nul
goto loop