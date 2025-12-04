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
    당신은 전문 주식 애널리스트입니다. 아래 제공된 '{stock_name}' 관련 최신 뉴스를 바탕으로 투자 분석 보고서를 작성해주세요.

    [뉴스 데이터]
    {news_text}

    [분석 요구사항]
    1. **핵심 이슈 요약**: 뉴스에서 언급된 가장 중요한 호재와 악재를 요약하세요.
    2. **시장 반응 예측**: 이 뉴스가 주가에 긍정적일지, 부정적일지 예측하고 그 이유를 설명하세요.
    3. **투자 의견**: 매수(Buy), 보유(Hold), 매도(Sell) 중 하나의 의견을 제시하고 근거를 대세요.
    4. **리스크 요인**: 투자자가 주의해야 할 잠재적 리스크를 언급하세요.

    보고서는 Markdown 형식으로 깔끔하게 작성해주세요.
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

    # 상위 3개 종목만 분석 (API 비용 및 시간 고려)
    top_stocks = results_df.head(3)
    
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
