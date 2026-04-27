import streamlit as st
import yfinance as yf
import pandas as pd
st.title("📊 Smart Stock App")
stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])
df = yf.download(stock, period="6mo")
# Moving averages
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()
# Remove NaN values
df = df.dropna()
# Check if data exists
if not df.empty:
    ma50 = df['MA50'].iloc[-1]
    ma200 = df['MA200'].iloc[-1]
    if ma50 > ma200:
        st.success("🟢 BUY Signal")
    else:
        st.error("🔴 SELL Signal")

    st.line_chart(df[['Close','MA50','MA200']])
else:
    st.warning("Not enough data")
