import time
import pandas as pd
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. 수집 대상 가맹점 정보 세팅 (매장명: 네이버플레이스 링크)
# 과장님이 관리하시는 100개 매장 리스트로 아래 딕셔너리를 채워주시면 됩니다.
TARGET_STORES = {
    "테스트매장(강남)": "https://m.place.naver.com/restaurant/2010196121/review/visitor?entry=plt",
    # "홍대점": "https://m.place.naver.com/restaurant/xxxxxxx/review/visitor",
    # "부산서면점": "https://m.place.naver.com/restaurant/yyyyyyy/review/visitor",
}

# 네이버 봇 탐지 우회를 위한 대기 시간 (10분 = 600초)
WAIT_TIME_SECONDS = 600 

def analyze_sentiment(text):
    """간단한 키워드 기반 긍정/부정 분석 (대시보드 표출용)"""
    positive_keywords = ["맛있", "최고", "친절", "좋", "깔끔", "청결", "완벽", "추천", "가성비"]
    negative_keywords = ["불친절", "늦", "맛없", "최악", "더럽", "비싸", "별로", "실망", "벌레", "짜다"]
    
    if any(keyword in text for keyword in negative_keywords):
        return "부정"
    elif any(keyword in text for keyword in positive_keywords):
        return "긍정"
    return "중립"

def setup_driver():
    """크롬 브라우저 자동화 설정"""
    chrome_options = Options()
    # 개발 테스트 시에는 아래 '--headless' 주석 처리를 해제하여 눈으로 브라우저가 움직이는지 확인하는 것도 좋습니다.
    # chrome_options.add_argument('--headless') 
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_store_reviews(driver, store_name, url):
    """개별 매장 리뷰 데이터 추출"""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] '{store_name}' 접속 중...")
    driver.get(url)
    reviews_data = []
    
    try:
        # 리뷰 리스트 로딩 대기 (최대 10초)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.owAeM")) 
        )
        
        # 스크롤 없이 최상단에 보이는 최신 리뷰 5개만 수집
        review_elements = driver.find_elements(By.CSS_SELECTOR, "li.owAeM")[:5]
        
        for element in review_elements:
            try:
                # 텍스트 내용 추출
                content = element.find_element(By.CSS_SELECTOR, "span.zPfVt").text
                # 날짜 추출
                date_str = element.find_elements(By.CSS_SELECTOR, "span.tzZTf")[0].text
                
                # 대시보드 규격에 맞게 데이터 적재
                reviews_data.append({
                    "매장명": store_name,
                    "작성일": date_str,
                    "리뷰내용": content,
                    "감정분석": analyze_sentiment(content)
                })
            except Exception:
                continue # 글 없는 사진 리뷰 등 예외 처리
                
    except Exception as e:
        print(f"⚠️ '{store_name}' 리뷰 로딩 실패 (URL 확인 필요)")
        
    return reviews_data

def main():
    print("--- 🚀 가맹점 리뷰 자동 수집 프로세스를 시작합니다 ---")
    driver = setup_driver()
    all_reviews = []
    
    try:
        store_items = list(TARGET_STORES.items())
        total_stores = len(store_items)
        
        for idx, (store_name, url) in enumerate(store_items):
            print(f"\n[{idx+1}/{total_stores}] 매장 데이터 수집 시작")
            
            store_reviews = crawl_store_reviews(driver, store_name, url)
            all_reviews.extend(store_reviews)
            
            # 마지막 매장이 아니면 대기 (안티 크롤링 회피)
            if idx < total_stores - 1:
                print(f"  -> 다음 매장 수집 전까지 안전하게 {WAIT_TIME_SECONDS/60}분 대기합니다...")
                time.sleep(WAIT_TIME_SECONDS)
                
    finally:
        driver.quit()
        
    # 데이터 저장 처리
    if all_reviews:
        df = pd.DataFrame(all_reviews)
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"가맹점_리뷰수집결과_{today_str}.csv"
        
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n✅ 수집 완료! 총 {len(all_reviews)}개의 리뷰가 '{filename}'에 저장되었습니다.")
        print("  -> 이제 대시보드를 새로고침하시면 수집된 데이터가 바로 반영됩니다.")
    else:
        print("\n⚠️ 수집된 리뷰가 없습니다.")

if __name__ == "__main__":
    main()