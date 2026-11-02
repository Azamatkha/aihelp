@echo off
rem Botni ishga tushiradi; yiqilsa 10 soniyadan keyin qayta ko'taradi
cd /d "%~dp0.."
set PYTHONUTF8=1
set PYTHONUNBUFFERED=1
if not exist logs mkdir logs

:loop
echo [%date% %time%] Bot ishga tushmoqda >> logs\bot.log
venv\Scripts\python.exe manage.py migrate --noinput >> logs\bot.log 2>&1
venv\Scripts\python.exe manage.py runbot >> logs\bot.log 2>&1
echo [%date% %time%] Bot to'xtadi, qayta ishga tushiriladi >> logs\bot.log
rem "timeout" fon rejimida ishlamaydi, shuning uchun ping bilan kutamiz
ping -n 11 127.0.0.1 > nul
goto loop