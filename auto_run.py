import time
import subprocess
import datetime
import sys
import os

def run_pipeline():
    print(f"\n[AutoRun] Starting analysis pipeline at {datetime.datetime.now()}...")
    try:
        # 현재 디렉토리에서 run_analysis.py 실행
        result = subprocess.run([sys.executable, 'run_analysis.py'], check=True)
        print(f"[AutoRun] Analysis completed successfully at {datetime.datetime.now()}")
    except subprocess.CalledProcessError as e:
        print(f"[AutoRun] Error running analysis: {e}")
    except Exception as e:
        print(f"[AutoRun] Unexpected error: {e}")

def main():
    # 목표 실행 시간 리스트 (시, 분)
    # 1. 08:30 : 장 시작 전 (미국장 마감 반영 + 한국장 준비)
    # 2. 18:30 : 장 마감 후 (한국장 마감 데이터 분석)
    SCHEDULES = [(8, 30), (18, 30)]
    
    print(f"🕒 StockAI Auto-Scheduler started.")
    print(f"🚀 Analysis scheduled at: {[f'{h:02d}:{m:02d}' for h, m in SCHEDULES]}")
    
    while True:
        now = datetime.datetime.now()
        candidates = []
        
        # 각 스케줄에 대해 다음 실행 시간 계산
        for hour, minute in SCHEDULES:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if now >= target:
                target += datetime.timedelta(days=1)
            candidates.append(target)
            
        # 가장 가까운 다음 실행 시간 선택
        next_run = min(candidates)
        
        wait_seconds = (next_run - now).total_seconds()
        
        print(f"💤 Waiting for next run in {wait_seconds/3600:.1f} hours ({next_run})")
        
        # 대기 (CPU 사용 최소화)
        time.sleep(wait_seconds)
        
        # 실행
        run_pipeline()
        
        # 중복 실행 방지를 위해 잠시 대기
        time.sleep(60)

if __name__ == "__main__":
    main()
