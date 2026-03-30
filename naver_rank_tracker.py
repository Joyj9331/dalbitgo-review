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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 파일 경로 설정
TARGET_EXCEL = "가맹점_리뷰링크.xlsx"
KEYWORD_SOURCE_CSV = "가맹점_키워드수집결과.csv"
RESULT_CSV = "가맹점_순위추적_결과.csv"

print("==========================================")
print("[시스템] 달빛에구운고등어 순위 추적 자동화 봇 V4.4 (스텔스 우회 기능 및 지침 초안 탑재)")
print("==========================================")

if not os.path.exists(TARGET_EXCEL):
    print(f"[오류] '{TARGET_EXCEL}' 파일이 없습니다. 리뷰링크 엑셀 파일을 준비해주세요.")
    exit()

# 1. 기초 데이터 로드
target_df = pd.read_excel(TARGET_EXCEL)
keyword_source_df = pd.read_csv(KEYWORD_SOURCE_CSV) if os.path.exists(KEYWORD_SOURCE_CSV) else pd.DataFrame()

scan_tasks = []
print("[진행] 추적 타겟 분석 및 자동 키워드 생성 중...")

for _, row in target_df.iterrows():
    store_name = str(row['매장명']).strip()
    manual_kws = str(row.get('타겟키워드', 'nan'))
    final_kws = []
    
    if manual_kws != 'nan' and manual_kws.strip():
        final_kws = [k.strip() for k in manual_kws.split(',')]
    else:
        if not keyword_source_df.empty:
            match = keyword_source_df[keyword_source_df['매장명'] == store_name]
            if not match.empty:
                extracted_str = str(match.iloc[0]['추출된_키워드'])
                if extracted_str not in ["키워드 미설정", "키워드 없음", "nan"]:
                    final_kws = [k.strip() for k in extracted_str.split(',')[:3]]
        
        if not final_kws:
            branch_name = store_name.replace("달빛에구운고등어", "").replace("달빛고등어", "").strip()
            final_kws = [f"{branch_name} 맛집", f"{branch_name} 생선구이"]

    for kw in final_kws:
        if kw:
            scan_tasks.append({"매장명": store_name, "타겟키워드": kw})

print(f"[완료] 분석 완료: 총 {len(target_df)}개 매장에서 {len(scan_tasks)}개의 추적 타겟을 자동 확정했습니다.\n")

# --- 크롤링 엔진 시작 ---
mobile_emulation = { "deviceName": "iPhone X" }
options = webdriver.ChromeOptions()
options.add_argument('--headless') 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("mobileEmulation", mobile_emulation)

# [우회 기능 1] 일반 스마트폰 브라우저로 위장
options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")

# [우회 기능 2] 자동화 도구 흔적(플래그) 지우기
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
options.add_experimental_option('useAutomationExtension', False)

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # [우회 기능 3 핵심] 네이버 자바스크립트 봇 탐지기(navigator.webdriver) 강제 무력화
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''Object.defineProperty(navigator, 'webdriver', {get: () => undefined})'''
    })
except Exception as e:
    print(f"[오류] 크롬 드라이버 에러: {e}")
    exit()

results = []
today_str = datetime.now().strftime('%Y-%m-%d')

# 2. 기존 데이터 로드 (등락폭 비교용)
old_data = {}
if os.path.exists(RESULT_CSV):
    try:
        old_df = pd.read_csv(RESULT_CSV)
        latest_history = old_df.sort_values('수집일자').groupby(['매장명', '타겟키워드']).last().reset_index()
        for _, row in latest_history.iterrows():
            key = f"{row['매장명']}_{row['타겟키워드']}"
            old_data[key] = row['현재순위']
    except: pass

# 3. 랭킹 스캔 및 1위 매장 정보 수집 루프
for task in scan_tasks:
    store_name = task['매장명']
    keyword = task['타겟키워드']
    
    # 봇이 서버 IP로 검색하여 타지역 전국구 맛집이 1등으로 나오는 현상 방지 로직
    branch_only = store_name.replace("달빛에구운고등어", "").replace("달빛고등어", "").replace("점", "").strip()
    
    search_query = keyword
    is_missing_local_name = False
    
    if len(branch_only) >= 2 and branch_only[:2] not in keyword:
        search_query = f"{branch_only} {keyword}"
        is_missing_local_name = True
        
    print(f"[조회] [{store_name}] 순위 조회 중... (설정키워드: {keyword} -> 실제검색: {search_query})")
    
    search_url = f"https://m.search.naver.com/search.naver?where=m&query={search_query}"
    driver.get(search_url)
    
    # [우회 기능 4] 사람처럼 약간의 불규칙한 대기 시간 부여
    time.sleep(random.uniform(2.5, 4.0))
    
    rank = 0
    found = False
    
    first_place_name = "-"
    first_place_url = ""
    first_place_kws = "-"
    
    try:
        try:
            more_btn = driver.find_elements(By.XPATH, "//a[contains(text(), '플레이스 더보기')] | //span[contains(text(), '플레이스 더보기')]")
            if more_btn:
                driver.execute_script("arguments[0].click();", more_btn[0])
                time.sleep(2.5)
        except: pass
            
        # 순위 스캔 (최대 50위)
        for scroll in range(4): 
            places = driver.find_elements(By.CSS_SELECTOR, ".place_bluelink, .tit_inner, .TYaxT, .C_N_u")
            
            for p in places:
                text = p.text.replace(" ", "")
                if not text: continue
                rank += 1
                
                # 1위 매장 정보 포착
                if rank == 1 and not first_place_url:
                    first_place_name = p.text.split('\n')[0] if '\n' in p.text else p.text
                    try:
                        href = p.get_attribute('href')
                        if not href:
                            href = p.find_element(By.XPATH, "./ancestor::a").get_attribute('href')
                        first_place_url = href
                    except: pass
                
                store_clean = store_name.replace(" ", "")
                
                match_condition = False
                if not branch_only: match_condition = store_clean in text
                else: match_condition = ("달빛" in text) and (branch_only in text)
                
                if match_condition or store_clean in text:
                    found = True
                    break
            
            if found or rank >= 50: break
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            
    except Exception as e:
        print(f"  - [경고] 오류: {e}")

    final_rank = rank if found else 999
    display_rank = f"{final_rank}위" if found else "순위 밖(50위+)"
    
    # 등락폭 계산
    history_key = f"{store_name}_{keyword}"
    trend = "-"
    if history_key in old_data:
        old_val = old_data[history_key]
        if old_val == 999 and final_rank != 999: trend = "신규진입"
        elif old_val != 999 and final_rank == 999: trend = "순위이탈"
        elif old_val > final_rank: trend = f"+{old_val - final_rank}"
        elif old_val < final_rank: trend = f"-{final_rank - old_val}"
        
    print(f"  - [확인] 우리 매장 순위 확인: {display_rank} ({trend})")
    
    # [본사 지침 초안 생성 로직] 전문적인 분석 및 제안
    ai_insight = ""
    if is_missing_local_name:
        ai_insight = f"[지역명 누락] '{keyword}'는 전국구 경쟁 단어라 노출이 어렵습니다. '{search_query}'(으)로 수정 등록 지침을 하달하십시오."
    elif final_rank == 999:
        ai_insight = "[노출 실패] 현재 50위 밖입니다. 주변 경쟁업체의 키워드를 분석하여 전면 교체 초안을 마련하십시오."
    elif trend == "순위이탈":
        ai_insight = "[순위 이탈] 노출 순위가 50위 밖으로 이탈했습니다. 주변 경쟁업체를 파악하여 키워드 재배열 지침을 수립하십시오."
    elif trend.startswith("-"):
        ai_insight = "[순위 하락] 노출 순위가 하락했습니다. 주변 경쟁업체의 신규 키워드 유무를 파악하여 방어 지침을 수립하십시오."
    elif final_rank == 1:
        ai_insight = "[순위 유지] 현재 1위입니다. 현행 키워드 세팅을 유지하도록 매장에 안내하십시오."
    elif final_rank <= 5:
        ai_insight = "[1페이지 노출 중] 양호합니다. 1위 탈환을 위해 주변 경쟁업체의 서브 키워드 조합을 분석하여 추가 지침을 기획하십시오."
    else:
        ai_insight = "[노출 저조] 1페이지 진입을 위해 주변 경쟁업체의 키워드를 파악하여 재배열 초안을 작성하십시오."
    
    # 1위 주변 경쟁업체 정보 수집 및 키워드 분석
    if first_place_url and first_place_name.replace(" ", "") != store_name.replace(" ", ""):
        print(f"  - [분석] 1위 경쟁업체 [{first_place_name}] 키워드 분석 중...")
        try:
            driver.get(first_place_url)
            time.sleep(random.uniform(2.0, 3.0))
            page_source = driver.page_source
            
            raw_keywords_str = ""
            match_arr1 = re.search(r'"keywords"\s*:\s*\[(.*?)\]', page_source)
            match_arr2 = re.search(r'"keywordList"\s*:\s*\[(.*?)\]', page_source)
            match_arr3 = re.search(r'\\\"keywords\\\"\s*:\s*\[(.*?)\]', page_source)
            match_meta1 = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\'](.*?)["\']', page_source, re.IGNORECASE)
            
            if match_arr1: raw_keywords_str = match_arr1.group(1)
            elif match_arr2: raw_keywords_str = match_arr2.group(1)
            elif match_arr3: raw_keywords_str = match_arr3.group(1).replace('\\"', '"')
            elif match_meta1: raw_keywords_str = match_meta1.group(1)
                
            if raw_keywords_str:
                clean_keywords = [k.strip().strip('"').strip("'").strip('\\"').replace('\\"', '') for k in raw_keywords_str.split(',')]
                kws = [k for k in clean_keywords if k and k.lower() not in ['naver', '네이버', '스마트플레이스']]
                first_place_kws = ", ".join(kws[:5]) if kws else "미설정"
            else:
                first_place_kws = "미설정"
                
            print(f"  - [완료] 1위 매장 키워드 확인 완료: {first_place_kws}")
        except Exception as e:
            print(f"  - [오류] 1위 매장 분석 실패: {e}")
            first_place_kws = "분석 불가"
    elif first_place_name.replace(" ", "") == store_name.replace(" ", ""):
        first_place_name = "달빛에구운고등어 1위 유지"
        first_place_kws = "-"
    
    results.append({
        "수집일자": today_str,
        "매장명": store_name,
        "타겟키워드": keyword,
        "현재순위": final_rank,
        "등락폭": trend,
        "1위_매장명": first_place_name,
        "1위_사용_키워드": first_place_kws,
        "AI_인사이트": ai_insight
    })

driver.quit()

# 4. 결과 누적 저장
new_res_df = pd.DataFrame(results)
if os.path.exists(RESULT_CSV):
    final_df = pd.concat([pd.read_csv(RESULT_CSV), new_res_df], ignore_index=True)
else:
    final_df = new_res_df

final_df.to_csv(RESULT_CSV, index=False, encoding='utf-8-sig')

print("\n==========================================")
print(f"[시스템] 순위 추적 및 주변 경쟁업체 파악 데이터 수집 완료! '{RESULT_CSV}' 업데이트 됨.")
print("==========================================")