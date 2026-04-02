import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
import re
from datetime import datetime, timedelta

# 💡 [핵심 버그 해결] 대시보드 실행 시 현재 폴더 경로를 강제로 고정하여 데이터를 못 찾는 현상 방지
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)
except:
    BASE_DIR = os.getcwd()

# ==========================================
# 1. 페이지 기본 설정 및 상태 초기화
# ==========================================
st.set_page_config(page_title="가맹점 통합 관제 시스템", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "trigger_scroll" not in st.session_state:
    st.session_state.trigger_scroll = False

# ==========================================
# 2. 공통 CSS (기존 디자인 및 경쟁사 4열 병렬 스타일 통합)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"]  { font-family: 'Noto Sans KR', sans-serif !important; }
    h1, h2, h3, .brand-title { font-family: 'Gowun Dodum', sans-serif !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] { background-color: #111111 !important; border-right: none !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #FFFFFF !important; }
    div[data-testid="InputInstructions"] { display: none !important; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
    div[data-testid="column"] { padding: 0 8px !important; }
    [data-testid="baseButton-primary"] { border-radius: 4px !important; height: 42px !important; transition: all 0.2s ease; }
    [data-testid="baseButton-primary"] p, [data-testid="baseButton-primary"] span { font-weight: 700 !important; color: #FFFFFF !important; }
    .top-theme-marker + div button {
        border-radius: 50% !important; width: 40px !important; height: 40px !important;
        padding: 0 !important; float: right !important; margin-top: 10px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        transition: all 0.3s ease;
    }
    .top-theme-marker + div button p, .top-theme-marker + div button span { font-size: 16px !important; line-height: 1 !important; }
    
    /* 육하원칙 보고서 스타일 박스 (기존 유지) */
    .report-container { border: 1px solid #444; border-radius: 6px; background-color: #1e1e1e; padding: 20px; margin-top: 10px; margin-bottom: 15px; }
    .report-header { font-size: 15px; font-weight: 700; color: #90caf9; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 8px; }
    .report-section { margin-bottom: 15px; }
    .report-label { font-size: 13px; color: #aaaaaa; margin-bottom: 4px; display: block; }
    .report-value { font-size: 14.5px; color: #ffffff; font-weight: 500; }
    .report-action-box { background-color: #2b2b2b; padding: 15px; border-radius: 4px; margin-top: 15px; }
    .report-action-title { font-weight: 700; font-size: 14px; margin-bottom: 8px; }
    .report-action-text { color: #e0e0e0; font-size: 14.5px; line-height: 1.6; }
    .warning-text { color: #ef5350; font-weight: 700; }
    .success-text { color: #66bb6a; font-weight: 700; }
    .reference-box { background-color: #3e2723; border-left: 4px solid #ff7043; padding: 10px 15px; margin-top: 10px; border-radius: 4px; font-size: 13.5px; color: #ffccbc; }
    
    /* 브랜드 전광판(KPI) 스타일 */
    .brand-kpi-box { background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border: 2px solid #deff9a; border-radius: 12px; padding: 30px 20px; text-align: center; margin-bottom: 25px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); position: relative; overflow: hidden; }
    .brand-kpi-box::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: #deff9a; }
    .brand-kpi-name { font-family: 'Gowun Dodum', sans-serif; font-size: 26px; font-weight: 700; color: #ffffff; margin-bottom: 15px; letter-spacing: -0.5px; }
    .brand-kpi-price { font-size: 42px; font-weight: 900; color: #deff9a; line-height: 1; margin-bottom: 5px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    .brand-kpi-desc { font-size: 14px; color: #aaaaaa; font-weight: 500; margin-bottom: 10px; }
    
    .trend-up { color: #ff5252; font-size: 15px; font-weight: 700; background: rgba(255,82,82,0.1); padding: 4px 12px; border-radius: 20px; display: inline-block; margin-top: 5px; }
    .trend-down { color: #448aff; font-size: 15px; font-weight: 700; background: rgba(68,138,255,0.1); padding: 4px 12px; border-radius: 20px; display: inline-block; margin-top: 5px; }
    .trend-flat { color: #aaaaaa; font-size: 14px; font-weight: 500; background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 20px; display: inline-block; margin-top: 5px; }
    .brand-empty-box { background-color: #111; border: 1px dashed #444; border-radius: 12px; padding: 40px 20px; text-align: center; color: #666; margin-bottom: 25px; }

    /* 개별 가맹점 카드 스타일 */
    .comp-card { background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; }
    .comp-card-title { font-weight: 700; font-size: 15px; color: #ffffff; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; display: flex; align-items: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .comp-kpi-label { font-size: 12px; color: #888888; display: block; margin-bottom: 2px; }
    .comp-keyword-value { font-size: 12.5px; color: #b3e5fc; margin-bottom: 0; display: block; word-break: keep-all; font-weight: 500; }
    
    .comp-menu-list { list-style-type: none; padding-left: 0; margin: 0; max-height: 250px; overflow-y: auto; flex-grow: 1; }
    .comp-menu-item { font-size: 12.5px; color: #bbbbbb; margin-bottom: 6px; padding-bottom: 6px; display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px dashed #2a2a2a; }
    .comp-menu-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .comp-menu-item.highlight { color: #deff9a; font-weight: 700; }
    
    /* 긴 메뉴명 자동 말줄임 처리 */
    .menu-name-text { flex-grow: 1; padding-right: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
    
    .comp-menu-list::-webkit-scrollbar { width: 4px; }
    .comp-menu-list::-webkit-scrollbar-track { background: transparent; }
    .comp-menu-list::-webkit-scrollbar-thumb { background: #555; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

if st.session_state.theme == "light":
    st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA !important; }
        h1, h2, h3, h4, h5, h6, p, label, span { color: #111111 !important; }
        div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important; padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F !important; }
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input { background-color: #FFFFFF !important; color: #111111 !important; -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important; border-radius: 4px !important; }
        div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0 !important; border-left: 3px solid #D32F2F !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #111111 !important; }
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }
        [data-testid="baseButton-primary"] { background-color: #111111 !important; border: 1px solid #000000 !important; }
        .top-theme-marker + div button { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
        
        .report-container { background-color: #ffffff; border: 1px solid #ddd; }
        .report-header { color: #1565c0; border-bottom: 1px solid #eee; }
        .report-label { color: #666; }
        .report-value { color: #111; }
        .report-action-box { background-color: #f1f8e9; }
        .report-action-text { color: #333; }
        .warning-text { color: #d32f2f; }
        .success-text { color: #2e7d32; }
        
        .brand-kpi-box { background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%); border: 2px solid #2e7d32; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .brand-kpi-box::before { background: #2e7d32; }
        .brand-kpi-name { color: #111; }
        .brand-kpi-price { color: #2e7d32; text-shadow: none; }
        .brand-kpi-desc { color: #666; }
        .brand-empty-box { background-color: #f9f9f9; border-color: #ccc; color: #999; }
        
        .trend-up { background: #ffebee; }
        .trend-down { background: #e3f2fd; }
        .trend-flat { background: #f5f5f5; color: #666; }
        
        .comp-card { background-color: #ffffff; border: 1px solid #e0e0e0; }
        .comp-card-title { color: #111; border-bottom-color: #eee; }
        .comp-keyword-value { color: #1565c0; }
        .comp-menu-item { color: #444; border-bottom-color: #eee; }
        .comp-menu-item.highlight { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 로그인 및 기초 데이터 로드
# ==========================================
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]: return True
    st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        @keyframes logoZoomIn { 0% { transform: scale(3.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
        .animated-logo { animation: logoZoomIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; max-width: 280px; margin: 0 auto 30px auto; display: block; }
        [data-testid="stForm"] { max-width: 280px !important; margin: 0 auto !important; background-color: transparent !important; border: none !important; }
        div[data-baseweb="input"] > div { background-color: #111111 !important; border: 1px solid #444444 !important; border-radius: 4px !important; height: 42px !important; }
        input[type="password"] { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-align: center !important; font-size: 13px !important; letter-spacing: 2px; background-color: transparent !important; }
        [data-testid="stFormSubmitButton"] > button { background-color: #444444 !important; border: 1px solid #666666 !important; border-radius: 4px !important; height: 42px !important; width: 100% !important; padding: 0 !important; }
        [data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 1px; margin: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top: 25vh; text-align: center;'>", unsafe_allow_html=True)
        st.markdown('<img src="https://dalbitgo.com/images/main_logo.png" class="animated-logo">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=True):
            c_in, c_btn = st.columns([2.5, 1])
            with c_in: pwd = st.text_input("auth", type="password", placeholder="인증코드", label_visibility="collapsed")
            with c_btn: submit = st.form_submit_button("LOGIN")
            if submit:
                if pwd == "51015":
                    st.session_state["password_correct"] = True
                    st.rerun()
                elif pwd: st.error("인증 코드가 일치하지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password(): st.stop()

# 파일 경로 강제 절대 경로 맵핑
STATE_RESOLVED  = os.path.join(BASE_DIR, "state_resolved.csv")
STATE_OVERRIDDEN = os.path.join(BASE_DIR, "state_overridden.csv")

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].astype(str).tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if str(new_id) not in ids:
        ids.append(str(new_id))
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    # 💡 [핵심 버그 해결] 띄어쓰기나 줄바꿈이 섞여 들어오면서 해시값(지문)이 달라지는 현상 원천 차단
    # 텍스트의 모든 공백을 없애고 딱 30글자만 압착해서 절대 변하지 않는 영구 지문을 생성합니다.
    safe_text = re.sub(r'\s+', '', str(row['리뷰내용']))[:30]
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{safe_text}".encode('utf-8')).hexdigest()

def load_data():
    filename = os.path.join(BASE_DIR, "가맹점_리뷰수집결과_누적.csv")
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

df = load_data()
full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else []

# ==========================================
# 4. 사이드바 및 메인 프레임
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px; text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;"
        onerror="this.onerror=null; this.style.display='none'; this.insertAdjacentHTML('afterend', '<span style=\\'color:#FFFFFF; font-size:15px; font-weight:700;\\'>달빛에 구운 고등어</span>');">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 통합 관제 시스템</p>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("<div style='height: 45vh;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='text-align: center; font-size: 11px; line-height: 1.6; color: #666666 !important; border-top: 1px solid #333333; padding-top: 15px;'>
    <b>(주)새모양에프앤비</b><br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_title, col_theme = st.columns([10, 1])
with col_title:
    st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 통합 관제 시스템 <span style='font-size: 18px; color: #888 !important; font-weight: 500;'>| Headquarters Dashboard</span></h1>", unsafe_allow_html=True)
with col_theme:
    st.markdown('<div class="top-theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "dark"
    if st.button(theme_icon, key="top_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석", "로컬 마케팅 통합 관제", "4대 핵심 경쟁사 병렬 모니터링"])

# ── 탭 1, 2 (기존 기능 100% 복구 유지) ─────────────────
with tab1:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>즉각 조치 요망 매장 리스트 (영구 보존)</h3>", unsafe_allow_html=True)
    if df.empty: st.info("아직 수집된 리뷰 데이터가 없습니다.")
    else:
        total_neg_df = df[df['감정분석'] == '부정']
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        active_neg = total_neg_df[~total_neg_df['id'].isin(resolved_ids)].sort_values(by='작성일', ascending=False)
        if total_neg_df.empty: st.success("누적된 수집 리뷰 중 부정 키워드가 감지된 내역이 없습니다.")
        elif not active_neg.empty:
            st.error(f"총 {len(active_neg)}건의 미조치 부정 리뷰가 남아있습니다.")
            for _, row in active_neg.iterrows():
                with st.expander(f"[{row['매장명']}] {row['작성일']} | {str(row['리뷰내용'])[:35]}..."):
                    st.write(f"**상세 내용:** {row['리뷰내용']}")
                    c1, c2, _ = st.columns([1.5, 1.5, 3])
                    if c1.button("해피콜 조치 완료", key=f"re_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_RESOLVED, row['id']); st.rerun()
                    if c2.button("긍정 분류 예외 처리", key=f"ov_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_OVERRIDDEN, row['id']); st.rerun()
        else: st.success(f"부정 리뷰 {len(total_neg_df)}건 조치 완료되었습니다.")
        
        st.divider()
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        st.markdown(f"<h3 style='margin-bottom: 15px;'>매장별 활성도 랭킹 (기준일: {yesterday_str})</h3>", unsafe_allow_html=True)
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
        with col_l: st.info("리뷰 활성화 우수 매장 (TOP 5)"); st.dataframe(all_counts.head(5), use_container_width=True)
        with col_r: st.warning("리뷰 관리 필요 매장 (BOTTOM 5)"); st.dataframe(all_counts.tail(5), use_container_width=True)

with tab2:
    st.markdown("<b style='font-size: 14px; display: block; margin-bottom: 8px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store_tab2", label_visibility="collapsed")
    f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores, key="sb_tab2", label_visibility="collapsed")
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
                
                st.markdown("<div style='margin-top: 35px; margin-bottom: 10px;'><b>일자별 리뷰 감정 추이</b></div>", unsafe_allow_html=True)
                trend_df = s_df.groupby(['작성일', '감정분석']).size().reset_index(name='건수').sort_values(by='작성일')
                chart_font_color = "#E0E0E0" if st.session_state.theme == "dark" else "#111111"
                chart_grid_color = "#333333" if st.session_state.theme == "dark" else "#EAEAEA"
                color_map = {'긍정': '#4CAF50', '부정': '#E53935', '중립': '#9E9E9E'}
                fig_bar = px.bar(trend_df, x='작성일', y='건수', color='감정분석', text='건수', color_discrete_map=color_map, barmode='stack')
                fig_bar.update_layout(margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=chart_font_color, family="Noto Sans KR"), xaxis=dict(title="", type='category', showgrid=False), yaxis=dict(title="건수", showgrid=True, gridcolor=chart_grid_color, dtick=1), legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)

with tab3:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>로컬 마케팅 통합 관제 (ROI & Ranking)</h3>", unsafe_allow_html=True)
    roi_file = os.path.join(BASE_DIR, "가맹점_키워드_ROI_분석결과.csv")
    track_file = os.path.join(BASE_DIR, "가맹점_순위추적_결과.csv")
    
    if os.path.exists(roi_file) and os.path.exists(track_file):
        roi_df = pd.read_csv(roi_file)
        track_df = pd.read_csv(track_file)
        
        def parse_rate(x):
            try: return float(str(x).replace('%', '').replace('분석 불가 (리뷰 없음)', '0'))
            except: return 0.0
            
        roi_df['적중률_num'] = roi_df['키워드_적중률'].apply(parse_rate)
        roi_df['미등록_플래그'] = roi_df['세팅된_키워드'].apply(lambda x: True if str(x) in ["키워드 미설정", "키워드 없음", "nan"] else False)
        
        if not track_df.empty:
            latest_date = track_df['수집일자'].max()
            latest_track_df = track_df[track_df['수집일자'] == latest_date].copy()
            latest_track_df = latest_track_df.drop_duplicates(subset=['매장명', '타겟키워드'], keep='last')
            
            if '1위_매장명' not in latest_track_df.columns:
                latest_track_df['1위_매장명'] = "-"
                latest_track_df['1위_사용_키워드'] = "-"
            if 'AI_인사이트' not in latest_track_df.columns:
                latest_track_df['AI_인사이트'] = "-"
            
            c1, c2, c3 = st.columns(3)
            c1.metric("분석 완료 가맹점", f"{len(roi_df)}개 지점")
            c2.metric("1페이지(Top 5) 방어 성공", f"{len(latest_track_df[latest_track_df['현재순위'] <= 5])}개 타겟")
            c3.metric("노출 실패 및 하락 경고", f"{len(latest_track_df[(latest_track_df['현재순위'] >= 999) | latest_track_df['등락폭'].str.contains('하락|이탈', na=False) | latest_track_df['등락폭'].str.startswith('-', na=False)])}건")
            
            st.divider()
            
            st.markdown("<h3 style='margin-bottom: 20px;'>본사 지침 수립용 가맹점 정밀 진단</h3>", unsafe_allow_html=True)
            all_stores = sorted(roi_df['매장명'].unique().tolist())
            
            if "prev_roi_selection" not in st.session_state:
                st.session_state.prev_roi_selection = []
            current_selection = []
            if "integrated_table" in st.session_state:
                current_selection = st.session_state.integrated_table.get("selection", {}).get("rows", [])
            if current_selection != st.session_state.prev_roi_selection:
                st.session_state.prev_roi_selection = current_selection

            sorted_raw_df = roi_df.sort_values(by=['미등록_플래그', '적중률_num'], ascending=[False, True]).reset_index(drop=True)
            
            selected_store_from_table = None
            if current_selection:
                selected_store_from_table = sorted_raw_df.iloc[current_selection[0]]['매장명']

            search_query = st.text_input("분석할 매장명을 검색하세요 (예: 첨단, 어양)", key="s_store_tab3")
            filtered_stores = [s for s in all_stores if search_query.replace(" ", "") in s.replace(" ", "")] if search_query else all_stores
            
            if filtered_stores:
                default_idx = 0
                if selected_store_from_table and selected_store_from_table in filtered_stores:
                    default_idx = filtered_stores.index(selected_store_from_table)
                    
                selected_store = st.selectbox("진단할 가맹점 선택", filtered_stores, index=default_idx, label_visibility="collapsed")
                
                store_roi_data = roi_df[roi_df['매장명'] == selected_store].iloc[0]
                s_rate = store_roi_data['키워드_적중률']
                s_vol = store_roi_data['네이버_월간_총검색량']
                s_kw = str(store_roi_data['세팅된_키워드'])
                is_empty = store_roi_data['미등록_플래그']
                
                r1, r2, r3 = st.columns(3)
                r1.metric("현재 설정된 매장 키워드", "미설정 (시스템 임의 부여 진행)" if is_empty else f"{len(s_kw.split(','))}개 세팅됨")
                r2.metric("고객 리뷰 적중률 (ROI)", f"{s_rate}")
                r3.metric("키워드 총 월간 검색량", f"{s_vol}")
                
                st.markdown(f"<br><b style='font-size: 16px;'>[{selected_store}] 상세 진단 리포트</b>", unsafe_allow_html=True)
                store_targets = latest_track_df[latest_track_df['매장명'] == selected_store]
                
                if store_targets.empty:
                    st.info("해당 매장의 순위 추적 데이터가 존재하지 않습니다.")
                else:
                    for _, row in store_targets.iterrows():
                        kw = str(row['타겟키워드']).replace('\n', ' ').replace('\r', '')
                        rank = row['현재순위']
                        trend = str(row['등락폭']).replace('\n', ' ').replace('\r', '')
                        first_name = str(row['1위_매장명']).replace('\n', ' ').replace('\r', '')
                        first_kws = str(row['1위_사용_키워드']).replace('\n', ' ').replace('\r', '')
                        ai_insight = str(row['AI_인사이트']).replace('\n', ' ').replace('\r', '')
                        
                        rank_str = "노출 실패 (허수 키워드)" if rank >= 999 else f"{int(rank)}위"
                        trend_display = f"({trend})" if trend != "-" else ""
                        
                        with st.expander(f"검색 타겟: [{kw}] ➡️ 상태: {rank_str} {trend_display}", expanded=(rank > 1)):
                            expander_html1 = f"<div class='report-container'><div class='report-header'>[진단 개요]</div><div class='report-section'><span class='report-label'>현재 노출 상태:</span><span class='report-value {'warning-text' if rank >= 999 else 'success-text'}'>{rank_str} {trend_display}</span></div></div>"
                            st.markdown(expander_html1, unsafe_allow_html=True)
                            
                            if "달빛" in first_name or "우리 매장" in first_name:
                                expander_html2 = "<div class='report-action-box' style='border-left: 4px solid #4CAF50;'><div class='report-action-title' style='color: #81c784;'>[본사 조치 권고 사항]</div><div class='report-action-text'>해당 상권에서 당사 매장이 1위를 유지 중입니다. 현행 키워드 설정을 변경하지 않도록 지도하십시오.</div></div>"
                                st.markdown(expander_html2, unsafe_allow_html=True)
                            else:
                                if first_name != "-" and first_name != "nan":
                                    expander_html3 = f"<div class='report-container' style='border-color: #4CAF50; background-color: #1b281c;'><div class='report-header' style='color: #daffde; border-bottom: 1px solid #334e35;'>[주변 경쟁업체 파악 데이터]</div><div class='report-section'><span class='report-label' style='color: #81c784;'>현재 1위 매장:</span><span class='report-value'>{first_name}</span></div><div class='report-section'><span class='report-label' style='color: #81c784;'>경쟁업체 핵심 키워드 조합:</span><span class='report-value'>{first_kws}</span></div></div>"
                                    st.markdown(expander_html3, unsafe_allow_html=True)
                                
                                action_title_color = "#ef5350" if rank >= 999 else "#81c784"
                                action_border_color = "#ef5350" if rank >= 999 else "#4CAF50"
                                
                                expander_html4 = f"<div class='report-action-box' style='border-left: 4px solid {action_border_color};'><div class='report-action-title' style='color: {action_title_color};'>[본사 조치 권고 사항]</div><div class='report-action-text'>{ai_insight}</div></div>"
                                st.markdown(expander_html4, unsafe_allow_html=True)
                
            st.divider()
            st.markdown("<b style='font-size: 16px;'>전체 가맹점 로컬 마케팅 성적표 원본</b>", unsafe_allow_html=True)
            st.dataframe(sorted_raw_df.drop(columns=['적중률_num', '미등록_플래그']), use_container_width=True, hide_index=True, key="integrated_table", on_select="rerun", selection_mode="single-row")
        else:
            st.info("순위 추적 데이터가 없습니다. 먼저 백엔드에서 봇을 실행하십시오.")
    else:
        st.info("데이터 파일이 부족합니다. 백엔드에서 ROI 분석기 및 순위 추적 봇을 실행해 주십시오.")

with tab4:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>경쟁 브랜드 전력 비교 모니터링 (4대 핵심 타겟)</h3>", unsafe_allow_html=True)
    
    comp_file = os.path.join(BASE_DIR, "경쟁업체_메뉴키워드_수집결과.csv")
    
    if os.path.exists(comp_file):
        comp_df = pd.read_csv(comp_file)
        
        if not comp_df.empty:
            dates = sorted(comp_df['수집일자'].unique().tolist())
            latest_date = dates[-1]
            prev_date = dates[-2] if len(dates) > 1 else None
            
            df_latest = comp_df[comp_df['수집일자'] == latest_date].copy()
            df_prev = comp_df[comp_df['수집일자'] == prev_date].copy() if prev_date else pd.DataFrame()
            
            df_latest['매칭용_브랜드명'] = df_latest['경쟁브랜드명_엑셀'].astype(str).str.replace(" ", "")
            if not df_prev.empty:
                df_prev['매칭용_브랜드명'] = df_prev['경쟁브랜드명_엑셀'].astype(str).str.replace(" ", "")
            
            st.markdown(f"<div style='color: #888; margin-bottom: 20px; font-size: 14px;'>데이터 기준일: {latest_date} | 시스템이 전국 프랜차이즈의 공통 가격 동향을 감지합니다.</div>", unsafe_allow_html=True)
            
            def parse_menus(menu_str):
                if pd.isna(menu_str) or menu_str in ["수집 실패", "-"]: return []
                return [m.strip() for m in str(menu_str).split('|') if m.strip()]

            def clean_price_to_int(price_str):
                try: return int(re.sub(r'[^0-9]', '', str(price_str)))
                except: return 0

            def extract_rep_mackerel_price(menu_list):
                for item in menu_list:
                    if "고등어" in item:
                        try:
                            price_str = item.split(':')[-1].strip()
                            val = clean_price_to_int(price_str)
                            if 0 < val <= 20000:
                                return f"{val:,}원", val
                        except: pass
                return "확인 불가", 0

            def get_brand_min_max_price(group_df):
                prices = []
                for _, row in group_df.iterrows():
                    store_name = str(row['실제_플레이스_업체명'])
                    if "반상" in store_name: continue
                    
                    menu_list = parse_menus(row['메뉴_및_가격'])
                    _, val = extract_rep_mackerel_price(menu_list)
                    if val > 0: prices.append(val)
                    
                if prices:
                    return min(prices), max(prices)
                return 0, 0

            target_brands = ['산으로간고등어', '화덕으로간고등어', '부산에뜬고등어', '북극해고등어']
            cols = st.columns(4)
            
            for idx, brand_name in enumerate(target_brands):
                with cols[idx]:
                    brand_latest_df = df_latest[df_latest['경쟁브랜드명_엑셀'].astype(str).str.contains(brand_name, na=False)]
                    
                    if not brand_latest_df.empty:
                        min_latest, max_latest = get_brand_min_max_price(brand_latest_df)
                        rep_price_latest = "확인 불가"
                        
                        if min_latest > 0:
                            rep_price_latest = f"{min_latest:,}원" if min_latest == max_latest else f"{min_latest:,}원 ~ {max_latest:,}원"
                        
                        trend_html = "<div class='trend-flat'>비교 데이터 부족</div>"
                        if prev_date and not df_prev.empty:
                            brand_prev_df = df_prev[df_prev['경쟁브랜드명_엑셀'].astype(str).str.contains(brand_name, na=False)]
                            min_prev, max_prev = get_brand_min_max_price(brand_prev_df)
                            
                            if min_latest > 0 and min_prev > 0:
                                diff = min_latest - min_prev
                                if diff > 0:
                                    trend_html = f"<div class='trend-up'>▲ 최저가 기준 {diff:,}원 인상 감지</div>"
                                elif diff < 0:
                                    trend_html = f"<div class='trend-down'>▼ 최저가 기준 {abs(diff):,}원 인하 감지</div>"
                                else:
                                    trend_html = f"<div class='trend-flat'>변동 없음 (어제와 동일)</div>"

                        kpi_html = f"<div class='brand-kpi-box'><div class='brand-kpi-name'>{brand_name}</div><div class='brand-kpi-price' style='font-size: 34px;'>{rep_price_latest}</div><div class='brand-kpi-desc'>대표 고등어구이 가격</div>{trend_html}</div>"
                        st.markdown(kpi_html, unsafe_allow_html=True)
                        
                        for _, row in brand_latest_df.iterrows():
                            store_name = str(row['실제_플레이스_업체명'])
                            if store_name == "확인 불가": store_name = f"{brand_name} (매장명 확인 불가)"
                            
                            keyword_status = str(row['타겟_키워드'])
                            menu_list = parse_menus(row['메뉴_및_가격'])
                            card_rep_price, _ = extract_rep_mackerel_price(menu_list)
                            
                            bansang_badge = ""
                            if "반상" in store_name:
                                bansang_badge = "<span style='background:#D32F2F; color:#fff; font-size:11px; padding:2px 6px; border-radius:4px; margin-left:8px; vertical-align:middle;'>반상 별도단가</span>"
                            
                            menu_html = ""
                            for m in menu_list:
                                m_name = m.split(':')[0].strip() if ':' in m else m
                                if len(m_name) > 18: m_name = m_name[:16] + "..."
                                m_price = m.split(':')[-1].strip() if ':' in m else ""
                                
                                h_class = "highlight" if "고등어" in m else ""
                                menu_html += f"<li class='comp-menu-item {h_class}'><span class='menu-name-text' title='{m_name}'>{m_name}</span><span style='font-weight: 500; white-space: nowrap; margin-left: 10px;'>{m_price}</span></li>"
                            
                            if not menu_html:
                                menu_html = "<li class='comp-menu-item' style='color:#666;'>수집된 메뉴가 없습니다.</li>"
                                
                            card_html = f"<div class='comp-card'><div class='comp-card-title'>{store_name} {bansang_badge}</div><div style='margin-bottom: 15px;'><span class='comp-kpi-label'>대표 고등어구이</span><span class='comp-kpi-value' style='font-size:22px;'>{card_rep_price}</span></div><ul class='comp-menu-list'>{menu_html}</ul><div style='margin-top: 15px; border-top: 1px dashed #333; padding-top: 12px;'><span class='comp-kpi-label'>사용 중인 타겟 키워드</span><span class='comp-keyword-value'>{keyword_status}</span></div></div>"
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                    else:
                        empty_html = f"<div class='brand-kpi-box' style='border-color: #444;'><div class='brand-kpi-name' style='color:#888;'>{brand_name}</div><div class='brand-kpi-price' style='color:#555;'>-</div><div class='brand-kpi-desc'>데이터 수집 전</div></div><div class='brand-empty-box'>엑셀에 해당 브랜드와<br>매칭되는 데이터가 없습니다.</div>"
                        st.markdown(empty_html, unsafe_allow_html=True)
                        
        else:
            st.info("수집된 경쟁사 데이터 내용이 비어 있습니다.")
    else:
        st.info("아직 수집된 경쟁사 데이터가 없습니다. 백엔드에서 봇(competitor_brand_crawler.py)을 먼저 실행해 주십시오.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚀 백그라운드 자동 구동 로직
# ==========================================
if __name__ == '__main__':
    import sys
    import os
    if os.environ.get("STREAMLIT_DASHBOARD_RUNNING") != "True":
        os.environ["STREAMLIT_DASHBOARD_RUNNING"] = "True"
        os.system(f'python -m streamlit run "{__file__}"')
        sys.exit()
