import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 기본 설정
st.set_page_config(page_title="프랜차이즈 가맹점 리뷰 관리", page_icon="🚨", layout="wide")

# ==========================================
# 🔒 보안 로그인 시스템 (사내 기밀 유지용)
# ==========================================
def check_password():
    """비밀번호가 맞으면 True를 반환합니다."""
    def password_entered():
        # 💡 직원 공용 비밀번호 변경: 51015
        if st.session_state["password"] == "51015":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 보안을 위해 세션에서 비밀번호 삭제
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; margin-top: 100px;'>🔒 본사 사내망 접근 (기밀)</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>프랜차이즈 가맹점 평판 데이터는 외부 유출이 엄격히 금지됩니다.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.text_input("직원 공용 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
        
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center; margin-top: 100px;'>🔒 본사 사내망 접근 (기밀)</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.text_input("직원 공용 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
            st.error("❌ 비밀번호가 틀렸습니다. (힌트: 51015)")
        return False
    else:
        return True

# 비밀번호를 통과하지 못하면 여기서 대시보드 화면 송출을 멈춥니다.
if not check_password():
    st.stop()

# ==========================================
# 📊 대시보드 본문 (인증된 직원만 볼 수 있음)
# ==========================================
def load_data():
    # 💡 누적 데이터 파일명으로 연동
    filename = "가맹점_리뷰수집결과_누적.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        st.warning("현재 수집된 누적 데이터 파일이 없어 샘플 화면을 보여드립니다.")
        data = {
            "매장명": ["파주심학산점", "강남역점", "강남역점", "홍대점", "부산서면점"],
            "작성일": ["2026-03-26", "2026-03-26", "2026-03-26", "2026-03-26", "2026-03-26"],
            "리뷰내용": ["고등어가 너무 맛있어요!", "직원 불친절하네요.", "늦게 나와서 화났음.", "가성비 최고", "매장이 청결해요"],
            "감정분석": ["긍정", "부정", "부정", "긍정", "긍정"]
        }
        df = pd.DataFrame(data)
    return df

def load_store_list():
    excel_file = "가맹점_리뷰링크.xlsx"
    if os.path.exists(excel_file):
        try:
            store_df = pd.read_excel(excel_file)
            if '매장명' in store_df.columns:
                return sorted(store_df['매장명'].dropna().unique().tolist())
        except Exception as e:
            pass
    return []

df = load_data()
full_store_list = load_store_list()
if not full_store_list:
    full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else ["매장 없음"]

st.sidebar.title("👨‍💼 가맹점 관리 비서")
st.sidebar.markdown("과장님 및 본사 직원 전용 패널")

menu = st.sidebar.radio("분석 모드", ["🌐 1. 전체 브랜드 누적 평판", "🏪 2. 개별 가맹점 돋보기 분석"])
st.sidebar.divider()

if st.sidebar.button("🔄 최신 데이터 새로고침"):
    st.rerun()
    
st.sidebar.info("💡 **슈퍼바이저 활용 팁**\n\n'위험 감지' 탭에 뜬 매장 점주님들께 가장 먼저 오전 해피콜을 진행하시면 CS 방어에 효과적입니다.")

if menu == "🌐 1. 전체 브랜드 누적 평판":
    st.title("🌐 전체 가맹점 누적 평판 & 리스크 리포트")
    st.subheader("🚨 긴급 연락 요망 매장 (최근 부정 리뷰 감지)")
    
    negative_df = df[df['감정분석'] == '부정']
    if not negative_df.empty:
        st.error(f"⚠️ **{len(negative_df)}건**의 부정/불만 리뷰가 감지되었습니다. 아래 리스트를 확인하시고 점주님들께 연락해 주십시오.")
        st.dataframe(negative_df[['매장명', '리뷰내용', '작성일']].sort_values(by='작성일', ascending=False).reset_index(drop=True), use_container_width=True)
    else:
        st.success("🎉 감지된 부정/불만 리뷰가 한 건도 없습니다. 가맹점 현장 관리가 아주 훌륭하게 이루어지고 있습니다!")
        
    st.divider()
    st.subheader("📊 누적 리뷰 발생량 분석 (Top & Bottom)")
    
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '누적 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.info("🔥 리뷰 활성 매장 (고객 반응 폭발)")
        st.dataframe(review_counts.head(5), use_container_width=True)
    with col_bottom:
        st.warning("❄️ 리뷰 저조 매장 (마케팅/이벤트 점검 필요)")
        st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

else:
    st.title("🏪 개별 가맹점 상세 분석 (누적)")
    selected_store = st.selectbox("📌 분석하실 특정 가맹점을 선택하십시오", full_store_list)
    store_df = df[df['매장명'] == selected_store]
    st.subheader(f"[{selected_store}] 고객 반응 누적 요약")
    
    if store_df.empty:
        st.success(f"✅ 수집된 리뷰가 없습니다. 평시와 동일하게 관리해주시면 됩니다.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("누적 총 리뷰", f"{len(store_df)}건")
        with col2: st.metric("긍정 평가 (칭찬/추천)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
        with col3: st.metric("부정 평가 (불만/개선)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
            
        st.divider()
        col_chart, col_list = st.columns([1, 2])
        
        with col_chart:
            st.markdown("**누적 감정 비율**")
            sentiment_counts = store_df['감정분석'].value_counts().reset_index()
            sentiment_counts.columns = ['감정', '비율']
            fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', color_discrete_map={'긍정':'#00CC96', '부정':'#EF553B', '중립':'#636EFA'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_list:
            st.markdown("**해당 매장 누적 리뷰 상세 내역**")
            display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True)
