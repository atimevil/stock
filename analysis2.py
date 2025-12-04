import pandas as pd
import numpy as np
from tqdm import tqdm

class EnhancedWaveTransitionAnalyzerV3:
    def __init__(self):
        pass

    def load_data(self):
        try:
            self.prices_df = pd.read_csv('daily_prices.csv', dtype={'code': str})
            self.investor_df = pd.read_csv('all_institutional_trend_data.csv', dtype={'code': str})
            
            # 재무 데이터 로드 (Optional)
            try:
                self.fundamentals_df = pd.read_csv('fundamentals.csv', dtype={'code': str})
            except FileNotFoundError:
                self.fundamentals_df = pd.DataFrame()
            
            # 날짜 형식 변환
            self.prices_df['date'] = pd.to_datetime(self.prices_df['date'])
            self.investor_df['date'] = pd.to_datetime(self.investor_df['date'])
            
            # 데이터 병합
            self.merged_df = pd.merge(self.prices_df, self.investor_df, on=['date', 'code'], how='left')
            
            # 결측치 처리 (투자자 데이터가 없는 경우 0으로 채움)
            self.merged_df['institution_net_buy'] = self.merged_df['institution_net_buy'].fillna(0)
            self.merged_df['foreigner_net_buy'] = self.merged_df['foreigner_net_buy'].fillna(0)
            
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            return False
        return True

    def _calculate_technical_indicators(self, df):
        df = df.sort_values('date').copy()
        
        # 이동평균선
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        df['ma200'] = df['close'].rolling(window=200).mean()
        
        # 거래량 이동평균
        df['vol_ma20'] = df['volume'].rolling(window=20).mean()
        
        # RSI (14일)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 52주 최고/최저
        df['52w_high'] = df['close'].rolling(window=250, min_periods=1).max()
        df['52w_low'] = df['close'].rolling(window=250, min_periods=1).min()
        
        # 52주 위치 (0~1)
        df['52w_pos'] = (df['close'] - df['52w_low']) / (df['52w_high'] - df['52w_low'])
        
        # 수익률 (20일)
        df['return_20d'] = df['close'].pct_change(periods=20) * 100
        
        return df

    def analyze_stock(self, df, fundamentals=None):
        # 최근 데이터 기준 분석
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        score = 0
        wave_stage = "Unknown"
        
        # 기본 데이터 확인
        if pd.isna(latest['ma20']) or pd.isna(latest['ma50']):
            return 0, "Insufficient Data"

        # 1. 2단계 중기 (Strong Uptrend) - 90점
        # 정배열, 신고가 근처, 거래량 급증, RSI 적정
        if (latest['ma20'] > latest['ma50'] > latest['ma200']) and \
           (0.6 <= latest['52w_pos'] <= 0.9) and \
           (latest['volume'] > latest['vol_ma20'] * 1.3) and \
           (55 <= latest['rsi'] <= 75) and \
           (latest['return_20d'] >= 10):
            score = 90
            wave_stage = "Strong Uptrend"
            
        # 2. 2단계 초기 (Early Uptrend) - 80점
        # 골든크로스 이후, 20일선 지지
        elif (latest['ma20'] > latest['ma50']) and \
             (0.4 <= latest['52w_pos'] <= 0.75) and \
             (latest['close'] > latest['ma20']) and \
             (latest['volume'] > latest['vol_ma20'] * 1.2):
            score = 80
            wave_stage = "Early Uptrend"
            
        # 3. 1단계 -> 2단계 전환 (Transition) - 70점
        # 수렴/교차 직전, 바닥 탈출
        elif (abs(latest['ma20'] - latest['ma50']) / latest['ma50'] < 0.05) and \
             (0.25 <= latest['52w_pos'] <= 0.6) and \
             (45 <= latest['rsi'] <= 65):
            score = 70
            wave_stage = "Transition"
            
        # 4. 일반 상승 추세 (General Uptrend) - 60점
        elif (latest['ma20'] > latest['ma50']) and \
             (0.3 <= latest['52w_pos'] <= 0.7):
            score = 60
            wave_stage = "General Uptrend"
        else:
            score = 40
            wave_stage = "Weak/Downtrend"
            
        # 수급 가산점 (기관/외국인 순매수 지속 시)
        # 최근 5일간 순매수 합계가 양수이면 가산점
        recent_5d = df.tail(5)
        inst_sum = recent_5d['institution_net_buy'].sum()
        for_sum = recent_5d['foreigner_net_buy'].sum()
        
        if inst_sum > 0:
            score += 5
        if for_sum > 0:
            score += 5
            
        # 재무 가산점 (Fundamental Bonus)
        if fundamentals is not None and not fundamentals.empty:
            # PER < 15 (저평가)
            if pd.notna(fundamentals['PER']) and fundamentals['PER'] < 15 and fundamentals['PER'] > 0:
                score += 5
            # PBR < 1.0 (자산가치)
            if pd.notna(fundamentals['PBR']) and fundamentals['PBR'] < 1.0 and fundamentals['PBR'] > 0:
                score += 5
            # ROE > 10 (수익성)
            if pd.notna(fundamentals['ROE']) and fundamentals['ROE'] > 10:
                score += 5
            
        return score, wave_stage

    def run(self):
        if not self.load_data():
            return
            
        results = []
        
        # 종목별로 그룹화하여 분석
        grouped = self.merged_df.groupby('code')
        
        for code, group in tqdm(grouped, desc="Analyzing Stocks"):
            if len(group) < 50: # 데이터 부족 시 스킵 (기준 완화: 200 -> 50, 신규 상장주 등 고려)
                continue
                
            processed_df = self._calculate_technical_indicators(group)
            
            # 재무 데이터 찾기
            fund_data = None
            if not self.fundamentals_df.empty:
                fund_rows = self.fundamentals_df[self.fundamentals_df['code'] == code]
                if not fund_rows.empty:
                    fund_data = fund_rows.iloc[0]
            
            score, stage = self.analyze_stock(processed_df, fund_data)
            
            latest = processed_df.iloc[-1]
            
            results.append({
                'code': code,
                'name': latest['name'],
                'date': latest['date'],
                'close': latest['close'],
                'score': score,
                'wave_stage': stage,
                'rsi': latest['rsi'],
                '52w_pos': latest['52w_pos']
            })
            
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('score', ascending=False)
        results_df.to_csv('wave_transition_analysis_results.csv', index=False)
        print(f"Analysis complete. Saved {len(results_df)} results to wave_transition_analysis_results.csv")

if __name__ == "__main__":
    analyzer = EnhancedWaveTransitionAnalyzerV3()
    analyzer.run()
