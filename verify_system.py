import os
import pandas as pd
import sys

# Add dashboard directory to path to import utils
sys.path.append(os.path.join(os.getcwd(), 'dashboard'))
from utils import load_analysis_results, load_daily_prices, load_ai_report

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > 0:
            print(f"✅ [PASS] {description} exists ({size} bytes).")
            return True
        else:
            print(f"❌ [FAIL] {description} exists but is empty.")
            return False
    else:
        print(f"❌ [FAIL] {description} not found at {filepath}.")
        return False

def verify_data_content():
    print("\n--- Verifying Data Content ---")
    
    # Check daily prices
    df_prices = load_daily_prices()
    if df_prices is not None and not df_prices.empty:
        print(f"✅ [PASS] Daily prices loaded: {len(df_prices)} rows.")
        print(f"   - Columns: {list(df_prices.columns)}")
        print(f"   - Date Range: {df_prices['date'].min()} to {df_prices['date'].max()}")
    else:
        print("❌ [FAIL] Failed to load daily prices.")

    # Check analysis results
    df_results = load_analysis_results()
    if df_results is not None and not df_results.empty:
        print(f"✅ [PASS] Analysis results loaded: {len(df_results)} rows.")
        print(f"   - Top 3 Scores:\n{df_results[['name', 'score', 'wave_stage']].head(3)}")
    else:
        print("❌ [FAIL] Failed to load analysis results.")

    # Check AI Report
    report = load_ai_report()
    if report and len(report) > 100:
        print(f"✅ [PASS] AI Report loaded ({len(report)} chars).")
        print(f"   - Preview: {report[:100]}...")
    else:
        print("❌ [FAIL] Failed to load AI report or report is too short.")

def main():
    print("🚀 Starting System Verification...\n")
    
    # 1. File Existence Checks
    files_to_check = [
        ('daily_prices.csv', 'Daily Prices Data'),
        ('all_institutional_trend_data.csv', 'Institutional Trend Data'),
        ('wave_transition_analysis_results.csv', 'Analysis Results'),
        ('korean_stocks_list.csv', 'Stock List'),
        ('us_stocks_list.csv', 'US Stock List'),
        ('fundamentals.csv', 'Fundamental Data'),
        ('.env', 'Environment Variables')
    ]
    
    all_files_exist = True
    for filename, desc in files_to_check:
        if not check_file_exists(filename, desc):
            all_files_exist = False
            
    if not all_files_exist:
        print("\n❌ Critical files are missing. Please run 'python run_analysis.py' first.")
        return

    # 2. Data Integrity Checks
    verify_data_content()
    
    print("\n✨ Verification Complete.")

if __name__ == "__main__":
    main()
