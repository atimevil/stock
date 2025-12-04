import pandas as pd
import yfinance as yf
import requests
import os
import time

def get_naver_fundamentals(code):
    """네이버 금융에서 한국 주식 재무 정보 크롤링"""
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        dfs = pd.read_html(response.text, encoding='euc-kr')
        
        # 네이버 금융 페이지 구조상 '종목분석' 테이블 찾기
        # 보통 3번째 또는 4번째 테이블에 주요 재무 정보가 있음
        # 하지만 테이블 순서가 바뀔 수 있으므로, 특정 키워드로 찾음
        
        fund_df = None
        for df in dfs:
            if 'PER' in df.iloc[:, 0].values or 'PER(배)' in str(df.columns):
                fund_df = df
                break
                
        if fund_df is None:
            return {}
            
        # 데이터 추출 (단순화를 위해 주요 지표만 추출 시도)
        # 네이버 금융 메인 페이지의 '투자지표' 섹션 파싱이 더 쉬울 수 있음
        # 여기서는 requests + string parsing으로 핵심 지표만 빠르게 가져옴
        
        html = response.text
        data = {}
        
        # PER
        try:
            # <em id="_per">10.5</em>
            import re
            per_match = re.search(r'<em id="_per">([\d\.]+)</em>', html)
            if per_match:
                data['PER'] = float(per_match.group(1))
        except: pass
        
        # PBR
        try:
            pbr_match = re.search(r'<em id="_pbr">([\d\.]+)</em>', html)
            if pbr_match:
                data['PBR'] = float(pbr_match.group(1))
        except: pass
        
        # 배당수익률
        try:
            div_match = re.search(r'<em id="_dvr">([\d\.]+)</em>', html)
            if div_match:
                data['Dividend_Yield'] = float(div_match.group(1))
        except: pass
        
        # 시가총액 (억)
        try:
            cap_match = re.search(r'<em id="_market_sum">([\d,]+)</em>', html)
            if cap_match:
                data['Market_Cap'] = int(cap_match.group(1).replace(',', '')) * 100000000 # 억 단위 -> 원
        except: pass
        
        return data
        
    except Exception as e:
        # print(f"Error fetching fundamentals for KR {code}: {e}")
        return {}

def get_us_fundamentals(ticker):
    """yfinance에서 미국 주식 재무 정보 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        data = {
            'PER': info.get('trailingPE'),
            'PBR': info.get('priceToBook'),
            'ROE': info.get('returnOnEquity'),
            'Dividend_Yield': info.get('dividendYield'), # 0.05 = 5%
            'Market_Cap': info.get('marketCap'),
            'Revenue_Growth': info.get('revenueGrowth')
        }
        
        # None 값 제거
        return {k: v for k, v in data.items() if v is not None}
        
    except Exception as e:
        # print(f"Error fetching fundamentals for US {ticker}: {e}")
        return {}

def main():
    print("📊 Collecting Fundamentals (KR & US)...")
    
    fundamentals = []
    
    # 1. 한국 주식
    if os.path.exists('korean_stocks_list.csv'):
        kr_stocks = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
        print(f"- Processing {len(kr_stocks)} Korean stocks...")
        
        for _, row in kr_stocks.iterrows():
            code = str(row['ticker']).zfill(6)
            name = row['name']
            
            data = get_naver_fundamentals(code)
            data['code'] = code
            data['name'] = name
            data['country'] = 'KR'
            
            fundamentals.append(data)
            time.sleep(0.1) # 서버 부하 방지
            
    # 2. 미국 주식
    if os.path.exists('us_stocks_list.csv'):
        us_stocks = pd.read_csv('us_stocks_list.csv')
        print(f"- Processing {len(us_stocks)} US stocks...")
        
        for _, row in us_stocks.iterrows():
            ticker = row['ticker']
            name = row['name']
            
            data = get_us_fundamentals(ticker)
            data['code'] = ticker
            data['name'] = name
            data['country'] = 'US'
            
            # 배당수익률 단위 통일 (네이버는 %, yfinance는 소수점)
            if 'Dividend_Yield' in data and data['Dividend_Yield']:
                data['Dividend_Yield'] = data['Dividend_Yield'] * 100
                
            fundamentals.append(data)
            
    # 저장
    if fundamentals:
        df = pd.DataFrame(fundamentals)
        df.to_csv('fundamentals.csv', index=False, encoding='utf-8')
        print(f"💾 Saved fundamentals for {len(df)} stocks to fundamentals.csv")
    else:
        print("No fundamental data collected.")

if __name__ == "__main__":
    main()
