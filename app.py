import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.title("Stock Buy/Sell Recommender")

# Input: Stock Ticker
ticker = st.text_input("Enter NSE Stock Ticker (e.g., RELIANCE):", "RELIANCE")

if st.button("Get Recommendation"):
    # Fetch and analyze data
    stock = yf.Ticker(ticker + ".NS")
    data = stock.history(period="1y")
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['SMA_50'] = ta.sma(data['Close'], length=50)
    data['SMA_200'] = ta.sma(data['Close'], length=200)

    # Generate recommendation
    latest_rsi = data['RSI'].iloc[-1]
    latest_close = data['Close'].iloc[-1]

    if latest_rsi < 30:
        recommendation = "BUY"
        target_price = latest_close * 1.1  # 10% target price
    elif latest_rsi > 70:
        recommendation = "SELL"
        target_price = latest_close * 0.9  # 10% stop-loss
    else:
        recommendation = "HOLD"
        target_price = latest_close

    # Display results
    st.write(f"**Stock:** {ticker}")
    st.write(f"**Latest Close Price:** ₹{latest_close:.2f}")
    st.write(f"**Recommendation:** {recommendation}")
    st.write(f"**Target Price:** ₹{target_price:.2f}")

    # Plot closing price and RSI
    st.line_chart(data['Close'])
    st.line_chart(data['RSI'])
