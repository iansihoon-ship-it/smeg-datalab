import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

# naver_datalap 모듈에서 필요한 변수 및 함수 불러오기
from naver_datalap import CATEGORIES, get_datalab_trend, analyze_trend_short

def init_page():
    st.set_page_config(
        page_title="네이버 데이터랩 브랜드 트렌드 대시보드",
        page_icon="📈",
        layout="wide"
    )

def main():
    init_page()
    
    def process_data(data):
        if not data or 'results' not in data:
            return None
        df_list = []
        for group in data['results']:
            title = group['title']
            for item in group['data']:
                df_list.append({
                    'Date': item['period'],
                    'Brand': title, 
                    'Ratio': item['ratio']
                })
        if not df_list:
            return None
        df = pd.DataFrame(df_list)
        df['Date'] = pd.to_datetime(df['Date'])
        df_pivot = df.pivot(index='Date', columns='Brand', values='Ratio').fillna(0)
        df_chart = df_pivot.copy()
        df_chart.index = df_chart.index.strftime('%y-%m-%d').tolist()
        return df_pivot, df_chart

    # 1. 사이드바 - 타이틀 및 카테고리 선택
    st.sidebar.title("📈 네이버 데이터랩")
    st.sidebar.markdown("""
        네이버 데이터랩 API를 활용하여 각 카테고리별 주요 브랜드의 **검색 트렌드 (1년/1개월/1주일)**를 제공합니다.
    """)
    st.sidebar.write("---")
    st.sidebar.header("🔍 카테고리 선택")
    category_list = list(CATEGORIES.keys())
    selected_category = st.sidebar.selectbox("비교할 카테고리를 선택하세요", category_list)

    st.subheader(f"[{selected_category}] 브랜드 트렌드 분석")
    
    # 선택된 카테고리의 브랜드 목록
    brands = CATEGORIES[selected_category]
    st.write(f"**비교 브랜드:** {', '.join(brands)}")
    
    # 2. 데이터 가져오기 및 처리 (1년 - 주간)
    with st.spinner("최근 1년 데이터를 가져오는 중입니다..."):
        data_1y = get_datalab_trend(selected_category, brands, period_days=365, time_unit='week')
        processed_1y = process_data(data_1y)
        
    if not processed_1y:
        st.error("데이터를 불러오지 못했습니다. API 설정(Client ID/Secret) 또는 일일 호출 한도를 확인해주세요.")
        return

    df_pivot_1y, df_chart_1y = processed_1y

    # 3. 데이터 시각화 및 결과 분석 도출
    st.markdown("### 💡 AI 트렌드 인사이트 (1년 기반)")
    analysis_text = analyze_trend_short(df_pivot_1y, selected_category)
    st.success(f"**요약 내용:**\n\n{analysis_text}")
    
    st.write("---")
    
    # --- [차트 1: 최근 1년 (주간)] ---
    st.markdown("#### 1️⃣ 최근 1년 트렌드 (주간 단위)")
    st.line_chart(df_chart_1y)
    
    # --- [차트 2: 최근 1개월 (일간)] ---
    st.markdown("#### 2️⃣ 최근 1개월 트렌드 (일간 단위)")
    with st.spinner("최근 1개월 데이터를 가져오는 중입니다..."):
        data_1m = get_datalab_trend(selected_category, brands, period_days=30, time_unit='date')
        processed_1m = process_data(data_1m)
        if processed_1m:
            st.line_chart(processed_1m[1])
        else:
            st.warning("1개월 데이터를 불러오지 못했습니다.")

    st.write("---")
    
    st.markdown("#### 📊 최근 상세 데이터 요약 (1년 기준)")
    # 데이터프레임 요약본 (최근 5주 표시, 포맷팅: 소수점 첫째자리 & 인덱스 월일화)
    df_summary = df_chart_1y.tail(5).sort_index(ascending=False).round(1)
    st.dataframe(df_summary, use_container_width=True)

if __name__ == "__main__":
    main()
