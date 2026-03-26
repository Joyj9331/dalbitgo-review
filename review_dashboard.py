import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
import time

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 공식 브랜드 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 리뷰 관리", page_icon="🐟", layout="wide")

# (주)새모양에프앤비 - 프리미엄 B2B 어드민 UI 적용 & 애니메이션 추가
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 다크모드 충돌 방지: 본문 텍스트 강제 다크 처리 */
    h1, h2, h3, h4, h5, h6, p, label, li {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* 전체 배경: 깨끗하고 전문적인 라이트 그레이 */
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* 사이드바: 텍스트 화이트 강제 유지 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important; 
    }
    
    /* 상단 요약 카드 디자인 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #E8B923; 
    }
    
    /* =========================================
       🚀 프리미엄 애니메이션 (Zoom-in & Suck-in)
       ========================================= */
    @keyframes zoomInBack {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes suckIn {
        0% { transform: scale(1.05); opacity: 0; filter: blur(3px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10vh;
        margin-bottom: 2vh;
        animation: zoomInBack 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .login-container {
        background-color: #111111 !important; 
        padding: 40px 50px; 
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        text-align: center;
        border-top: 5px solid #E8B923;
        width: 100%;
    }
    
    /* 로그인 컨테이너 내부 텍스트 화이트 강제 유지 */
    .login-container p, .login-container span, .login-container div, .login-container label {
        color: #FFFFFF !important;
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-size: 26px;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .brand-subtitle {
        color: #E8B923 !important;
        font-size: 14px;
        margin-bottom: 30px;
        font-weight: 400;
    }

    /* 💡 1. 투두리스트(Expander) 강제 하얀색 배경 및 글씨체 완벽 복원 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 8px;
        border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        overflow: hidden;
    }
    div[data-testid="stExpander"] details {
        background-color: #FFFFFF !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #F8F9FA !important; 
        color: #111111 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #EEEEEE !important;
    }
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: #111111 !important;
        font-weight: 600 !important;
    }

    /* 💡 2. 드롭다운(Selectbox) 및 드롭다운 팝업 리스트 강제 화이트 처리 */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #111111 !important;
    }
    
    /* 클릭 시 튀어나오는 팝업 영역 (Portal 영역 강제 제어) */
    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    
    /* 팝업 안의 각 매장 리스트 항목 글씨 먹색 제어 */
    li[role="option"], 
    li[role="option"] span {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        font-weight: 500 !important;
    }
    
    /* 마우스 올렸을 때(Hover) 약간 밝은 회색으로 피드백 */
    li[role="option"]:hover, 
    li[role="option"]:hover span,
    li[role="option"][aria-selected="true"] {
        background-color: #F4F6F8 !important;
        color: #D32F2F !important; /* 포인트 컬러인 레드로 강조 */
    }

    /* 💡 3. 입력창(TextInput) 강제 하얀색 배경 및 먹색 글씨 */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="input"] input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important; /* 강력한 다크모드 방어 */
        border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="input"] input::placeholder {
        color: #AAAAAA !important;
        -webkit-text-fill-color: #AAAAAA !important;
    }
    
    /* 버튼 통합 디자인 (고급스러운 레드) */
    .stButton > button {
        background-color: #D32F2F !important;
        border-radius: 6px !important;
        border: none !important;
        height: 42px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(211,47,47,0.2);
    }
    .stButton > button * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .stButton > button:hover {
        background-color: #B71C1C !important;
        box-shadow: 0 4px 8px rgba(211,47,47,0.3);
    }
    
    /* 데이터프레임 테두리 깔끔하게 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #EAEAEA;
        background-color: #FFFFFF;
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
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.markdown("""
            <div class="login-wrapper">
                <div class="login-container">
                    <img src="https://dalbitgo.com/images/main_logo.png" style="height: 60px; object-fit: contain;">
                    <div class="brand-title">리뷰 관리 프로그램</div>
                    <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("🔑 본사 직원 인증 코드 (비밀번호)를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="여기를 클릭하여 입력하세요")
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ 인증 코드가 일치하지 않습니다.")
        return False
    else:
        st.markdown("<style>[data-testid='block-container'] { animation: suckIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }</style>", unsafe_allow_html=True)
        return True

if not check_password():
    st.stop()


# ==========================================
# 💾 3. 영구 보존 상태 관리 (해피콜 완료 & 오분류 수정)
# ==========================================
STATE_RESOLVED = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"

def get_saved_ids(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)['id'].tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if new_id not in ids:
        ids.append(new_id)
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()


# ==========================================
# 📊 4. 대시보드 본문 (인증된 직원 전용)
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
    else:
        # 데이터가 없을 때의 UI용 샘플
        data = {
            "매장명": ["달빛에구운고등어 어양점", "달빛에구운고등어 첨단점", "달빛에구운고등어 군산미장점"],
            "작성일": ["2026-03-26", "2026-03-26", "2026-03-26"],
            "리뷰내용": ["화덕에 구워서 육즙이 살아있어요! 너무 맛있네요.", "웨이팅이 좀 있었지만 맛있게 먹었어요. 다음에 또 올게요.", "직원분이 너무 바빠보여서 부르기 미안했습니다."],
            "감정분석": ["긍정", "부정", "부정"]
        }
        df = pd.DataFrame(data)

    df['id'] = df.apply(generate_id, axis=1)
    overridden_ids = get_saved_ids(STATE_OVERRIDDEN)
    df.loc[df['id'].isin(overridden_ids), '감정분석'] = '긍정'
    
    return df

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

# 사이드바
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 85%;">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #E8B923 !important; font-weight: 500;'>가맹관리팀 슈퍼바이저 패널</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio("🔎 데이터 분석 메뉴", ["전체 브랜드 리뷰 현황", "개별 가맹점 집중 분석"])
st.sidebar.divider()

if st.sidebar.button("🔄 최신 데이터 동기화", use_container_width=True):
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
# 메뉴 1. 전체 브랜드 리뷰 현황
# ------------------------------------------
if menu == "전체 브랜드 리뷰 현황":
    st.markdown("<h1>전체 가맹점 리뷰 리포트 <span style='font-size: 18px; color: #777;'>| Daily Dashboard</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 30px; color: #111111 !important;'>🚨 즉각 조치 요망 매장 (To-Do List)</h3>", unsafe_allow_html=True)
    
    resolved_ids = get_saved_ids(STATE_RESOLVED)
    negative_df = df[df['감정분석'] == '부정'].copy()
    active_negative_df = negative_df[~negative_df['id'].isin(resolved_ids)]
    
    if not active_negative_df.empty:
        st.markdown(f"<div style='color: #D32F2F; font-size: 15px; margin-bottom: 15px; font-weight: 600;'>⚠️ 총 {len(active_negative_df)}건의 부정/불만 리뷰가 남아있습니다. 해피콜 조치 후 완료 버튼을 누르거나, 긍정 리뷰일 경우 수정해주세요.</div>", unsafe_allow_html=True)
        
        for idx, row in active_negative_df.iterrows():
            short_text = row['리뷰내용'][:20] + "..." if len(row['리뷰내용']) > 20 else row['리뷰내용']
            with st.expander(f"📌 [{row['매장명']}] {row['작성일']} | {short_text}"):
                st.write(f"💬 **전체 리뷰 내용:** {row['리뷰내용']}")
                
                col_btn1, col_btn2, _ = st.columns([1, 1, 2])
                with col_btn1:
                    if st.button("✅ 조치 완료 (삭제)", key=f"resolve_{row['id']}", use_container_width=True):
                        add_saved_id(STATE_RESOLVED, row['id'])
                        st.rerun() 
                with col_btn2:
                    if st.button("🌟 긍정 평가로 변경", key=f"override_{row['id']}", use_container_width=True):
                        add_saved_id(STATE_OVERRIDDEN, row['id'])
                        st.rerun()
    else:
        st.success("🎉 현재 조치가 필요한 부정/불만 리뷰가 없습니다. 가맹점 관리가 완벽하게 이루어지고 있습니다!")
        
    st.divider()
    
    st.markdown("<h3 style='margin-top: 30px;'>📊 누적 고객 반응 모니터링</h3>", unsafe_allow_html=True)
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '누적 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.markdown("<b style='font-size: 16px; color: #2E7D32;'>🔥 고객 반응 우수 매장 (리뷰 활성화)</b>", unsafe_allow_html=True)
        st.dataframe(review_counts.head(5), use_container_width=True)
    with col_bottom:
        st.markdown("<b style='font-size: 16px; color: #D32F2F;'>❄️ 리뷰 관리 필요 매장 (온라인 홍보 저조)</b>", unsafe_allow_html=True)
        st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

# ------------------------------------------
# 메뉴 2. 개별 가맹점 분석
# ------------------------------------------
else:
    st.markdown("<h1>가맹점 상세 분석 <span style='font-size: 18px; color: #777;'>| Store Big Data</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px; margin-bottom: -15px;'><b style='font-size: 14px; color: #666;'>🔍 매장명 검색</b></div>", unsafe_allow_html=True)
    search_query = st.text_input(" ", placeholder="예: 첨단, 어양 (검색 즉시 아래 목록이 필터링됩니다)")
    
    if search_query:
        filtered_stores = [store for store in full_store_list if search_query.replace(" ", "") in store.replace(" ", "")]
    else:
        filtered_stores = full_store_list
        
    if not filtered_stores:
        st.warning(f"'{search_query}'에 해당하는 매장이 없습니다. 검색어를 다시 확인해주세요.")
    else:
        selected_store = st.selectbox("📌 조회할 매장을 선택하십시오", filtered_stores)
        
        store_df = df[df['매장명'] == selected_store]
        
        if store_df.empty:
            st.info(f"ℹ️ 아직 [{selected_store}]에 수집된 누적 리뷰 데이터가 없습니다.")
        else:
            st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{selected_store}] 빅데이터 분석 리포트</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("누적 전체 리뷰", f"{len(store_df)}건")
            with col2: st.metric("긍정 평가 (맛/서비스 만족)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
            with col3: st.metric("부정 평가 (개선 필요)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
            
            st.divider()
            
            st.markdown("<b style='font-size: 16px;'>📈 일별 리뷰 발생 추이</b>", unsafe_allow_html=True)
            trend_df = store_df.groupby('작성일').size().reset_index(name='리뷰 발생 건수')
            trend_df = trend_df.sort_values(by='작성일')
            fig_trend = px.line(trend_df, x='작성일', y='리뷰 발생 건수', markers=True, color_discrete_sequence=['#D32F2F'])
            fig_trend.update_layout(margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_trend, use_container_width=True)
            
            st.divider()
            
            col_chart, col_list = st.columns([1, 2])
            
            with col_chart:
                st.markdown("<b style='font-size: 16px;'>누적 감정 비율</b>", unsafe_allow_html=True)
                sentiment_counts = store_df['감정분석'].value_counts().reset_index()
                sentiment_counts.columns = ['감정', '비율']
                fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', color_discrete_map={'긍정':'#111111', '부정':'#D32F2F', '중립':'#AAAAAA'})
                fig.update_layout(margin=dict(t=20, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
            with col_list:
                st.markdown("<b style='font-size: 16px;'>최신 리뷰 상세 내역</b>", unsafe_allow_html=True)
                display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
                st.dataframe(display_df, use_container_width=True)
