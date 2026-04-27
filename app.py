import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="NIFTY AI STOCK FINDER", layout="wide")

st.title("🤖 NIFTY 50 AI STOCK FINDER")

# 🔄 Auto refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")
st.write("⏱ Auto-refreshing every 5 minutes")

# ✅ STATIC NIFTY LIST (No lxml issue)
def load_nifty():
    return [
        "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
        "KOTAKBANK.NS","LT.NS","SBIN.NS","AXISBANK.NS","ITC.NS",
        "HINDUNILVR.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS",
        "SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS",
        "NESTLEIND.NS","POWERGRID.NS","ADANIENT.NS","ADANIPORTS.NS",
        "BHARTIARTL.NS","HCLTECH.NS","TECHM.NS","TATAMOTORS.NS",
        "TATASTEEL.NS","JSWSTEEL.NS","GRASIM.NS","HEROMOTOCO.NS",
        "INDUSINDBK.NS","DRREDDY.NS","CIPLA.NS","EICHERMOT.NS",
        "APOLLOHOSP.NS","DIVISLAB.NS","BRITANNIA.NS","COALINDIA.NS",
        "ONGC.NS","BPCL.NS","SHREECEM.NS","BAJAJFINSV.NS",
        "HDFCLIFE.NS","SBILIFE.NS","ICICIPRULI.NS","UPL.NS",
        "NTPC.NS","TATACONSUM.NS","HINDALCO.NS"
    ]

stocks = load_nifty()

st.subheader("🔥 AI Top Picks (Live)")

results = []

# 🔍 Scan stocks
for stock in stocks[:25]:  # limit for speed
    try:
        df = yf.download(stock, period="1y", progress=False)

        if len(df) < 200:
            continue

        # Moving averages
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA200'] = df['Close'].rolling(200).mean()

        # RSI
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

        results.append((stock, signal))

    except:
        continue

# 📊 DISPLAY
if len(results) == 0:
    st.warning("No strong signals right now")
else:
    for stock, signal in results[:10]:
        if signal == "BUY":
            st.success(f"{stock} → 🟢 BUY")
        elif signal == "SELL":
            st.error(f"{stock} → 🔴 SELL")
        else:
            st.write(f"{stock} → HOLD")
