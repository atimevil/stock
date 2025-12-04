import pandas as pd
import os

def load_analysis_results():
    """분석 결과 데이터를 로드합니다."""
    try:
        # 대시보드 디렉토리에서 실행될 경우를 대비해 상위 디렉토리 경로 확인
        path = 'wave_transition_analysis_results.csv'
        if not os.path.exists(path):
            path = '../wave_transition_analysis_results.csv'
            
        if os.path.exists(path):
            df = pd.read_csv(path, dtype={'code': str})
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            return None
    except Exception as e:
        print(f"Error loading analysis results: {e}")
        return None

def load_daily_prices():
    """일별 시세 데이터를 로드합니다."""
    try:
        path = 'daily_prices.csv'
        if not os.path.exists(path):
            path = '../daily_prices.csv'
            
        if os.path.exists(path):
            df = pd.read_csv(path, dtype={'code': str})
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            return None
    except Exception as e:
        print(f"Error loading daily prices: {e}")
        return None

def load_ai_report():
    """가장 최근의 AI 분석 리포트를 로드합니다."""
    try:
        # 현재 디렉토리 또는 상위 디렉토리에서 md 파일 검색
        search_dirs = ['.', '..']
        
        latest_file = None
        latest_time = 0
        
        for d in search_dirs:
            if not os.path.exists(d):
                continue
                
            for f in os.listdir(d):
                if f.startswith('ai_analysis_report_') and f.endswith('.md'):
                    full_path = os.path.join(d, f)
                    mtime = os.path.getmtime(full_path)
                    if mtime > latest_time:
                        latest_time = mtime
                        latest_file = full_path
                        
        if latest_file:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        print(f"Error loading AI report: {e}")
        return None
