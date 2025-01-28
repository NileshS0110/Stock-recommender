import streamlit as st
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

st.title("Stock Buy/Sell Recommender")

# Input: Stock Ticker
ticker = st.text_input("Enter NSE Stock Ticker (e.g., RELIANCE):", "RELIANCE")

if st.button("Get Recommendation"):
    # Fetch data
    stock = yf.Ticker(ticker + ".NS")
    data = stock.history(period="2y")  # Fetch 2 years of data for SMA stability
    
    if data.empty:
        st.error("No data found for this ticker. Please try another.")
    else:
        # Clean data and rename columns to lowercase (required by `ta`)
        data = data.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        
        # Calculate RSI
        rsi_indicator = RSIIndicator(data["close"], window=14)
        data["rsi"] = rsi_indicator.rsi()
        
        # Calculate SMAs
        sma_50 = SMAIndicator(data["close"], window=50)
        sma_200 = SMAIndicator(data["close"], window=200)
        data["sma_50"] = sma_50.sma_indicator()
        data["sma_200"] = sma_200.sma_indicator()
        
        # Drop NaN values (from SMA calculations)
        data = data.dropna()
        
        # Extract latest values
        latest_rsi = data["rsi"].iloc[-1]
        latest_close = data["close"].iloc[-1]
        latest_sma_50 = data["sma_50"].iloc[-1]
        latest_sma_200 = data["sma_200"].iloc[-1]
        
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
        st.write(f"**SMA 50:** ₹{latest_sma_50:.2f}")
        st.write(f"**SMA 200:** ₹{latest_sma_200:.2f}")
        st.write(f"**Recommendation:** {recommendation}")
        st.write(f"**Target Price:** ₹{target_price:.2f}")
        
        # Plot closing price and RSI
        st.line_chart(data["close"])
        st.line_chart(data["rsi"])
