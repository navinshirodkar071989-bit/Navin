import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Smart Stock App")

# Select stock
stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])

# Select time
period = st.selectbox("Select Period", ["6mo", "1y", "2y"])

# Get data
df = yf.download(stock, period=period)

# Fix column issue
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# If no data
if df.empty:
    st.write("No data found")

else:
    # Moving average
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    # Check data
    if df['MA200'].isna().all():
        st.write("Not enough data for analysis")

    else:
        latest = df.iloc[-1]

        if latest['MA50'] > latest['MA200']:
            st.write("🟢 BUY Signal")
        else:
            st.write("🔴 SELL Signal")

        st.write("Price:", latest['Close'])

        st.line_chart(df[['Close','MA50','MA200']])
