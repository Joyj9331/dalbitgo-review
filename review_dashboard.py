import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 공식 브랜드 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 평판관리", page_icon="🐟", layout="wide")

# (주)새모양에프앤비 - 달빛에구운고등어 공식 홈페이지 기반 CSS
st.markdown("""
<style>
    /* 한식 프랜차이즈의 고급스러움을 살리는 폰트 조합 */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 제목 및 브랜드명에 고급스러운 '고운돋움' 폰트 적용 */
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
        color: #111111 !important;
    }
    
    /* 전체 배경색 (홈페이지 bg-very-light-gray 톤 반영) */
    .stApp {
        background-color: #F9F9F9;
    }
    
    /* 사이드바 테마 (홈페이지 footer의 bg-black 반영) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333333;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* 메트릭(숫자 요약) 카드 디자인 - 깔끔한 화이트 & 레드 포인트 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border-left: 5px solid #D32F2F; /* 홈페이지 text-red 강조 컬러 */
    }
    
    /* 로그인 박스 전용 디자인 */
    .login-container {
        background-color: #FFFFFF;
        padding: 50px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 6px solid #D32F2F;
        margin-top: 50px;
    }
    .brand-title {
        color: #111111;
        font-size: 36px;
        margin-bottom: 5px;
    }
    .brand-subtitle {
        color: #666666;
        font-size: 16px;
        margin-bottom: 5px;
        font-weight: 500;
    }
    .brand-desc {
        color: #999999;
        font-size: 13px;
        margin-bottom: 30px;
    }
    
    /* 버튼 디자인 (홈페이지 btn-red 스타일 반영) */
    .stButton > button {
        background-color: #D32F2F !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 5px !important;
        border: none !important;
        height: 45px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }
    
    /* 데이터프레임 테두리 깔끔하게 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #EAEAEA;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🔒 2. 브랜드 맞춤형 보안 로그인 시스템
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == "51015":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
            <div class="login-container">
                <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                <div class="brand-title">달빛에 구운 고등어</div>
                <div class="brand-desc">가맹점 통합 평판관리 인트라넷 (본사 전용)</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.text_input("본사 직원 인증 코드를 입력하십시오.", type="password", on_change=password_entered, key="password")
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ 인증 코드가 일치하지 않습니다. (문의: 가맹관리팀)")
        return False
    else:
        return True

if not check_password():
    st.stop()


# ==========================================
# 📊 3. 대시보드 본문 (인증된 직원 전용)
# ==========================================
def load_data():
    filename_new = "가맹점_리뷰수집결과_누적.csv"
    filename_old = "가맹점_리뷰수집결과_20260325.csv"
    
    df_list = []
    if os.path.exists(filename_old):
        df_list.append(pd.read_csv(filename_old))
    if os.path.exists(filename_new):
        df_list.append(pd.read_csv(filename_new))
        
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
        return df
    else:
        data = {
            "매장명": ["달빛에구운고등어 어양점", "달빛에구운고등어 첨단점"],
            "작성일": ["2026-03-26", "2026-03-26"],
            "리뷰내용": ["화덕에 구워서 육즙이 살아있어요! 12첩 반찬도 최고!", "웨이팅이 너무 길어서 불편했습니다."],
            "감정분석": ["긍정", "부정"]
        }
        return pd.DataFrame(data)

def load_store_list():
    excel_file = "가맹점_리뷰링크.xlsx"
    if os.path.exists(excel_file):
        try:
            store_df = pd.read_excel(excel_file)
            if '매장명' in store_df.columns:
                return sorted(store_df['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list()
if not full_store_list:
    full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else ["매장 없음"]

# 사이드바 (메뉴) - 홈페이지 푸터 정보 활용
st.sidebar.markdown("<h2 style='color: #FFFFFF !important; text-align: center;'>🌙 달빛 비서</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #AAAAAA !important;'>가맹관리팀 슈퍼바이저 패널</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio("🔎 데이터 분석 메뉴", ["전체 브랜드 평판 현황", "개별 가맹점 집중 분석"])
st.sidebar.divider()

if st.sidebar.button("🔄 최신 데이터 동기화"):
    st.rerun()

st.sidebar.write("")
st.sidebar.info("💡 **슈퍼바이저 업무 팁**\n\n'위험 감지' 리스트에 노출된 매장은 익일 오전 해피콜 및 식자재 발주 확인 시 우선 점검하십시오.")

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size: 11px; color: #888888; text-align: center; line-height: 1.5;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# 메뉴 1. 전체 브랜드 평판
# ------------------------------------------
if menu == "전체 브랜드 평판 현황":
    st.markdown("<h1>전체 가맹점 평판 리포트 <span style='font-size: 18px; color: #999;'>| Daily Dashboard</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 30px; color: #D32F2F !important;'>🚨 즉각 조치 요망 매장 (CS 리스크 감지)</h3>", unsafe_allow_html=True)
    negative_df = df[df['감정분석'] == '부정']
    
    if not negative_df.empty:
        st.error(f"⚠️ **총 {len(negative_df)}건**의 부정/불만 리뷰가 감지되었습니다. 아래 내역을 확인하고 해당 점주님께 연락해 주십시오.")
        st.dataframe(negative_df[['매장명', '리뷰내용', '작성일']].sort_values(by='작성일', ascending=False).reset_index(drop=True), use_container_width=True)
    else:
        st.success("🎉 현재 감지된 부정/불만 리뷰가 없습니다. 전체 가맹점의 서비스 품질이 우수하게 유지되고 있습니다.")
        
    st.divider()
    
    st.markdown("<h3 style='margin-top: 30px;'>📊 누적 고객 반응 모니터링</h3>", unsafe_allow_html=True)
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '누적 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.info("🔥 고객 반응 우수 매장 (리뷰 활성화)")
        st.dataframe(review_counts.head(5), use_container_width=True)
    with col_bottom:
        st.warning("❄️ 리뷰 관리 필요 매장 (온라인 홍보 저조)")
        st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

# ------------------------------------------
# 메뉴 2. 개별 가맹점 분석
# ------------------------------------------
else:
    st.markdown("<h1>가맹점 상세 분석 <span style='font-size: 18px; color: #999;'>| Store Details</span></h1>", unsafe_allow_html=True)
    selected_store = st.selectbox("📌 집중 분석할 매장을 선택하십시오", full_store_list)
    
    store_df = df[df['매장명'] == selected_store]
    
    if store_df.empty:
        st.info(f"ℹ️ 아직 [{selected_store}]에 수집된 누적 리뷰 데이터가 없습니다.")
    else:
        st.markdown(f"<h3 style='margin-top: 20px;'>[{selected_store}] 고객 반응 요약</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("누적 전체 리뷰", f"{len(store_df)}건")
        with col2: st.metric("긍정 평가 (맛/서비스 만족)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
        with col3: st.metric("부정 평가 (개선 필요)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
            
        st.divider()
        col_chart, col_list = st.columns([1, 2])
        
        with col_chart:
            st.markdown("<b style='font-size: 16px;'>누적 감정 비율</b>", unsafe_allow_html=True)
            sentiment_counts = store_df['감정분석'].value_counts().reset_index()
            sentiment_counts.columns = ['감정', '비율']
            # 차트 색상 (블랙/화이트/레드 브랜드 톤에 맞춤)
            fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', color_discrete_map={'긍정':'#111111', '부정':'#D32F2F', '중립':'#AAAAAA'})
            fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_list:
            st.markdown("<b style='font-size: 16px;'>최신 리뷰 상세 내역</b>", unsafe_allow_html=True)
            display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True)
