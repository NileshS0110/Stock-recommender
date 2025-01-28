import streamlit as st
import yfinance as yf
from ta import add_all_ta_features
from ta.utils import dropna

st.title("Stock Buy/Sell Recommender")

# Input: Stock Ticker
ticker = st.text_input("Enter NSE Stock Ticker (e.g., RELIANCE):", "RELIANCE")

if st.button("Get Recommendation"):
    # Fetch data
    stock = yf.Ticker(ticker + ".NS")
    data = stock.history(period="1y")
    
    # Clean data and rename columns to lowercase (required by `ta`)
    data = data.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    
    # Add technical indicators using `ta`
    data = dropna(data)  # Clean NaN values
    data = add_all_ta_features(
        data,
        open="open",
        high="high",
        low="low",
        close="close",
        volume="volume"
    )
    
    # Extract latest values
    latest_rsi = data["momentum_rsi"].iloc[-1]
    latest_close = data["close"].iloc[-1]
    sma_50 = data["trend_sma_50"].iloc[-1]
    sma_200 = data["trend_sma_200"].iloc[-1]

    # Generate recommendation
    recommendation = "HOLD"
    target_price = latest_close
    
    if latest_rsi < 30:
        recommendation = "BUY"
        target_price = latest_close * 1.1  # 10% target
    elif latest_rsi > 70:
        recommendation = "SELL"
        target_price = latest_close * 0.9  # 10% stop-loss

    # Display results
    st.write(f"**Stock:** {ticker}")
    st.write(f"**Latest Close Price:** ₹{latest_close:.2f}")
    st.write(f"**RSI:** {latest_rsi:.2f}")
    st.write(f"**SMA 50:** ₹{sma_50:.2f}")
    st.write(f"**SMA 200:** ₹{sma_200:.2f}")
    st.write(f"**Recommendation:** {recommendation}")
    st.write(f"**Target Price:** ₹{target_price:.2f}")
    
    # Plot closing price and RSI
    st.line_chart(data["close"])
    st.line_chart(data["momentum_rsi"])
