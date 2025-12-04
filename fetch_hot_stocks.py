import pandas as pd
import requests
import os

def get_top_volume_stocks(limit=10):
    """거래량 상위 종목 수집 (KOSPI + KOSDAQ)"""
    print("Fetching Top Volume Stocks...")
    stocks = []
    
    # 0: KOSPI, 1: KOSDAQ
    for market_code in [0, 1]:
        url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={market_code}"
        try:
            df = pd.read_html(url, encoding='euc-kr')[1]
            df = df.dropna(subset=['종목명'])
            
            # 상위 N개 추출
            top_n = df.head(limit)
            
            for _, row in top_n.iterrows():
                # 종목코드를 알기 위해선 링크 파싱이 필요하지만, read_html로는 어려움.
                # 대신 종목명으로 나중에 매핑하거나, requests로 직접 파싱해야 함.
                # 간단하게는 종목명만 저장하고 나중에 코드를 찾는 방식이 있지만,
                # 여기서는 정확성을 위해 requests + lxml or string parsing을 사용하는게 좋음.
                # 하지만 복잡도를 낮추기 위해 일단 종목명만 수집하고, 
                # 별도의 종목코드 매핑 로직(예: 전체 종목 리스트에서 찾기)을 사용하는 것이 일반적임.
                # 다행히 Naver Finance 테이블에는 종목코드가 텍스트로 안나옴.
                # 따라서 이 방법보다는 '전체 종목 코드'를 미리 가지고 있거나,
                # 페이지 소스를 긁어서 코드를 추출해야 함.
                pass
                
        except Exception as e:
            print(f"Error fetching volume stocks: {e}")
            
    # read_html 만으로는 종목코드를 가져오기 어려우므로, 
    # requests로 HTML을 가져와서 정규식으로 코드를 추출하는 방식을 사용하겠습니다.
    return []

def fetch_naver_stocks_with_code(url, limit=10):
    """URL에서 종목명과 코드를 함께 추출"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        html = response.text
        
        # pandas read_html로 테이블 구조 파악
        dfs = pd.read_html(html, encoding='euc-kr')
        
        # 대부분의 네이버 랭킹 페이지에서 메인 테이블은 인덱스 1 또는 2에 있음
        target_df = None
        for df in dfs:
            if '종목명' in df.columns:
                target_df = df
                break
        
        if target_df is None:
            return []
            
        target_df = target_df.dropna(subset=['종목명'])
        target_df = target_df.head(limit)
        
        # HTML에서 종목코드 추출 (정규식 사용)
        import re
        # <a href="/item/main.naver?code=005930" class="tltle">삼성전자</a> 패턴 찾기
        
        stocks = []
        for name in target_df['종목명']:
            # 종목명으로 링크 찾기
            # 주의: 종목명이 중복되거나 특수문자가 있을 수 있음.
            # 단순하게 HTML 전체에서 "code=\d+" 패턴을 순서대로 찾으면 테이블 순서와 일치할 가능성이 높음.
            pass
            
        # 더 확실한 방법: lxml 사용
        from lxml import html as lhtml
        tree = lhtml.fromstring(html)
        
        # 테이블의 행(tr)을 순회하며 종목명과 링크(코드) 추출
        # 네이버 금융 랭킹 페이지의 일반적인 구조: table.type_2 tr td a.tltle
        elements = tree.xpath('//table[contains(@class, "type_2")]//tr//td//a[contains(@class, "tltle") or contains(@class, "tit")]')
        
        count = 0
        for el in elements:
            if count >= limit:
                break
                
            name = el.text_content().strip()
            href = el.get('href') # /item/main.naver?code=005930
            
            match = re.search(r'code=(\d+)', href)
            if match:
                code = match.group(1)
                stocks.append({'code': code, 'name': name})
                count += 1
                
        return stocks
        
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []

def main():
    print("🚀 Fetching Hot & Growth Stocks (Short-term & Long-term)...")
    
    all_stocks = []
    
    # === Short-term (단기투자) ===
    print("\n[Short-term] Fetching Momentum Stocks...")
    # 1. 거래량 상위
    print("- Top Volume...")
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_quant.naver?sosok=0", 30))
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_quant.naver?sosok=1", 30))
    
    # 2. 상승률 상위
    print("- Top Risers...")
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_rise.naver?sosok=0", 20))
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_rise.naver?sosok=1", 20))
    
    # === Long-term (장기투자) ===
    print("\n[Long-term] Fetching Value & Stable Stocks...")
    # 3. 시가총액 상위 (우량주)
    print("- Top Market Cap...")
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_market_sum.naver?sosok=0", 50)) # KOSPI Top 50
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_market_sum.naver?sosok=1", 30))  # KOSDAQ Top 30
    
    # 4. 외국인/기관 순매수 상위 (스마트머니)
    print("- Smart Money (Foreigner/Institutional)...")
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_deal_rank.naver?investor_gubun=9000", 20))
    all_stocks.extend(fetch_naver_stocks_with_code("https://finance.naver.com/sise/sise_deal_rank.naver?investor_gubun=1000", 20))
    
    # 중복 제거
    unique_stocks = {}
    for s in all_stocks:
        unique_stocks[s['code']] = s['name']
        
    print(f"\n✨ Found {len(unique_stocks)} unique stocks.")
    
    # 기존 리스트 로드 (있다면)
    if os.path.exists('korean_stocks_list.csv'):
        try:
            existing_df = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
            for _, row in existing_df.iterrows():
                unique_stocks[str(row['ticker']).zfill(6)] = row['name']
        except Exception as e:
            print(f"Error reading existing list: {e}")

    # 저장
    with open('korean_stocks_list.csv', 'w', encoding='utf-8') as f:
        f.write("ticker,name\n")
        for code, name in unique_stocks.items():
            f.write(f"{code},{name}\n")
            
    print(f"💾 Updated korean_stocks_list.csv with {len(unique_stocks)} stocks.")

if __name__ == "__main__":
    main()
