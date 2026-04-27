import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.title("🚀 NIFTY Auto Stock Finder (Live)")

# 🔄 Auto refresh every 5 minutes
st_autorefresh(interval=300000, key="refresh")

st.write("⏱ Auto-refreshing every 5 minutes")

# Load NIFTY 50
@st.cache_data
def load_nifty():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pd.read_html(url)
    df = table[1]
    df['Symbol'] = df['Symbol'] + ".NS"
    return df['Symbol'].tolist()

stocks = load_nifty()

# Period
period = "1y"

results = []

# Scan all stocks
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

# Sort best stocks
top = sorted(results, key=lambda x: x[2], reverse=True)[:10]

st.subheader("🔥 Live Signals (Top Stocks)")

for s, sig, sc in top:
    if sig == "BUY":
        st.success(f"{s} → 🟢 BUY")
    elif sig == "SELL":
        st.error(f"{s} → 🔴 SELL")
    else:
        st.write(f"{s} → HOLD")
