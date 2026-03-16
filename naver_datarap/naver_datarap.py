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
    "토스트기": ["드롱기", "발뮤다"],
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
    
    # 최근 3개월 데이터(주간 단위) 세팅
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # keywordGroups 형식으로 파라미터 구성 (검색어엔 "브랜드명 + 카테고리명" 적용, 표기 그룹명은 "브랜드명" 유지)
    keyword_groups = [{"groupName": brand, "keywords": [f"{brand}{category}"]} for brand in brands]
    
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
def analyze_trend_short(df_pivot):
    if len(df_pivot) < 2:
        return "데이터 부족으로 유의미한 트렌드 진단이 어렵습니다. 향후 데이터가 누적되면 다시 확인해 주세요."
    
    last_week = df_pivot.iloc[-1]
    prev_week = df_pivot.iloc[-2]
    
    # 현재 1위 브랜드 및 검색 지수
    top_brand = last_week.idxmax()
    top_score = last_week.max()
    
    # 스메그 점수 확인 (자사 기준)
    smeg_score = last_week.get("스메그", 0)
    
    # 전주 대비 상승폭 계산
    diff = last_week - prev_week
    rising_brand = diff.idxmax()
    max_rise = diff.max()
    
    # 30자 이상의 스메그(SMEG) 마케터 관점 비즈니스 인사이트 생성 로직
    if top_brand == "스메그":
        if top_brand == rising_brand and max_rise > 10:
            insight = f"▶ [자사 우위] 자사(스메그)가 검색지수 {top_score:.1f}로 압도적 1위를 기록하며 브랜드 파워를 과시 중입니다. 최근 진행된 스메그 중심의 프로모션 혜택이나 오프라인 행사의 바이럴 효과로 소비자 관심도가 급등한 것으로 분석됩니다. 이 기세를 몰아 프리미엄 시장 점유율을 더욱 공고히 할 적기입니다."
        else:
            insight = f"▶ [수성 유지] 자본과 프리미엄 브랜드 이미지가 견고하게 맞물려 자사(스메그)가 1위를 안정적으로 이끌고 있습니다. 다만 경쟁사가 신제품 출시나 특가 이벤트로 언제든 치고 올라올 수 있으니, 스메그만의 오리지널리티를 강조하는 브랜드 캠페인을 지속 전개해야 합니다."
    else:
        if rising_brand == "스메그" and max_rise > 5:
            insight = f"▶ [추격 모멘텀] 현재 전체 1위는 '{top_brand}'에 내주었지만, 자사(스메그) 검색량이 눈에 띄게 상승하며 1위를 맹렬히 뒤쫓고 있습니다. 최근 전개된 스메그의 감성 캠페인이나 한정판 에디션 전략이 소비자들의 호기심을 효과적으로 자극한 결과입니다. 이 상승세를 구매로 직결시킬 온라인 프로모션 기획이 필요합니다."
        else:
            insight = f"▶ [위기 및 과제] '{top_brand}'가 선두를 달리는 가운데 자사(스메그)의 검색량은 {smeg_score:.1f}에 그쳐 다소 정체된 흐름입니다. 경쟁 브랜드가 대규모 광고나 인플루언서 협업으로 트래픽을 선점하고 있을 확률이 높습니다. 하반기 시즌 특수를 겨냥하여 스메그의 강점인 '디자인과 감성'을 전면 내세운 화제성 있는 마케팅 액션이 시급합니다."
            
    return insight

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