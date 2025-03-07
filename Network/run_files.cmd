@echo off
setlocal enabledelayedexpansion
set n=5

for /L %%i in (1,1,%n%) do (
    set /A port=5000 + %%i
    start "" python main.py --ip 172.20.10.9 --port !port! --uuid %%i --file connections.json
)
