import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
import re
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 메인 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

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
    
    /* 🌟 메인 화면 배경 (밝은 그레이) 및 기본 텍스트 색상 */
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, label, span { color: #111111 !important; }
    
    /* 🌟 사이드바 블랙 모드 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: none !important;
    }
    /* 사이드바 내 모든 텍스트 하얀색 강제 적용 */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important; 
    }
    /* 사이드바 하얀색 버튼 */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #FFFFFF !important;
        border-radius: 4px !important;
        border: none !important;
        height: 42px;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #111111 !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #E0E0E0 !important;
    }

    /* 🌟 드롭다운 리스트 블랙 바탕 & 하얀 글씨 */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    li[role="option"] { color: #FFFFFF !important; }
    li[role="option"]:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    li[role="option"][aria-selected="true"] { background-color: #D32F2F !important; color: #FFFFFF !important; }

    /* 🌟 "Press Enter to apply" 숨김 처리 (전역 적용) */
    div[data-testid="InputInstructions"] { display: none !important; }

    /* 메인 화면 메트릭/입력창 플랫 디자인 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF; border: 1px solid #E0E0E0;
        padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F; 
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
        background-color: #FFFFFF !important; color: #111111 !important;
        -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important; border-radius: 4px !important;
    }
    div[data-baseweb="input"] > div:focus-within, .stTextInput input:focus {
        border-color: #111111 !important; box-shadow: none !important;
    }
    
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0; border-left: 3px solid #D32F2F;
    }
    div[data-testid="stExpander"] summary { background-color: transparent !important; }
    div[data-testid="stExpander"] summary p { font-weight: 600 !important; }

    /* 메인 화면 전문성 있는 버튼 */
    .main-btn .stButton > button {
        background-color: #111111 !important; border-radius: 4px !important; border: none !important; height: 42px;
    }
    .main-btn .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    .main-btn .stButton > button:hover { background-color: #333333 !important; }
    
    /* 폼 컨테이너 선명하게 */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
    [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0; background-color: #FFFFFF; }

    /* 🌟 은닉된 동기화 버튼 디자인 */
    .hidden-sync-btn .stButton > button {
        background-color: transparent !important;
        color: #CCCCCC !important;
        border: none !important;
        font-size: 12px !important;
        height: auto;
        padding: 5px 10px;
    }
    .hidden-sync-btn .stButton > button * {
        color: #CCCCCC !important;
        font-weight: 400 !important;
    }
    .hidden-sync-btn .stButton > button:hover * {
        color: #888888 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 보안 로그인 시스템 (풀스크린 블랙 / 로고 모션 / 콤팩트 인풋)
# ==========================================
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    # 로그인 화면 전용 전체화면 블랙 CSS 주입
    st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        /* 🌟 [요청1] 로고 페이드인 & 스케일 애니메이션 */
        @keyframes logoZoomIn {
            0% { transform: scale(3.5); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        .animated-logo {
            animation: logoZoomIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            max-width: 320px; 
            margin: 0 auto 20px auto;
            display: block;
        }
        
        /* 🌟 [요청2] 인증코드 폼 사이즈 축소 및 중앙 정렬 */
        .login-box {
            max-width: 260px;
            margin: 0 auto;
        }
        .login-box .stTextInput input {
            background-color: #111111 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            border: 1px solid #333333 !important;
            text-align: center;
            font-size: 14px !important;
            letter-spacing: 2px;
            padding: 8px;
        }
        .login-box .stTextInput input:focus {
            border-color: #666666 !important;
        }
        
        /* 🌟 [요청2] 패스워드 보기/숨기기 눈동자 아이콘 하얀색 처리 (검은 배경 대비) */
        div[data-testid="stTextInput"] svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }
        
        /* 🌟 [요청2] 시스템 로그인 버튼 축소 및 하얀색 텍스트 지정 */
        .login-btn {
            max-width: 140px;
            margin: 0 auto;
        }
        .login-btn .stButton > button {
            background-color: #222222 !important;
            border: 1px solid #444444 !important;
            height: 38px !important;
        }
        .login-btn .stButton > button * {
            color: #FFFFFF !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            letter-spacing: 1px;
        }
        .login-btn .stButton > button:hover {
            background-color: #444444 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top: 22vh; text-align: center;'>", unsafe_allow_html=True)
        # 애니메이션이 적용된 로고 호출
        st.markdown('<img src="https://dalbitgo.com/images/main_logo.png" class="animated-logo">', unsafe_allow_html=True)
        st.markdown('<div style="color: #555555 !important; font-size: 13px; margin-bottom: 50px; letter-spacing: 1px;">프리미엄 450°C 화덕 생선구이 전문점</div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            pwd = st.text_input("auth", type="password", placeholder="인증코드를 입력하세요", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            st.markdown('<div class="login-btn">', unsafe_allow_html=True)
            submit = st.form_submit_button("SYSTEM LOGIN", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
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
# 4. 사이드바 메뉴 (푸터 최하단 고정)
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px; text-align: center; margin-top: 20px; margin-bottom: 40px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;">
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 리뷰 통합 관리</p>", unsafe_allow_html=True)
st.sidebar.divider()

# 🌟 [요청3] 회사 정보를 사이드바 가장 아래쪽으로 배치
st.sidebar.markdown("""
<div style='margin-top: 50vh; text-align: center; font-size: 11px; line-height: 1.6; color: #666666 !important;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 가맹점 리뷰 관리 메인 화면
# ==========================================
st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #888 !important; font-weight: 500;'>| Review Management</span></h1>", unsafe_allow_html=True)
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
                    
                    st.markdown('<div class="main-btn">', unsafe_allow_html=True)
                    c1, c2, _ = st.columns([1.5, 1.5, 3])
                    if c1.button("해피콜 조치 완료", key=f"re_{row['id']}", use_container_width=True): 
                        add_saved_id(STATE_RESOLVED, row['id'])
                        st.rerun()
                    if c2.button("긍정 분류로 예외 처리", key=f"ov_{row['id']}", use_container_width=True): 
                        add_saved_id(STATE_OVERRIDDEN, row['id'])
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
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
                
                st.markdown("<div style='margin-top: 35px; margin-bottom: 10px;'><b>일자별 리뷰 작성 추이</b></div>", unsafe_allow_html=True)
                
                trend_df = s_df.groupby('작성일').size().reset_index(name='건수').sort_values(by='작성일')
                
                fig_bar = px.bar(trend_df, x='작성일', y='건수', text='건수')
                fig_bar.update_traces(
                    marker_color='#111111',
                    textposition='outside', 
                    textfont=dict(color='#111111', size=13, family="Noto Sans KR"),
                    hoverlabel=dict(bgcolor="#D32F2F", font_size=13, font_family="Noto Sans KR")
                )
                fig_bar.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0), 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color="#111111", family="Noto Sans KR"),
                    xaxis=dict(title="리뷰 작성 일자", type='category', showgrid=False, tickfont=dict(color="#666666")),
                    yaxis=dict(title="작성 건수(건)", showgrid=True, gridcolor="#EAEAEA", tickfont=dict(color="#666666"), dtick=1),
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

# 최신 데이터 동기화 버튼을 화면 우측 최하단에 작게 은닉
st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
col_empty, col_sync = st.columns([10, 1])
with col_sync:
    st.markdown('<div class="hidden-sync-btn">', unsafe_allow_html=True)
    if st.button("최신 데이터 동기화", help="최근 수집 데이터를 불러옵니다.", use_container_width=True):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
