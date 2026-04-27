import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import pytz

st.set_page_config(page_title="AI TOP MOVER SCANNER", layout="wide")

st.title("🚀 AI TOP MOVER SCANNER")

# -----------------------------
# TIME
# -----------------------------
ist = pytz.timezone('Asia/Kolkata')
now = datetime.datetime.now(ist)
st.write("⏰ Time:", now.strftime("%Y-%m-%d %H:%M"))

# -----------------------------
# LARGE STOCK UNIVERSE (~60)
# -----------------------------
stocks = [
"RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
"SBIN.NS","ITC.NS","BHARTIARTL.NS","KOTAKBANK.NS",
"IRCTC.NS","RVNL.NS","IREDA.NS","NBCC.NS","HUDCO.NS",
"SUZLON.NS","YESBANK.NS","IDFCFIRSTB.NS","PNB.NS","BANKBARODA.NS",
"TATAPOWER.NS","ADANIPOWER.NS","NHPC.NS","SJVN.NS",
"ZOMATO.NS","NYKAA.NS","PAYTM.NS","ADANIGREEN.NS",
"WIPRO.NS","HCLTECH.NS","TECHM.NS",
"DLF.NS","GAIL.NS","HAVELLS.NS","PIDILITIND.NS","NAUKRI.NS",
"DIXON.NS","POLYCAB.NS","ASTRAL.NS","BSE.NS"
]

# -----------------------------
# FETCH DATA (FAST)
# -----------------------------
@st.cache_data(ttl=300)
def fetch_data(stocks):
    return yf.download(
        stocks,
        period="2mo",
        interval="1d",
        group_by='ticker',
        threads=True,
        progress=False
    )

data = fetch_data(stocks)

# -----------------------------
# STEP 1: FIND TOP MOVERS
# -----------------------------
movers = []

for stock in stocks:
    try:
        df = data[stock].dropna()
        if len(df) < 2:
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

        movers.append((stock, change))

    except:
        continue

# Sort by movement
movers = sorted(movers, key=lambda x: abs(x[1]), reverse=True)

# Pick top 15 movers
top_movers = [x[0] for x in movers[:15]]

st.subheader("📈 Top Movers (Auto Detected)")
st.write(top_movers)

# -----------------------------
# INDICATOR
# -----------------------------
def rsi(df, window=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# -----------------------------
# STEP 2: SIGNALS ON MOVERS
# -----------------------------
results = []

for stock in top_movers:
    try:
        df = data[stock].dropna()
        if len(df) < 25:
            continue

        df['RSI'] = rsi(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        high_20 = df['High'].rolling(20).max().iloc[-2]
        breakout = latest['Close'] > high_20

        rsi_val = latest['RSI']

        change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

        signal = "HOLD"
        entry = 0
        stoploss = 0
        target = 0

        if breakout and rsi_val > 55:
            signal = "🟢 BUY"
            entry = latest['Close']
            stoploss = entry * 0.97
            target = entry * 1.05

        elif rsi_val > 70:
            signal = "🔴 SELL"
            entry = latest['Close']
            stoploss = entry * 1.03
            target = entry * 0.95

        results.append({
            "Stock": stock,
            "Price": round(latest['Close'], 2),
            "Change %": round(change, 2),
            "RSI": round(rsi_val, 2),
            "Signal": signal,
            "Entry": round(entry, 2),
            "Stop Loss": round(stoploss, 2),
            "Target": round(target, 2)
        })

    except:
        continue

df_all = pd.DataFrame(results)

# -----------------------------
# DISPLAY
# -----------------------------
if df_all.empty:
    st.error("No data")
else:
    st.subheader("🔥 Trading Signals (Top Movers Only)")
    st.dataframe(df_all)

    trades = df_all[df_all["Signal"] != "HOLD"]

    st.subheader("🚀 Actionable Trades")
    if not trades.empty:
        st.dataframe(trades)
    else:
        st.info("No strong trades right now")

st.caption("⚠️ Signals are probabilistic, not guaranteed")
