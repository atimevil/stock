import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import load_analysis_results, load_daily_prices, load_ai_report

st.set_page_config(page_title="StockAI Dashboard", layout="wide", page_icon="🥝")

def main():
    st.title("🥝 StockAI: Intelligent Korean Stock Analysis System")
    st.markdown("""
    **StockAI**는 기술적 분석(파동 이론), 수급 분석, 그리고 Generative AI를 결합하여 최적의 투자 기회를 발굴합니다.
    """)
    
    # 데이터 로드
    results_df = load_analysis_results()
    prices_df = load_daily_prices()
    ai_report = load_ai_report()
    
    if results_df is None:
        st.error("분석 결과 파일(wave_transition_analysis_results.csv)을 찾을 수 없습니다. 먼저 분석을 실행해주세요.")
        return

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "📈 Chart Analysis", "💎 Oversold (Value)", "🤖 AI Report"])
    
    # 국가 구분 헬퍼 함수
    def get_country(code):
        return 'KR' if str(code).isdigit() else 'US'

    results_df['country'] = results_df['code'].apply(get_country)

    with tab1:
        st.header("Today's Top Picks")
        
        # 점수별 필터링
        min_score = st.slider("Minimum Score", 0, 100, 30)
        
        # 서브탭으로 국가 구분
        subtab_kr, subtab_us = st.tabs(["🇰🇷 Domestic (Korea)", "🇺🇸 Overseas (USA)"])
        
        with subtab_kr:
            kr_df = results_df[(results_df['country'] == 'KR') & (results_df['score'] >= min_score)]
            st.dataframe(
                kr_df[['code', 'name', 'score', 'wave_stage', 'close', 'rsi', '52w_pos']],
                use_container_width=True,
                column_config={
                    "score": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=100),
                    "52w_pos": st.column_config.ProgressColumn("52W Position", format="%.2f", min_value=0, max_value=1),
                }
            )
            
        with subtab_us:
            us_df = results_df[(results_df['country'] == 'US') & (results_df['score'] >= min_score)]
            st.dataframe(
                us_df[['code', 'name', 'score', 'wave_stage', 'close', 'rsi', '52w_pos']],
                use_container_width=True,
                column_config={
                    "score": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=100),
                    "52w_pos": st.column_config.ProgressColumn("52W Position", format="%.2f", min_value=0, max_value=1),
                }
            )
        
        st.subheader("Wave Stage Distribution")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Korea")
            st.bar_chart(results_df[results_df['country']=='KR']['wave_stage'].value_counts())
        with col2:
            st.caption("USA")
            st.bar_chart(results_df[results_df['country']=='US']['wave_stage'].value_counts())

    with tab2:
        st.header("Detailed Chart Analysis")
        
        if prices_df is not None:
            # 국가 필터
            market_filter = st.radio("Select Market", ["All", "Korea", "USA"], horizontal=True)
            
            filtered_names = results_df['name'].unique()
            if market_filter == "Korea":
                filtered_names = results_df[results_df['country'] == 'KR']['name'].unique()
            elif market_filter == "USA":
                filtered_names = results_df[results_df['country'] == 'US']['name'].unique()
            
            # 종목 선택
            selected_stock = st.selectbox("Select Stock", filtered_names)
            
            if selected_stock:
                stock_info = results_df[results_df['name'] == selected_stock].iloc[0]
                code = stock_info['code']
                
                # 해당 종목 데이터 필터링
                code_str = str(code)
                if code_str.isdigit():
                    code_str = code_str.zfill(6)
                    
                stock_data = prices_df[prices_df['code'] == code_str].copy()
                
                if not stock_data.empty:
                    # 캔들스틱 차트 생성
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, subplot_titles=('Price', 'Volume'), 
                                        row_width=[0.2, 0.7])

                    # Candlestick
                    fig.add_trace(go.Candlestick(x=stock_data['date'],
                                    open=stock_data['open'],
                                    high=stock_data['high'],
                                    low=stock_data['low'],
                                    close=stock_data['close'],
                                    name='OHLC'), row=1, col=1)
                    
                    # MA Lines
                    stock_data['ma20'] = stock_data['close'].rolling(window=20).mean()
                    stock_data['ma50'] = stock_data['close'].rolling(window=50).mean()
                    
                    fig.add_trace(go.Scatter(x=stock_data['date'], y=stock_data['ma20'], line=dict(color='orange', width=1), name='MA20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=stock_data['date'], y=stock_data['ma50'], line=dict(color='green', width=1), name='MA50'), row=1, col=1)

                    # Volume
                    colors = ['red' if row['open'] - row['close'] >= 0 else 'green' for index, row in stock_data.iterrows()]
                    fig.add_trace(go.Bar(x=stock_data['date'], y=stock_data['volume'], marker_color=colors, name='Volume'), row=2, col=1)

                    fig.update_layout(title=f"{selected_stock} ({code})", xaxis_rangeslider_visible=False, height=600)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 상세 정보 표시
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Score", f"{stock_info['score']}")
                    col2.metric("Wave Stage", stock_info['wave_stage'])
                    col3.metric("RSI", f"{stock_info['rsi']:.1f}")
                    currency = "KRW" if stock_info['country'] == 'KR' else "USD"
                    col4.metric("Close", f"{stock_info['close']:,} {currency}")
                    
                else:
                    st.warning("No price data available for this stock.")
        else:
            st.error("Price data not loaded.")

    with tab3:
        st.header("💎 Hidden Gems (Oversold)")
        st.markdown("""
        **"공포에 사서 환희에 팔아라"** 
        현재 주가는 하락세(낮은 점수)지만, 과매도 구간(RSI < 40)에 진입하여 반등 가능성이 있는 종목들입니다.
        장기 투자를 고려한다면 저점 매수의 기회가 될 수 있습니다.
        """)
        
        # 과매도 필터링 (RSI < 40)
        oversold_df = results_df[results_df['rsi'] < 40].sort_values('rsi')
        
        # 서브탭으로 국가 구분
        subtab_kr, subtab_us = st.tabs(["🇰🇷 Domestic (Korea)", "🇺🇸 Overseas (USA)"])
        
        with subtab_kr:
            kr_oversold = oversold_df[oversold_df['country'] == 'KR']
            if not kr_oversold.empty:
                st.dataframe(
                    kr_oversold[['code', 'name', 'close', 'rsi', 'score', 'wave_stage']],
                    use_container_width=True,
                    column_config={
                        "rsi": st.column_config.NumberColumn("RSI", format="%.1f"),
                        "score": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=100),
                    }
                )
            else:
                st.info("국내 주식 중 과매도 종목이 없습니다.")

        with subtab_us:
            us_oversold = oversold_df[oversold_df['country'] == 'US']
            if not us_oversold.empty:
                st.dataframe(
                    us_oversold[['code', 'name', 'close', 'rsi', 'score', 'wave_stage']],
                    use_container_width=True,
                    column_config={
                        "rsi": st.column_config.NumberColumn("RSI", format="%.1f"),
                        "score": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=100),
                    }
                )
            else:
                st.info("미국 주식 중 과매도 종목이 없습니다.")

    with tab4:
        st.header("🤖 AI Analyst Report")
        if ai_report:
            st.markdown(ai_report)
        else:
            st.info("No AI report available yet. Run the analysis pipeline to generate one.")

if __name__ == "__main__":
    main()
