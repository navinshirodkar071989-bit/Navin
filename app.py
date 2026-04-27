import streamlit as st
import yfinance as yf
import pandas as pd

# Title
st.title("📊 Smart Stock App")
st.subheader("📈 Live Stock Analysis")

# Stock selection
stock = st.selectbox("Select Stock", [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS"
])

# Time selection
period = st.selectbox("Select Period", ["6mo", "1y", "2y"])

# Download data
df = yf.download(stock, period=period)

# Fix column issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Check if data exists
if df.empty:
    st.write("No data found")

else:
    # Moving averages
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    # Check enough data
    if df['MA200'].isna().all():
        st.write("Not enough data for analysis")

    else:
        latest = df.iloc[-1]

        # BUY/SELL signal
        if latest['MA50'] > latest['MA200']:
            st.success("🟢 BUY Signal")
        else:
            st.error("🔴 SELL Signal")

        # Price box
        st.metric("💰 Current Price", round(latest['Close'], 2))

        # Chart
        st.line_chart(df[['Close','MA50','MA200']])
