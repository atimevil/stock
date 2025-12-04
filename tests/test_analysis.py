import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import analysis2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis2 import EnhancedWaveTransitionAnalyzerV3

class TestWaveAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = EnhancedWaveTransitionAnalyzerV3()

    def create_mock_data(self, trend='uptrend'):
        dates = pd.date_range(start='2024-01-01', periods=250, freq='D')
        
        if trend == 'uptrend':
            # 상승 추세 데이터 생성
            close = np.linspace(10000, 20000, 250) # 2배 상승
            # 노이즈 추가
            close += np.random.normal(0, 100, 250)
        elif trend == 'downtrend':
            # 하락 추세 데이터 생성
            close = np.linspace(20000, 10000, 250)
            close += np.random.normal(0, 100, 250)
        else:
            # 횡보
            close = np.full(250, 10000)
            close += np.random.normal(0, 100, 250)
            
        df = pd.DataFrame({
            'date': dates,
            'close': close,
            'open': close, # 단순화
            'high': close * 1.01,
            'low': close * 0.99,
            'volume': np.random.randint(10000, 50000, 250),
            'institution_net_buy': np.random.randint(-1000, 1000, 250),
            'foreigner_net_buy': np.random.randint(-1000, 1000, 250),
            'name': 'TestStock',
            'code': '000000'
        })
        
        return df

    def test_technical_indicators(self):
        df = self.create_mock_data('uptrend')
        processed_df = self.analyzer._calculate_technical_indicators(df)
        
        # 필수 컬럼 생성 확인
        required_cols = ['ma20', 'ma50', 'ma200', 'rsi', '52w_high', '52w_low', '52w_pos']
        for col in required_cols:
            self.assertIn(col, processed_df.columns)
            
        # MA 계산 확인 (마지막 값)
        self.assertFalse(pd.isna(processed_df.iloc[-1]['ma20']))
        
    def test_strong_uptrend_logic(self):
        # 강한 상승 추세 조건 시뮬레이션
        df = self.create_mock_data('uptrend')
        processed_df = self.analyzer._calculate_technical_indicators(df)
        
        # 강제로 조건 만족시키기
        latest_idx = processed_df.index[-1]
        
        # 정배열
        processed_df.at[latest_idx, 'ma20'] = 15000
        processed_df.at[latest_idx, 'ma50'] = 14000
        processed_df.at[latest_idx, 'ma200'] = 12000
        
        # 신고가 근처
        processed_df.at[latest_idx, '52w_pos'] = 0.8
        
        # 거래량 급증
        processed_df.at[latest_idx, 'vol_ma20'] = 10000
        processed_df.at[latest_idx, 'volume'] = 15000 # 1.5배
        
        # RSI
        processed_df.at[latest_idx, 'rsi'] = 60
        
        # 수익률
        processed_df.at[latest_idx, 'return_20d'] = 15
        
        score, stage = self.analyzer.analyze_stock(processed_df)
        
        # 수급 점수 제외하고 기본 점수 확인 (90점)
        # 수급은 랜덤이라 점수가 더해질 수 있음. 최소 90점 이상이어야 함.
        self.assertGreaterEqual(score, 90)
        self.assertEqual(stage, "Strong Uptrend")

    def test_downtrend_logic(self):
        df = self.create_mock_data('downtrend')
        processed_df = self.analyzer._calculate_technical_indicators(df)
        
        # 하락 추세 조건 강제
        latest_idx = processed_df.index[-1]
        processed_df.at[latest_idx, 'ma20'] = 9000
        processed_df.at[latest_idx, 'ma50'] = 10000
        
        score, stage = self.analyzer.analyze_stock(processed_df)
        
        # 점수가 낮아야 함 (기본 40점 + 수급 보너스 최대 10점 = 50점 이하)
        self.assertLessEqual(score, 50)
        self.assertEqual(stage, "Weak/Downtrend")

if __name__ == '__main__':
    unittest.main()
