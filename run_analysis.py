import os
import subprocess
import time

def run_script(script_name):
    print(f"\n{'='*50}")
    print(f"Running {script_name}...")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    try:
        # python3 대신 python 사용 (Windows 환경 고려)
        result = subprocess.run(['python', script_name], check=True)
        end_time = time.time()
        print(f"\nSuccessfully finished {script_name} in {end_time - start_time:.2f} seconds.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running {script_name}: {e}")
        return False
    except FileNotFoundError:
        # python 명령어가 없을 경우 python3 시도
        try:
            result = subprocess.run(['python3', script_name], check=True)
            end_time = time.time()
            print(f"\nSuccessfully finished {script_name} in {end_time - start_time:.2f} seconds.")
            return True
        except Exception as e:
            print(f"\nError running {script_name}: {e}")
            return False

def main():
    print("🚀 Starting StockAI Analysis Pipeline...")
    
    scripts = [
        'fetch_hot_stocks.py',
        'fetch_us_stocks.py',
        'create_complete_daily_prices.py',
        'collect_us_daily_prices.py',
        'all_institutional_trend_data.py',
        'collect_fundamentals.py',
        'analysis2.py',
        'investigate_top_stocks.py'
    ]
    
    for script in scripts:
        if not run_script(script):
            print(f"\n❌ Pipeline stopped due to error in {script}")
            return
            
    print("\n✨ All analysis steps completed successfully!")
    print("Run 'streamlit run dashboard/app.py' to view the results.")

if __name__ == "__main__":
    main()
