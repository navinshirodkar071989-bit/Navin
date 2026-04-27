import streamlit as st
import yfinance as yf
import pandas as pd
st.set_page_config(page_title="AI Stock App", layout="wide")
st.title("📊 Indian Stock Viewer")
# Stock list
stocks = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS"
}
# Dropdown
stock_name = st.selectbox("Select Stock", list(stocks.keys()))
symbol = stocks[stock_name]
# Date range
period = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y"])
# Fetch data
df = yf.download(symbol, period=period)
# Check if data exists
if df.empty:
    st.error("No data found. Try another stock.")
else:
    # Show price
    st.subheader(f"📈 {stock_name} Price Chart")
    st.line_chart(df['Close'])
    # Show table
    st.subheader("📊 Data")
    st.dataframe(df.tail())
    # Simple signal
    latest_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    if latest_price > prev_price:
        st.success("📢 Signal: UP (Bullish)")
    else:
        st.error("📢 Signal: DOWN (Bearish)")
