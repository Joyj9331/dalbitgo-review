import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import hashlib
import re
import hmac
import base64
import time
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv # 💡 금고 여는 부품 추가

# ==========================================
# 1. 페이지 기본 설정 및 상태 초기화
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# 💡 환경 변수 로드
load_dotenv()

# ==========================================
# 2. 공통 CSS
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
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important; 
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #111111 !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    li[role="option"] { color: #FFFFFF !important; }
    li[role="option"]:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    li[role="option"][aria-selected="true"] { background-color: #D32F2F !important; color: #FFFFFF !important; }
    div[data-testid="InputInstructions"] { display: none !important; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
    div[data-testid="column"] { padding: 0 4px !important; }
    [data-testid="baseButton-primary"] {
        border-radius: 4px !important;
        height: 42px !important;
        transition: all 0.2s ease;
    }
    [data-testid="baseButton-primary"] p, [data-testid="baseButton-primary"] span {
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    .theme-marker + div button {
        border-radius: 50% !important;
        width: 40px !important; height: 40px !important;
        padding: 0 !important; margin: 0 auto !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        transition: all 0.3s ease;
    }
    .theme-marker + div button p, .theme-marker + div button span { font-size: 16px !important; line-height: 1 !important; }
    .top-theme-marker + div button {
        border-radius: 50% !important;
        width: 40px !important; height: 40px !important;
        padding: 0 !important; float: right !important; margin-top: 10px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        transition: all 0.3s ease;
    }
    .top-theme-marker + div button p, .top-theme-marker + div button span { font-size: 16px !important; line-height: 1 !important; }

    /* 키워드 카드 */
    .kw-card {
        border-radius: 4px; padding: 14px 18px; margin-bottom: 8px;
        border-left: 3px solid #D32F2F;
    }
    .kw-card .kw-name { font-size: 15px; font-weight: 700; }
    .kw-card .kw-meta { font-size: 12px; margin-top: 4px; opacity: 0.75; }
    .kw-badge-hot { background: #E65100; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 20px; margin-left: 7px; color: #FFFFFF !important; }
    .kw-badge-good { background: #2E7D32; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 20px; margin-left: 7px; color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 다크/라이트 테마 CSS 동적 주입
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
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #222222 !important; color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important; border: 1px solid #444444 !important; border-radius: 4px !important;
        }
        .main-content div[data-baseweb="input"] > div:focus-within, .main-content .stTextInput input:focus { border-color: #888888 !important; }
        div[data-testid="stExpander"] {
            background-color: #222222 !important; border-radius: 4px; border: 1px solid #333333 !important; border-left: 3px solid #D32F2F !important;
        }
        div[data-testid="stExpander"] summary { background-color: transparent !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #F0F0F0 !important; }
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #333333 !important; background-color: #222222 !important; }
        [data-testid="baseButton-primary"] { background-color: #333333 !important; border: 1px solid #555555 !important; }
        [data-testid="baseButton-primary"]:hover { background-color: #555555 !important; border-color: #888888 !important; }
        .theme-marker + div button, .top-theme-marker + div button { background-color: #222222 !important; border: 1px solid #444444 !important; }
        .theme-marker + div button:hover, .top-theme-marker + div button:hover { background-color: #444444 !important; }
        .theme-marker + div button p, .top-theme-marker + div button p { color: #888888 !important; }
        .kw-card { background-color: #222222; border: 1px solid #333333; }
        .kw-card .kw-name { color: #F0F0F0 !important; }
        .kw-card .kw-meta { color: #AAAAAA !important; }
        .strategy-box { background: #0A0A0A; border: 1px solid #333333; border-top: 3px solid #D32F2F; border-radius: 4px; padding: 22px 26px; margin-top: 14px; }
        .strategy-box h4 { color: #E8B923 !important; font-size: 14px; margin-bottom: 10px; }
        .strategy-box p { color: #CCCCCC !important; font-size: 13px; line-height: 1.8; }
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
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #FFFFFF !important; color: #111111 !important;
            -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important; border-radius: 4px !important;
        }
        .main-content div[data-baseweb="input"] > div:focus-within, .main-content .stTextInput input:focus { border-color: #111111 !important; }
        div[data-testid="stExpander"] {
            background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0 !important; border-left: 3px solid #D32F2F !important;
        }
        div[data-testid="stExpander"] summary { background-color: transparent !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #111111 !important; }
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }
        [data-testid="baseButton-primary"] { background-color: #111111 !important; border: 1px solid #000000 !important; }
        [data-testid="baseButton-primary"]:hover { background-color: #333333 !important; }
        .theme-marker + div button, .top-theme-marker + div button { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
        .theme-marker + div button:hover, .top-theme-marker + div button:hover { background-color: #E0E0E0 !important; }
        .theme-marker + div button p, .top-theme-marker + div button p { color: #888888 !important; }
        .kw-card { background-color: #FFFFFF; border: 1px solid #E0E0E0; }
        .kw-card .kw-name { color: #111111 !important; }
        .kw-card .kw-meta { color: #666666 !important; }
        .strategy-box { background: #111111; border-top: 3px solid #D32F2F; border-radius: 4px; padding: 22px 26px; margin-top: 14px; }
        .strategy-box h4 { color: #E8B923 !important; font-size: 14px; margin-bottom: 10px; }
        .strategy-box p { color: #CCCCCC !important; font-size: 13px; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. 보안 로그인 시스템
# ==========================================
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

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
            max-width: 280px; margin: 0 auto 30px auto; display: block;
        }
        [data-testid="stForm"] { max-width: 280px !important; margin: 0 auto !important; background-color: transparent !important; border: none !important; }
        [data-testid="column"] { padding: 0 4px !important; display: flex; flex-direction: column; justify-content: center; }
        div[data-baseweb="input"] > div { background-color: #111111 !important; border: 1px solid #444444 !important; border-radius: 4px !important; height: 42px !important; }
        input[type="password"] { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-align: center !important; font-size: 13px !important; letter-spacing: 2px; background-color: transparent !important; }
        div[data-baseweb="input"] > div:focus-within { border-color: #888888 !important; }
        div[data-testid="stTextInput"] svg { fill: #FFFFFF !important; color: #FFFFFF !important; }
        [data-testid="stFormSubmitButton"] { margin: 0 !important; padding: 0 !important; }
        [data-testid="stFormSubmitButton"] > button { background-color: #444444 !important; border: 1px solid #666666 !important; border-radius: 4px !important; height: 42px !important; width: 100% !important; padding: 0 !important; transition: all 0.2s ease; }
        [data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 1px; margin: 0 !important; }
        [data-testid="stFormSubmitButton"] > button:hover { background-color: #555555 !important; border-color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top: 25vh; text-align: center;'>", unsafe_allow_html=True)
        st.markdown('<img src="https://dalbitgo.com/images/main_logo.png" class="animated-logo">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=True):
            c_in, c_btn = st.columns([2.5, 1])
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
STATE_RESOLVED  = "state_resolved.csv"
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
# 6. 네이버 검색광고 API (보안 수술 완료)
# ==========================================
# 💡 하드코딩된 위험한 텍스트 키워드를 제거하고 .env 금고에서 꺼내오도록 변경
NAVER_AD = {
    "CUSTOMER_ID": os.getenv("NAVER_CUSTOMER_ID"),
    "ACCESS_LICENSE": os.getenv("NAVER_ACCESS_LICENSE"),
    "SECRET_KEY": os.getenv("NAVER_SECRET_KEY"),
}

def _sign(timestamp, method, path):
    if not NAVER_AD["SECRET_KEY"]:
        return ""
    msg = f"{timestamp}.{method}.{path}"
    h = hmac.new(NAVER_AD["SECRET_KEY"].encode(), msg.encode(), digestmod="sha256").digest()
    return base64.b64encode(h).decode()

def get_keyword_stats(keywords: list):
    if not NAVER_AD["ACCESS_LICENSE"]:
        st.error("🚨 서버 .env 파일에 네이버 API 키가 설정되지 않았습니다.")
        return []
        
    path = "/keywordstool"
    all_results = []
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        ts = str(int(time.time() * 1000))
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Timestamp": ts,
            "X-API-KEY": NAVER_AD["ACCESS_LICENSE"],
            "X-Customer": NAVER_AD["CUSTOMER_ID"],
            "X-Signature": _sign(ts, "GET", path),
        }
        query = "&".join([f"hintKeywords={urllib.parse.quote(kw)}" for kw in batch]) + "&showDetail=1"
        url = "https://api.naver.com" + path + "?" + query
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if "keywordList" in data:
                    all_results.extend(data["keywordList"])
        except Exception as e:
            st.warning(f"API 오류: {e}")
        time.sleep(0.3)
    return all_results

def extract_keywords_from_reviews(store_df):
    stop = {'이', '가', '을', '를', '은', '는', '에', '의', '도', '로', '와', '과', '하', '고',
            '서', '에서', '있어요', '있어', '없어요', '없어', '이에요', '이예요', '습니다', '했어요',
            '했습니다', '같아요', '같습니다', '너무', '정말', '진짜', '아주', '매우', '더', '가장',
            '좀', '또', '잘', '안', '못', '제', '저', '우리', '그', '이', '저', '그냥', '좋아요', '좋았어요'}
    word_count = {}
    for review in store_df['리뷰내용'].dropna():
        words = re.findall(r'[가-힣]{2,6}', str(review))
        for w in words:
            if w not in stop:
                word_count[w] = word_count.get(w, 0) + 1
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [w for w, c in sorted_words[:20] if c >= 2]

def classify_keyword(total):
    if total >= 30000: return "🔴 고경쟁", "롱테일 조합 키워드 권장"
    elif total >= 5000: return "🟡 중경쟁", "블로그+플레이스 동시 공략"
    else: return "🟢 저경쟁", "상위노출 최적 키워드 ✨"

# ==========================================
# 7. 사이드바
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px; text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;"
        onerror="this.onerror=null; this.style.display='none'; this.insertAdjacentHTML('afterend', '<span style=\\'color:#FFFFFF; font-size:15px; font-weight:700;\\'>🐟 달빛에 구운 고등어</span>');">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 리뷰 통합 관리</p>", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
c1, c2, c3 = st.sidebar.columns([1, 1, 1])
with c2:
    st.markdown('<div class="theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "●"
    if st.button(theme_icon, key="sidebar_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

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
# 8. 메인 화면
# ==========================================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_title, col_theme = st.columns([10, 1])
with col_title:
    st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #888 !important; font-weight: 500;'>| Review Management</span></h1>", unsafe_allow_html=True)
with col_theme:
    st.markdown('<div class="top-theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "●"
    if st.button(theme_icon, key="top_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# ── 탭 3개로 확장 ──────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석", "🔍 키워드 전략 센터"])

# ── 탭1: 전체 브랜드 현황 (기존 동일) ─────────────────
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
                    if c1.button("해피콜 조치 완료", key=f"re_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_RESOLVED, row['id']); st.rerun()
                    if c2.button("긍정 분류로 예외 처리", key=f"ov_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_OVERRIDDEN, row['id']); st.rerun()
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
        with col_l: st.info("리뷰 활성화 우수 매장 (TOP 5)"); st.dataframe(all_counts.head(5), use_container_width=True)
        with col_r: st.warning("리뷰 관리 필요 매장 (BOTTOM 5)"); st.dataframe(all_counts.tail(5), use_container_width=True)

# ── 탭2: 개별 매장 상세분석 (기존 동일) ───────────────
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
                color_map = {'긍정': '#4CAF50', '부정': '#E53935', '중립': '#9E9E9E'}
                fig_bar = px.bar(trend_df, x='작성일', y='건수', color='감정분석',
                                 text='건수', color_discrete_map=color_map, barmode='stack')
                fig_bar.update_traces(
                    textposition='inside',
                    textfont=dict(color='#FFFFFF', size=12, family="Noto Sans KR"),
                    hoverlabel=dict(font_size=13, font_family="Noto Sans KR")
                )
                fig_bar.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=chart_font_color, family="Noto Sans KR"),
                    xaxis=dict(title="리뷰 작성 일자", type='category', showgrid=False,
                               tickfont=dict(color="#888888"), tickangle=-40, automargin=True),
                    yaxis=dict(title="작성 건수(건)", showgrid=True, gridcolor=chart_grid_color,
                               tickfont=dict(color="#888888"), dtick=1),
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

# ── 탭3: 키워드 전략 센터 (신규) ──────────────────────
with tab3:
    st.markdown("<h3 style='margin-top: 20px; margin-bottom: 4px;'>🔍 키워드 전략 센터</h3>", unsafe_allow_html=True)
    st.caption("네이버 검색광고 API 연동 · 리뷰 데이터 기반 키워드 자동 추출 · 상위노출 전략 생성")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 2.2])

    with col_a:
        st.markdown("**① 분석할 매장 선택**")
        q2 = st.text_input("매장 검색", placeholder="매장명 입력", key="kw_search", label_visibility="collapsed")
        f2 = [s for s in full_store_list if q2.replace(" ","") in s.replace(" ","")] if q2 else full_store_list
        kw_store = st.selectbox("매장 선택", f2, key="kw_store", label_visibility="collapsed")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("**② 추가 키워드 입력** (선택)")
        st.caption("지역명·메뉴명 등 쉼표로 구분")
        manual_kw = st.text_input("예: 전주 생선구이, 화덕고등어", key="manual_kw", label_visibility="collapsed")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        run_btn = st.button("🚀 키워드 분석 시작", use_container_width=True, key="run_kw")

    with col_b:
        if run_btn:
            store_df = df[df['매장명'] == kw_store] if not df.empty else pd.DataFrame()
            review_keywords = extract_keywords_from_reviews(store_df) if not store_df.empty else []
            extra_kws = [k.strip() for k in manual_kw.split(",") if k.strip()] if manual_kw else []
            all_kws = list(dict.fromkeys(extra_kws + review_keywords))[:20]

            if not all_kws:
                st.warning("리뷰 데이터가 없고 추가 키워드도 입력되지 않았습니다. ②에서 직접 입력해 주세요.")
            else:
                with st.spinner(f"{len(all_kws)}개 키워드 검색량 조회 중..."):
                    raw = get_keyword_stats(all_kws)

                if not raw:
                    st.error("API 응답이 없습니다. 키를 확인하거나 잠시 후 다시 시도해 주세요.")
                else:
                    rows = []
                    for item in raw:
                        kw  = item.get("relKeyword", "")
                        pc  = item.get("monthlyPcQcCnt", 0)
                        mo  = item.get("monthlyMobileQcCnt", 0)
                        try: pc = int(str(pc).replace("< 10","5").replace(",",""))
                        except: pc = 0
                        try: mo = int(str(mo).replace("< 10","5").replace(",",""))
                        except: mo = 0
                        label, desc = classify_keyword(pc + mo)
                        rows.append({"키워드": kw, "PC": pc, "모바일": mo, "합계": pc+mo, "경쟁도": label, "전략": desc})

                    result_df = pd.DataFrame(rows).sort_values("합계", ascending=False).reset_index(drop=True)

                    # 요약 메트릭
                    st.markdown(f"<b>[{kw_store}] 키워드 분석 결과</b>", unsafe_allow_html=True)
                    r1, r2, r3 = st.columns(3)
                    r1.metric("분석 키워드", f"{len(result_df)}개")
                    r2.metric("최고 월간 검색량", f"{result_df['합계'].max():,}회")
                    r3.metric("저경쟁 추천", f"{len(result_df[result_df['경쟁도'].str.contains('저경쟁')])}개")

                    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                    # 바 차트 — 테마 반영
                    chart_font = "#E0E0E0" if st.session_state.theme == "dark" else "#111111"
                    chart_grid = "#333333" if st.session_state.theme == "dark" else "#EAEAEA"
                    top15 = result_df.head(15)
                    fig_kw = go.Figure()
                    fig_kw.add_trace(go.Bar(name="모바일", x=top15['키워드'], y=top15['모바일'],
                                            marker_color='#D32F2F', opacity=0.85))
                    fig_kw.add_trace(go.Bar(name="PC", x=top15['키워드'], y=top15['PC'],
                                            marker_color='#EF9A9A', opacity=0.85))
                    fig_kw.update_layout(
                        barmode='stack', margin=dict(t=20, b=100, l=0, r=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=chart_font, family='Noto Sans KR'),
                        xaxis=dict(tickangle=-40, automargin=True, tickfont=dict(size=11, color="#888888"), showgrid=False),
                        yaxis=dict(gridcolor=chart_grid, tickfont=dict(size=11, color="#888888")),
                        legend=dict(orientation="h", y=1.08),
                        hoverlabel=dict(bgcolor="#111111", font_color="#FFFFFF"),
                        bargap=0.3,
                    )
                    st.plotly_chart(fig_kw, use_container_width=True)

                    st.divider()

                    # 키워드 카드 (저경쟁 우선)
                    st.markdown("**🎯 상위노출 추천 키워드 (저경쟁 우선 정렬)**")
                    priority_df = result_df.sort_values(by=['경쟁도', '합계'], ascending=[True, False])
                    for _, row in priority_df.iterrows():
                        if "저경쟁" in row['경쟁도']:
                            badge = '<span class="kw-badge-good">추천</span>'
                        elif "중경쟁" in row['경쟁도']:
                            badge = '<span class="kw-badge-hot">검토</span>'
                        else:
                            badge = ''
                        st.markdown(f"""
                        <div class="kw-card">
                            <div class="kw-name">{row['키워드']} {badge}</div>
                            <div class="kw-meta">
                                월간 {row['합계']:,}회 검색 &nbsp;(PC {row['PC']:,} + 모바일 {row['모바일']:,})
                                &nbsp;|&nbsp; {row['경쟁도']} &nbsp;|&nbsp; {row['전략']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # 전략 리포트
                    top3 = result_df[result_df['경쟁도'].str.contains("저경쟁")].head(3)['키워드'].tolist()
                    if not top3: top3 = result_df.head(3)['키워드'].tolist()
                    top3_str = ", ".join(top3)
                    st.markdown(f"""
                    <div class="strategy-box">
                        <h4>📋 [{kw_store}] 상위노출 전략 리포트</h4>
                        <p>
                        <b>핵심 공략 키워드:</b> {top3_str}<br><br>
                        ① <b>블로그 포스팅</b> — 제목 첫 10자 안에 핵심 키워드 포함. 본문 1,500자 이상, 사진 10장 이상.<br>
                        ② <b>플레이스 최적화</b> — 매장 소개글에 저경쟁 키워드 자연스럽게 삽입. 영업시간·메뉴·가격 최신화.<br>
                        ③ <b>리뷰 유도</b> — 방문객에게 플레이스 리뷰 작성 시 키워드 포함 문구 안내.<br>
                        ④ <b>포스팅 주기</b> — 주 1회 이상 블로그 발행이 상위노출 유지에 가장 효과적.
                        </p>
                        <p style="font-size:11px; opacity:0.5; margin-top:12px;">
                        ※ 검색량·경쟁도는 네이버 검색광고 API 기준이며, 실제 노출 순위는 콘텐츠 품질·최신성·리뷰 수에 따라 달라질 수 있습니다.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.divider()

                    # CSV 다운로드
                    csv_data = result_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 전체 결과 CSV 다운로드",
                        data=csv_data,
                        file_name=f"{kw_store}_키워드분석_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
        else:
            # 대기 안내 화면
            guide_bg   = "#222222" if st.session_state.theme == "dark" else "#FFFFFF"
            guide_border = "#333333" if st.session_state.theme == "dark" else "#E0E0E0"
            guide_text = "#AAAAAA" if st.session_state.theme == "dark" else "#666666"
            badge_bg   = "#333333" if st.session_state.theme == "dark" else "#FFF3F3"
            badge_text = "#CCCCCC" if st.session_state.theme == "dark" else "#333333"
            st.markdown(f"""
            <div style="background:{guide_bg}; border-radius:4px; border:1px solid {guide_border}; padding:36px; text-align:center; margin-top:10px;">
                <div style="font-size:44px; margin-bottom:14px;">🔍</div>
                <div style="font-size:17px; font-weight:700;">키워드 분석 준비 완료</div>
                <div style="font-size:13px; color:{guide_text}; margin-top:10px; line-height:1.8;">
                    왼쪽에서 매장을 선택하고 <b>키워드 분석 시작</b>을 누르면<br>
                    리뷰 기반 키워드 추출 → 네이버 검색량 조회 → 상위노출 전략 리포트가 자동 생성됩니다.
                </div>
                <div style="margin-top:20px; display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
                    <div style="background:{badge_bg}; border-radius:4px; padding:10px 16px; font-size:12px; color:{badge_text};">📊 월간 검색량 조회</div>
                    <div style="background:{badge_bg}; border-radius:4px; padding:10px 16px; font-size:12px; color:{badge_text};">🏆 저경쟁 키워드 발굴</div>
                    <div style="background:{badge_bg}; border-radius:4px; padding:10px 16px; font-size:12px; color:{badge_text};">📋 맞춤 전략 리포트</div>
                    <div style="background:{badge_bg}; border-radius:4px; padding:10px 16px; font-size:12px; color:{badge_text};">📥 CSV 다운로드</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)