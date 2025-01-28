import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

st.title("Smart Stock Advisor (Indian Markets)")

# Inputs
ticker = st.text_input("Enter NSE Stock Ticker (e.g., RELIANCE):", "RELIANCE").upper()
capital = st.number_input("Enter Capital to Risk (₹):", min_value=1000, value=100000)

if st.button("Generate Expert Recommendation"):
    try:
        # Fetch 2 years of data for robust calculations
        stock = yf.Ticker(ticker + ".NS")
        data = stock.history(period="2y")
        
        if data.empty:
            st.error("No data found. Check the ticker symbol!")
        else:
            # Clean and prepare data
            data = data.rename(columns={
                "Open": "open", "High": "high", "Low": "low", 
                "Close": "close", "Volume": "volume"
            })
            
            # Calculate Indicators
            # 1. Trend: 50 vs 200 SMA Crossover
            sma_50 = SMAIndicator(data["close"], window=50).sma_indicator()
            sma_200 = SMAIndicator(data["close"], window=200).sma_indicator()
            
            # 2. Momentum: RSI + MACD
            rsi = RSIIndicator(data["close"], window=14).rsi()
            macd = MACD(data["close"]).macd_diff()
            
            # 3. Volatility: ATR for Stop-Loss
            atr = AverageTrueRange(data["high"], data["low"], data["close"], window=14).average_true_range()
            
            # 4. Volume: VWAP + Volume Spike (50% above 30-day avg)
            vwap = VolumeWeightedAveragePrice(
                data["high"], data["low"], data["close"], data["volume"]
            ).volume_weighted_average_price()
            avg_volume = data["volume"].rolling(30).mean()
            volume_spike = (data["volume"].iloc[-1] > 1.5 * avg_volume.iloc[-1])
            
            # 5. Support/Resistance: Recent 20-day low as stop-loss
            recent_low = data["low"].rolling(20).min().iloc[-1]
            
            # Latest Values
            latest_close = data["close"].iloc[-1]
            latest_rsi = rsi.iloc[-1]
            latest_macd = macd.iloc[-1]
            latest_atr = atr.iloc[-1]
            
            # Generate Signals
            signals = []
            
            # Buy Signal: RSI < 35 + SMA50 > SMA200 + MACD bullish
            if (latest_rsi < 35) and (sma_50.iloc[-1] > sma_200.iloc[-1]) and (latest_macd > 0):
                signals.append("BUY")
                stop_loss = max(recent_low, latest_close - 1.5 * latest_atr)
                target_price = latest_close * 1.15  # 15% target
            # Sell Signal: RSI > 65 + SMA50 < SMA200 + MACD bearish
            elif (latest_rsi > 65) and (sma_50.iloc[-1] < sma_200.iloc[-1]) and (latest_macd < 0):
                signals.append("SELL")
                stop_loss = latest_close + 1.5 * latest_atr
                target_price = latest_close * 0.85  # 15% downside
            else:
                signals.append("HOLD")
                stop_loss = None
                target_price = latest_close
            
            # Position Sizing (1% Risk Rule)
            if stop_loss:
                risk_per_share = abs(latest_close - stop_loss)
                position_size = (0.01 * capital) / risk_per_share
                position_size = int(position_size)
            else:
                position_size = 0
            
            # Display Expert Advice
            st.subheader(f"Expert Analysis for {ticker}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Price", f"₹{latest_close:.2f}")
                st.metric("RSI (14)", f"{latest_rsi:.1f}", 
                          help="Oversold (<30) / Overbought (>70)")
                st.metric("SMA 50/200", f"₹{sma_50.iloc[-1]:.1f} / ₹{sma_200.iloc[-1]:.1f}",
                          help="Golden Cross (50>200) = Bullish")
            with col2:
                st.metric("MACD", f"{latest_macd:.2f}", 
                          help="Bullish if >0, Bearish if <0")
                st.metric("Volume Spike", "🔥 Detected" if volume_spike else "🚫 None",
                          help="Volume > 150% of 30-day average")
                st.metric("VWAP", f"₹{vwap.iloc[-1]:.2f}",
                          help="Price above VWAP = Bullish")
            
            st.divider()
            
            # Recommendation
            st.subheader("Recommendation")
            st.write(f"**Action:** {signals[0]}")
            if signals[0] in ["BUY", "SELL"]:
                st.write(f"**Target Price:** ₹{target_price:.2f}")
                st.write(f"**Stop-Loss:** ₹{stop_loss:.2f}")
                st.write(f"**Position Size:** {position_size} shares (1% risk rule)")
            
            # Market Health Check
            nifty = yf.Ticker("^NSEI").history(period="1mo")["Close"].iloc[-1]
            if nifty > 50:
                st.success("✅ Market Trend: Bullish (Nifty 50 Rising)")
            else:
                st.warning("⚠️ Market Trend: Bearish (Avoid New Trades)")

    except Exception as e:
        st.error(f"Error: {str(e)}")
