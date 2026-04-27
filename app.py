import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Smart Stock App")

stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])

df = yf.download(stock, period="1y")

# Check if data exists
if df.empty:
    st.error("No data found")
else:
    # Moving averages
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    # Drop NaN
    df = df.dropna()

    # Check again after cleaning
    if len(df) == 0:
        st.warning("Not enough data for analysis")
    else:
        ma50 = df['MA50'].iloc[-1]
        ma200 = df['MA200'].iloc[-1]

        if ma50 > ma200:
            st.success("🟢 BUY Signal")
        else:
            st.error("🔴 SELL Signal")

        st.line_chart(df[['Close','MA50','MA200']])
