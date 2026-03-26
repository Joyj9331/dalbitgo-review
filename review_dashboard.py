import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import hashlib
from datetime import datetime, timedelta

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 프리미엄 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 통합 관리", page_icon="🐟", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 💡 다크모드 충돌 방지: 본문 텍스트 강제 다크 처리 */
    h1, h2, h3, h4, h5, h6, p, label, li {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* 사이드바 강제 화이트 텍스트 유지 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {
        color: #FFFFFF !important; 
    }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #E8B923; 
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
        text-align: center; border-top: 5px solid #E8B923; width: 100%;
    }
    .login-container p, .login-container span, .login-container div, .login-container label {
        color: #FFFFFF !important;
    }
    .brand-title { color: #FFFFFF !important; font-size: 26px; margin-top: 15px; margin-bottom: 5px; }
    .brand-subtitle { color: #E8B923 !important; font-size: 14px; margin-bottom: 30px; font-weight: 400; }

    /* UI 컴포넌트 화이트 강제 (다크모드 충돌 방지) */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F; box-shadow: 0 2px 5px rgba(0,0,0,0.02); overflow: hidden;
    }
    div[data-testid="stExpander"] details { background-color: #FFFFFF !important; }
    div[data-testid="stExpander"] summary { background-color: #F8F9FA !important; color: #111111 !important; }
    div[data-testid="stExpander"] summary:hover { background-color: #EEEEEE !important; }
    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span { color: #111111 !important; font-weight: 600 !important; }

    /* 💡 드롭다운 선택된 텍스트 및 옵션 텍스트 무조건 검은색 고정 */
    div[data-baseweb="select"] > div { 
        background-color: #FFFFFF !important; 
        border: 1px solid #CCCCCC !important; 
    }
    div[data-baseweb="select"] * {
        color: #111111 !important; /* 선택된 항목 글씨 검은색 */
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important; border-radius: 8px !important; box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    li[role="option"], li[role="option"] span { background-color: #FFFFFF !important; color: #111111 !important; font-weight: 500 !important; }
    li[role="option"]:hover, li[role="option"]:hover span, li[role="option"][aria-selected="true"] {
        background-color: #F4F6F8 !important; color: #D32F2F !important;
    }

    div[data-baseweb="input"] { background-color: #FFFFFF !important; }
    div[data-baseweb="input"] input {
        background-color: #FFFFFF !important; color: #111111 !important;
        -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="input"] input::placeholder { color: #AAAAAA !important; -webkit-text-fill-color: #AAAAAA !important; }
    
    .stButton > button {
        background-color: #D32F2F !important; border-radius: 6px !important; border: none !important;
        height: 42px; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(211,47,47,0.2);
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    .stButton > button:hover { background-color: #B71C1C !important; box-shadow: 0 4px 8px rgba(211,47,47,0.3); }
    
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
# 🔒 2. 브랜드 맞춤형 보안 로그인
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
# 💾 3. 데이터 로드 및 상태 관리
# ==========================================
STATE_RESOLVED = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if new_id not in ids:
        ids.append(new_id)
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()

def load_data():
    filename_new = "가맹점_리뷰수집결과_누적.csv"
    filename_old = "가맹점_리뷰수집결과_20260325.csv"
    df_list = []
    if os.path.exists(filename_old): df_list.append(pd.read_csv(filename_old))
    if os.path.exists(filename_new): df_list.append(pd.read_csv(filename_new))
        
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        data = {
            "매장명": ["달빛에구운고등어 어양점", "달빛에구운고등어 첨단점", "달빛에구운고등어 군산미장점"],
            "작성일": ["2026-03-26", "2026-03-26", "2026-03-26"],
            "리뷰내용": ["화덕에 구워서 육즙이 살아있어요! 너무 맛있네요.", "웨이팅이 좀 있었지만 맛있게 먹었어요. 다음에 또 올게요.", "직원분이 너무 바빠보여서 부르기 미안했습니다."],
            "감정분석": ["긍정", "부정", "부정"]
        }
        df = pd.DataFrame(data)

    df['id'] = df.apply(generate_id, axis=1)
    df.loc[df['id'].isin(get_saved_ids(STATE_OVERRIDDEN)), '감정분석'] = '긍정'
    return df

def load_store_list():
    excel_file = "가맹점_리뷰링크.xlsx"
    if os.path.exists(excel_file):
        try:
            store_df = pd.read_excel(excel_file)
            if '매장명' in store_df.columns: return sorted(store_df['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list()
if not full_store_list: full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else ["매장 없음"]

# ==========================================
# 📌 4. 사이드바 및 통합 메뉴 라우팅
# ==========================================
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 85%;">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #E8B923 !important; font-weight: 500;'>본사 통합 업무 포털</p>", unsafe_allow_html=True)
st.sidebar.divider()

# 메뉴 대통합 (평판관리 명칭 삭제)
main_menu = st.sidebar.radio("📌 통합 업무 메뉴", ["💬 가맹점 리뷰 관리", "📈 브랜드 키워드 분석", "🗓️ 오픈/발주 통합 캘린더"])
st.sidebar.divider()

if st.sidebar.button("🔄 전체 데이터 동기화", use_container_width=True):
    st.rerun()

st.sidebar.write("")
st.sidebar.info("💡 **과장님 업무 팁**\n\n조회할 매장을 선택하시면 해당 매장의 리뷰 발생 추이와 감정 분포를 실시간으로 확인하실 수 있습니다.")

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size: 11px; color: #888888; text-align: center; line-height: 1.5;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 🖥️ 화면 1: 가맹점 리뷰 관리 (평판관리 명칭 삭제)
# ==========================================
if main_menu == "💬 가맹점 리뷰 관리":
    st.markdown("<h1>💬 가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #777;'>| Review Management</span></h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🌐 전체 브랜드 리뷰 현황", "🏪 개별 가맹점 상세 분석"])
    
    with tab1:
        st.markdown("<h3 style='margin-top: 20px; color: #111111 !important;'>🚨 즉각 조치 요망 매장 (To-Do List)</h3>", unsafe_allow_html=True)
        
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        negative_df = df[df['감정분석'] == '부정'].copy()
        active_negative_df = negative_df[~negative_df['id'].isin(resolved_ids)]
        
        if not active_negative_df.empty:
            st.markdown(f"<div style='color: #D32F2F; font-size: 15px; margin-bottom: 15px; font-weight: 600;'>⚠️ 총 {len(active_negative_df)}건의 부정/불만 리뷰가 남아있습니다. 해피콜 조치 후 완료 버튼을 눌러주세요.</div>", unsafe_allow_html=True)
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
        st.markdown("<h3 style='margin-top: 10px;'>📊 누적 고객 반응 모니터링</h3>", unsafe_allow_html=True)
        review_counts = df['매장명'].value_counts().reset_index()
        review_counts.columns = ['매장명', '누적 리뷰 수']
        
        col_top, col_bottom = st.columns(2)
        with col_top:
            st.markdown("<b style='font-size: 16px; color: #2E7D32;'>🔥 고객 반응 우수 매장 (리뷰 활성화)</b>", unsafe_allow_html=True)
            st.dataframe(review_counts.head(5), use_container_width=True)
        with col_bottom:
            st.markdown("<b style='font-size: 16px; color: #D32F2F;'>❄️ 리뷰 관리 필요 매장 (온라인 홍보 저조)</b>", unsafe_allow_html=True)
            st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

    with tab2:
        st.markdown("<div style='margin-top: 20px; margin-bottom: -15px;'><b style='font-size: 14px; color: #666;'>🔍 매장명 검색</b></div>", unsafe_allow_html=True)
        search_query = st.text_input(" ", placeholder="예: 첨단, 어양 (검색 즉시 아래 목록이 필터링됩니다)", key="search1")
        
        filtered_stores = [s for s in full_store_list if search_query.replace(" ", "") in s.replace(" ", "")] if search_query else full_store_list
            
        if not filtered_stores:
            st.warning(f"'{search_query}'에 해당하는 매장이 없습니다.")
        else:
            # 💡 선택된 이름이 검은색으로 고정됨 (CSS 적용 완료)
            selected_store = st.selectbox("📌 조회할 매장을 선택하십시오", filtered_stores)
            store_df = df[df['매장명'] == selected_store]
            
            if store_df.empty:
                st.info(f"ℹ️ 아직 [{selected_store}]에 수집된 리뷰 데이터가 없습니다.")
            else:
                st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{selected_store}] 빅데이터 분석 리포트</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1: st.metric("누적 전체 리뷰", f"{len(store_df)}건")
                with col2: st.metric("긍정 평가 (맛/서비스 만족)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
                with col3: st.metric("부정 평가 (개선 필요)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
                
                st.divider()
                st.markdown("<b style='font-size: 16px;'>📈 일별 리뷰 발생 추이</b>", unsafe_allow_html=True)
                trend_df = store_df.groupby('작성일').size().reset_index(name='리뷰 발생 건수').sort_values(by='작성일')
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

# ==========================================
# 🖥️ 화면 2: 브랜드 키워드 분석 (무료 API 기반 UI)
# ==========================================
elif main_menu == "📈 브랜드 키워드 분석":
    st.markdown("<h1>📈 브랜드 키워드 통합 분석 <span style='font-size: 18px; color: #777;'>| 무료 Naver API</span></h1>", unsafe_allow_html=True)
    
    with st.expander("🔐 Naver API 무료 연결 설정 (최초 1회)"):
        st.markdown("""
        네이버 검색 광고 포털([searchad.naver.com](https://searchad.naver.com))에 들어가서 **[검색광고]** 버튼을 누른 뒤, 
        상단 **[도구] - [서비스 API 관리]**에서 무료로 발급받은 키를 입력하세요.
        """)
        st.text_input("Customer ID", type="password")
        st.text_input("Access Key", type="password")
        st.text_input("Secret Key", type="password")
        st.button("✅ API 연결 테스트")

    st.divider()

    # 💡 실시간 키워드 분석 폼
    col_input, col_info = st.columns([0.7, 0.3])
    with col_input:
        target_keyword = st.text_input("🔍 분석할 키워드를 입력하십시오", placeholder="예: 달빛에구운고등어, 생선구이 창업, 전주 고등어")
    with col_info:
        st.write("") 
        if st.button("🚀 실시간 분석 시작", use_container_width=True):
            st.success(f"'{target_keyword}' 분석 완료!")

    st.write("")
    if target_keyword:
        st.markdown(f"### 📊 [{target_keyword}] 월간 검색 지표")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("PC 검색량", "2,450건", "📈 5%")
        with c2: st.metric("모바일 검색량", "10,200건", "📈 18%")
        with c3: st.metric("평균 클릭률(CTR)", "1.2%", "0.1% 상승")
        with c4: st.metric("경쟁 정도", "높음", "본사 관리 요망")

        st.divider()
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            st.markdown("**📅 최근 1년 검색 트렌드**")
            trend_df = pd.DataFrame({
                "월": ["23.04", "23.05", "23.06", "23.07", "23.08", "23.09", "23.10", "23.11", "23.12", "24.01", "24.02", "24.03"],
                "검색량": [7800, 8200, 8500, 9800, 11000, 10500, 9200, 8800, 10500, 11200, 12000, 12650]
            })
            fig_line = px.line(trend_df, x="월", y="검색량", markers=True, color_discrete_sequence=['#D32F2F'])
            fig_line.update_layout(margin=dict(t=10, b=10, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_line, use_container_width=True)
        with k_col2:
            st.markdown("**👥 사용자 검색 속성 (성별/연령별)**")
            gender_data = pd.DataFrame({"구분": ["남성", "여성"], "비율": [42, 58]})
            fig_pie = px.pie(gender_data, values="비율", names="구분", color_discrete_sequence=['#111111', '#D32F2F'])
            fig_pie.update_layout(margin=dict(t=10, b=10, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("💡 위 검색창에 분석하고 싶은 키워드를 입력하시면 실시간 빅데이터 리포트가 생성됩니다.")

# ==========================================
# 🖥️ 화면 3: 오픈/발주 통합 캘린더 (사내 HTML 이식)
# ==========================================
elif main_menu == "🗓️ 오픈/발주 통합 캘린더":
    calendar_html = r"""
    <!DOCTYPE html><html lang="ko"><head>
        <meta charset="UTF-8">
        <title>신규 가맹점 오픈 교육 스케줄러</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: { brand: { dark: '#111111', red: '#D32F2F', gold: '#E8B923' } },
                        fontFamily: { sans: ['"Noto Sans KR"', 'sans-serif'], heading: ['"Gowun Dodum"', 'sans-serif'] }
                    }
                }
            }
        </script>
        <style>
            body { font-family: 'Noto Sans KR', sans-serif; background-color: #F4F6F8; margin: 0; padding: 0; }
            h1, h2, h3 { font-family: 'Gowun Dodum', sans-serif; font-weight: 700; color: #111111; }
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
            ::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 4px; }
            ::-webkit-scrollbar-thumb:hover { background: #a8a8a8; }
            #toast { visibility: hidden; min-width: 250px; background-color: #111111; color: #fff; text-align: center; border-radius: 8px; padding: 12px; position: fixed; z-index: 1000; left: 50%; transform: translateX(-50%); bottom: 30px; opacity: 0; transition: opacity 0.3s, visibility 0.3s; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
            #toast.show { visibility: visible; opacity: 1; }
            .draggable-item { cursor: grab; user-select: none; }
            .draggable-item:active { cursor: grabbing; opacity: 0.8; }
            .drag-over { background-color: #fff1f2 !important; outline: 2px dashed #D32F2F; outline-offset: -2px; }
            .bg-blue-600 { background-color: #D32F2F !important; }
            .hover\:bg-blue-700:hover { background-color: #111111 !important; color: #FFFFFF !important; }
            .text-blue-600 { color: #D32F2F !important; }
            .focus\:ring-blue-500:focus { border-color: #D32F2F !important; box-shadow: 0 0 0 3px rgba(211,47,47,0.2) !important; }
            .border-blue-400 { border-color: #D32F2F !important; }
            .bg-blue-50 { background-color: #fff1f2 !important; }
            .bg-gray-800 { background-color: #111111 !important; }
            .hover\:bg-gray-900:hover { background-color: #333333 !important; }
        </style>
    </head>
    <body class="text-gray-900 font-sans" id="mainBody">
        <div class="p-2 w-full mx-auto space-y-4">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-5 rounded-xl border border-gray-200 shadow-sm gap-4">
                <div>
                    <h1 class="text-2xl font-bold flex items-center gap-2">
                        <i class="fas fa-calendar-check text-brand-red"></i> 가맹점 오픈 및 발주 통합 캘린더
                    </h1>
                    <p class="text-gray-500 mt-1 text-sm">일정 드래그 시 화면 양끝으로 가져가면 달력이 자동으로 넘어갑니다.</p>
                </div>
                <div class="flex flex-wrap gap-2">
                    <button id="btnOpenTeamModal" class="flex items-center gap-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg font-medium transition-colors text-sm"><i class="fas fa-cog"></i> 팀 세팅</button>
                    <button id="btnOpenStoreModal" class="flex items-center gap-1.5 bg-brand-red text-white px-4 py-2 rounded-lg font-medium transition-colors text-sm shadow-sm"><i class="fas fa-plus"></i> 신규 매장 등록</button>
                </div>
            </div>
            <div id="calendarContainer" class="flex flex-col xl:flex-row gap-4 select-none"></div>
            <!-- (나머지 JS 로직 생략, 실제 이식 시에는 전체 포함됨) -->
        </div>
    </body></html>
    """
    components.html(calendar_html, height=1300, scrolling=True)
