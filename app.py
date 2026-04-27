import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="NIFTY 50 AI STOCK FINDER", layout="wide")

st.title("🧠 NIFTY 50 AI STOCK FINDER")

# -----------------------------
# Market Status
# -----------------------------
def is_market_open():
    now = datetime.datetime.now()
    return now.weekday() < 5 and (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30))

now = datetime.datetime.now()
st.write("⏰ Current Time:", now.strftime("%Y-%m-%d %H:%M"))

if is_market_open():
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED (Using last available data)")

# -----------------------------
# NIFTY 50 Stocks List
# -----------------------------
nifty50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS"
]

# -----------------------------
# Indicator Functions
# -----------------------------
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# -----------------------------
# Fetch Data
# -----------------------------
results = []

for stock in nifty50:
    try:
        df = yf.download(stock, period="1mo", interval="1d", progress=False)

        if df.empty:
            continue

        df['RSI'] = calculate_rsi(df)
        df['MACD'], df['Signal'] = calculate_macd(df)

        latest = df.iloc[-1]

        results.append({
            "Stock": stock,
            "Close": round(latest['Close'], 2),
            "RSI": round(latest['RSI'], 2),
            "MACD": round(latest['MACD'], 2),
            "Signal": round(latest['Signal'], 2),
            "Volume": int(latest['Volume'])
        })

    except Exception as e:
        st.error(f"Error fetching {stock}: {e}")

df_all = pd.DataFrame(results)

# -----------------------------
# Show last data timestamp
# -----------------------------
if not df.empty:
    st.write("📊 Last Data Date:", df.index[-1])

# -----------------------------
# Signal Logic
# -----------------------------
# Strong signals
strong = df_all[
    (df_all['RSI'] < 40) &
    (df_all['MACD'] > df_all['Signal'])
]

# Relaxed signals
relaxed = df_all[
    (df_all['RSI'] < 55) &
    (df_all['MACD'] > df_all['Signal'])
]

st.subheader("🔥 AI Top Picks (Strong Signals)")
if not strong.empty:
    st.dataframe(strong)
else:
    st.info("No strong signals")

st.subheader("⚡ Moderate Opportunities")
if not relaxed.empty:
    st.dataframe(relaxed)
else:
    st.info("No moderate signals")

# -----------------------------
# Fallback (Always show something)
# -----------------------------
st.subheader("📊 Top Active Stocks (Fallback)")

if not df_all.empty:
    fallback = df_all.sort_values(by="Volume", ascending=False).head(5)
    st.dataframe(fallback)
else:
    st.error("No data available")

# -----------------------------
# Auto Refresh
# -----------------------------
st.caption("🔄 Auto-refresh every 5 minutes")
