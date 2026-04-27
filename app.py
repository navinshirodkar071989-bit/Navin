import streamlit as st
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(layout="wide")
st.title("🚀 Elite NIFTY AI Scanner")

# NIFTY stocks (you can expand)
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

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs)

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2

    # Breakout
    df['Breakout'] = df['Close'] > df['Close'].rolling(20).max().shift(1)

    df = df.dropna()

    # AI Target
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()

    X = df[['MA50','MA200','RSI','MACD']]
    y = df['Target']

    # AI Model (auto-learning)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    pred = model.predict([X.iloc[-1]])[0]

    latest = df.iloc[-1]

    # Scoring system
    score = 0
    if pred == 1:
        score += 2
    if latest['MA50'] > latest['MA200']:
        score += 2
    if latest['RSI'] < 60:
        score += 1
    if latest['MACD'] > 0:
        score += 1
    if latest['Breakout']:
        score += 2

    results.append((stock, score))

# Sort top picks
top = sorted(results, key=lambda x: x[1], reverse=True)[:5]

st.subheader("🔥 Top 5 Stocks Today")

for stock, score in top:
    st.write(f"{stock} → Score: {score}")

# Chart section
selected = st.selectbox("📈 View Chart", [x[0] for x in top])

df = yf.download(selected, period="1y")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df['MA50'] = df['Close'].rolling(50).mean()
df['MA200'] = df['Close'].rolling(200).mean()

st.line_chart(df[['Close','MA50','MA200']])
