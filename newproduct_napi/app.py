# /// script
# dependencies = [
#   "streamlit",
#   "pandas",
#   "plotly",
# ]
# ///
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="우유거품기 트렌드 분석 대시보드", layout="wide")

# 데이터 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

@st.cache_data
def load_data():
    files = os.listdir(PROCESSED_DATA_DIR)
    
    blog_file = [f for f in files if "블로그검색" in f][0]
    shop_file = [f for f in files if "쇼핑상품검색" in f][0]
    trend_file = [f for f in files if "쇼핑트랜드" in f][0]
    
    def read_csv_safe(filename):
        try:
            return pd.read_csv(os.path.join(PROCESSED_DATA_DIR, filename))
        except pd.errors.EmptyDataError:
            return pd.DataFrame()

    df_blog = read_csv_safe(blog_file)
    df_shop = read_csv_safe(shop_file)
    df_trend = read_csv_safe(trend_file)
    
    return df_blog, df_shop, df_trend

try:
    df_blog, df_shop, df_trend = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 설정
st.sidebar.title("🔍 분석 필터")
keywords = sorted(df_shop['search_keyword'].unique())
selected_keywords = st.sidebar.multiselect("분석할 키워드를 선택하세요", keywords, default=keywords)

if not selected_keywords:
    st.warning("분석을 위해 최소 하나 이상의 키워드를 선택해주세요.")
    st.stop()

# 데이터 필터링
f_blog = df_blog[df_blog['search_keyword'].isin(selected_keywords)] if not df_blog.empty else pd.DataFrame()
f_shop = df_shop[df_shop['search_keyword'].isin(selected_keywords)] if not df_shop.empty else pd.DataFrame()
f_trend = df_trend[df_trend['키워드'].isin(selected_keywords)] if not df_trend.empty else pd.DataFrame()

# 메인 타이틀
st.title("🥛 우유거품기 제품 트렌드 분석 리포트")
st.markdown(f"**수집 일자**: {datetime.now().strftime('%Y-%m-%d')} | **분석 대상**: {', '.join(selected_keywords)}")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📉 검색 트랜드 비교", "📝 블로그 여론 분석", "🛒 쇼핑 시장 분석"])

# --- Tab 1: 검색 트랜드 ---
with tab1:
    st.header("네이버 쇼핑 인사이트 검색 트랜드")
    if f_trend.empty:
        st.info("현재 선택된 키워드 및 카테고리에 대한 일별 검색 트랜드 데이터가 존재하지 않습니다.")
    else:
        fig_trend = px.line(f_trend, x='날짜', y='수치', color='키워드', title="최근 1년 키워드별 검색량 변화")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.subheader("키워드별 트랜드 데이터 요약")
        st.dataframe(f_trend.pivot_table(index='날짜', columns='키워드', values='수치'), use_container_width=True)

# --- Tab 2: 블로그 분석 ---
with tab2:
    st.header("블로그 검색 결과 기반 EDA")
    
    if f_blog.empty:
        st.info("현재 선택된 키워드에 대한 블로그 데이터가 존재하지 않습니다.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. 블로그 게시글 수 비교
            fig_blog_count = px.bar(f_blog['search_keyword'].value_counts().reset_index(), 
                                    x='search_keyword', y='count', color='search_keyword',
                                    title="키워드별 블로그 게시글 수", labels={'search_keyword': '키워드', 'count': '게시글 수'})
            st.plotly_chart(fig_blog_count, use_container_width=True)
        
        with col2:
            # 2. 블로그 작성일 분포 (월별)
            f_blog['month'] = pd.to_datetime(f_blog['postdate'], format='%Y%m%d').dt.strftime('%Y-%m')
            blog_monthly = f_blog.groupby(['month', 'search_keyword']).size().reset_index(name='count')
            fig_blog_monthly = px.area(blog_monthly, x='month', y='count', color='search_keyword', title="월별 블로그 작성 추이")
            st.plotly_chart(fig_blog_monthly, use_container_width=True)

        # 3. 블로그 상세 데이터 표
        st.subheader("블로그 검색 결과 상세 리스트")
        st.dataframe(f_blog[['search_keyword', 'title', 'bloggername', 'postdate', 'link']], use_container_width=True)
        
        # 4. 블로거 랭킹 (다작 블로거)
        st.subheader("주요 블로거 분석 (Top 10)")
        blogger_top = f_blog['bloggername'].value_counts().head(10).reset_index()
        st.table(blogger_top)

# --- Tab 3: 쇼핑 분석 ---
with tab3:
    st.header("네이버 쇼핑 상품 데이터 EDA")
    
    if f_shop.empty:
        st.info("현재 선택된 키워드에 대한 쇼핑 상품 데이터가 존재하지 않습니다.")
    else:
        # 상단 지표
        m1, m2, m3 = st.columns(3)
        m1.metric("총 수집 상품 수", f"{len(f_shop):,}개")
        m2.metric("평균 가격", f"{int(f_shop['lprice'].mean()):,}원")
        m3.metric("최고가 상품 브랜드", f_shop.sort_values('lprice', ascending=False).iloc[0]['brand'] if not f_shop['brand'].isna().all() else "N/A")

        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            # 1. 가격 분포 히스토그램
            fig_price_dist = px.histogram(f_shop, x='lprice', color='search_keyword', nbins=50, 
                                         title="상품 가격대 분포", labels={'lprice': '최저가 (원)'}, barmode='overlay')
            st.plotly_chart(fig_price_dist, use_container_width=True)
            
        with col_s2:
            # 2. 브랜드 점유율 (Top 15)
            brand_counts = f_shop['brand'].value_counts().head(15).reset_index()
            fig_brand = px.bar(brand_counts, x='count', y='brand', orientation='h', color='brand',
                              title="상위 브랜드 점유율 (Top 15)", labels={'count': '상품 수', 'brand': '브랜드'})
            st.plotly_chart(fig_brand, use_container_width=True)

        col_s3, col_s4 = st.columns(2)
        
        with col_s3:
            # 3. 몰(Mall)별 비중 파이 차트
            mall_counts = f_shop['mallName'].value_counts().head(10).reset_index()
            fig_mall = px.pie(mall_counts, values='count', names='mallName', title="주요 판매처 비중 (Top 10)")
            st.plotly_chart(fig_mall, use_container_width=True)
            
        with col_s4:
            # 4. 키워드별 평균 가격 비교 (박스플롯)
            fig_price_box = px.box(f_shop, x='search_keyword', y='lprice', color='search_keyword',
                                 title="키워드별 가격 분포 상세 (Box Plot)", labels={'lprice': '가격', 'search_keyword': '키워드'})
            st.plotly_chart(fig_price_box, use_container_width=True)

        # 5. 가성비 상품 랭킹 (최저가 순)
        st.subheader("최저가 기준 가성비 상품 리스트 (Top 20)")
        st.dataframe(f_shop.sort_values('lprice')[['search_keyword', 'title', 'brand', 'lprice', 'mallName', 'link']].head(20), use_container_width=True)

        # 6. 키워드별 기술통계 표 요약
        st.subheader("키워드별 가격 통계 요약")
        price_stats = f_shop.groupby('search_keyword')['lprice'].agg(['count', 'mean', 'std', 'min', 'median', 'max']).reset_index()
        price_stats.columns = ['키워드', '상품수', '평균가', '표준편차', '최소가', '중위수', '최대가']
        st.dataframe(price_stats.style.format({
            '평균가': '{:,.0f}', '표준편차': '{:,.0f}', '최소가': '{:,.0f}', '중위수': '{:,.0f}', '최대가': '{:,.0f}'
        }), use_container_width=True)
