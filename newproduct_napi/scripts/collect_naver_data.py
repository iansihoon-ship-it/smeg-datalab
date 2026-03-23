# /// script
# dependencies = [
#   "requests",
#   "pandas",
#   "python-dotenv",
# ]
# ///
import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# .env 로드
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("API credentials (CLIENT_ID, CLIENT_SECRET) not found in .env")

# 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# 키워드 및 설정
KEYWORDS = ["우유거품기", "밀크포머", "밀크프로더", "에어로치노", "우유스팀기"]
CAT_ID = "50002543" # 생활/가전 > 주방가전 > 커피머신
COL_DATE = datetime.now().strftime("%Y%m%d")

def save_json(data, filename):
    path = os.path.join(RAW_DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved RAW JSON: {path}")

def save_csv(df, filename):
    path = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved PROCESSED CSV: {path}")

def fetch_datalab_search():
    print("\n--- Fetching General Search Trend (DataLab) ---")
    url = "https://openapi.naver.com/v1/datalab/search"
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    keyword_params = [{"groupName": kw, "keywords": [kw]} for kw in KEYWORDS]
    
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": keyword_params,
        "device": "",
        "gender": "",
        "ages": []
    }
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        res_json = response.json()
        save_json(res_json, f"datalab_search_raw_{COL_DATE}.json")
        
        all_data = []
        for result in res_json['results']:
            kw_name = result['title']
            for item in result['data']:
                all_data.append({
                    "날짜": item['period'],
                    "수치": item['ratio'],
                    "키워드": kw_name
                })
        
        if all_data:
            df = pd.DataFrame(all_data)
        else:
            df = pd.DataFrame(columns=["날짜", "수치", "키워드"])
            
        range_str = f"{start_date.replace('-', '')}-{end_date.replace('-', '')}"
        filename = f"쇼핑트랜드_우유거품기외{len(KEYWORDS)-1}건_{range_str}_{COL_DATE}.csv"
        save_csv(df, filename)
    else:
        print(f"DataLab Error: {response.status_code}, {response.text}")

def fetch_search_data(category_type, keywords):
    """ category_type: 'blog' or 'shop' """
    print(f"\n--- Fetching {category_type.upper()} Search Data ---")
    
    api_map = {
        "blog": "https://openapi.naver.com/v1/search/blog.json",
        "shop": "https://openapi.naver.com/v1/search/shop.json"
    }
    url = api_map[category_type]
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    all_results = []
    for kw in keywords:
        params = {"query": kw, "display": 50, "start": 1, "sort": "sim"}
        resp = requests.get(url, headers=headers, params=params)
        
        if resp.status_code == 200:
            res_json = resp.json()
            save_json(res_json, f"search_{category_type}_{kw}_{COL_DATE}.json")
            
            items = res_json.get('items', [])
            for item in items:
                item['search_keyword'] = kw
                all_results.append(item)
            time.sleep(0.1) # 속도 조절
        else:
            print(f"Search {category_type} Error for {kw}: {resp.status_code}")
            
    if all_results:
        df = pd.DataFrame(all_results)
    else:
        # 블로그와 쇼핑은 컬럼구조가 다르므로 단순 빈 프레임 생성
        df = pd.DataFrame()
        
    # 명명 규칙: [종류]_우유거품기외N건_수집일.csv
    prefix = "블로그검색" if category_type == "blog" else "쇼핑상품검색"
    filename = f"{prefix}_우유거품기외{len(keywords)-1}건_{COL_DATE}.csv"
    save_csv(df, filename)

if __name__ == "__main__":
    fetch_datalab_search()
    fetch_search_data("blog", KEYWORDS)
    fetch_search_data("shop", KEYWORDS)
    print("\n--- Data Collection Complete ---")
