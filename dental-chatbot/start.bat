@echo off
chcp 65001 >nul
title 치과 AI 서버

:: ── .env 파일에서 API 키 로드 ──────────────────────────────
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%.env" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%SCRIPT_DIR%.env") do (
    if "%%A"=="ANTHROPIC_API_KEY" set "ANTHROPIC_API_KEY=%%B"
  )
)

:: ── API 키 확인 ─────────────────────────────────────────────
if "%ANTHROPIC_API_KEY%"=="" (
  echo.
  echo  [오류] ANTHROPIC_API_KEY 가 설정되지 않았습니다.
  echo.
  echo  dental-chatbot 폴더에 .env 파일을 만들고 아래 내용을 저장하세요:
  echo  ANTHROPIC_API_KEY=sk-ant-...
  echo.
  pause
  exit /b 1
)

:: ── Python 확인 ─────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo  [오류] Python 이 설치되어 있지 않습니다.
  echo  https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

:: ── 의존성 설치 ─────────────────────────────────────────────
python -c "import anthropic, fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo  패키지 설치 중... 잠시 기다려주세요.
  pip install -r "%SCRIPT_DIR%requirements.txt" -q
)

:: ── 포트 8000 사용 중이면 브라우저만 열기 ──────────────────
netstat -an | find "0.0.0.0:8000" | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
  start "" "http://localhost:8000"
  exit /b 0
)

:: ── 서버 시작 + 브라우저 자동 오픈 ────────────────────────
echo.
echo  ====================================
echo   치과 AI  ^|  X-ray 판독 + 상담 AI
echo  ====================================
echo   주소: http://localhost:8000
echo   종료: 이 창을 닫거나 Ctrl+C
echo  ====================================
echo.

:: 2초 후 브라우저 열기 (백그라운드)
start "" /b cmd /c "timeout /t 2 >nul && start "" http://localhost:8000"

cd /d "%SCRIPT_DIR%"
python server.py
pause
