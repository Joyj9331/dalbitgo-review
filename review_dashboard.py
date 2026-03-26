import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import hashlib
from datetime import datetime, timedelta

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 프리미엄 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", page_icon="🐟", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
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

    div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #111111 !important; }
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
                    <div class="brand-title">본사 통합 관리 시스템</div>
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

# 💡 메뉴 대통합 (리뷰, 키워드, 일정)
main_menu = st.sidebar.radio("📌 통합 업무 메뉴", ["💬 가맹점 리뷰 관리", "📈 브랜드 키워드 분석", "🗓️ 오픈/발주 통합 캘린더"])
st.sidebar.divider()

if st.sidebar.button("🔄 전체 데이터 동기화", use_container_width=True):
    st.rerun()

st.sidebar.write("")
st.sidebar.info("💡 **과장님 업무 팁**\n\n'통합 캘린더'에 도면 수정 및 발주 일정을 업데이트하시면 전 직원이 실시간으로 공유받을 수 있습니다.")

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
# 🖥️ 화면 1: 가맹점 리뷰 관리 (기존 기능 탭으로 통합)
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
# 🖥️ 화면 2: 브랜드 키워드 분석 (새로운 제안)
# ==========================================
elif main_menu == "📈 브랜드 키워드 분석":
    st.markdown("<h1>📈 브랜드 키워드 & 검색량 분석 <span style='font-size: 18px; color: #777;'>| Keyword Trend</span></h1>", unsafe_allow_html=True)
    st.info("💡 **안내:** 현재 화면은 향후 네이버 검색광고 API 연동을 위한 UI 뼈대 및 샘플 데이터입니다. 개발사 전달용 기획안으로 활용하십시오.")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("이번 달 '달빛에구운고등어' 검색량", "12,450건", "📈 15% 증가")
    with col2: st.metric("연관 검색어 1위", "생선구이 창업", "유지")
    with col3: st.metric("가장 많이 검색된 지역", "전주/광주 지역", "신규 오픈 영향")
    
    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("<b style='font-size: 16px;'>📊 최근 6개월 메인 키워드 검색량 트렌드</b>", unsafe_allow_html=True)
        # 샘플 데이터 생성
        trend_data = pd.DataFrame({
            "월": ["10월", "11월", "12월", "1월", "2월", "3월"],
            "달빛에구운고등어": [8500, 9200, 10500, 11000, 11800, 12450],
            "경쟁사A": [9000, 9100, 8900, 9500, 9200, 9000]
        })
        fig = px.line(trend_data, x="월", y=["달빛에구운고등어", "경쟁사A"], markers=True, color_discrete_sequence=['#D32F2F', '#AAAAAA'])
        fig.update_layout(margin=dict(t=20, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)
        
    with col_chart2:
        st.markdown("<b style='font-size: 16px;'>🔥 급상승 연관 검색어 (Top 5)</b>", unsafe_allow_html=True)
        keyword_data = pd.DataFrame({
            "키워드": ["생선구이 창업", "화덕 생선구이", "달빛고등어 메뉴", "전주 맛집", "달빛에구운고등어 가격"],
            "검색비율": [35, 25, 20, 15, 5]
        })
        fig2 = px.bar(keyword_data, x="검색비율", y="키워드", orientation='h', color_discrete_sequence=['#111111'])
        fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 🖥️ 화면 3: 오픈/발주 통합 캘린더 (과장님 맞춤형 제안)
# ==========================================
elif main_menu == "🗓️ 오픈/발주 통합 캘린더":
    st.markdown("<h1>🗓️ 가맹점 오픈 및 발주 통합 보드 <span style='font-size: 18px; color: #777;'>| Schedule & Order</span></h1>", unsafe_allow_html=True)
    st.write("본사 직원 누구나 실시간으로 가맹점 오픈 일정과 발주 상태를 확인하고 공유할 수 있는 공간입니다.")
    
    st.divider()
    
    # 간이 칸반보드(Kanban) 스타일의 일정 관리 샘플
    col_plan, col_order, col_open = st.columns(3)
    
    with col_plan:
        st.markdown("<div style='background-color:#111111; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold;'>📝 도면 확인 및 컨펌</div>", unsafe_allow_html=True)
        st.info("**[경기 평택점]**\n- 주방 동선 도면 1차 수정 중\n- 담당: 과장님\n- 기한: 금주 금요일")
        st.info("**[부산 해운대점]**\n- 홀 테이블 배치도 완료\n- 점주 최종 컨펌 대기")
        
    with col_order:
        st.markdown("<div style='background-color:#E8B923; color:#111111; padding:10px; border-radius:5px; text-align:center; font-weight:bold;'>🍽️ 그릇류 및 식자재 발주</div>", unsafe_allow_html=True)
        st.warning("**[광주 수완점]**\n- 12첩 반찬 그릇 세트 발주 완료\n- 입고 예정: 다음 주 화요일")
        st.error("🚨 **[서울 강남점]**\n- 화덕 예열판 추가 발주 필요\n- 확인 요망 (긴급)")
        
    with col_open:
        st.markdown("<div style='background-color:#D32F2F; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold;'>🎉 오픈 교육 및 D-Day</div>", unsafe_allow_html=True)
        st.success("**[대전 유성점] D-3**\n- 홀 서비스 및 조리 교육 중\n- 특이사항 없음")
        st.info("**[전북 정읍점] D-14**\n- 현장 직원 채용 마무리 단계\n- 다음 주 교육팀 파견 예정")
