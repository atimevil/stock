import pandas as pd

def check_us_scores():
    try:
        df = pd.read_csv('wave_transition_analysis_results.csv', dtype={'code': str})
        
        # Identify US stocks (non-numeric code)
        us_stocks = df[~df['code'].str.isdigit()]
        
        print(f"Total US Stocks in Results: {len(us_stocks)}")
        
        if not us_stocks.empty:
            print("\n--- US Stock Scores ---")
            print(us_stocks[['code', 'name', 'score', 'wave_stage']].sort_values('score', ascending=False))
            
            print("\n--- Summary ---")
            print(us_stocks['score'].describe())
        else:
            print("No US stocks found in results.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_us_scores()
