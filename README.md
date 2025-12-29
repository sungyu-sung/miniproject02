# 뉴스 요약 및 감정 분석 챗봇

Hugging Face 모델을 활용한 한국어 뉴스 요약 및 감정 분석 시스템

## 프로젝트 개요

뉴스 URL을 입력하면 AI가 자동으로 기사를 크롤링하여 요약하고, 해당 기사의 감정(긍정/부정/중립)을 분석해주는 웹 애플리케이션입니다.

### 주요 기능

| 기능 | 설명 |
|------|------|
| 뉴스 크롤링 | URL에서 뉴스 본문 자동 추출 |
| 텍스트 요약 | KoBART 모델로 핵심 내용 요약 |
| 감정 분석 | 긍정/부정/중립 분류 및 신뢰도 점수 |
| 키워드 추출 | 주요 키워드 자동 추출 |

## 기술 스택

### Frontend
- **Streamlit** - Python 기반 웹 UI 프레임워크
- **Plotly** - 인터랙티브 시각화

### Backend & ML
- **Python 3.10+**
- **Transformers** - Hugging Face 모델 활용
- **newspaper3k / BeautifulSoup4** - 웹 크롤링

### Hugging Face 모델

| 용도 | 모델 |
|------|------|
| 텍스트 요약 | `gogamza/kobart-summarization` |
| 감정 분석 | `snunlp/KR-FinBert-SC` |
| 키워드 추출 | `KeyBERT` + `jhgan/ko-sroberta-multitask` |

## 프로젝트 구조

```
miniproject02/
├── app.py                      # Streamlit 메인 앱
├── requirements.txt            # 의존성 패키지
├── SYSTEM_DESIGN.md            # 시스템 설계 문서
├── README.md                   # 프로젝트 설명
│
├── services/                   # 비즈니스 로직
│   ├── crawler.py              # 뉴스 크롤링 서비스
│   ├── summarizer.py           # 텍스트 요약 서비스
│   ├── sentiment.py            # 감정 분석 서비스
│   └── keywords.py             # 키워드 추출 서비스
│
├── models/                     # 모델 관련
│   ├── model_loader.py         # Hugging Face 모델 로더
│   └── schemas.py              # 데이터 스키마 정의
│
├── utils/                      # 유틸리티
│   ├── text_processor.py       # 텍스트 전처리
│   └── validators.py           # URL/텍스트 검증
│
├── components/                 # Streamlit UI 컴포넌트
│   ├── sidebar.py              # 사이드바 컴포넌트
│   ├── result_display.py       # 결과 표시 컴포넌트
│   └── charts.py               # 차트 컴포넌트
│
└── tests/                      # 테스트
    └── __init__.py
```

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│   URL 입력 → 요약 결과 표시 → 감정 분석 시각화              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│   Crawler → Summarizer → Sentiment Analyzer → Keywords      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Hugging Face Models                         │
│      KoBART (요약)  |  KR-FinBert (감정)  |  KeyBERT        │
└─────────────────────────────────────────────────────────────┘
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
streamlit run app.py
```

### 3. 브라우저에서 접속

```
http://localhost:8501
```

## 사용 방법

1. 뉴스 URL 입력란에 분석하고 싶은 뉴스 기사 URL을 입력
2. "분석하기" 버튼 클릭
3. AI가 자동으로 기사를 분석하여 결과 표시:
   - 기사 요약
   - 감정 분석 (긍정/부정/중립)
   - 주요 키워드

## 지원 뉴스 사이트

- 네이버 뉴스
- 다음 뉴스
- 조선일보, 동아일보, 중앙일보
- 한겨레, 경향신문
- 연합뉴스
- 그 외 대부분의 한국어 뉴스 사이트

## 개발 현황

- [x] 시스템 설계
- [x] 프로젝트 구조 생성
- [x] 서비스 로직 구현
- [x] UI 컴포넌트 구현
- [ ] 테스트 코드 작성
- [ ] 배포

## 라이선스

MIT License
