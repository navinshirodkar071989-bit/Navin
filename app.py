import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.title("🤖 NIFTY 50 AI STOCK FINDER")

# Auto refresh every 5 min
st_autorefresh(interval=300000, key="refresh")

st.write("🔥 AI Top Picks (Auto Updated)")

# Load NIFTY 50
@st.cache_data
def load_nifty():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pd.read_html(url)
    df = table[1]
    df['Symbol'] = df['Symbol'] + ".NS"
    return df['Symbol'].tolist()

stocks = load_nifty()

results = []

# Scan stocks
for stock in stocks[:20]:   # limit to 20 for speed
    try:
        df = yf.download(stock, period="1y", progress=False)

        if len(df) < 200:
            continue

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

        if latest['MA50'] > latest['MA200'] and latest['RSI'] < 60:
            results.append((stock, "BUY"))

        elif latest['MA50'] < latest['MA200'] and latest['RSI'] > 40:
            results.append((stock, "SELL"))

    except:
        continue

# DISPLAY RESULTS
if len(results) == 0:
    st.warning("No strong signals right now")
else:
    for stock, signal in results[:10]:
        if signal == "BUY":
            st.success(f"{stock} → 🟢 BUY")
        else:
            st.error(f"{stock} → 🔴 SELL")
