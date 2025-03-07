@echo off
setlocal enabledelayedexpansion
set n=6

for /L %%i in (1,1,%n%) do (
    set /A port=5000 + %%i
    start "" python main.py --port !port! --uuid %%i --file connections.json
)
