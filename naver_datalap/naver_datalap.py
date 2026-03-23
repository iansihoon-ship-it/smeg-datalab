import os
import json
import urllib.request
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib  # 한글 폰트 깨짐 방지용 외부 라이브러리
import streamlit as st
from dotenv import load_dotenv

# 내부 실행 시 로컬의 .env 읽어오기
load_dotenv()

# ==========================================
# 1. API 설정 및 카테고리 정의
# ==========================================
# 네이버 개발자 센터에서 발급받은 정보 (Streamlit Cloud 배포 고려)
# 1) Streamlit st.secrets (배포 시) 2) 로컬 .env 또는 os.environ 환경변수
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception: # 로컬 환경 등 secrets.toml 파일이 없을 때 발생하는 모든 예외 처리
    CLIENT_ID = os.environ.get("CLIENT_ID", "Waa8neiFscq90VwwTvw8")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "J0lCX7GEEv")

# 비교할 카테고리 및 브랜드 (최대 5개 이하) [1]
CATEGORIES = {
    "냉장고": ["스메그", "리페르", "밀레", "피아바"],
    "인덕션": ["스메그", "디트리쉬", "밀레", "시리우스", "틸만"],
    "와인셀러": ["스메그", "아르떼비노", "리페르", "유로까브"],
    "주방 후드": ["스메그", "팔멕", "엘리카"],
    "후드인덕션": ["스메그", "밀레", "보라", "시리우스", "가게나우"],
    "전기포트": ["스메그", "드롱기", "발뮤다"],
    "토스트기": ["스메그", "드롱기", "발뮤다"],
    "커피머신": ["스메그", "브레빌", "유라", "필립스", "드롱기"],
    "오븐": ["스메그", "우녹스", "지에라", "에카", "베닉스"],
    "식기세척기": ["스메그", "돌핀", "우성", "호바트"],
    "반죽기": ["스메그", "키친에이드", "켄우드", "스파", "베닉스"]
}

# ==========================================
# 2. 통합 검색어 트렌드 API 호출 함수
# ==========================================
def get_datalab_trend(category, brands):
    url = "https://openapi.naver.com/v1/datalab/search"
    
    # 최근 1년 데이터(주간 단위) 세팅
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # keywordGroups 형식으로 파라미터 구성
    keyword_groups = []
    for brand in brands:
        keywords = [f"{brand}{category}", f"{brand}{category.replace(' ', '')}"]
        # '주방 후드'의 경우 '브랜드 + 후드' 키워드가 누락되지 않도록 추가
        if "후드" in category:
            keywords.append(f"{brand}후드")
        # '토스트기'의 경우 '토스터', '토스터기' 및 띄어쓰기 포함 키워드 추가
        if category == "토스트기":
            keywords.extend([
                f"{brand}토스터", f"{brand}토스터기",
                f"{brand} 토스트기", f"{brand} 토스터", f"{brand} 토스터기"
            ])
        
        keyword_groups.append({
            "groupName": f"{brand}{category}", # 사용자 요청 이미지와 동일하게 라벨링 (예: 스메그토스트기)
            "keywords": list(set(keywords))  # 중복 제거
        })
    
    body = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": "week", 
        "keywordGroups": keyword_groups
    }
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    request.add_header("Content-Type", "application/json")
    
    try:
        response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
    return None

# ==========================================
# 3. 비즈니스 인사이트 트렌드 분석 함수 (스메그 마케터 관점)
# ==========================================
# 카테고리별 주요 시즌 이슈 정의
SEASON_ISSUES = {
    "냉장고": {"months": [3, 4, 5, 10, 11], "issue": "이사 및 혼수 가전 수요가 집중되는 시즌입니다."},
    "인덕션": {"months": [3, 4, 10, 11, 12], "issue": "주방 리모델링 및 연말 홈파티 수요가 발생하는 시기입니다."},
    "와인셀러": {"months": [11, 12, 1], "issue": "연말연시 파티 및 연간 와인 소비량이 가장 높은 극성수기입니다."},
    "커피머신": {"months": [5, 11, 12], "issue": "가정의 달 및 크리스마스 선물 수요가 급증하는 시기입니다."},
    "전기포트": {"months": [11, 12, 1, 2], "issue": "기온 하락으로 인한 따뜻한 음료 수요가 늘어나는 동절기 시즌입니다."},
    "오븐": {"months": [11, 12, 2], "issue": "홈베이킹 및 졸업/입학 시즌 선물 수요가 발생하는 시기입니다."}
}

def analyze_trend_short(df_pivot, selected_category=""):
    if len(df_pivot) < 4:
        return "데이터가 충분하지 않아 상세 분석이 어렵습니다."
    
    # 1. 상태 요약 (마지막 주 기준)
    last_week = df_pivot.iloc[-1]
    top_brand = last_week.idxmax()
    smeg_score = last_week.get("스메그", 0)
    
    # 2. 급상승(스파이크) 감지 로직
    # 전주 대비 20% 이상 급상승한 일자와 브랜드 탐색
    diff_pct = (df_pivot.pct_change() * 100).fillna(0)
    spikes = []
    
    # 최근 4주 데이터 중 눈에 띄게 튄 지점 탐색
    recent_diff = diff_pct.tail(4)
    for date, row in recent_diff.iterrows():
        for brand, val in row.items():
            if val > 40: # 40% 이상 급상승 시 유의미한 이벤트로 간주
                formatted_date = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
                spikes.append(f"'{brand}' 브랜드가 {formatted_date}경 검색량이 급증했습니다.")
    
    # 3. 시즌 이슈 확인
    current_month = datetime.now().month
    season_comment = ""
    if selected_category in SEASON_ISSUES:
        issue_info = SEASON_ISSUES[selected_category]
        if current_month in issue_info["months"]:
            season_comment = f"현재 {selected_category} 카테고리는 {issue_info['issue']}"

    # 4. 종합 인사이트 조립
    insight_parts = []
    
    # [섹션 1: 순위 진단]
    if top_brand == "스메그":
        insight_parts.append(f"▶ [수성] 자사(스메그)가 {last_week.max():.1f}의 지수로 시장 점유 1위를 유지하며 견고한 브랜드 선호도를 보이고 있습니다.")
    else:
        insight_parts.append(f"▶ [경쟁] 현재 '{top_brand}'가 차트 1위를 기록 중이며, 자사(스메그)는 지수 {smeg_score:.1f}로 이를 추격하는 양상입니다.")

    # [섹션 2: 특정 이벤트 언급]
    if spikes:
        # 중복 제거 및 최대 2개만 언급
        unique_spikes = list(set(spikes))[:2]
        insight_parts.append(f"▶ [특이사항] 데이터 관찰 결과, { ' '.join(unique_spikes) } 이는 해당 시점의 특정 할인 행사나 매체 노출의 영향일 수 있습니다.")

    # [섹션 3: 시즌 이슈 연계]
    if season_comment:
        insight_parts.append(f"▶ [시즌] {season_comment}")

    # 최종 조립 (항목 간 간격 추가)
    return "\n\n".join(insight_parts) if insight_parts else "특이한 트렌드 변화 없이 평이한 흐름을 보이고 있습니다."

# ==========================================
# 4. 전체 실행 및 시각화 프로세스
# ==========================================
def main():
    print(">>> 카테고리별 브랜드 트렌드 추출 시작\n")

    for category, brands in CATEGORIES.items():
        data = get_datalab_trend(category, brands)
        
        if data and 'results' in data:
            df_list = []
            for group in data['results']:
                title = group['title']
                for item in group['data']:
                    df_list.append({
                        'Date': item['period'],
                        'Brand': title, 
                        'Ratio': item['ratio']
                    })
                    
            if df_list:
                df = pd.DataFrame(df_list)
                # 날짜를 인덱스로, 브랜드를 컬럼으로 변환
                df_pivot = df.pivot(index='Date', columns='Brand', values='Ratio').fillna(0)
                
                # --- 그래프 시각화 ---
                plt.figure(figsize=(10, 5))
                df_pivot.plot(ax=plt.gca(), marker='o', linewidth=2)
                plt.title(f"[{category}] 브랜드 검색 트렌드 비교")
                plt.ylabel("검색 지수(Ratio)")
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                # 그래프 저장
                filename = f"trend_{category}.png"
                plt.savefig(filename)
                plt.close()
                
                # --- 20자 이내 분석 도출 ---
                analysis_text = analyze_trend_short(df_pivot)
                
                print(f"■ {category} 분석 완료 (저장: {filename})")
                print(f"분석 요약:\n{analysis_text}\n" + "-"*30)

if __name__ == "__main__":
    main()