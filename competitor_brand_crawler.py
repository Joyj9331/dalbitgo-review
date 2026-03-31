import pandas as pd
import time
import random
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 1. 시스템 및 파일 세팅
# ==========================================
TARGET_EXCEL = "경쟁사_매칭리스트.xlsx"
RESULT_CSV = "경쟁업체_메뉴키워드_수집결과.csv"

print("==========================================")
print("[시스템] 경쟁사 기초 데이터 수집 봇 가동 (메뉴명/가격 및 키워드 정밀 추출)")
print("==========================================")

if not os.path.exists(TARGET_EXCEL):
    print(f"[오류] '{TARGET_EXCEL}' 파일이 없습니다. 엑셀 파일을 확인해 주십시오.")
    exit()

try:
    df = pd.read_excel(TARGET_EXCEL)
except Exception as e:
    print(f"[오류] 엑셀 파일 로드 실패: {e}")
    exit()

# ==========================================
# 2. 브라우저 제어 엔진 (스텔스 모드)
# ==========================================
def init_stealth_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    return driver

# ==========================================
# 3. 데이터 추출 핵심 로직
# ==========================================
def extract_place_data(driver, expected_brand_name, url):
    print(f"\n[진행] 타겟 접속 중: {url}")
    
    data = {
        "경쟁브랜드명_엑셀": expected_brand_name,
        "실제_플레이스_업체명": "확인 불가",
        "명칭_일치_여부": "불일치",
        "타겟_키워드": "미설정",
        "메뉴_및_가격": "수집 실패",
        "타겟_URL": url
    }
    
    try:
        driver.get(url)
        time.sleep(random.uniform(3.0, 4.0))
        
        try: driver.switch_to.frame("entryIframe")
        except: pass
        
        # --- 업체명 추출 ---
        page_source = driver.page_source
        actual_name = ""
        try:
            title_elements = driver.find_elements(By.CSS_SELECTOR, "span.Fc1rA, span.GHAhO, .tit")
            if title_elements: actual_name = title_elements[0].text.strip()
            else:
                title_match = re.search(r'<title>(.*?)</title>', page_source)
                if title_match: actual_name = title_match.group(1).replace("네이버 지도", "").replace("-", "").strip()
        except: pass
        
        if actual_name:
            data["실제_플레이스_업체명"] = actual_name
            if expected_brand_name.replace(" ", "") in actual_name.replace(" ", ""):
                data["명칭_일치_여부"] = "일치"
                print(f"  - [확인] 업체명 식별: {actual_name}")
            else:
                data["명칭_일치_여부"] = "불일치"
                print(f"  - [경고] 업체명 불일치 의심 (실제: {actual_name})")

        # --- 숨겨진 타겟 키워드 추출 ---
        raw_keywords_str = ""
        match_arr1 = re.search(r'"keywords"\s*:\s*\[(.*?)\]', page_source)
        match_arr2 = re.search(r'"keywordList"\s*:\s*\[(.*?)\]', page_source)
        match_arr3 = re.search(r'\\\"keywords\\\"\s*:\s*\[(.*?)\]', page_source)
        match_meta1 = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\'](.*?)["\']', page_source, re.IGNORECASE)
        match_meta2 = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']keywords["\']', page_source, re.IGNORECASE)

        if match_arr1: raw_keywords_str = match_arr1.group(1)
        elif match_arr2: raw_keywords_str = match_arr2.group(1)
        elif match_arr3: raw_keywords_str = match_arr3.group(1).replace('\\"', '"')
        elif match_meta1: raw_keywords_str = match_meta1.group(1)
        elif match_meta2: raw_keywords_str = match_meta2.group(1)
            
        if raw_keywords_str:
            clean_keywords = [k.strip().strip('"').strip("'").strip('\\"').replace('\\"', '') for k in raw_keywords_str.split(',')]
            keywords = [k for k in clean_keywords if k and k.lower() not in ['naver', '네이버', '스마트플레이스']]
            if keywords:
                data["타겟_키워드"] = ", ".join(keywords)
                print(f"  - [성공] 타겟 키워드 추출 완료 ({len(keywords)}개)")
            else:
                print("  - [경고] 유효한 키워드가 없습니다.")
        else:
            print("  - [경고] 키워드 미설정 매장입니다.")
        
        # --- 메뉴/가격 정밀 추출 (메뉴 설명 원천 차단) ---
        try:
            menu_btn = driver.find_elements(By.XPATH, "//a[contains(., '메뉴')]")
            if menu_btn:
                driver.execute_script("arguments[0].click();", menu_btn[0])
                print("  - [진행] '메뉴' 탭 진입 완료")
                time.sleep(2.0)
            else:
                print("  - [경고] '메뉴' 탭이 없습니다. 홈 화면에서 메뉴 강제 스캔을 시도합니다.")
            
            # 끝까지 스크롤하여 로딩 유도
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: break
                last_height = new_height
            
            menu_text = driver.find_element(By.TAG_NAME, "body").text
            lines = [line.strip() for line in menu_text.split('\n') if line.strip()]
            
            menu_list = []
            last_price_idx = -1
            
            for i, line in enumerate(lines):
                # 💡 정규식: 완벽한 가격 라인 인식
                if re.match(r'^[0-9]{1,3}(?:,[0-9]{3})+원$', line) or re.match(r'^[0-9]{4,6}원$', line):
                    price = line
                    
                    # 이전 가격 인덱스부터 현재 가격 인덱스 사이의 텍스트 블록 추출
                    block_start = last_price_idx + 1 if last_price_idx != -1 else max(0, i - 10)
                    block_lines = lines[block_start:i]
                    
                    # 💡 [핵심 조치] 네이버 UI 찌꺼기 버튼 텍스트 원천 차단 목록 대폭 강화
                    ignore_tags = [
                        "대표", "추천", "사진", "주문", "예약", "배달", "포장", "메뉴", "리뷰", "정보", 
                        "소식", "홈", "저장", "공유", "거리뷰", "방문자리뷰", "블로그리뷰", "길찾기", 
                        "전화", "더보기", "영수증", "네이버예약", "네이버주문", "펼쳐보기"
                    ]
                    valid_candidates = []
                    
                    for b_line in block_lines:
                        b_line_clean = b_line.strip()
                        if b_line_clean in ignore_tags: continue
                        if re.match(r'^[0-9]+$', b_line_clean): continue # 의미 없는 숫자 라인 배제
                        
                        # 파생 쓰레기 데이터 (버튼류) 패턴 차단
                        if "리뷰" in b_line_clean and len(b_line_clean) <= 6: continue
                        if "사진" in b_line_clean and len(b_line_clean) <= 6: continue
                        
                        valid_candidates.append(b_line_clean)
                        
                    if valid_candidates:
                        # 💡 블록의 맨 첫 줄을 무조건 메뉴명으로 채택하고, 나머지는 설명문이므로 버림
                        menu_name = valid_candidates[0]
                        
                        # 예외적인 초장문 방어 (25자 초과 시 컷팅)
                        if len(menu_name) > 25:
                            menu_name = menu_name[:25] + "..."
                            
                        menu_list.append(f"{menu_name} : {price}")
                    
                    last_price_idx = i # 다음 메뉴 파싱을 위해 현재 가격 인덱스 갱신
            
            if menu_list:
                # 중복 제거
                unique_menus = list(dict.fromkeys(menu_list))
                data["메뉴_및_가격"] = " | ".join(unique_menus)
                print(f"  - [성공] 메뉴 데이터 수집 완료 ({len(unique_menus)}개 품목, 설명문 제거됨)")
            else:
                print("  - [실패] 텍스트에서 가격 패턴을 찾지 못했습니다.")
                
        except Exception as e:
            print(f"  - [오류] 메뉴 스캔 중 에러 발생: {e}")

    except Exception as e:
        print(f"  - [오류] 페이지 접속 실패: {e}")
        
    return data

# ==========================================
# 4. 메인 컨트롤러
# ==========================================
if __name__ == "__main__":
    final_results = []
    today = datetime.now().strftime('%Y-%m-%d')
    driver = init_stealth_driver()
    
    try:
        for _, row in df.iterrows():
            if len(row) < 2: continue
            
            brand_name = str(row.iloc[0]).strip() 
            place_url = str(row.iloc[1]).strip() 
            
            if pd.isna(row.iloc[1]) or 'http' not in place_url:
                continue
                
            res = extract_place_data(driver, brand_name, place_url)
            res["수집일자"] = today
            final_results.append(res)
            
    finally:
        driver.quit()
        
    if final_results:
        result_df = pd.DataFrame(final_results)
        cols = ['수집일자', '경쟁브랜드명_엑셀', '실제_플레이스_업체명', '명칭_일치_여부', '타겟_키워드', '메뉴_및_가격', '타겟_URL']
        result_df = result_df[cols]
        
        if os.path.exists(RESULT_CSV):
            old = pd.read_csv(RESULT_CSV)
            result_df = pd.concat([old, result_df], ignore_index=True)
            result_df.drop_duplicates(subset=['수집일자', '타겟_URL'], keep='last', inplace=True)
            
        result_df.to_csv(RESULT_CSV, index=False, encoding='utf-8-sig')
        print(f"\n[작업완료] 기초 데이터 수집 종료. 결과 파일: {RESULT_CSV}")
    else:
        print("\n[시스템] 수집된 데이터가 없습니다.")