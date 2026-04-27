import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(layout="wide")
st.title("🤖 NIFTY 50 AI STOCK FINDER")

# 🔄 Auto refresh
st_autorefresh(interval=300000, key="refresh")

# ✅ Fixed NIFTY list
stocks = [
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

results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="1y", progress=False)

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

        # AI target (next day up/down)
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

        features = df[['MA50','MA200','RSI']]
        target = df['Target']

        # Train model
        model = RandomForestClassifier(n_estimators=50)
        model.fit(features[:-1], target[:-1])

        # Predict latest
        latest_features = features.iloc[-1].values.reshape(1, -1)
        prediction = model.predict(latest_features)[0]

        latest = df.iloc[-1]

        # Signal logic
        signal = "HOLD"

        if latest['MA50'] > latest['MA200'] and latest['RSI'] < 60:
            signal = "BUY"
        elif latest['MA50'] < latest['MA200'] and latest['RSI'] > 40:
            signal = "SELL"

        # Combine AI + signal
        if prediction == 1:
            ai_signal = "UP"
        else:
            ai_signal = "DOWN"

        score = 0
        if signal == "BUY" and ai_signal == "UP":
            score = 3
        elif signal == "BUY":
            score = 2
        elif signal == "SELL":
            score = 1

        results.append((stock, signal, ai_signal, score))

    except:
        continue

# Sort
top = sorted(results, key=lambda x: x[3], reverse=True)[:10]

st.subheader("🔥 AI Top Picks")

for s, sig, ai, sc in top:
    if sig == "BUY":
        st.success(f"{s} → 🟢 BUY | AI: {ai}")
    elif sig == "SELL":
        st.error(f"{s} → 🔴 SELL | AI: {ai}")
    else:
        st.write(f"{s} → HOLD | AI: {ai}")
