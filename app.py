import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("🚀 NIFTY 50 AUTO STOCK FINDER")

# 🔄 Auto refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")
st.write("⏱ Auto-refresh every 5 minutes")

# ✅ Fixed NIFTY 50 list (no error)
def load_nifty():
    return [
        "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
        "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
        "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
        "TITAN.NS","ULTRACEMCO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","HCLTECH.NS",
        "WIPRO.NS","TECHM.NS","NESTLEIND.NS","POWERGRID.NS","NTPC.NS",
        "ONGC.NS","JSWSTEEL.NS","TATASTEEL.NS","INDUSINDBK.NS","ADANIENT.NS",
        "ADANIPORTS.NS","GRASIM.NS","DRREDDY.NS","CIPLA.NS","COALINDIA.NS",
        "BRITANNIA.NS","EICHERMOT.NS","HEROMOTOCO.NS","SHREECEM.NS","BPCL.NS",
        "DIVISLAB.NS","APOLLOHOSP.NS","HDFCLIFE.NS","SBILIFE.NS","ICICIPRULI.NS",
        "BAJAJ-AUTO.NS","TATACONSUM.NS","UPL.NS","M&M.NS","TATAMOTORS.NS"
    ]

stocks = load_nifty()

period = "1y"
results = []

# 🔍 Scan all stocks
for stock in stocks:
    try:
        df = yf.download(stock, period=period, progress=False)

        if len(df) < 200:
            continue

        # Indicators
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df = df.dropna()
        if df.empty:
            continue

        latest = df.iloc[-1]

        signal = "HOLD"

        # 📊 Signal logic
        if latest['MA50'] > latest['MA200'] and latest['RSI'] < 60:
            signal = "BUY"
        elif latest['MA50'] < latest['MA200'] and latest['RSI'] > 40:
            signal = "SELL"

        score = 0
        if signal == "BUY":
            score = 2
        elif signal == "SELL":
            score = 1

        results.append((stock, signal, score))

    except:
        continue

# 🔥 Top stocks
top = sorted(results, key=lambda x: x[2], reverse=True)[:10]

st.subheader("🔥 Top NIFTY 50 Signals")

for s, sig, sc in top:
    if sig == "BUY":
        st.success(f"{s} → 🟢 BUY")
    elif sig == "SELL":
        st.error(f"{s} → 🔴 SELL")
    else:
        st.write(f"{s} → HOLD")
