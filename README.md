# INMA (Influencer Matching Agent)

**INMA**는 AI 기반의 **인플루언서-상품 매칭 자동화 시스템**입니다.
GPT-4o와 임베딩 기술을 활용하여, 상품의 특성을 분석하고 가장 적합한 인플루언서를 정밀하게 추천합니다.

## 🚀 주요 기능 및 파이프라인 (Pipeline)

본 시스템은 다음과 같은 4단계 데이터 파이프라인으로 동작합니다.

1.  **데이터 감지 (Data Ingestion)**
    *   `watch_db.py`가 3초 간격으로 데이터베이스를 모니터링하여 새로운 인플루언서, 브랜드, 상품 데이터를 감지합니다.
2.  **자동 태깅 (Auto-Tagging with LLM)**
    *   GPT-4o-mini가 채널 설명, 상품 상세 정보를 분석하여 '산업(Industry)', '니치(Niche)', '매칭 태그' 등을 추출합니다.
    *   한국어 표준화 및 카테고리 정규화(Mapping)가 자동으로 수행됩니다.
3.  **벡터화 (Vector Embedding)**
    *   구조화된 태그와 설명을 텍스트 임베딩(`text-embedding-3-small`)으로 변환하여 의미(Semantic) 정보를 저장합니다.
4.  **하이브리드 매칭 (Hybrid Matching)**
    *   **벡터 유사도(40%)** + **키워드 일치(30%)** + **카테고리 규칙** + **참여율(ER)**을 종합하여 최적의 매칭 점수를 산출합니다.

---

## 🛠 기술 스택 (Tech Stack)

이 프로젝트는 다음의 핵심 기술을 기반으로 구축되었습니다.

*   **Language**: Python 3.x
*   **Database**: MongoDB (NoSQL) - 유연한 스키마 및 고속 데이터 처리
*   **AI / LLM**:
    *   **OpenAI API (GPT-4o-mini)**: 데이터 분석 및 구조화된 태깅
    *   **OpenAI Embeddings**: 벡터 검색 구현 (Semantic Search)
*   **Libraries**:
    *   `scikit-learn`: 코사인 유사도 계산
    *   `pymongo`: DB 연동
    *   `numpy`: 벡터 연산

---

## 💻 실행 방법 (How to Run)

### 1. 사전 준비 (Prerequisites)
*   Python 3.10+ 설치
*   MongoDB 연결 문자열 (URI)
*   OpenAI API Key

`.env` 파일을 프로젝트 루트에 생성하고 다음 변수를 설정하세요.
```ini
MONGODB_URI=your_mongodb_uri
OPENAI_API_KEY=your_openai_api_key
DB_NAME=INMA
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 시스템 실행

**A. 자동 태깅 데몬 실행 (Background Service)**
새로운 데이터가 들어오면 자동으로 태깅하고 임베딩을 생성합니다.
```bash
python watch_db.py
```

**B. 인플루언서 태깅 (일회성 배치)**
기존 데이터베이스에 있는 인플루언서들을 일괄 태깅합니다.
```bash
python tag_influencers.py
```

**C. 매칭 & 추천 실행**
특정 상품명에 대해 적합한 인플루언서를 추천받습니다.
```bash
python recommend.py "상품명"
# 예시: python recommend.py 네모팬티
```
