# 비로그인 방식 오픈 API 리스트

비로그인 방식 오픈 API는 HTTP 헤더에 클라이언트 아이디와 클라이언트 시크릿 값만 전송하여 사용할 수 있는 API로, 별도의 로그인 인증 과정이 필요 없습니다.

## 주요 비로그인 방식 API

### 1. 데이터랩 (DataLab)
- **검색어 트렌드**: `https://openapi.naver.com/v1/datalab/search`
- **쇼핑인사이트 분야별**: `https://openapi.naver.com/v1/datalab/shopping/categories`
- **쇼핑인사이트 키워드별**: `https://openapi.naver.com/v1/datalab/shopping/category/keywords`

### 2. 검색 (Search)
- **뉴스**: `https://openapi.naver.com/v1/search/news`
- **블로그**: `https://openapi.naver.com/v1/search/blog`
- **쇼핑**: `https://openapi.naver.com/v1/search/shop`
- **지역/웹문서/이미지/지식iN/책/카페글**: 각 카테고리별 URL 제공

### 3. 기타 서비스
- **이미지/음성 캡차**: 인증 기능을 위한 캡차 서비스
- **네이버 공유하기**: 콘텐츠 공유 기능
- **Clova Face Recognition**: 얼굴 인식 및 감지 기능

---
*출처: [네이버 개발자 센터 - API 종류](https://developers.naver.com/docs/common/openapiguide/apilist.md)*
