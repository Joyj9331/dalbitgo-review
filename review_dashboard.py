import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib

# ==========================================
# 1. 페이지 기본 설정 및 고정형 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", page_icon="bar-chart", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 텍스트 색상 먹색 강제 고정 */
    h1, h2, h3, h4, h5, h6, p, label, li, span {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* 전체 배경 라이트 그레이 */
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* 사이드바 다크 톤 강제 고정 및 텍스트 화이트 처리 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important; 
    }
    
    /* 메트릭 카드 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #D32F2F; 
    }
    
    /* 애니메이션 */
    @keyframes zoomInBack {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes suckIn {
        0% { transform: scale(1.05); opacity: 0; filter: blur(3px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    /* 로그인 컨테이너 */
    .login-wrapper {
        display: flex; justify-content: center; align-items: center;
        margin-top: 10vh; margin-bottom: 2vh;
        animation: zoomInBack 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .login-container {
        background-color: #FFFFFF !important; 
        padding: 40px 50px; border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        text-align: center; border-top: 5px solid #D32F2F; width: 100%;
        border: 1px solid #EAEAEA;
    }
    .brand-title { font-size: 26px; margin-top: 15px; margin-bottom: 5px; color: #111111 !important; }
    .brand-subtitle { color: #666666 !important; font-size: 14px; margin-bottom: 30px; }

    /* 입력창 및 드롭다운 화이트 강제 고정 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: 1px solid #CCCCCC !important;
    }
    
    /* 드롭다운 팝업 리스트 색반전 (다크 배경 + 화이트 텍스트) */
    div[data-baseweb="popover"], 
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"], 
    ul[role="listbox"] {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
    }
    li[role="option"], li[role="option"] span, li[role="option"] div {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }
    li[role="option"]:hover, li[role="option"]:hover span, li[role="option"]:hover div {
        background-color: #D32F2F !important;
        color: #FFFFFF !important;
    }

    /* Expander 디자인 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    div[data-testid="stExpander"] summary { background-color: #F8F9FA !important; }
    div[data-testid="stExpander"] summary p { color: #111111 !important; font-weight: 600 !important; }

    /* 버튼 디자인 */
    .stButton > button {
        background-color: #D32F2F !important; border-radius: 6px !important; border: none !important;
        height: 42px; transition: all 0.3s ease;
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    
    /* 데이터프레임 */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #EAEAEA; background-color: #FFFFFF; }
    
    /* 커스텀 탭 디자인 */
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 16px !important; font-weight: 700 !important; color: #888888 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {
        color: #D32F2F !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 보안 로그인 시스템
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
            st.text_input("본사 직원 인증 코드를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="비밀번호 입력 후 엔터")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("[오류] 인증 코드가 일치하지 않습니다.")
        return False
    else:
        st.markdown("<style>[data-testid='block-container'] { animation: suckIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }</style>", unsafe_allow_html=True)
        return True

if not check_password():
    st.stop()

# ==========================================
# 3. 데이터 및 상태 관리 (영구 보존)
# ==========================================
STATE_RESOLVED = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].astype(str).tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if str(new_id) not in ids:
        ids.append(str(new_id))
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()

def load_data():
    filename = "가맹점_리뷰수집결과_누적.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        df = pd.DataFrame({"매장명": ["데이터 없음"], "작성일": ["2026-03-26"], "리뷰내용": ["수집기 실행 필요"], "감정분석": ["중립"]})
    
    df['id'] = df.apply(generate_id, axis=1)
    overridden_ids = get_saved_ids(STATE_OVERRIDDEN)
    df.loc[df['id'].isin(overridden_ids), '감정분석'] = '긍정'
    return df

def load_store_list():
    if os.path.exists("가맹점_리뷰링크.xlsx"):
        try:
            sdf = pd.read_excel("가맹점_리뷰링크.xlsx")
            return sorted(sdf['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list() or sorted(df['매장명'].unique().tolist())

# ==========================================
# 4. 사이드바 메뉴 (단일 메뉴 구성)
# ==========================================
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 80%; filter: invert(1) brightness(2);">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #CCCCCC !important; font-weight: 700;'>본사 통합 업무 포털</p>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700;'>가맹점 리뷰 관리</p>", unsafe_allow_html=True)

st.sidebar.divider()
if st.sidebar.button("최신 데이터 동기화", use_container_width=True): 
    st.rerun()

st.sidebar.markdown("""
<div style='font-size: 11px; color: #888888; text-align: center; line-height: 1.5; margin-top: 50px;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 가맹점 리뷰 관리 (빅데이터 검증형 메인 화면)
# ==========================================
st.markdown("<h1>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #777;'>| Review Management</span></h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석"])

with tab1:
    st.markdown("<h3 style='margin-top: 20px;'>즉각 조치 요망 매장 리스트</h3>", unsafe_allow_html=True)
    resolved_ids = get_saved_ids(STATE_RESOLVED)
    active_neg = df[(df['감정분석'] == '부정') & (~df['id'].isin(resolved_ids))]
    
    if not active_neg.empty:
        st.error(f"[경고] 총 {len(active_neg)}건의 미조치 부정 리뷰가 있습니다.")
        for _, row in active_neg.iterrows():
            with st.expander(f"[{row['매장명']}] {row['작성일']} | {row['리뷰내용'][:30]}..."):
                st.write(f"내용: {row['리뷰내용']}")
                c1, c2, _ = st.columns([1, 1, 2])
                if c1.button("조치 완료", key=f"re_{row['id']}"): 
                    add_saved_id(STATE_RESOLVED, row['id'])
                    st.rerun()
                if c2.button("긍정 변경", key=f"ov_{row['id']}"): 
                    add_saved_id(STATE_OVERRIDDEN, row['id'])
                    st.rerun()
    else: 
        st.success("모든 부정 리뷰에 대한 조치가 완료되었습니다.")
    
    st.divider()
    st.markdown("<h3>매장별 누적 리뷰 랭킹</h3>", unsafe_allow_html=True)
    counts = df['매장명'].value_counts().reset_index()
    counts.columns = ['매장명', '리뷰수']
    col_l, col_r = st.columns(2)
    with col_l: 
        st.info("리뷰 활성화 상위 5개 매장")
        st.dataframe(counts.head(5), use_container_width=True)
    with col_r: 
        st.warning("리뷰 관리 필요 하위 5개 매장")
        st.dataframe(counts.tail(5), use_container_width=True)

with tab2:
    st.markdown("<b style='font-size: 14px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store")
    f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
    
    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores)
        s_df = df[df['매장명'] == sel_store]
        
        if not s_df.empty:
            st.markdown(f"### [{sel_store}] 리뷰 분석 리포트")
            m1, m2, m3 = st.columns(3)
            m1.metric("누적 전체 리뷰", f"{len(s_df)}건")
            m2.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
            m3.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")
            
            st.markdown("**일별 리뷰 발생 추이**")
            fig_line = px.line(s_df.groupby('작성일').size().reset_index(name='건수'), x='작성일', y='건수', markers=True, color_discrete_sequence=['#D32F2F'])
            fig_line.update_layout(margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#111111"))
            st.plotly_chart(fig_line, use_container_width=True)
            
            st.divider()
            st.markdown("### 수집 데이터 전수 검증 (원본 내역)")
            st.write("자동 수집된 원본 리뷰 텍스트입니다. 인공지능 분류 내역을 확인해 보십시오.")
            st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)
        else: 
            st.info("선택하신 매장의 수집된 데이터가 없습니다.")
