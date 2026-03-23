# 스메그 EGF03 데이터 수집 및 저장 계획

본 문서는 스메그(SMEG) EGF03 그라인더 일체형 반자동 커피머신의 리뷰 및 제품 데이터를 수집하기 위한 기술적 가이드라인을 담고 있습니다.

## 1) HTTP 요청 정보 (HTTP Request Info)

Request URL
https://search.shopping.naver.com/api/review?nvMid=53263372916&page=1&pageSize=20&sortType=QUALITY&isNeedAggregation=Y
Request Method
GET
Status Code
200 OK
Remote Address
223.130.192.241:443
Referrer Policy
unsafe-url

referer
https://search.shopping.naver.com/catalog/54608922345?query=%EC%8A%A4%EB%A9%94%EA%B7%B8%20EGF03&NaPm=ct%3Dmmvmzp3k%7Cci%3D9f97c422e2f79e08f42e55ff60c56959593a525a%7Ctr%3Dslsl%7Csn%3D95694%7Chk%3Dde7f616d5da490f0b5c2400bcc596e144532bc13
sec-ch-ua
"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"
sec-ch-ua-arch
"x86"
sec-ch-ua-bitness
"64"
sec-ch-ua-form-factors
"Desktop"
sec-ch-ua-full-version-list
"Not:A-Brand";v="99.0.0.0", "Google Chrome";v="145.0.7632.160", "Chromium";v="145.0.7632.160"
sec-ch-ua-mobile
?0
sec-ch-ua-model
""
sec-ch-ua-platform
"Windows"
sec-ch-ua-platform-version
"19.0.0"
sec-ch-ua-wow64
?0
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36

## 2) Payload 정보 (Request Payload)

nvMid=53263372916&page=1&pageSize=20&sortType=QUALITY&isNeedAggregation=Y


## 3) Response 일부 (JSON Snippet)

서버로부터 반환되는 리뷰 데이터의 구조입니다.

```json
{
{
    "totalCount": 102,
    "reviews": [
        {
            "id": "4734563663-smegkorea1-11461851831",
            "buyOption": "통합색상: 크림 / 사은품: 반자동 마스터 키트+빅토리아 블렌드 원두 1봉",
            "content": "드디어 저희 집에도 꿈에 그리던 머신이 도착했어요!<br>주문은 4월 30일에 했고, 5월 12일에 기사님이 직접 오셔서 설치부터 사용방법까지 꼼꼼히 설명해주셨습니다. 덕분에 처음부터 어렵지 않게 사용할 수 있었어요.<br><br>저희 부부는 평소에 커피를 정말 좋아해서 거의 매일 카페에 들렀는데, &lsquo;우리만의 홈카페&rsquo;를 꾸미는 게 소원이었거든요. 그래서 디자인뿐 아니라 성능까지 꼼꼼히 비교해보고 스메그 커피머신을 선택했어요.<br><br>같이 주신 원두로 매일 아침 신선한 커피를 내려 마시는데 향도 좋고 깊은 맛이 정말 일품이에요. 특히 분쇄도 조절이 가능해서 원두 종류에 따라 저희 입맛에 맞게 세팅을 바꿔가며 다양한 맛을 즐길 수 있다는 게 큰 장점이었어요.<br><br>카푸치노를 좋아해서 우유 스팀도 자주 해 먹는데, 처음엔 거품 내는 게 서툴러서 조금 연습이 필요했지만, 스팀봉이 사용하기 편리해서 몇 번 하다보니 점점 익숙해지고 있어요. 이제 카페에서 마시는 것 못지않게 맛있게 만들어 마십니다.<br><br>그리고 무엇보다 좋은 점은, 원두뿐만 아니라 저울과 템퍼 등 커피 만들 때 필요한 구성품도 함께 주셔서 별도로 구매하지 않아도 바로 커피를 내릴 수 있어 정말 편리했습니다. 좋은 구성품을 따로 찾아 사는 것도 은근히 일인데, 스메그에서 고급 구성품을 함께 주셔서 너무 만족스러웠어요.<br><br>집안 분위기도 확 바뀌고, 나만의 카페를 차린 것처럼 기분이 좋아요. 홈카페를 준비하시는 분들께 정말 추천드려요.<br><br>스메그 EGF03, 디자인부터 성능까지 정말 만족스러운 머신이에요. 커피를 사랑하는 분들이라면 정말 후회 없으실 거예요!<br><br>💖 감사합니다! 💖",
            "aidaCreateTime": "2025-05-31 15:44:24",
            "aidaModifyTime": "2025-06-01 03:46:58",
            "esModi
}
``` 하위 내용

## 4) 수집 확인 결과

- **수집 성공 여부**: 확인됨 (HTTP 200 OK)
- **수집 내용**: 1페이지 요청 시 20개의 리뷰 데이터가 JSON 형식으로 정확하게 수신되었습니다.
- **특이 사항**: `Referer` 헤더가 누락될 경우 403 Forbidden 오류가 발생할 수 있으므로 주의가 필요합니다.

## 5) 해당 수집 내용을 바탕으로 sqlitedb 스키마를 구성하고 해당 db에 데이터를 저장할 것