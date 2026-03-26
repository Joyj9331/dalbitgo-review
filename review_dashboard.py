import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
import re
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 미니멀/플랫 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

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
        background-color: #F8F9FA;
    }
    
    /* 사이드바 순백색 강제 고정 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0;
    }
    [data-testid="stSidebar"] * {
        color: #111111 !important; 
    }
    
    /* 🌟 정통 실무형 플랫 디자인 메트릭 카드 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px 25px;
        border-radius: 4px;
        box-shadow: none;
        border-left: 4px solid #D32F2F; 
    }
    
    /* 로그인 컨테이너 간결화 */
    .login-wrapper {
        display: flex; justify-content: center; align-items: center;
        margin-top: 10vh; margin-bottom: 2vh;
    }
    .login-container {
        background-color: #FFFFFF !important; 
        padding: 40px 50px; border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center; border-top: 4px solid #D32F2F; width: 100%;
        border: 1px solid #E0E0E0;
    }
    .login-container p, .login-container span, .login-container div, .login-container label {
        color: #111111 !important;
    }
    .brand-title { font-size: 24px; margin-top: 15px; margin-bottom: 5px; color: #111111 !important; font-weight: 700 !important; }
    .brand-subtitle { color: #666666 !important; font-size: 13px; margin-bottom: 30px; }

    /* 입력창 및 드롭다운 플랫 디자인 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 4px !important;
    }
    div[data-baseweb="input"] > div:focus-within, .stTextInput input:focus {
        border-color: #111111 !important;
        box-shadow: none !important;
    }
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 4px !important;
    }
    li[role="option"] { color: #111111 !important; }
    li[role="option"]:hover { background-color: #F8F9FA !important; color: #D32F2F !important; }

    /* 🌟 미니멀 Expander 디자인 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0;
        border-left: 3px solid #D32F2F; box-shadow: none;
    }
    div[data-testid="stExpander"] summary { background-color: transparent !important; }
    div[data-testid="stExpander"] summary p { color: #111111 !important; font-weight: 600 !important; }

    /* 🌟 실무형 버튼 디자인 (애니메이션 제거, 깔끔함 유지) */
    .stButton > button {
        background-color: #111111 !important; border-radius: 4px !important; border: none !important;
        height: 42px;
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    .stButton > button:hover {
        background-color: #333333 !important;
    }
    
    /* 데이터프레임 각진 디자인 */
    [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0; background-color: #FFFFFF; }
    
    /* 커스텀 탭 디자인 */
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 15px !important; font-weight: 700 !important; color: #888888 !important;
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
                    <div style="background-color: #111111; padding: 20px; border-radius: 4px; margin-bottom: 15px;">
                        <img src="https://dalbitgo.com/images/main_logo.png" style="height: 50px; object-fit: contain;">
                    </div>
                    <div class="brand-title">본사 통합 관리 시스템</div>
                    <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.text_input("본사 직원 인증 코드를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="비밀번호 입력 후 엔터")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("인증 코드가 일치하지 않습니다.")
        return False
    else:
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
    if '시간 전' in d_str or '분 전' in d_str: return today.strftime('%Y-%m-%d')
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
# 4. 사이드바 메뉴
# ==========================================
st.sidebar.markdown("""
<!-- 로고 뒷배경에만 먹색(#111111) 박스 적용 (라운딩 최소화) -->
<div style="background-color: #111111; padding: 15px; border-radius: 4px; text-align: center; margin-top: 10px; margin-bottom: 25px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;">
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #666666 !important; font-weight: 700; letter-spacing: 1px;'>본사 통합 업무 포털</p>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 리뷰 통합 관리</p>", unsafe_allow_html=True)
st.sidebar.divider()

# 직관적인 버튼 명칭으로 변경
if st.sidebar.button("🔄 최신 리뷰 불러오기", use_container_width=True): 
    st.rerun()

st.sidebar.markdown("""
<div style='font-size: 11px; color: #999999; text-align: center; line-height: 1.6; margin-top: 60px;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 가맹점 리뷰 관리 메인 화면
# ==========================================
st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #888; font-weight: 500;'>| Review Management</span></h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석"])

with tab1:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>즉각 조치 요망 매장 리스트</h3>", unsafe_allow_html=True)
    resolved_ids = get_saved_ids(STATE_RESOLVED)
    active_neg = df[(df['감정분석'] == '부정') & (~df['id'].isin(resolved_ids))]
    
    if not active_neg.empty:
        st.error(f"총 {len(active_neg)}건의 미조치 부정 리뷰가 있습니다.")
        for _, row in active_neg.iterrows():
            with st.expander(f"[{row['매장명']}] {row['작성일']} | {row['리뷰내용'][:35]}..."):
                st.write(f"**상세 내용:** {row['리뷰내용']}")
                st.write("") # 여백
                c1, c2, _ = st.columns([1.5, 1.5, 3])
                if c1.button("조치 완료", key=f"re_{row['id']}", use_container_width=True): 
                    add_saved_id(STATE_RESOLVED, row['id'])
                    st.rerun()
                if c2.button("긍정 분류로 변경", key=f"ov_{row['id']}", use_container_width=True): 
                    add_saved_id(STATE_OVERRIDDEN, row['id'])
                    st.rerun()
    else: 
        st.success("모든 부정 리뷰에 대한 조치가 완료되었습니다.")
    
    st.divider()
    st.markdown("<h3 style='margin-bottom: 15px;'>매장별 누적 리뷰 랭킹</h3>", unsafe_allow_html=True)
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
    st.markdown("<b style='font-size: 14px; display: block; margin-bottom: 8px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store", label_visibility="collapsed")
    f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
    
    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores, label_visibility="collapsed")
        s_df = df[df['매장명'] == sel_store]
        
        if not s_df.empty:
            st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{sel_store}] 리뷰 분석 리포트</h3>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("누적 수집된 전체 리뷰", f"{len(s_df)}건")
            m2.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
            m3.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")
            
            st.markdown("<div style='margin-top: 35px; margin-bottom: 10px;'><b>일별 리뷰 수집 및 발생 추이</b></div>", unsafe_allow_html=True)
            trend_df = s_df.groupby('작성일').size().reset_index(name='건수').sort_values(by='작성일')
            
            # 고급스러운 바 차트 디자인 적용
            fig_bar = px.bar(trend_df, x='작성일', y='건수', text='건수')
            fig_bar.update_traces(
                marker_color='#111111', # 바 차트도 먹색으로 변경하여 차분함 유지
                textposition='outside', 
                textfont=dict(color='#111111', size=13, family="Noto Sans KR"),
                hoverlabel=dict(bgcolor="#D32F2F", font_size=13, font_family="Noto Sans KR")
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=20, l=0, r=0), 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font=dict(color="#111111", family="Noto Sans KR"),
                xaxis=dict(title="수집 일자", type='category', showgrid=False, tickfont=dict(color="#666666")),
                yaxis=dict(title="수집 건수", showgrid=True, gridcolor="#EAEAEA", tickfont=dict(color="#666666"), dtick=1),
                hovermode="x unified"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            st.markdown("<h3 style='margin-bottom: 15px;'>수집 데이터 전수 검증 (원본 내역)</h3>", unsafe_allow_html=True)
            st.write("자동 수집된 원본 리뷰 텍스트입니다. 인공지능 분류 내역을 확인해 보십시오.")
            st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)
        else: 
            st.info("선택하신 매장의 수집된 데이터가 없습니다.")
