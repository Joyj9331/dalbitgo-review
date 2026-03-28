import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
import re
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 상태 초기화
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

# 💡 누구든 처음 입장 시 '다크 모드'로 시작하도록 기본값 변경
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ==========================================
# 2. 공통 CSS (폰트, 사이드바, 공통 디자인)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* 🌟 사이드바는 모드 상관없이 무조건 블랙 고정 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important; 
    }
    
    /* 드롭다운 리스트 블랙 고정 */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    li[role="option"] { color: #FFFFFF !important; }
    li[role="option"]:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    li[role="option"][aria-selected="true"] { background-color: #D32F2F !important; color: #FFFFFF !important; }

    /* "Press Enter to apply" 숨김 처리 */
    div[data-testid="InputInstructions"] { display: none !important; }
    
    /* 폼 컨테이너 클리어 및 컬럼 간격 최소화 */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
    div[data-testid="column"] { padding: 0 4px !important; }

    /* 🌟 [핵심 수술] 조치 완료 액션 버튼 공통 속성 (Primary Button) */
    [data-testid="baseButton-primary"] {
        border-radius: 4px !important;
        height: 42px !important;
        transition: all 0.2s ease;
    }
    [data-testid="baseButton-primary"] p, [data-testid="baseButton-primary"] span {
        font-weight: 700 !important;
        color: #FFFFFF !important; /* 텍스트는 어떤 모드든 무조건 하얀색 강제 고정 */
    }

    /* 🌟 사이드바 테마 변경 버튼 (동그라미) */
    .theme-marker + div button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    .theme-marker + div button p, .theme-marker + div button span {
        font-size: 16px !important;
        line-height: 1 !important;
    }

    /* 🌟 우측 상단 테마 변경 버튼 (동그라미) */
    .top-theme-marker + div button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        float: right !important;
        margin-top: 10px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    .top-theme-marker + div button p, .top-theme-marker + div button span {
        font-size: 16px !important;
        line-height: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 다크/라이트 모드 테마 CSS 동적 주입
# ==========================================
if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #1A1A1A !important; }
        h1, h2, h3, h4, h5, h6, p, label, span { color: #F0F0F0 !important; }
        
        div[data-testid="metric-container"] {
            background-color: #222222 !important; border: 1px solid #333333 !important;
            padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F !important; 
        }
        
        /* 메인화면 폼 요소 (로그인 화면 간섭 방지) */
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #222222 !important; color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important; border: 1px solid #444444 !important; border-radius: 4px !important;
        }
        .main-content div[data-baseweb="input"] > div:focus-within, .main-content .stTextInput input:focus {
            border-color: #888888 !important;
        }
        
        div[data-testid="stExpander"] {
            background-color: #222222 !important; border-radius: 4px; border: 1px solid #333333 !important; border-left: 3px solid #D32F2F !important;
        }
        div[data-testid="stExpander"] summary { background-color: transparent !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #F0F0F0 !important; }
        
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #333333 !important; background-color: #222222 !important; }
        
        /* 🌟 조치 완료 버튼 다크모드 배경 */
        [data-testid="baseButton-primary"] {
            background-color: #333333 !important;
            border: 1px solid #555555 !important;
        }
        [data-testid="baseButton-primary"]:hover {
            background-color: #555555 !important;
            border-color: #888888 !important;
        }

        /* 다크모드 테마 전환 버튼 */
        .theme-marker + div button, .top-theme-marker + div button { background-color: #222222 !important; border: 1px solid #444444 !important; }
        .theme-marker + div button:hover, .top-theme-marker + div button:hover { background-color: #444444 !important; }
        .theme-marker + div button p, .top-theme-marker + div button p { color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA !important; }
        h1, h2, h3, h4, h5, h6, p, label, span { color: #111111 !important; }
        
        div[data-testid="metric-container"] {
            background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important;
            padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F !important; 
        }
        
        /* 메인화면 폼 요소 (로그인 화면 간섭 방지) */
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #FFFFFF !important; color: #111111 !important;
            -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important; border-radius: 4px !important;
        }
        .main-content div[data-baseweb="input"] > div:focus-within, .main-content .stTextInput input:focus {
            border-color: #111111 !important;
        }
        
        div[data-testid="stExpander"] {
            background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0 !important; border-left: 3px solid #D32F2F !important;
        }
        div[data-testid="stExpander"] summary { background-color: transparent !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #111111 !important; }
        
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }
        
        /* 🌟 조치 완료 버튼 라이트모드 배경 */
        [data-testid="baseButton-primary"] {
            background-color: #111111 !important;
            border: 1px solid #000000 !important;
        }
        [data-testid="baseButton-primary"]:hover {
            background-color: #333333 !important;
        }

        /* 라이트모드 테마 전환 버튼 */
        .theme-marker + div button, .top-theme-marker + div button { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
        .theme-marker + div button:hover, .top-theme-marker + div button:hover { background-color: #E0E0E0 !important; }
        .theme-marker + div button p, .top-theme-marker + div button p { color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# 4. 보안 로그인 시스템 (풀스크린 블랙 / 완벽한 가로 정렬 폼)
# ==========================================
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    # 🌟 로그인 화면 전용 독자적 CSS
    st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        @keyframes logoZoomIn {
            0% { transform: scale(3.5); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        .animated-logo {
            animation: logoZoomIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            max-width: 280px; 
            margin: 0 auto 30px auto;
            display: block;
        }
        
        /* 폼 폭 강제 고정 및 컬럼 간섭 제거 */
        [data-testid="stForm"] {
            max-width: 280px !important;
            margin: 0 auto !important;
            background-color: transparent !important;
            border: none !important;
        }
        
        /* 컬럼을 수직 중앙으로 강제 정렬하여 삐뚤어짐 방지 */
        [data-testid="column"] {
            padding: 0 4px !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        /* 입력창 높이 고정 및 세련된 디자인 */
        div[data-baseweb="input"] > div {
            background-color: #111111 !important;
            border: 1px solid #444444 !important;
            border-radius: 4px !important;
            height: 42px !important;
        }
        input[type="password"] {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            text-align: center !important;
            font-size: 13px !important;
            letter-spacing: 2px;
            background-color: transparent !important;
        }
        div[data-baseweb="input"] > div:focus-within {
            border-color: #888888 !important;
        }
        
        /* 패스워드 눈동자 아이콘 하얀색 */
        div[data-testid="stTextInput"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }
        
        /* 버튼 시인성 대폭 강화 및 높이 완벽 일치 */
        [data-testid="stFormSubmitButton"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stFormSubmitButton"] > button {
            background-color: #444444 !important;
            border: 1px solid #666666 !important;
            border-radius: 4px !important;
            height: 42px !important;
            width: 100% !important;
            padding: 0 !important;
            transition: all 0.2s ease;
        }
        [data-testid="stFormSubmitButton"] > button p {
            color: #FFFFFF !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 1px;
            margin: 0 !important;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #555555 !important;
            border-color: #888888 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top: 25vh; text-align: center;'>", unsafe_allow_html=True)
        
        # 애니메이션 로고
        st.markdown('<img src="https://dalbitgo.com/images/main_logo.png" class="animated-logo">', unsafe_allow_html=True)
        
        # 폼 내부 레이아웃
        with st.form("login_form", clear_on_submit=True):
            c_in, c_btn = st.columns([2.5, 1]) # 가로 비율 설정
            with c_in:
                pwd = st.text_input("auth", type="password", placeholder="인증코드", label_visibility="collapsed")
            with c_btn:
                submit = st.form_submit_button("LOGIN")
                
            if submit:
                if pwd == "51015":
                    st.session_state["password_correct"] = True
                    st.rerun()
                elif pwd:
                    st.error("인증 코드가 일치하지 않습니다.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    return False

if not check_password():
    st.stop()

# ==========================================
# 5. 데이터 정제 및 상태 관리
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
        df = pd.DataFrame(columns=["매장명", "작성일", "리뷰내용", "감정분석"])
    
    if not df.empty:
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
full_store_list = load_store_list() or (sorted(df['매장명'].unique().tolist()) if not df.empty else [])

# ==========================================
# 6. 사이드바 메뉴 
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px; text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;">
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 리뷰 통합 관리</p>", unsafe_allow_html=True)
st.sidebar.divider()

# 🌟 사이드바 테마 버튼 (만약 사용할 경우를 대비한 뼈대 마커)
st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.sidebar.columns([1, 1, 1])
with c2:
    st.markdown('<div class="theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "●"
    if st.button(theme_icon, key="sidebar_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# 🌟 겹침(오버랩) 버그 원천 차단
st.sidebar.markdown("<div style='height: 45vh;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='text-align: center; font-size: 11px; line-height: 1.6; color: #666666 !important; border-top: 1px solid #333333; padding-top: 15px;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. 가맹점 리뷰 관리 메인 화면
# ==========================================
# 로그인 후 간섭을 막기 위한 메인 컨텐츠 래퍼 적용
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# 💡 상단 타이틀과 우측 테마 전환 버튼 배치
col_title, col_theme = st.columns([10, 1])
with col_title:
    st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #888 !important; font-weight: 500;'>| Review Management</span></h1>", unsafe_allow_html=True)
with col_theme:
    # 🌟 우측 상단 테마 버튼 전용 마커
    st.markdown('<div class="top-theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "●"
    if st.button(theme_icon, key="top_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

tab1, tab2 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석"])

with tab1:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>즉각 조치 요망 매장 리스트 (영구 보존)</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("아직 수집된 리뷰 데이터가 없습니다. 크롤링 봇을 실행해 주십시오.")
    else:
        total_neg_df = df[df['감정분석'] == '부정']
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        active_neg = total_neg_df[~total_neg_df['id'].isin(resolved_ids)].sort_values(by='작성일', ascending=False)
        
        if total_neg_df.empty:
            st.success("누적된 수집 리뷰 중 '부정(불만)' 키워드가 감지된 내역이 단 한 건도 없습니다.")
        elif not active_neg.empty:
            st.error(f"총 {len(active_neg)}건의 미조치 부정 리뷰가 남아있습니다. 반드시 점주 확인 후 [조치 완료]를 눌러 전산에서 소거해 주십시오.")
            for _, row in active_neg.iterrows():
                with st.expander(f"[{row['매장명']}] {row['작성일']} | {str(row['리뷰내용'])[:35]}..."):
                    st.write(f"**상세 내용:** {row['리뷰내용']}")
                    st.write("") 
                    
                    c1, c2, _ = st.columns([1.5, 1.5, 3])
                    # 💡 [핵심 수술] type="primary"를 명시하여 제가 짠 디자인 락(Lock)이 정확히 체결되도록 조치
                    if c1.button("해피콜 조치 완료", key=f"re_{row['id']}", use_container_width=True, type="primary"): 
                        add_saved_id(STATE_RESOLVED, row['id'])
                        st.rerun()
                    if c2.button("긍정 분류로 예외 처리", key=f"ov_{row['id']}", use_container_width=True, type="primary"): 
                        add_saved_id(STATE_OVERRIDDEN, row['id'])
                        st.rerun()
        else: 
            st.success(f"발견되었던 부정 리뷰 {len(total_neg_df)}건에 대한 본사 해피콜 및 전산 조치가 100% 완료되었습니다.")
        
        st.divider()
        
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        st.markdown(f"<h3 style='margin-bottom: 15px;'>매장별 활성도 랭킹 (어제 기준: {yesterday_str})</h3>", unsafe_allow_html=True)
        
        all_counts = pd.DataFrame({'매장명': full_store_list, '리뷰수': 0})
        yesterday_df = df[df['작성일'] == yesterday_str]
        
        if not yesterday_df.empty:
            y_counts = yesterday_df['매장명'].value_counts().reset_index(name='리뷰수')
            merged_counts = pd.merge(all_counts, y_counts, on='매장명', how='left').fillna(0)
            merged_counts['리뷰수'] = merged_counts['리뷰수_x'] + merged_counts['리뷰수_y']
            merged_counts.drop(columns=['리뷰수_x', '리뷰수_y'], inplace=True)
            all_counts = merged_counts
            
        all_counts['리뷰수'] = all_counts['리뷰수'].astype(int)
        all_counts = all_counts.sort_values(by=['리뷰수', '매장명'], ascending=[False, True]).reset_index(drop=True)
        
        col_l, col_r = st.columns(2)
        with col_l: 
            st.info("리뷰 활성화 우수 매장 (TOP 5)")
            st.dataframe(all_counts.head(5), use_container_width=True)
        with col_r: 
            st.warning("리뷰 관리 필요 매장 (BOTTOM 5)")
            st.dataframe(all_counts.tail(5), use_container_width=True)

with tab2:
    st.markdown("<b style='font-size: 14px; display: block; margin-bottom: 8px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store", label_visibility="collapsed")
    f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
    
    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores, label_visibility="collapsed")
        
        if not df.empty:
            s_df = df[df['매장명'] == sel_store]
            
            if not s_df.empty:
                st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{sel_store}] 리뷰 분석 리포트</h3>", unsafe_allow_html=True)
                
                unique_days = s_df['작성일'].nunique()
                daily_average = round(len(s_df) / unique_days, 1) if unique_days > 0 else 0
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("누적 수집 리뷰", f"{len(s_df)}건")
                m2.metric("일평균 작성량", f"{daily_average}건")
                m3.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
                m4.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")
                
                st.markdown("<div style='margin-top: 35px; margin-bottom: 10px;'><b>일자별 리뷰 감정 추이 (개선/악화 지표)</b></div>", unsafe_allow_html=True)
                
                trend_df = s_df.groupby(['작성일', '감정분석']).size().reset_index(name='건수').sort_values(by='작성일')
                
                chart_font_color = "#E0E0E0" if st.session_state.theme == "dark" else "#111111"
                chart_grid_color = "#333333" if st.session_state.theme == "dark" else "#EAEAEA"
                
                color_map = {
                    '긍정': '#4CAF50',  
                    '부정': '#E53935',  
                    '중립': '#9E9E9E'   
                }

                fig_bar = px.bar(trend_df, x='작성일', y='건수', color='감정분석', 
                                 text='건수', color_discrete_map=color_map,
                                 barmode='stack')
                                 
                fig_bar.update_traces(
                    textposition='inside', 
                    textfont=dict(color='#FFFFFF', size=12, family="Noto Sans KR"),
                    hoverlabel=dict(font_size=13, font_family="Noto Sans KR")
                )
                fig_bar.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0), 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color=chart_font_color, family="Noto Sans KR"),
                    xaxis=dict(title="리뷰 작성 일자", type='category', showgrid=False, tickfont=dict(color="#888888")),
                    yaxis=dict(title="작성 건수(건)", showgrid=True, gridcolor=chart_grid_color, tickfont=dict(color="#888888"), dtick=1),
                    legend=dict(title="감정 분류", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode="x unified"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.divider()
                st.markdown("<h3 style='margin-bottom: 15px;'>수집 데이터 전수 검증 (원본 내역)</h3>", unsafe_allow_html=True)
                st.write("자동 수집된 원본 리뷰 텍스트입니다. 인공지능 분류 내역을 확인해 보십시오.")
                st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)
            else: 
                st.info("선택하신 매장의 수집된 데이터가 없습니다.")
        else:
            st.info("전체 리뷰 데이터가 아직 수집되지 않았습니다.")

st.markdown('</div>', unsafe_allow_html=True)
