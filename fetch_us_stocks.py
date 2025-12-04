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
        {'ticker': 'INTC', 'name': 'Intel'},
        {'ticker': 'AVGO', 'name': 'Broadcom'},
        {'ticker': 'ORCL', 'name': 'Oracle'},
        {'ticker': 'ADBE', 'name': 'Adobe'},
        {'ticker': 'CRM', 'name': 'Salesforce'},
        {'ticker': 'QCOM', 'name': 'Qualcomm'}
    ]

    # Major Sector Leaders (Finance, Healthcare, Consumer, Energy)
    sector_leaders = [
        {'ticker': 'JPM', 'name': 'JPMorgan Chase'},
        {'ticker': 'V', 'name': 'Visa'},
        {'ticker': 'MA', 'name': 'Mastercard'},
        {'ticker': 'BAC', 'name': 'Bank of America'},
        {'ticker': 'LLY', 'name': 'Eli Lilly'},
        {'ticker': 'JNJ', 'name': 'Johnson & Johnson'},
        {'ticker': 'UNH', 'name': 'UnitedHealth'},
        {'ticker': 'PFE', 'name': 'Pfizer'},
        {'ticker': 'WMT', 'name': 'Walmart'},
        {'ticker': 'PG', 'name': 'Procter & Gamble'},
        {'ticker': 'KO', 'name': 'Coca-Cola'},
        {'ticker': 'PEP', 'name': 'PepsiCo'},
        {'ticker': 'COST', 'name': 'Costco'},
        {'ticker': 'XOM', 'name': 'Exxon Mobil'},
        {'ticker': 'CVX', 'name': 'Chevron'}
    ]
    
    # Popular ETFs
    etfs = [
        {'ticker': 'QQQ', 'name': 'Invesco QQQ (Nasdaq 100)'},
        {'ticker': 'SPY', 'name': 'SPDR S&P 500'},
        {'ticker': 'DIA', 'name': 'SPDR Dow Jones Industrial Average'},
        {'ticker': 'IWM', 'name': 'iShares Russell 2000'},
        {'ticker': 'SOXL', 'name': 'Direxion Daily Semiconductor Bull 3X'},
        {'ticker': 'SOXX', 'name': 'iShares Semiconductor ETF'},
        {'ticker': 'TQQQ', 'name': 'ProShares UltraPro QQQ'},
        {'ticker': 'JEPI', 'name': 'JPMorgan Equity Premium Income'},
        {'ticker': 'SCHD', 'name': 'Schwab US Dividend Equity'},
        {'ticker': 'TLT', 'name': 'iShares 20+ Year Treasury Bond'},
        {'ticker': 'ARKK', 'name': 'ARK Innovation ETF'},
        {'ticker': 'XLE', 'name': 'Energy Select Sector SPDR'},
        {'ticker': 'XLF', 'name': 'Financial Select Sector SPDR'},
        {'ticker': 'XLV', 'name': 'Health Care Select Sector SPDR'}
    ]
    
    return tech_stocks + sector_leaders + etfs

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
