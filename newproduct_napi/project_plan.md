# 프로젝트 계획서: newproduct_napi

본 문서는 `newproduct_napi` 프로젝트의 일관된 구조와 데이터 관리 체계를 정의합니다.

## 1. 파일 트리 구조 (File Tree)

```text
newproduct_napi/
├── .env                # API 자격 증명 (Client ID, Secret) - GIT 제외 필수
├── .gitignore          # 보안 및 대용량 데이터 업로드 방지
├── docs/               # 문서 및 가이드
│   ├── datalab_intro.md
│   ├── shopping_insight.md
│   ├── shopping_search.md
│   ├── non_login_api_list.md
│   └── instruction_shopping_trend.md
├── scripts/            # 데이터 수집 및 전처리 파이썬 스크립트 (향후 작성)
│   ├── collect_trend.py
│   └── preprocess_data.py
└── data/               # 수집 및 처리된 데이터 저장소
    ├── raw/            # API에서 받은 원본 데이터 (JSON)
    └── processed/      # 분석용 정제 데이터 (CSV)
```

## 2. 데이터 수집 및 저장 규칙

### 2.1 CSV 파일 명명 규칙
수집된 데이터는 분석의 가공성 및 추적성을 위해 다음 형식을 따릅니다.

- **형식**: `[데이터종류]_[카테고리명]_[수집대상기간]_[수집날짜].csv`
- **예시**: `쇼핑트렌드_패션의류_20250317-20260316_20260317.csv`
    - `쇼핑트렌드`: 데이터의 성격 (Shopping Insight - Category Trend)
    - `패션의류`: 조회한 카테고리 명칭
    - `20250317-20260316`: 수집 대상이 된 실제 데이터의 시작일-종료일
    - `20260317`: 실제 API를 호출하여 파일을 생성한 날짜

### 2.2 데이터 포맷
- **파일 형식**: CSV (Comma-Separated Values)
- **인코딩**: `utf-8-sig` (Excel 한글 깨짐 방지)
- **필수 컬럼**: `period` (날짜), `ratio` (상대 수치), `category_name` (추적용)

## 3. 보안 관리 계획

### 3.1 자격 증명 관리 (.env)
`client_id`와 `client_secret`은 코드나 문서에 포함하지 않고, 루트의 `.env` 파일을 통해 관리합니다.

**[.env 예시]**
```env
CLIENT_ID=Waa8neiFscq90VwwTvw8
CLIENT_SECRET=J0lCX7GEEv
```

### 3.2 소스 코드 반영
모든 파이썬 스크립트는 `python-dotenv` 패키지를 사용하여 아래와 같이 자격 증명을 로드하도록 설계합니다.

```python
import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
```

---
*본 계획서는 프로젝트의 표준 가이드라인이며, 작업 진행 상황에 따라 업데이트될 수 있습니다.*
