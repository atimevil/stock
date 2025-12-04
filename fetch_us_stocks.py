import pandas as pd
import os

def get_us_stocks_list():
    """미국 주식 및 ETF 리스트 정의"""
    
    # Magnificent 7 + Popular Tech
    tech_stocks = [
        {'ticker': 'AAPL', 'name': 'Apple'},
        {'ticker': 'MSFT', 'name': 'Microsoft'},
        {'ticker': 'GOOGL', 'name': 'Alphabet (Google)'},
        {'ticker': 'AMZN', 'name': 'Amazon'},
        {'ticker': 'NVDA', 'name': 'NVIDIA'},
        {'ticker': 'TSLA', 'name': 'Tesla'},
        {'ticker': 'META', 'name': 'Meta Platforms'},
        {'ticker': 'AMD', 'name': 'AMD'},
        {'ticker': 'NFLX', 'name': 'Netflix'},
        {'ticker': 'INTC', 'name': 'Intel'}
    ]
    
    # Popular ETFs
    etfs = [
        {'ticker': 'QQQ', 'name': 'Invesco QQQ (Nasdaq 100)'},
        {'ticker': 'SPY', 'name': 'SPDR S&P 500'},
        {'ticker': 'SOXL', 'name': 'Direxion Daily Semiconductor Bull 3X'},
        {'ticker': 'TQQQ', 'name': 'ProShares UltraPro QQQ'},
        {'ticker': 'JEPI', 'name': 'JPMorgan Equity Premium Income'},
        {'ticker': 'SCHD', 'name': 'Schwab US Dividend Equity'}
    ]
    
    return tech_stocks + etfs

def main():
    print("🇺🇸 Fetching US Stocks List...")
    
    us_stocks = get_us_stocks_list()
    
    df = pd.DataFrame(us_stocks)
    
    # 저장
    filename = 'us_stocks_list.csv'
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"💾 Saved {len(df)} US stocks to {filename}")
    print(df)

if __name__ == "__main__":
    main()
