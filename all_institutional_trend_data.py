import pandas as pd
import requests
import time
from tqdm import tqdm
import io

def get_investor_trend(code, pages=10):
    """
    네이버 금융에서 투자자별 매매동향(외국인/기관)을 가져옵니다.
    :param code: 종목코드
    :param pages: 가져올 페이지 수
    :return: DataFrame
    """
    url = f"https://finance.naver.com/item/frgn.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    df_list = []
    
    for page in range(1, pages + 1):
        pg_url = f'{url}&page={page}'
        try:
            response = requests.get(pg_url, headers=headers)
            tables = pd.read_html(io.StringIO(response.text))
            # 투자자별 매매동향 테이블은 보통 3번째(인덱스 2)에 위치함 (페이지 구조에 따라 확인 필요)
            # 네이버 금융 '투자자별 매매동향' 탭의 테이블 구조 확인 필요.
            # 보통 class='type2' 테이블이 여러개 있는데, 그 중 날짜, 종가, 등락률, 기관, 외국인 등이 있는 테이블을 찾아야 함.
            
            # 테이블 순회하며 적절한 컬럼을 가진 테이블 찾기
            target_df = None
            for table in tables:
                if '날짜' in table.columns and '기관' in table.columns and '외국인' in table.columns:
                    target_df = table
                    break
            
            if target_df is None and len(tables) > 1:
                 # fallback: 보통 두번째나 세번째 테이블
                 target_df = tables[1]

            if target_df is not None:
                # 날짜 컬럼 확인
                date_col = None
                for col in target_df.columns:
                    if '날짜' in str(col) or 'date' in str(col).lower():
                        date_col = col
                        break
                
                if date_col:
                    df = target_df.dropna(subset=[date_col])
                    # 날짜 컬럼 표준화
                    df = df.rename(columns={date_col: '날짜'})
                    df_list.append(df)
                else:
                    print(f"Date column not found in table for {code}. Columns: {target_df.columns}")
            else:
                 print(f"Target table not found for {code}")
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching investor data page {page} for code {code}: {e}")
            import traceback
            traceback.print_exc()
            break
            
    if not df_list:
        return None
        
    df = pd.concat(df_list, ignore_index=True)
    
    # 컬럼 정리 (네이버 금융 테이블 컬럼명에 따라 조정 필요)
    # 보통: 날짜, 종가, 전일비, 등락률, 거래량, 기관, 외국인, ...
    # 실제 컬럼명을 확인하고 rename 해야 함. 여기서는 일반적인 구조 가정.
    
    # 컬럼명에 멀티인덱스가 있을 수 있음. 단순화.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
        
    # 주요 컬럼만 선택 및 리네임 (실제 컬럼명 확인 후 수정 가능성 있음)
    # 여기서는 단순 매핑 시도
    rename_map = {
        '날짜': 'date',
        '기관': 'institution_net_buy',
        '외국인': 'foreigner_net_buy',
        '외국인_순매수': 'foreigner_net_buy', # 컬럼명이 다를 수 있음
        '기관_순매수': 'institution_net_buy'
    }
    
    # 실제 존재하는 컬럼만 매핑
    new_cols = {}
    for col in df.columns:
        for k, v in rename_map.items():
            if k in col:
                new_cols[col] = v
                break
                
    df = df.rename(columns=new_cols)
    
    # 필요한 컬럼이 없으면 생성 (0으로 채움)
    if 'institution_net_buy' not in df.columns:
        df['institution_net_buy'] = 0
    if 'foreigner_net_buy' not in df.columns:
        df['foreigner_net_buy'] = 0
        
    df = df[['date', 'institution_net_buy', 'foreigner_net_buy']]
    
    # 데이터 전처리
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['code'] = code
    
    return df

def main():
    print("Starting institutional trend data collection...")
    
    try:
        stocks = pd.read_csv('korean_stocks_list.csv', dtype={'ticker': str})
    except FileNotFoundError:
        print("Error: korean_stocks_list.csv not found.")
        return

    all_data = []
    
    for _, row in tqdm(stocks.iterrows(), total=len(stocks), desc="Collecting Investor Data"):
        code = row['ticker']
        
        # 최근 데이터 수집 (테스트를 위해 5페이지로 축소)
        df = get_investor_trend(code, pages=5)
        
        if df is not None:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('all_institutional_trend_data.csv', index=False)
        print(f"Successfully saved {len(final_df)} rows to all_institutional_trend_data.csv")
    else:
        print("No investor data collected.")

if __name__ == "__main__":
    main()
