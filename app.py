import streamlit as st
import yfinance as yf
st.title("📊 Stock App")
stock = st.selectbox("Select Stock", ["RELIANCE.NS","TCS.NS","INFY.NS"])
df = yf.download(stock, period="6mo")
st.line_chart(df['Close'])
