@echo off
chcp 65001 >nul
title 바로가기 생성

set "SCRIPT_DIR=%~dp0"
set "SHORTCUT=%USERPROFILE%\Desktop\치과 AI.lnk"

:: PowerShell 로 데스크탑 바로가기 생성
powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$s = $ws.CreateShortcut('%SHORTCUT%');" ^
  "$s.TargetPath = '%SCRIPT_DIR%start.bat';" ^
  "$s.WorkingDirectory = '%SCRIPT_DIR%';" ^
  "$s.Description = '치과 AI — X-ray 판독 + 상담 AI';" ^
  "$s.IconLocation = 'shell32.dll,13';" ^
  "$s.Save();"

if exist "%SHORTCUT%" (
  echo.
  echo  [완료] 데스크탑에 "치과 AI" 바로가기가 생성되었습니다!
  echo.
  echo  실행 전 준비사항:
  echo    dental-chatbot 폴더에 .env 파일 생성
  echo    내용: ANTHROPIC_API_KEY=sk-ant-...
  echo.
) else (
  echo  [오류] 바로가기 생성 실패. 관리자 권한으로 다시 실행해보세요.
)
pause
