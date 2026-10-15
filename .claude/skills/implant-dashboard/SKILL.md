---
name: implant-dashboard
description: 임플란트 수술 현황판(대시보드)을 매달 갱신한다. 수술관리 시스템에서 내보낸 월별 엑셀(View·실적요약 시트, 파일명에 "YYYY-MM-01_YYYY-MM-DD")을 기존 대시보드 데이터에 병합하고 다시 게시한다. "대시보드 업데이트", "이번 달 데이터 넣어줘", "임플란트 통계 갱신", 월간 예약 실행에 사용.
---

# 임플란트 수술 현황판 월간 갱신

현황판: https://claude.ai/artifact/SmkW2javknCmVvzVbLtNbZ (비공개)

대시보드의 누적 데이터는 **게시된 페이지 안의 `const RAW = {...}`** 에만 있다.
이 저장소는 공개 저장소이므로 데이터·HTML 결과물·엑셀 파일은 절대 커밋하지 않는다(코드와 템플릿만).

## 1. 내보내기 파일 확보

대상 월은 따로 지정이 없으면 **지난달**이다.

- 사용자가 엑셀을 첨부했으면 그 파일을 쓴다.
- 아니면 Google Drive에서 찾는다: `title contains 'YYYY-MM-01_YYYY-MM-'` (예: `2026-10-01_2026-10-`),
  xlsx 파일. 여러 개면 가장 최근 수정본. `download_file_content`로 받아 스크래치패드의 빈 폴더에 저장한다.
- 못 찾으면 멈추고, 어느 달 파일이 필요한지와 파일명 형식을 사용자에게 알린다. 추측으로 진행하지 않는다.

이미 반영된 달의 파일(예: 마감 후 다시 내보낸 파일)을 넣어도 된다. 같은 달은 통째로 교체된다.

## 2. 현재 대시보드 가져오기

`Artifact` 도구 `action: "read"`, `url`: 위 현황판 링크. 결과에 표시된 저장 파일 경로가 `--current` 입력이다.

## 3. 병합·재생성

```bash
python3 -I .claude/skills/implant-dashboard/scripts/update_dashboard.py \
  --current <읽어온 html 경로> --export <엑셀1> [--export <엑셀2>] --out <스크래치패드>/out
```

출력 JSON 보고서를 확인한다.

- `cases`·`fixtures`가 `check_cases`·`check_fixtures`(엑셀 실적요약)와 다르면 게시하지 말고 원인을 보고한다.
- `new_doctors`가 있으면 기존 표기와 맞출지 사용자에게 묻는다. 맞추려면 `out/data.json`의
  `config.doctor_alias`에 `{"원본이름": "표기"}`를 넣고 `--current out/data.json`으로 다시 실행한다.
- `closed: false`(미마감)이거나 `last_day`가 월말보다 4일 이상 이르면, 다음 달에 마감본으로 다시 돌리라고 안내한다.

## 4. 게시

`Artifact` 도구로 `file_path: <out>/implant-dashboard.html`, `url`: 현황판 링크로 게시한다(같은 링크 유지).
`icon`은 넘기지 않는다.

## 5. 보고 (한국어, 짧게)

- 반영한 달, 신규 식립·제거·재식립, 전월·전년 동월 대비
- 연 누계 전년 대비
- 눈에 띄는 변화 2~3개(업체 점유율, 골이식 비율, 제거 원인, 시뮬레이션·해피콜 시행률)
- 검증 결과(실적요약과 일치 여부), 미마감 여부
- 현황판 링크

## 집계 기준 (템플릿 하단 설명과 동일하게 유지)

- 신규 식립: 구분 "일반·보험"의 `신규` 행 사용수량 합. 구분 `Free`는 제외.
- 제거: `제거` 행. 재식립: `재식립` + `제거&재식립` 행.
- 수술 건: 수술일자+차트번호 1건. 해피콜 "제외" 건은 해피콜 시행률 분모에서 뺀다.
- 업체: OSSTEM(TS3BA→TS3, TS4, TS5)→Osstem, NEO→Neo, 유한양행→유한_EVER, 신흥→신흥_EVER, 확인안됨→미기재.

## 파일

- `scripts/update_dashboard.py` — 엑셀 파싱, 월별 집계, 병합, HTML 생성
- `assets/template.html` — 대시보드 템플릿(`__DATA__` 자리에 데이터 삽입). 차트 색은 dataviz 기준
  검증 팔레트(고정 순서)를 쓰며, 업체 색은 업체에 고정된다. 7개 주요 업체 외는 "기타"로 묶는다.
