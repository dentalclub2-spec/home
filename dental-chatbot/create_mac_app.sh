#!/bin/bash
# Mac 데스크탑 앱 아이콘 생성 스크립트
# 실행: bash create_mac_app.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="치과 AI"
APP_PATH="$HOME/Desktop/${APP_NAME}.app"

echo "🦷 Mac 앱 아이콘 생성 중..."

# .app 폴더 구조 생성
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# 실행 파일 생성
cat > "$APP_PATH/Contents/MacOS/치과AI" << LAUNCHER
#!/bin/bash
SCRIPT_DIR="${SCRIPT_DIR}"

# .env 파일에서 API 키 로드
if [ -f "\$SCRIPT_DIR/.env" ]; then
  export \$(grep -v '^#' "\$SCRIPT_DIR/.env" | xargs)
fi

# API 키 확인
if [ -z "\$ANTHROPIC_API_KEY" ]; then
  osascript -e 'display alert "API 키 없음" message "dental-chatbot/.env 파일에 다음 내용을 저장하세요:\n\nANTHROPIC_API_KEY=sk-ant-..." as critical'
  exit 1
fi

# 의존성 확인 및 설치
if ! python3 -c "import anthropic, fastapi, uvicorn" 2>/dev/null; then
  osascript -e 'display notification "패키지 설치 중... 잠시 기다려주세요" with title "치과 AI"'
  pip3 install -r "\$SCRIPT_DIR/requirements.txt" -q
fi

# 이미 실행 중이면 브라우저만 열기
if lsof -i :8000 -t &>/dev/null; then
  open "http://localhost:8000"
  exit 0
fi

# 서버 시작 + 브라우저 자동 오픈
(sleep 2 && open "http://localhost:8000") &
osascript -e 'display notification "브라우저가 자동으로 열립니다" with title "🦷 치과 AI 시작됨"'

cd "\$SCRIPT_DIR"
python3 "\$SCRIPT_DIR/server.py"
LAUNCHER

chmod +x "$APP_PATH/Contents/MacOS/치과AI"

# Info.plist 생성
cat > "$APP_PATH/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>치과 AI</string>
  <key>CFBundleDisplayName</key>
  <string>치과 AI</string>
  <key>CFBundleExecutable</key>
  <string>치과AI</string>
  <key>CFBundleIdentifier</key>
  <string>com.dentalclub.ai</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleIconFile</key>
  <string>AppIcon</string>
  <key>LSUIElement</key>
  <false/>
</dict>
</plist>
PLIST

# 치아 이모지 아이콘 생성 (Python 이용)
python3 << 'PYICON'
import os, struct, zlib

# 간단한 PNG 아이콘 (흰 배경 + 🦷 텍스트) 생성
# Python 기본 라이브러리만 사용
try:
    from PIL import Image, ImageDraw, ImageFont
    size = 512
    img = Image.new("RGBA", (size, size), (43, 108, 176, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 300)
    except Exception:
        font = ImageFont.load_default()
    draw.text((size//2, size//2), "🦷", font=font, anchor="mm")
    icon_path = os.path.expanduser("~/Desktop/치과 AI.app/Contents/Resources/AppIcon.png")
    img.save(icon_path)
    print("아이콘 생성 완료 (PIL)")
except ImportError:
    print("PIL 없음 — 기본 아이콘 사용")
PYICON

echo ""
echo "✅ 완료! 데스크탑에 '치과 AI.app' 아이콘이 생성되었습니다."
echo ""
echo "📌 첫 실행 전 필수 설정:"
echo "   1. dental-chatbot 폴더에 .env 파일 생성"
echo "   2. 파일 내용:  ANTHROPIC_API_KEY=sk-ant-..."
echo ""
echo "⚠️  처음 실행 시 '확인되지 않은 개발자' 경고가 뜨면:"
echo "   시스템 설정 → 개인정보 보호 및 보안 → '확인 없이 열기' 클릭"
echo ""
