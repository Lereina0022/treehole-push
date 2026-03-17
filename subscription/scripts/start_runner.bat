@echo off
cd /d %~dp0\..
:loop
C:\Users\Zys90\.conda\envs\general\python.exe -m app.runner_core
timeout /t 6000 >nul
goto loop