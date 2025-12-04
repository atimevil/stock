#!/bin/bash
set -e

echo "🐳 StockAI Container Started"

# Check if data exists
if [ ! -f "daily_prices.csv" ]; then
    echo "📉 No data found. Running initial analysis..."
    python run_analysis.py
else
    echo "✅ Data found. Skipping initial analysis."
fi

echo "🚀 Starting Streamlit Dashboard..."
exec streamlit run dashboard/app.py --server.address=0.0.0.0
