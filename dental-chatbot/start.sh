#!/bin/bash
# 치과 AI — 서버 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# .env 파일에서 API 키 로드
if [ -f "$SCRIPT_DIR/.env" ]; then
  export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

# API 키 확인
if [ -z "$ANTHROPIC_API_KEY" ]; then
  osascript -e 'display alert "API 키 없음" message "dental-chatbot/.env 파일에 ANTHROPIC_API_KEY=sk-ant-... 를 입력해주세요." as critical'
  exit 1
fi

# 의존성 설치
if ! python3 -c "import anthropic, fastapi, uvicorn" 2>/dev/null; then
  osascript -e 'display notification "패키지를 설치합니다. 잠시 기다려주세요..." with title "치과 AI"'
  pip3 install -r "$SCRIPT_DIR/requirements.txt" -q
fi

# 이미 실행 중이면 브라우저만 열기
if lsof -i :8000 -t &>/dev/null; then
  open "http://localhost:8000"
  exit 0
fi

# 서버 시작 후 브라우저 자동 오픈
(sleep 2 && open "http://localhost:8000") &

osascript -e 'display notification "http://localhost:8000 에서 이용하세요" with title "🦷 치과 AI 시작됨"'

python3 "$SCRIPT_DIR/server.py"
