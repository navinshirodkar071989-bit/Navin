import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Smart Stock App")

# Stock selection
stock = st.selectbox("Select Stock", [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS"
])

# Period selection
period = st.selectbox("Select Period", ["6mo", "1y", "2y"])

# Download data
df = yf.download(stock, period=period)

# Fix multi-index issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Check if data exists
if df.empty:
    st.error("No data found")
else:
    # Moving averages
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    st.subheader("📈 Trend Analysis")

    # Check enough data
    if df['MA200'].isna().all():
        st.warning("Not enough data for analysis")
    else:
        latest = df.iloc[-1]

        # Signal
        if latest['MA50'] > latest['MA200']:
            st.success("🟢 BUY Signal")
        else:
            st.error("🔴 SELL Signal")

        # Current price
        st.write("💰 Current Price:", round(latest['Close'], 2))

        # % Change
        change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
        st.write("📊 Change:", round(change, 2), "%")

        # Chart
        st.line_chart(df[['Close', 'MA50', 'MA200']])
