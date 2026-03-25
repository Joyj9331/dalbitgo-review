import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 기본 설정 (가로로 넓게 쓰기)
st.set_page_config(page_title="프랜차이즈 가맹점 리뷰 관리", page_icon="🚨", layout="wide")

@st.cache_data
def load_data():
    # 크롤러가 고정으로 생성하는 엑셀 파일명
    filename = "가맹점_리뷰수집결과_20260325.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        # 데이터가 없을 경우 대시보드 구조를 보여주기 위한 가상 샘플 데이터
        st.warning("현재 수집된 데이터 파일이 없어 샘플 화면을 보여드립니다.")
        data = {
            "매장명": ["파주심학산점", "강남역점", "강남역점", "홍대점", "부산서면점", "제주점", "파주심학산점", "판교점", "판교점"],
            "작성일": ["2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25", "2026-03-25"],
            "리뷰내용": ["고등어가 너무 맛있어요!", "직원 불친절하네요. 최악입니다.", "주문한 지 한참 지났는데 늦게 나와서 화났음.", "가성비 최고", "매장이 청결해요", "그냥 평범한 맛입니다.", "재방문 의사 100%", "매장이 너무 넓고 깔끔해요.", "웨이팅이 너무 길어요."],
            "감정분석": ["긍정", "부정", "부정", "긍정", "긍정", "중립", "긍정", "긍정", "부정"]
        }
        df = pd.DataFrame(data)
    return df

df = load_data()

# ==========================================
# 🗂️ 사이드바 (메뉴 네비게이션)
# ==========================================
st.sidebar.title("👨‍💼 가맹점 관리 비서")
st.sidebar.markdown("과장님, 원하시는 분석 뷰를 선택하십시오.")

menu = st.sidebar.radio("분석 모드", ["🌐 1. 전체 브랜드 평판 및 위험 감지", "🏪 2. 개별 가맹점 돋보기 분석"])
st.sidebar.divider()
st.sidebar.info("💡 **슈퍼바이저 활용 팁**\n\n'위험 감지' 탭에 뜬 매장 점주님들께 가장 먼저 오전 해피콜을 진행하시면 CS 방어에 효과적입니다.")

# ==========================================
# 🌐 메뉴 1. 전체 브랜드 평판 및 위험 감지
# ==========================================
if menu == "🌐 1. 전체 브랜드 평판 및 위험 감지":
    st.title("🌐 전체 가맹점 일일 평판 & 리스크 리포트")
    
    # 1. 가장 중요한 위험 감지망 (부정 리뷰 노출)
    st.subheader("🚨 당일 긴급 연락 요망 매장 (CS 리스크 감지)")
    
    # '부정'으로 분류된 데이터만 필터링
    negative_df = df[df['감정분석'] == '부정']
    
    if not negative_df.empty:
        st.error(f"⚠️ 과장님, 오늘 **{len(negative_df)}건**의 부정/불만 리뷰가 감지되었습니다. 아래 리스트를 확인하시고 해당 매장 점주님들께 즉시 연락해 주십시오.")
        # 최신 Streamlit 버전에 맞춰 width='stretch' 적용
        st.dataframe(negative_df[['매장명', '리뷰내용', '작성일']].reset_index(drop=True), width='stretch')
    else:
        st.success("🎉 오늘 감지된 부정/불만 리뷰가 한 건도 없습니다. 가맹점 현장 관리가 아주 훌륭하게 이루어지고 있습니다!")
        
    st.divider()
    
    # 2. 리뷰 발생량 랭킹 (인기 매장 vs 저조 매장)
    st.subheader("📊 일일 리뷰 발생량 분석 (Top & Bottom)")
    
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '오늘 수집된 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    
    with col_top:
        st.info("🔥 리뷰 활성 매장 (고객 반응 폭발)")
        top_stores = review_counts.head(5) # 가장 많은 5개
        st.dataframe(top_stores, width='stretch')
        
    with col_bottom:
        st.warning("❄️ 리뷰 저조 매장 (마케팅/이벤트 점검 필요)")
        # 데이터가 충분치 않을 수 있으므로, 하위 5개를 오름차순으로 정렬하여 표시
        bottom_stores = review_counts.tail(5).sort_values(by='오늘 수집된 리뷰 수', ascending=True).reset_index(drop=True)
        st.dataframe(bottom_stores, width='stretch')

# ==========================================
# 🏪 메뉴 2. 개별 가맹점 돋보기 분석
# ==========================================
else:
    st.title("🏪 개별 가맹점 상세 분석")
    
    store_list = sorted(df['매장명'].unique())
    selected_store = st.selectbox("📌 분석하실 특정 가맹점을 선택하십시오", store_list)
    
    # 선택한 매장의 데이터만 필터링
    store_df = df[df['매장명'] == selected_store]
    
    st.subheader(f"[{selected_store}] 고객 반응 요약")
    
    # 요약 지표 표시
    col1, col2, col3 = st.columns(3)
    total_rev = len(store_df)
    pos_rev = len(store_df[store_df['감정분석'] == '긍정'])
    neg_rev = len(store_df[store_df['감정분석'] == '부정'])
    
    with col1:
        st.metric("오늘 수집된 총 리뷰", f"{total_rev}건")
    with col2:
        st.metric("긍정 평가 (칭찬/추천)", f"{pos_rev}건", delta="강점 유지 필요")
    with col3:
        st.metric("부정 평가 (불만/개선)", f"{neg_rev}건", delta="- 즉각 원인 파악 필요", delta_color="inverse")
        
    st.divider()
    
    # 감정 파이 차트 및 리뷰 리스트 (매장별)
    col_chart, col_list = st.columns([1, 2])
    
    with col_chart:
        st.markdown("**고객 감정 비율**")
        sentiment_counts = store_df['감정분석'].value_counts().reset_index()
        sentiment_counts.columns = ['감정', '비율']
        fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', 
                      color_discrete_map={'긍정':'#00CC96', '부정':'#EF553B', '중립':'#636EFA'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, width='stretch')
        
    with col_list:
        st.markdown("**해당 매장 리뷰 상세 내역**")
        display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
        st.dataframe(display_df, width='stretch')
        
    # 메모 기능 (과장님 업무 편의용 UI)
    st.text_area(f"✍️ [{selected_store}] 슈퍼바이저 관리 메모 (점주 통화 내역 등)", placeholder="예: 3/25 오전 10시 점주 통화 완료. 조리 매뉴얼 재교육 지시함.")