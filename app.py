import streamlit as st
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(layout="wide")
st.title("📊 NIFTY AI Stock Scanner")

# NIFTY stocks (expand anytime)
stocks = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS",
    "ICICIBANK.NS","SBIN.NS","ITC.NS","LT.NS"
]

results = []

for stock in stocks:
    df = yf.download(stock, period="1y", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if len(df) < 200:
        continue

    # Indicators
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    df = df.dropna()

    # Target (next day up/down)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()

    # Features
    X = df[['MA50','MA200']]
    y = df['Target']

    # Auto-learning model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    pred = model.predict([X.iloc[-1]])[0]

    # Score system
    score = 0
    if pred == 1:
        score += 2
    if df['MA50'].iloc[-1] > df['MA200'].iloc[-1]:
        score += 2

    results.append((stock, score))

# Top picks
top = sorted(results, key=lambda x: x[1], reverse=True)[:5]

st.subheader("🔥 Top 5 Stocks Today")

for stock, score in top:
    st.write(f"{stock} → Score: {score}")

# Chart section
selected = st.selectbox("View Stock Chart", [x[0] for x in top])

df = yf.download(selected, period="1y")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()

st.line_chart(df[['Close','MA50','MA200']])
