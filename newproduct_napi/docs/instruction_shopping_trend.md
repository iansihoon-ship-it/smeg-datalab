# 작업 지시서: 최근 1년 일자별 쇼핑 트렌드 수집 및 확인

본 문서는 네이버 쇼핑인사이트 API를 활용하여 최근 1년 동안의 일자별 쇼핑 트렌드 데이터를 수집하고 검증하는 과정을 안내합니다.

## 1. 목적
- 최근 1년 내 특정 쇼핑 분야의 일간 클릭 트렌드 데이터 확보
- 데이터의 연속성 및 정합성 확인

## 2. 사전 준비 사항
- **API 권한**: 네이버 개발자 센터에서 '데이터랩(쇼핑인사이트)' API가 권한 설정된 App의 Client ID와 Client Secret 준비
- **가상환경**: 서비스 루트의 `.venv` 활성화 및 필요한 라이브러리(`requests`, `pandas` 등) 설치 확인

## 3. 데이터 수집 단계

### 3.1 기간 설정
- **시작일(startDate)**: 현재 날짜로부터 1년 전 (예: 2025-03-17)
- **종료일(endDate)**: 현재 날짜 (예: 2026-03-16)
- **시간 단위(timeUnit)**: `date` (일간 데이터 수집을 위해 필수)

### 3.2 대상 분야 설정
- 대상 분야의 `cat_id` 확인 (예: 패션의류 50000000)
- `category` 파라미터에 해당 이름과 ID 배열 설정

### 3.3 API 호출 (Python 예시)
```python
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 설정 (환경 변수 사용 권장)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
url = "https://openapi.naver.com/v1/datalab/shopping/categories"

# 기간 계산 (최근 1년)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

body = {
    "startDate": start_date,
    "endDate": end_date,
    "timeUnit": "date",
    "category": [
        {"name": "패션의류", "param": ["50000000"]}
    ],
    "device": "", # 전체
    "gender": "", # 전체
    "ages": []    # 전체
}

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret,
    "Content-Type": "application/json"
}

# 인증 정보 확인용 로그 (실서비스에서는 제거 권장)
if not client_id or not client_secret:
    print("Error: API credentials not found in environment variables.")
else:
    response = requests.post(url, headers=headers, data=json.dumps(body))
    res_code = response.status_code

    if res_code == 200:
        data = response.json()
        print("Successfully fetched data.")
        # 데이터 처리 로직
    else:
        print(f"Error Code: {res_code}")
        print(response.text)
```

> [!IMPORTANT]
> **보안 주의 사항**: API Client ID와 Secret은 소스 코드나 마크다운 문서에 직접 노출하지 마십시오. `.env` 파일을 프로젝트 루트에 생성하고 다음과 같이 설정한 뒤, `.gitignore`에 추가하여 관리하십시오.
> ```env
> NAVER_CLIENT_ID=여러분의_ID
> NAVER_CLIENT_SECRET=여러분의_SECRET
> ```

## 4. 데이터 확인 및 검증

### 4.1 데이터 구조 확인
- 응답 데이터 내 `results` -> `data` 배열에 각 날짜별 `period`와 `ratio` 값이 존재하는지 확인합니다.
- `ratio`는 해당 기간 내 최댓값을 100으로 설정한 상대적 수치임을 유의합니다.

### 4.2 누락 데이터 체크
- 수집된 데이터의 개수가 365개(또는 366개)인지 확인하여 중간에 누락된 날짜가 없는지 점검합니다.

### 4.3 데이터 시각화 및 검토
- 수집된 데이터를 시각화하여 비정상적인 튀는 값이나 끊김 현상이 있는지 확인합니다.
- (옵션) `py-eda` 스킬을 활용하여 수집된 데이터의 기초 통계 및 트렌드를 심층 분석합니다.

## 5. 결과 저장
- 수집된 원본 데이터는 `raw_data/` 폴더에 JSON 형식으로 저장합니다.
- 정제된 데이터는 `processed_data/` 폴더에 CSV 형식으로 저장하여 향후 분석에 활용합니다.

---
*참고 문서: [shopping_insight.md](./shopping_insight.md)*
