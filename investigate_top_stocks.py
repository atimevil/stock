import pandas as pd
import os
import google.generativeai as genai
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from datetime import datetime

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env file.")

# Gemini 설정
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

def search_news(query, max_results=5):
    """DuckDuckGo를 사용하여 뉴스 검색"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region="kr-kr", safesearch="off", max_results=max_results))
        return results
    except Exception as e:
        print(f"Error searching news for {query}: {e}")
        return []

def analyze_stock_with_gemini(stock_name, news_list):
    """Gemini를 사용하여 뉴스 분석 및 리포트 생성"""
    if not model:
        return "Gemini API Key is missing or invalid."

    news_text = ""
    for i, news in enumerate(news_list):
        news_text += f"{i+1}. {news['title']} ({news['date']})\n   {news['body']}\n   Link: {news['url']}\n\n"

    prompt = f"""
    당신은 월스트리트의 수석 애널리스트입니다. '{stock_name}'에 대한 최신 뉴스를 분석하여 전문적인 투자 리포트를 작성해주세요.

    [뉴스 데이터]
    {news_text}

    [작성 가이드]
    - **가독성**: 불렛 포인트와 표를 적극 활용하여 깔끔하게 작성하세요.
    - **전문성**: 금융 전문 용어를 적절히 사용하되, 일반 투자자도 이해하기 쉽게 설명하세요.
    - **객관성**: 뉴스에 기반한 사실과 당신의 분석 의견을 명확히 구분하세요.

    [리포트 포맷]
    다음 Markdown 형식을 엄격히 준수하여 작성해주세요:

    ### 📊 3줄 요약
    *   (핵심 내용 1)
    *   (핵심 내용 2)
    *   (핵심 내용 3)

    ### 📰 주요 이슈 분석
    *   **호재**: (상승 요인 상세 설명)
    *   **악재**: (하락 요인 상세 설명)

    ### 🧭 시장 예측 및 전략
    | 구분 | 내용 |
    |---|---|
    | **단기 전망** | (상승/하락/보합 예측 및 이유) |
    | **장기 전망** | (기업 펀더멘털 기반 예측) |
    | **투자 의견** | **매수(Buy) / 보유(Hold) / 매도(Sell)** |
    | **목표가** | (현 상황을 고려한 대략적인 목표 구간 제시, 없으면 생략) |

    ### ⚠️ 리스크 요인
    *   (주의해야 할 잠재적 위험 요소)
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"

def main():
    print("Starting AI News Analysis...")
    
    try:
        results_df = pd.read_csv('wave_transition_analysis_results.csv')
    except FileNotFoundError:
        print("Error: wave_transition_analysis_results.csv not found.")
        return

    # 국가 구분
    def get_country(code):
        return 'KR' if str(code).isdigit() else 'US'
    
    results_df['country'] = results_df['code'].apply(get_country)
    
    # 분석할 종목 수 설정
    TOP_N = 5
    
    # 한국/미국 각각 상위 종목 선정
    kr_stocks = results_df[results_df['country'] == 'KR'].head(TOP_N)
    us_stocks = results_df[results_df['country'] == 'US'].head(TOP_N)
    
    top_stocks = pd.concat([kr_stocks, us_stocks])
    
    print(f"Selected {len(top_stocks)} stocks for AI analysis (KR: {len(kr_stocks)}, US: {len(us_stocks)})")
    
    report_filename = f"ai_analysis_report_{datetime.now().strftime('%Y%m%d')}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(f"# 🤖 StockAI Daily Analysis Report ({datetime.now().strftime('%Y-%m-%d')})\n\n")
        
        for _, row in top_stocks.iterrows():
            stock_name = row['name']
            code = row['code']
            score = row['score']
            
            print(f"Analyzing {stock_name} ({code})...")
            
            f.write(f"## 📈 {stock_name} (Code: {code}) - Score: {score}\n\n")
            
            # 뉴스 검색
            news = search_news(f"{stock_name} 주식 뉴스")
            
            if not news:
                f.write("최신 뉴스를 찾을 수 없습니다.\n\n")
                continue
                
            # AI 분석
            analysis = analyze_stock_with_gemini(stock_name, news)
            f.write(analysis + "\n\n")
            f.write("---\n\n")
            
    print(f"Analysis complete. Report saved to {report_filename}")

if __name__ == "__main__":
    main()
