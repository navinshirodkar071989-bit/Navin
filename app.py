import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="NIFTY 50 AI STOCK FINDER", layout="wide")

st.title("🧠 NIFTY 50 AI STOCK FINDER")

# -----------------------------
# TIME (IST FIX)
# -----------------------------
ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)

st.write("⏰ Current Time:", now.strftime("%Y-%m-%d %H:%M"))

def is_market_open():
    return now.weekday() < 5 and (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30))

if is_market_open():
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# -----------------------------
# STOCK LIST
# -----------------------------
stocks = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS"]

# -----------------------------
# INDICATORS
# -----------------------------
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12).mean()
    exp2 = data['Close'].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal

# -----------------------------
# FETCH DATA
# -----------------------------
results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="1mo", interval="1d", progress=False)

        if df.empty:
            continue

        # ✅ FIX: Flatten columns (important for yfinance bug)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # Indicators
        df['RSI'] = calculate_rsi(df)
        df['MACD'], df['Signal'] = calculate_macd(df)

        df = df.dropna()

        if df.empty:
            continue

        latest = df.iloc[-1]

        # ✅ FIX: Force scalar values
        close = float(latest['Close'])
        rsi = float(latest['RSI'])
        macd = float(latest['MACD'])
        signal = float(latest['Signal'])
        volume = int(latest['Volume'])

        results.append({
            "Stock": stock,
            "Close": round(close, 2),
            "RSI": round(rsi, 2),
            "MACD": round(macd, 2),
            "Signal": round(signal, 2),
            "Volume": volume
        })

    except Exception as e:
        st.error(f"Error fetching {stock}: {e}")

df_all = pd.DataFrame(results)

# -----------------------------
# DISPLAY DATA
# -----------------------------
if df_all.empty:
    st.error("❌ No data available")
else:
    st.subheader("📊 Stock Data")
    st.dataframe(df_all)

    # -----------------------------
    # SIGNAL LOGIC
    # -----------------------------
    strong = df_all[
        (df_all['RSI'] < 40) &
        (df_all['MACD'] > df_all['Signal'])
    ]

    relaxed = df_all[
        (df_all['RSI'] < 55) &
        (df_all['MACD'] > df_all['Signal'])
    ]

    st.subheader("🔥 Strong Signals")
    if not strong.empty:
        st.dataframe(strong)
    else:
        st.info("No strong signals")

    st.subheader("⚡ Moderate Signals")
    if not relaxed.empty:
        st.dataframe(relaxed)
    else:
        st.info("No moderate signals")

    # -----------------------------
    # FALLBACK
    # -----------------------------
    st.subheader("📊 Top Active Stocks")
    fallback = df_all.sort_values(by="Volume", ascending=False).head(5)
    st.dataframe(fallback)

st.caption("🔄 Auto-refresh every 5 minutes")
