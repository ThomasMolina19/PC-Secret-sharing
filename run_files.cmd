@echo off
setlocal enabledelayedexpansion
set n=6

for /L %%i in (1,1,%n%) do (
    set /A port=5000 + %%i
    start "" python main.py --ip 192.168.1.5 --port !port! --uuid %%i --file connections.json
)
