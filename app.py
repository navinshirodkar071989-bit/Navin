import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Smart Stock App")

stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])

period = st.selectbox("Select Period", ["6mo", "1y", "2y"])

df = yf.download(stock, period=period)

# Fix column issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Moving averages
df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()

# Avoid empty data error
if df['MA200'].isna().all():
    st.warning("Not enough data for analysis")
else:
    latest = df.iloc[-1]

    if latest['MA50'] > latest['MA200']:
        st.success("🟢 BUY Signal")
    else:
        st.error("🔴 SELL Signal")

    st.line_chart(df[['Close','MA50','MA200']])
