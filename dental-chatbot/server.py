"""
치과 상담 AI 챗봇 서버
- Claude API (claude-opus-4-7) 기반
- FastAPI + 스트리밍 지원
- 카카오톡 연동 구조 포함
"""

import json
import os
from typing import Optional

import anthropic
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="치과 상담 AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── 시스템 프롬프트 ──────────────────────────────────────────────────────────

DENTAL_SYSTEM_PROMPT = """당신은 대한민국 최고 수준의 치과 상담 전문 AI 어시스턴트입니다.
환자가 편안하고 신뢰할 수 있는 상담 경험을 얻도록 최선을 다하세요.

## 역할
- 임플란트, 충치 치료, 스케일링, 잇몸 치료, 미백, 교정 등 폭넓은 치과 상담
- 환자의 불안과 걱정을 공감하며 해소
- 치료의 필요성과 효과를 설득력 있게 설명해 치료 수용률 향상
- 자연스러운 예약 유도

## 환자 유형별 맞춤 전략

### 비용 민감형 (치료비 걱정, 보험 관심)
- 건강보험 적용 항목 먼저 안내 (스케일링 연 1회, 임플란트 급여 기준 등)
- "지금 치료하면 나중에 더 큰 비용을 막을 수 있어요" 강조
- 치료 단계별 분납 가능성 언급

### 통증 공포형 (치과 공포증, 통증 두려움)
- 첫 마디에 공감: "많은 분들이 같은 걱정을 하세요"
- 무통 마취, 수면(의식하진정) 치료 옵션 소개
- "요즘은 정말 많이 발전했어요. 걱정보다 훨씬 편하실 거예요"

### 심미형 (외관·미용 결과 관심)
- 자연스러운 결과물, 전후 차이 강조
- 라미네이트, 올세라믹 크라운, 투명 교정 등 심미 치료 언급

### 건강 중심형 (예방, 구강 건강 전반)
- 방치 시 합병증 (잇몸뼈 소실, 인접 치아 영향) 설명
- 정기 검진·예방 치료의 장기적 이점 강조

### 빠른 결과형 (즉각적 해결 원함)
- 당일 치료 가능 여부, 치료 횟수 최소화 방안 안내
- "내원 횟수를 줄이는 방향으로 계획 세울 수 있어요"

## 주요 치료 정보

### 임플란트
- 자연치아와 동일한 기능과 심미성, 주변 치아 손상 없음
- 치료 기간: 뼈 이식 없는 경우 3~4개월, 뼈 이식 시 6개월 이상
- 건강보험: 65세 이상 평생 2개 급여 적용 (본인부담 30%)
- 주의: "정확한 비용은 파노라마 X-ray와 CT 촬영 후 안내드릴 수 있어요"

### 충치 치료
- 초기(레진): 1회 치료, 보험 적용
- 중기(인레이/온레이): 2회 내원, 재료별 비용 차이
- 신경 침범(근관치료+크라운): 3~5회 내원 필요
- "조기 발견이 치료비와 치료 기간 모두 줄여요"

### 스케일링
- 건강보험 연 1회 적용 (본인부담 약 15,000~20,000원)
- 시술 시간 20~30분, 잇몸 출혈은 정상 반응
- 6개월마다 권장, 잇몸병의 핵심 예방책

### 잇몸 치료
- 치석·치태 제거로 잇몸 염증 해소
- 심한 경우 잇몸 수술 필요, 단계별 접근

## 상담 진행 방식
1. **공감** → 2. **전문 정보 제공** → 3. **맞춤 해결책 제안** → 4. **예약 유도**

### 예약 유도 문장 (상황에 맞게 선택)
- "정확한 진단은 직접 보여야 알 수 있어요. 초진 상담은 무료로 진행하고 있어요."
- "지금 빠른 시일에 방문하시면 오늘 X-ray 촬영 후 바로 치료 계획 세울 수 있어요."
- "언제 시간이 가장 좋으세요? 방문 예약을 도와드릴게요."

## 응답 규칙
- **반드시 한국어**로만 답변
- 3~5문장 내외로 간결하게 (너무 길면 읽기 힘들어요)
- 공감 표현 먼저, 그다음 정보 제공
- 응급 증상(극심한 통증·부종·고열 동반)은 즉시 방문 강력 권고
- 진단이나 확정적 판단은 하지 않고, 방문 검진을 권유
"""

PATIENT_ANALYSIS_PROMPT = """치과 상담 대화를 분석해 환자 유형과 상담 인사이트를 JSON으로만 반환하세요.

환자 유형 코드:
- cost_sensitive: 비용 민감형
- pain_fearful: 통증 공포형
- aesthetic_focused: 심미형
- health_focused: 건강 중심형
- quick_result: 빠른 결과형
- general: 일반형

반환 형식 (JSON만, 설명 없이):
{
  "primary_type": "유형코드",
  "type_label": "한글 유형명",
  "confidence": 0.0~1.0,
  "concerns": ["걱정 키워드 1", "걱정 키워드 2"],
  "treatment_interest": ["관심 치료 1"],
  "appointment_readiness": "높음|중간|낮음",
  "strategy_tip": "이 환자에게 효과적인 상담 전략 한 줄"
}
"""

SUMMARY_PROMPT = """치과 상담 대화를 분석해 상담 요약을 JSON으로만 반환하세요.

반환 형식 (JSON만, 설명 없이):
{
  "chief_complaint": "주요 증상/불편 요약",
  "treatments_discussed": ["논의된 치료 1", "치료 2"],
  "patient_type": "환자 유형",
  "appointment_readiness": "높음|중간|낮음",
  "next_steps": ["권장 다음 단계 1", "단계 2"],
  "summary_text": "전체 상담 2~3문장 요약"
}
"""

# ── 요청/응답 모델 ────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

class AnalysisRequest(BaseModel):
    messages: list[Message]

class KakaoRequest(BaseModel):
    userRequest: dict
    bot: Optional[dict] = None
    action: Optional[dict] = None

class QuestionnaireRequest(BaseModel):
    name: Optional[str] = None
    birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    visit_reason: Optional[list[str] | str] = None
    chief_complaint: Optional[str] = None
    selected_teeth: Optional[str] = None
    has_pain: Optional[str] = None
    pain_level: Optional[str] = None
    pain_onset: Optional[str] = None
    pain_type: Optional[list[str] | str] = None
    last_visit: Optional[str] = None
    dental_anxiety: Optional[str] = None
    systemic: Optional[list[str] | str] = None
    has_medication: Optional[str] = None
    medications: Optional[str] = None
    has_allergy: Optional[str] = None
    allergy_type: Optional[list[str] | str] = None
    allergy_detail: Optional[str] = None
    pregnancy: Optional[str] = None
    brushing: Optional[str] = None
    oral_care: Optional[list[str] | str] = None
    smoking: Optional[str] = None
    drinking: Optional[str] = None
    privacy_agree: Optional[str] = None

# ── 엔드포인트 ────────────────────────────────────────────────────────────────

@app.post("/chat")
async def chat(req: ChatRequest):
    """스트리밍 채팅 엔드포인트"""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    def generate():
        try:
            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=1024,
                thinking={"type": "adaptive"},
                system=[
                    {
                        "type": "text",
                        "text": DENTAL_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
        except anthropic.APIError as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/analyze")
async def analyze_patient(req: AnalysisRequest):
    """환자 유형 분석"""
    if len(req.messages) < 2:
        return {"primary_type": "general", "type_label": "일반형", "confidence": 0.0,
                "concerns": [], "treatment_interest": [], "appointment_readiness": "낮음",
                "strategy_tip": "더 많은 대화가 필요합니다."}

    conversation = "\n".join(f"{m.role}: {m.content}" for m in req.messages)

    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        system=PATIENT_ANALYSIS_PROMPT,
        messages=[{"role": "user", "content": f"분석할 대화:\n\n{conversation}"}],
    )

    try:
        return json.loads(resp.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {"primary_type": "general", "type_label": "일반형", "confidence": 0.5,
                "concerns": [], "treatment_interest": [], "appointment_readiness": "중간",
                "strategy_tip": "분석 중 오류가 발생했습니다."}


@app.post("/summarize")
async def summarize(req: AnalysisRequest):
    """상담 내용 요약"""
    if not req.messages:
        raise HTTPException(status_code=400, detail="상담 내용이 없습니다.")

    conversation = "\n".join(f"{m.role}: {m.content}" for m in req.messages)

    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        system=SUMMARY_PROMPT,
        messages=[{"role": "user", "content": f"요약할 대화:\n\n{conversation}"}],
    )

    try:
        return json.loads(resp.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {"summary_text": resp.content[0].text if resp.content else "요약 실패"}


@app.post("/kakao")
async def kakao_webhook(req: KakaoRequest):
    """카카오톡 챗봇 연동 (i-talk/카카오채널 Skill 서버 형식)"""
    user_utterance = req.userRequest.get("utterance", "")
    if not user_utterance:
        return _kakao_simple_text("안녕하세요! 치과 상담 AI입니다. 궁금한 점을 말씀해주세요.")

    resp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=400,  # 카카오톡 말풍선 글자 수 고려
        system=[
            {
                "type": "text",
                "text": DENTAL_SYSTEM_PROMPT
                    + "\n\n카카오톡 채널이므로 200자 이내로 간결하게 답변하세요.",
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_utterance}],
    )

    reply = resp.content[0].text if resp.content else "잠시 후 다시 시도해주세요."

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": reply}}],
            "quickReplies": [
                {"label": "임플란트 문의", "action": "message",
                 "messageText": "임플란트에 대해 자세히 알고 싶어요"},
                {"label": "치료 비용", "action": "message",
                 "messageText": "치료비가 얼마나 드나요?"},
                {"label": "스케일링", "action": "message",
                 "messageText": "스케일링은 얼마나 자주 해야 하나요?"},
                {"label": "예약하기", "action": "message",
                 "messageText": "진료 예약하고 싶어요"},
            ],
        },
    }


def _kakao_simple_text(text: str) -> dict:
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": text}}]}}


@app.get("/questionnaire")
async def questionnaire_page():
    try:
        with open("questionnaire.html", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>questionnaire.html을 찾을 수 없습니다.</h1>", status_code=404)


@app.post("/questionnaire/submit")
async def questionnaire_submit(req: QuestionnaireRequest):
    """초진 설문지 제출 처리"""
    return {"status": "ok", "message": "설문지가 제출되었습니다."}


@app.get("/")
async def root():
    try:
        with open("index.html", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html을 찾을 수 없습니다.</h1>", status_code=404)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
