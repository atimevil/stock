import unittest
import pandas as pd
import os

class TestDataQuality(unittest.TestCase):
    def setUp(self):
        self.daily_prices_path = 'daily_prices.csv'
        self.investor_data_path = 'all_institutional_trend_data.csv'

    def test_daily_prices_quality(self):
        if not os.path.exists(self.daily_prices_path):
            self.skipTest("daily_prices.csv not found")
            
        df = pd.read_csv(self.daily_prices_path)
        
        # 1. Check for duplicates
        duplicates = df.duplicated(subset=['date', 'code'])
        self.assertEqual(duplicates.sum(), 0, f"Found {duplicates.sum()} duplicate rows in daily_prices")
        
        # 2. Check for missing values in critical columns
        self.assertEqual(df['close'].isnull().sum(), 0, "Found null values in 'close' column")
        self.assertEqual(df['date'].isnull().sum(), 0, "Found null values in 'date' column")
        
        # 3. Check data types
        self.assertTrue(pd.api.types.is_numeric_dtype(df['close']), "'close' column should be numeric")
        
        # 4. Check date sorting (within each code)
        df['date'] = pd.to_datetime(df['date'])
        for code, group in df.groupby('code'):
            self.assertTrue(group['date'].is_monotonic_increasing, f"Dates are not sorted for code {code}")

    def test_investor_data_quality(self):
        if not os.path.exists(self.investor_data_path):
            self.skipTest("all_institutional_trend_data.csv not found")
            
        df = pd.read_csv(self.investor_data_path)
        
        # 1. Check for duplicates
        duplicates = df.duplicated(subset=['date', 'code'])
        self.assertEqual(duplicates.sum(), 0, f"Found {duplicates.sum()} duplicate rows in investor data")
        
        # 2. Check for missing values
        # Note: It's possible to have missing values if data collection failed for some days, 
        # but we should at least check critical columns if they exist
        if 'institution_net_buy' in df.columns:
            self.assertTrue(pd.api.types.is_numeric_dtype(df['institution_net_buy']))
            
        # 3. Check date format
        df['date'] = pd.to_datetime(df['date'])
        self.assertFalse(df['date'].isnull().any(), "Found invalid dates in investor data")

if __name__ == '__main__':
    unittest.main()
