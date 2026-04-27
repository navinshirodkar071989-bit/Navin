import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import pytz

st.set_page_config(page_title="NIFTY 50 AI STOCK FINDER", layout="wide")

st.title("🧠 NIFTY 50 AI STOCK FINDER")

# -----------------------------
# TIME (IST)
# -----------------------------
ist = pytz.timezone('Asia/Kolkata')
now = datetime.datetime.now(ist)

st.write("⏰ Current Time:", now.strftime("%Y-%m-%d %H:%M"))

def is_market_open():
    return now.weekday() < 5 and (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30))

if is_market_open():
    st.success("🟢 Market is OPEN")
else:
    st.warning("🔴 Market is CLOSED")

# -----------------------------
# AUTO FETCH NIFTY 50
# -----------------------------
@st.cache_data(ttl=86400)
def get_nifty50():
    url = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pd.read_html(url)[0]
    symbols = table['Symbol'].tolist()
    
    # Convert to Yahoo format
    symbols = [s + ".NS" for s in symbols]
    return symbols

stocks = get_nifty50()

st.write(f"📊 Tracking {len(stocks)} stocks")

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
# FAST DATA FETCH (KEY OPTIMIZATION)
# -----------------------------
@st.cache_data(ttl=300)
def fetch_data(stocks):
    data = yf.download(
        stocks,
        period="1mo",
        interval="1d",
        group_by='ticker',
        threads=True,
        progress=False
    )
    return data

data = fetch_data(stocks)

# -----------------------------
# PROCESS DATA
# -----------------------------
results = []

for stock in stocks:
    try:
        df = data[stock].dropna()

        if df.empty:
            continue

        df['RSI'] = calculate_rsi(df)
        df['MACD'], df['Signal'] = calculate_macd(df)

        df = df.dropna()
        if df.empty:
            continue

        latest = df.iloc[-1]

        results.append({
            "Stock": stock,
            "Close": round(float(latest['Close']), 2),
            "RSI": round(float(latest['RSI']), 2),
            "MACD": round(float(latest['MACD']), 2),
            "Signal": round(float(latest['Signal']), 2),
            "Volume": int(latest['Volume'])
        })

    except:
        continue

df_all = pd.DataFrame(results)

# -----------------------------
# DISPLAY
# -----------------------------
if df_all.empty:
    st.error("No data available")
else:
    st.subheader("📊 Stock Data")
    st.dataframe(df_all)

# -----------------------------
# AI SIGNALS
# -----------------------------
if not df_all.empty:
    df_all['AI Signal'] = df_all.apply(
        lambda row: "🟢 BUY" if row['RSI'] < 45 and row['MACD'] > row['Signal']
        else "🔴 SELL" if row['RSI'] > 60 and row['MACD'] < row['Signal']
        else "🟡 HOLD",
        axis=1
    )

    st.subheader("🤖 AI Signals")
    st.dataframe(df_all)

# -----------------------------
# TOP ACTIVE
# -----------------------------
if not df_all.empty:
    st.subheader("📈 Top Active Stocks")
    top = df_all.sort_values(by="Volume", ascending=False)
    st.dataframe(top)

st.caption("🔄 Auto-refresh every 5 minutes")
