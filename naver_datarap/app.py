import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

# naver_datarap 모듈에서 필요한 변수 및 함수 불러오기
from naver_datarap import CATEGORIES, get_datalab_trend, analyze_trend_short

def init_page():
    st.set_page_config(
        page_title="네이버 데이터랩 브랜드 트렌드 대시보드",
        page_icon="📈",
        layout="wide"
    )
    st.title("📈 네이버 데이터랩 브랜드 트렌드 탐색기")
    st.markdown("""
        네이버 데이터랩 API를 활용하여 각 카테고리별 주요 브랜드의 **최근 3개월 검색 트렌드**를 제공합니다.
        좌측 사이드바에서 분석을 원하는 카테고리를 선택해 주세요.
    """)

def main():
    init_page()
    
    # 1. 사이드바 - 카테고리 선택
    st.sidebar.header("🔍 카테고리 선택")
    category_list = list(CATEGORIES.keys())
    selected_category = st.sidebar.selectbox("비교할 카테고리를 선택하세요", category_list)

    st.write("---")
    st.subheader(f"[{selected_category}] 브랜드 트렌드 분석")
    
    # 선택된 카테고리의 브랜드 목록
    brands = CATEGORIES[selected_category]
    st.write(f"**비교 브랜드:** {', '.join(brands)}")
    
    # 2. 데이터 가져오기 및 처리
    with st.spinner("네이버 데이터랩 API에서 데이터를 가져오는 중입니다..."):
        data = get_datalab_trend(selected_category, brands)
        
    if not data or 'results' not in data:
        st.error("데이터를 불러오지 못했습니다. API 설정(Client ID/Secret) 또는 일일 호출 한도를 확인해주세요.")
        return

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
        st.warning("조회된 데이터가 없습니다.")
        return
        
    df = pd.DataFrame(df_list)
    df['Date'] = pd.to_datetime(df['Date'])
    df_pivot = df.pivot(index='Date', columns='Brand', values='Ratio').fillna(0)
    
    # 3. 데이터 시각화 및 결과 분석 도출
    
    st.markdown("### 💡 AI 트렌드 인사이트")
    # 30자 이상 비즈니스 요약 도출
    analysis_text = analyze_trend_short(df_pivot)
    
    # X축(날짜) 포맷을 연-월-일(YY-MM-DD) 형식으로 변경 (차트 정렬 오류 방지)
    df_chart = df_pivot.copy()
    
    # st.line_chart가 내부적으로 문자열 인덱스를 처리할 때 순서가 꼬이는 문제 방지
    # 연도를 포함하여 '%y-%m-%d' 형태로 변환 (예: 25-12-25, 26-03-01 순서 보장)
    df_chart.index = df_chart.index.strftime('%y-%m-%d').tolist()
    
    # 눈에 잘 띄는 성공(success) 혹은 정보(info) 알림창 활용
    st.success(f"**요약 내용:**\n\n{analysis_text}")
    
    st.write("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 주간 트렌드 차트")
        # 차트 그리기 (Streamlit 내장 line_chart 활용, 날짜 포맷팅된 데이터 사용)
        st.line_chart(df_chart)
        
    with col2:
        st.markdown("#### 주간 상세 데이터 요약")
        # 데이터프레임 요약본 (최근 5주 표시, 포맷팅: 소수점 첫째자리 & 인덱스 월일화)
        df_summary = df_chart.tail(5).sort_index(ascending=False).round(1)
        st.dataframe(df_summary, use_container_width=True)

if __name__ == "__main__":
    main()
