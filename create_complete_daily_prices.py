import pandas as pd
import requests
from datetime import datetime
import time
from tqdm import tqdm
import os
import io

def get_daily_price(code, pages=10):
    """
    네이버 금융에서 일별 시세를 가져옵니다.
    :param code: 종목코드
    :param pages: 가져올 페이지 수 (1페이지당 10일치)
    :return: DataFrame
    """
    url = f"https://finance.naver.com/item/sise_day.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    df_list = []
    
    for page in range(1, pages + 1):
        pg_url = f'{url}&page={page}'
        try:
            response = requests.get(pg_url, headers=headers)
            # pandas read_html을 사용하여 테이블 파싱
            tables = pd.read_html(io.StringIO(response.text))
            # 일별 시세 테이블은 보통 첫 번째에 위치하지만, 구조에 따라 다를 수 있음
            # 네이버 금융 일별 시세 페이지 구조상 첫 번째 테이블이 시세 데이터임
            df = tables[0].dropna()
            df_list.append(df)
            time.sleep(0.1) # 서버 부하 방지
        except Exception as e:
            print(f"Error fetching page {page} for code {code}: {e}")
            break
            
    if not df_list:
        return None
        
    df = pd.concat(df_list, ignore_index=True)
    df = df.rename(columns={
        '날짜': 'date',
        '종가': 'close',
        '전일비': 'diff',
        '시가': 'open',
        '고가': 'high',
        '저가': 'low',
        '거래량': 'volume'
    })
    
    # 데이터 전처리
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['code'] = code
    
    return df

def main():
    print("Starting daily price collection...")
    
    # 종목 리스트 로드
    try:
        stocks = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
    except FileNotFoundError:
        print("Error: korean_stocks_list.csv not found.")
        return

    all_data = []
    
    # 기존 데이터가 있다면 로드하여 증분 수집 (여기서는 단순화를 위해 매번 새로 수집하거나 덮어쓰기)
    # 실제 운영 시에는 기존 파일 로드 후 최신 날짜 이후만 수집하는 로직 필요
    
    for _, row in tqdm(stocks.iterrows(), total=len(stocks), desc="Collecting Data"):
        code = row['ticker']
        name = row['name']
        
        # 최근 1년치 데이터 (약 25페이지) 수집
        df = get_daily_price(code, pages=25)
        
        if df is not None:
            df['name'] = name
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('daily_prices.csv', index=False)
        print(f"Successfully saved {len(final_df)} rows to daily_prices.csv")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
