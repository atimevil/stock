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
    # 목표 실행 시간 설정 (예: 오후 6시 30분 - 장 마감 및 데이터 업데이트 후)
    TARGET_HOUR = 18
    TARGET_MINUTE = 30
    
    print(f"🕒 StockAI Auto-Scheduler started.")
    print(f"🚀 Analysis will run daily at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    
    while True:
        now = datetime.datetime.now()
        
        # 다음 실행 시간 계산
        target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
        
        # 이미 지난 경우 내일로 설정
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
            
        wait_seconds = (target_time - now).total_seconds()
        
        print(f"💤 Waiting for next run in {wait_seconds/3600:.1f} hours ({target_time})")
        
        # 대기 (CPU 사용 최소화)
        time.sleep(wait_seconds)
        
        # 실행
        run_pipeline()
        
        # 중복 실행 방지를 위해 잠시 대기
        time.sleep(60)

if __name__ == "__main__":
    main()
