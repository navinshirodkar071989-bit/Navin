import streamlit as st
import yfinance as yf
import pandas as pd
st.title("📊 Smart Stock App")
stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])
df = yf.download(stock, period="6mo")
# Moving averages
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()
# Drop NaN rows (IMPORTANT)
df = df.dropna()
# Take last row properly
latest = df.iloc[-1]
# Convert to float (FIX)
ma50 = float(latest['MA50'])
ma200 = float(latest['MA200'])
# Signal
if ma50 > ma200:
    st.success("🟢 BUY Signal")
else:
    st.error("🔴 SELL Signal")

# Chart
st.line_chart(df[['Close','MA50','MA200']])
