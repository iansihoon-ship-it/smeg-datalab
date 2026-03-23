# 쇼핑 검색 API 가이드

쇼핑 검색 API는 네이버 검색의 쇼핑 검색 결과를 XML 또는 JSON 형식으로 반환하는 서비스입니다.

## 1. 개요
네이버 쇼핑에 등록된 수많은 상품 정보를 프로그램에서 검색하고 결과를 받아볼 수 있습니다.

- **인증 방식**: 비로그인 방식 (Client ID, Secret 사용)
- **프로토콜/메서드**: HTTPS / GET

## 2. API 레퍼런스

### 쇼핑 검색 결과 조회
- **요청 URL**: `https://openapi.naver.com/v1/search/shop.json` (또는 `.xml`)
- **HTTP 메서드**: GET
- **주요 파라미터**:
    - `query`: 검색어 (UTF-8 인코딩 필수)
    - `display`: 한 번에 표시할 검색 결과 개수 (최대 100)
    - `start`: 검색 시작 위치
    - `sort`: 정렬 기준 (sim: 유사도, date: 날짜, asc: 가격 오름차순, dsc: 가격 내림차순)
    - `exclude`: 특정 옵션 제외 (중고: used, 대여: rental 등)

## 3. 요청 예시 (cURL)
```bash
curl "https://openapi.naver.com/v1/search/shop.json?query=%EC%A3%BC%EC%8B%9D&display=10&start=1&sort=sim" \
  -H "X-Naver-Client-Id: {YOUR_CLIENT_ID}" \
  -H "X-Naver-Client-Secret: {YOUR_CLIENT_SECRET}"
```

## 4. 응답 구성
- `lastBuildDate`: 응답 생성 시간
- `total`: 총 검색 결과 수
- `start`: 시작 위치
- `display`: 표시 개수
- `items`: 개별 상품 정보 리스트 (title, link, image, lprice, hprice, mallName, productId, productType 등)

---
*출처: [네이버 개발자 센터 - 쇼핑 검색](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)*
