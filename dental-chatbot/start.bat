@echo off
for /f "tokens=1,* delims==" %%A in (.env) do (
  if "%%A"=="ANTHROPIC_API_KEY" set "ANTHROPIC_API_KEY=%%B"
)
pip install -r requirements.txt -q
start "" /b cmd /c "timeout /t 3 >nul && start http://localhost:8000"
python server.py
pause
