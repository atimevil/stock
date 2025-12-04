import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

def collect_us_prices():
    print("🇺🇸 Collecting US Daily Prices...")
    
    # US 주식 리스트 로드
    if not os.path.exists('us_stocks_list.csv'):
        print("Error: us_stocks_list.csv not found.")
        return
        
    us_stocks = pd.read_csv('us_stocks_list.csv')
    
    all_prices = []
    
    for _, row in us_stocks.iterrows():
        ticker = row['ticker']
        name = row['name']
        print(f"Fetching {name} ({ticker})...")
        
        try:
            # 최근 2년 데이터 가져오기
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2y")
            
            if hist.empty:
                print(f"Warning: No data for {ticker}")
                continue
                
            # 데이터 포맷팅
            hist = hist.reset_index()
            hist['date'] = hist['Date'].dt.strftime('%Y-%m-%d')
            hist['code'] = ticker # US stocks use ticker as code
            hist['name'] = name
            
            # 필요한 컬럼만 선택 및 이름 변경
            # yfinance columns: Date, Open, High, Low, Close, Volume, Dividends, Stock Splits
            # target columns: date, open, high, low, close, volume, code, name
            
            df = hist[['date', 'Open', 'High', 'Low', 'Close', 'Volume', 'code', 'name']].copy()
            df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'code', 'name']
            
            all_prices.append(df)
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    if not all_prices:
        print("No US price data collected.")
        return

    us_prices_df = pd.concat(all_prices, ignore_index=True)
    
    # 기존 daily_prices.csv와 병합
    if os.path.exists('daily_prices.csv'):
        try:
            kr_prices_df = pd.read_csv('daily_prices.csv', dtype={'code': str})
            
            # 병합 (US + KR)
            # 주의: 날짜 형식이 다를 수 있으므로 통일 필요하지만, 위에서 YYYY-MM-DD로 맞춤.
            combined_df = pd.concat([kr_prices_df, us_prices_df], ignore_index=True)
            
            # 중복 제거 (혹시 모를 중복 방지)
            combined_df = combined_df.drop_duplicates(subset=['date', 'code'])
            
            # 저장
            combined_df.to_csv('daily_prices.csv', index=False, encoding='utf-8')
            print(f"💾 Merged US prices. Total records: {len(combined_df)}")
            
        except Exception as e:
            print(f"Error merging with daily_prices.csv: {e}")
            # 실패 시 별도 저장
            us_prices_df.to_csv('us_daily_prices.csv', index=False, encoding='utf-8')
    else:
        us_prices_df.to_csv('daily_prices.csv', index=False, encoding='utf-8')
        print(f"💾 Saved US prices to daily_prices.csv")

if __name__ == "__main__":
    collect_us_prices()
