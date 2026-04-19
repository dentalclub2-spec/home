#!/bin/bash
# 치과 상담 AI 챗봇 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "오류: ANTHROPIC_API_KEY 환경변수를 설정해주세요."
  echo "  export ANTHROPIC_API_KEY=sk-ant-..."
  exit 1
fi

if ! python3 -c "import anthropic" 2>/dev/null; then
  echo "의존성 설치 중..."
  pip install -r requirements.txt -q
fi

echo ""
echo "🦷 치과 상담 AI 챗봇 시작"
echo "   http://localhost:8000 에서 이용하세요"
echo "   카카오톡 Webhook: POST http://localhost:8000/kakao"
echo "   종료: Ctrl+C"
echo ""

python3 server.py
