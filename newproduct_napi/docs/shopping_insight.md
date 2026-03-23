# 쇼핑인사이트 개요 및 API 레퍼런스

쇼핑인사이트 API는 네이버 데이터랩의 쇼핑인사이트 데이터를 프로그래밍 방식으로 추출할 수 있게 해주는 RESTful API입니다.

## 1. 개요
네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서의 검색 클릭 추이 데이터를 JSON 형식으로 반환합니다. 분야별 트렌드 및 키워드별 트렌드를 조회할 수 있습니다.

- **호출 한도**: 하루 1,000회
- **인증 방식**: 비로그인 방식 (Client ID, Client Secret 필요)

## 2. 주요 API 레퍼런스

### 쇼핑인사이트 분야별 트렌드 조회
쇼핑 분야별 검색 클릭 추이를 조회합니다.

- **요청 URL**: `https://openapi.naver.com/v1/datalab/shopping/categories`
- **HTTP 메서드**: POST
- **주요 파라미터 (JSON)**:
    - `startDate`, `endDate`: 조회 기간
    - `timeUnit`: 구간 단위 (date, week, month)
    - `category`: 분야 이름과 파라미터(cat_id)
    - `device`, `gender`, `ages`: 필터링 조건

### 제공되는 기타 API
- 쇼핑인사이트 분야 내 기기별/성별/연령별 트렌드 조회
- 쇼핑인사이트 키워드별 트렌드 조회
- 쇼핑인사이트 키워드 기기별/성별/연령별 트렌드 조회

## 3. 요청 예시 (cURL)
```bash
curl https://openapi.naver.com/v1/datalab/shopping/categories \
  --header "X-Naver-Client-Id: {YOUR_CLIENT_ID}" \
  --header "X-Naver-Client-Secret: {YOUR_CLIENT_SECRET}" \
  --header "Content-Type: application/json" \
  -d '{
    "startDate": "2017-08-01",
    "endDate": "2017-09-30",
    "timeUnit": "month",
    "category": [
      {"name": "패션의류", "param": ["50000000"]},
      {"name": "화장품/미용", "param": ["50000002"]}
    ],
    "device": "pc",
    "gender": "f",
    "ages": ["20", "30"]
  }'
```

---
*출처: [네이버 개발자 센터 - 쇼핑인사이트](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md)*
