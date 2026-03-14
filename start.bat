@echo off
echo Starting NaviX backend...
start /b python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 > nul 2>&1

timeout /t 2 /nobreak > nul

:: Capture the PID of the uvicorn process
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr "PID:"') do set BACKEND_PID=%%a

echo Backend started (PID: %BACKEND_PID%)
echo Starting NaviX Streamlit UI...

streamlit run scripts/demo_ui.py

echo Streamlit exited. Stopping backend (PID: %BACKEND_PID%)...
taskkill /PID %BACKEND_PID% /F > nul 2>&1
echo Done.
