import streamlit as st
import yfinance as yf
import pandas as pd
st.title("📊 Smart Stock App")
stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])
df = yf.download(stock, period="6mo")
# Moving Averages
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()
# Signal Logic
latest = df.iloc[-1]
if latest['MA50'] > latest['MA200']:
    st.success("🟢 BUY Signal")
else:
    st.error("🔴 SELL Signal")
# Show Chart
st.line_chart(df[['Close','MA50','MA200']])
