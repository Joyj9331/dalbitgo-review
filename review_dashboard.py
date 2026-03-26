import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import hashlib
import re
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 고정형 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, li, span {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stApp {
        background-color: #F4F6F8;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333333;
    }
    /* 사이드바 내부 텍스트는 밝게 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #EEEEEE !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #D32F2F; 
    }
    
    @keyframes zoomInBack {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes suckIn {
        0% { transform: scale(1.05); opacity: 0; filter: blur(3px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    .login-wrapper {
        display: flex; justify-content: center; align-items: center;
        margin-top: 10vh; margin-bottom: 2vh;
        animation: zoomInBack 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .login-container {
        background-color: #111111 !important; 
        padding: 40px 50px; border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        text-align: center; border-top: 5px solid #D32F2F; width: 100%;
        border: 1px solid #333333;
    }
    .login-container p, .login-container span, .login-container div, .login-container label {
        color: #FFFFFF !important;
    }
    .brand-title { font-size: 26px; margin-top: 15px; margin-bottom: 5px; color: #FFFFFF !important; font-weight: 700 !important; }
    .brand-subtitle { color: #E8B923 !important; font-size: 14px; margin-bottom: 30px; }

    /* 로고 폴백용 텍스트 스타일 */
    .logo-fallback {
        font-family: 'Gowun Dodum', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: #E8B923 !important;
        letter-spacing: 1px;
        padding: 8px 0;
    }

    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: 1px solid #CCCCCC !important;
    }
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC !important;
    }
    li[role="option"] { color: #111111 !important; }
    li[role="option"]:hover { background-color: #F4F6F8 !important; color: #D32F2F !important; }

    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    div[data-testid="stExpander"] summary { background-color: #F8F9FA !important; }
    div[data-testid="stExpander"] summary p { color: #111111 !important; font-weight: 600 !important; }

    .stButton > button {
        background-color: #D32F2F !important; border-radius: 6px !important; border: none !important;
        height: 42px; transition: all 0.3s ease;
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #EAEAEA; background-color: #FFFFFF; }
    
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 16px !important; font-weight: 700 !important; color: #888888 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {
        color: #D32F2F !important;
    }

    /* 사이드바 버튼 색상 */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #D32F2F !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 로고 렌더링 헬퍼 (이미지 실패 시 텍스트 폴백)
# ==========================================
LOGO_URL = "https://dalbitgo.com/images/main_logo.png"

def logo_html(height=60, dark_bg=True):
    """
    다크 배경용 로고 HTML을 반환합니다.
    이미지 로드 실패 시 onerror로 텍스트 폴백이 자동 표시됩니다.
    """
    bg = "#111111" if dark_bg else "transparent"
    return f"""
    <div style="background-color:{bg}; padding:15px; border-radius:8px; text-align:center;">
        <img src="{LOGO_URL}" height="{height}"
             style="object-fit:contain; display:block; margin:0 auto;"
             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
        <div class="logo-fallback" style="display:none;">🐟 달빛에 구운 고등어</div>
    </div>
    """

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
            st.markdown(f"""
            <div class="login-wrapper">
                <div class="login-container">
                    <img src="{LOGO_URL}" style="height:60px; object-fit:contain;"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="logo-fallback" style="display:none;">🐟 달빛에 구운 고등어</div>
                    <div class="brand-title">리뷰 관리 프로그램</div>
                    <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.text_input("본사 직원 인증 코드를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="비밀번호 입력 후 엔터")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("인증 코드가 일치하지 않습니다.")
        return False
    else:
        st.markdown("<style>[data-testid='block-container'] { animation: suckIn 0.6s cubic-bezier(0.2, 0.8, 1) forwards; }</style>", unsafe_allow_html=True)
        return True

if not check_password():
    st.stop()

# ==========================================
# 3. 데이터 정제 및 상태 관리
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

def clean_date_format(d_str):
    d_str = str(d_str).strip()
    m = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', d_str)
    if m: return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    m = re.search(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.', d_str)
    if m: return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', d_str)
    if m: return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    today = datetime.now()
    if '어제' in d_str: return (today - timedelta(days=1)).strftime('%Y-%m-%d')
    if '일 전' in d_str:
        try:
            days_ago = int(re.search(r'(\d+)일 전', d_str).group(1))
            return (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        except: pass
    if '시간 전' in d_str or '분 전' in d_str:
        return today.strftime('%Y-%m-%d')
    return today.strftime('%Y-%m-%d')

def load_data():
    filename = "가맹점_리뷰수집결과_누적.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        df = pd.DataFrame({"매장명": ["데이터 없음"], "작성일": ["2026-03-26"], "리뷰내용": ["수집기 실행 필요"], "감정분석": ["중립"]})
    df['작성일'] = df['작성일'].apply(clean_date_format)
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
# 4. 사이드바 메뉴 (다크 테마, 로고 폴백 적용)
# ==========================================
st.sidebar.markdown(logo_html(height=60, dark_bg=True), unsafe_allow_html=True)
st.sidebar.markdown(
    "<p style='text-align:center; font-size:13px; color:#AAAAAA !important; font-weight:700; margin-top:8px;'>본사 통합 업무 포털</p>",
    unsafe_allow_html=True
)
st.sidebar.divider()
st.sidebar.markdown(
    "<p style='font-size:15px; font-weight:700; text-align:center; color:#FFFFFF !important;'>가맹점 리뷰 통합 관리</p>",
    unsafe_allow_html=True
)
st.sidebar.divider()
if st.sidebar.button("최신 데이터 동기화", use_container_width=True):
    st.rerun()

st.sidebar.markdown("""
<div style='font-size:11px; color:#888888; text-align:center; line-height:1.7; margin-top:50px;'>
    <b style='color:#AAAAAA !important;'>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 그래프 공통 레이아웃 설정
# ==========================================
CHART_LAYOUT = dict(
    margin=dict(t=30, b=80, l=10, r=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#111111", family="Noto Sans KR", size=13),
    xaxis=dict(
        title=dict(text="수집 일자", font=dict(size=13, color="#444444")),
        type="category",
        showgrid=False,
        tickfont=dict(color="#333333", size=11),
        tickangle=-40,           # ✅ 날짜 레이블 45도 기울여 겹침 해소
        automargin=True,
    ),
    yaxis=dict(
        title=dict(text="수집 건수", font=dict(size=13, color="#444444")),
        showgrid=True,
        gridcolor="#EAEAEA",
        tickfont=dict(color="#333333", size=11),
        dtick=1,
        automargin=True,
    ),
    bargap=0.35,
)

def make_bar_chart(trend_df):
    """
    감정별 색상 구분 막대 그래프를 생성합니다.
    감정분석 컬럼이 없으면 단색으로 fallback합니다.
    """
    if '감정분석' in trend_df.columns:
        color_map = {"긍정": "#1976D2", "부정": "#D32F2F", "중립": "#78909C"}
        fig = px.bar(
            trend_df, x="작성일", y="건수",
            color="감정분석",
            color_discrete_map=color_map,
            text="건수",
            barmode="stack",
        )
    else:
        fig = px.bar(
            trend_df, x="작성일", y="건수",
            text="건수",
            color_discrete_sequence=["#D32F2F"],
        )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#111111", size=13, family="Noto Sans KR"),
        marker_line_width=0,
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig

# ==========================================
# 6. 가맹점 리뷰 관리 메인 화면
# ==========================================
st.markdown("<h1>가맹점 리뷰 통합 관리 <span style='font-size:18px; color:#777;'>| Review Management</span></h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석"])

with tab1:
    st.markdown("<h3 style='margin-top:20px;'>즉각 조치 요망 매장 리스트</h3>", unsafe_allow_html=True)
    resolved_ids = get_saved_ids(STATE_RESOLVED)
    active_neg = df[(df['감정분석'] == '부정') & (~df['id'].isin(resolved_ids))]
    
    if not active_neg.empty:
        st.error(f"총 {len(active_neg)}건의 미조치 부정 리뷰가 있습니다.")
        for _, row in active_neg.iterrows():
            with st.expander(f"[{row['매장명']}] {row['작성일']} | {row['리뷰내용'][:30]}..."):
                st.write(f"내용: {row['리뷰내용']}")
                c1, c2, _ = st.columns([1, 1, 2])
                if c1.button("조치 완료", key=f"re_{row['id']}"):
                    add_saved_id(STATE_RESOLVED, row['id'])
                    st.rerun()
                if c2.button("긍정 리뷰로 분류 변경", key=f"ov_{row['id']}"):
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
    st.markdown("<b style='font-size:14px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store")
    f_stores = [s for s in full_store_list if q.replace(" ", "") in s.replace(" ", "")] if q else full_store_list

    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores)
        s_df = df[df['매장명'] == sel_store].copy()

        if not s_df.empty:
            st.markdown(f"### [{sel_store}] 리뷰 분석 리포트")
            m1, m2, m3 = st.columns(3)
            m1.metric("누적 수집된 전체 리뷰", f"{len(s_df)}건")
            m2.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
            m3.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")

            st.markdown("**일별 리뷰 수집 및 발생 추이**")

            # 감정분석 포함 집계로 색상 구분 가능하게
            trend_df = (
                s_df.groupby(['작성일', '감정분석'])
                .size()
                .reset_index(name='건수')
                .sort_values(by='작성일')
            )
            fig = make_bar_chart(trend_df)
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("### 수집 데이터 전수 검증 (원본 내역)")
            st.write("자동 수집된 원본 리뷰 텍스트입니다. 인공지능 분류 내역을 확인해 보십시오.")
            st.dataframe(
                s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False),
                use_container_width=True
            )
        else:
            st.info("선택하신 매장의 수집된 데이터가 없습니다.")
