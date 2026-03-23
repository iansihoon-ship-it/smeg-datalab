import requests
import sqlite3
import json
import time
from datetime import datetime

# 설정 정보 (수정된 scraping_prompt.md 기반)
BASE_URL = "https://search.shopping.naver.com/api/review"
HEADERS = {
    "Referer": "https://search.shopping.naver.com/catalog/54608922345",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}
PARAMS_TEMPLATE = {
    "nvMid": "53263372916",
    "pageSize": 20,
    "sortType": "QUALITY",
    "isNeedAggregation": "Y"
}
DB_PATH = "egf03_reviews.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 기존 테이블 삭제 후 재생성 (구조 변경 대응)
    cursor.execute('DROP TABLE IF EXISTS reviews')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id TEXT PRIMARY KEY,
            buyOption TEXT,
            content TEXT,
            aidaCreateTime TEXT,
            aidaModifyTime TEXT,
            collectedAt TEXT
        )
    ''')
    conn.commit()
    return conn

def fetch_reviews(page):
    params = PARAMS_TEMPLATE.copy()
    params["page"] = page
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching page {page}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Request Exception on page {page}: {e}")
        return None

def save_to_db(conn, reviews_list):
    cursor = conn.cursor()
    current_time = datetime.now().isoformat()
    
    for review in reviews_list:
        cursor.execute('''
            INSERT OR IGNORE INTO reviews (id, buyOption, content, aidaCreateTime, aidaModifyTime, collectedAt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            review.get('id'),
            review.get('buyOption'),
            review.get('content'),
            review.get('aidaCreateTime'),
            review.get('aidaModifyTime'),
            current_time
        ))
    conn.commit()

def main():
    print("Starting Updated EGF03 Review Collection (GET API)...")
    conn = init_db()
    
    page = 1
    total_collected = 0
    
    while True:
        print(f"Fetching page {page}...")
        data = fetch_reviews(page)
        
        if not data or not data.get('reviews'):
            print("No more data or error occurred.")
            break
            
        reviews = data['reviews']
        save_to_db(conn, reviews)
        
        count = len(reviews)
        total_collected += count
        print(f"Saved {count} reviews from page {page}. (Total: {total_collected})")
        
        total_count = data.get('totalCount', 0)
        if total_collected >= total_count or count < 20:
            break
            
        page += 1
        time.sleep(1.5) # 안전을 위한 딜레이 상향
        
    conn.close()
    print(f"\nCollection Complete! Total reviews in DB: {total_collected}")

if __name__ == "__main__":
    main()
