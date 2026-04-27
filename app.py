import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import requests

st.set_page_config(page_title="Elite Stock App", layout="wide")

st.title("📊 Elite AI Stock Dashboard")

# Sidebar
stock = st.sidebar.selectbox("Select Stock", [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS"
])

period = st.sidebar.selectbox("Select Period", ["6mo","1y","2y"])

# Telegram settings (optional)
st.sidebar.subheader("🔔 Alerts")
TOKEN = st.sidebar.text_input("Bot Token")
CHAT_ID = st.sidebar.text_input("Chat ID")

# Download data
df = yf.download(stock, period=period)

# Fix columns
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

if df.empty:
    st.error("No data found")

else:
    # Indicators
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()
    df['RSI'] = (100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))))

    df = df.dropna()

    latest = df.iloc[-1]

    # AI model
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()

    features = df[['MA50','MA200']]
    target = df['Target']

    model = RandomForestClassifier(n_estimators=100)
    model.fit(features, target)

    pred = model.predict([features.iloc[-1]])[0]

    # Layout
    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Price", round(latest['Close'],2))

    change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0])*100
    col2.metric("📊 Change %", round(change,2))

    # Signal
    if latest['MA50'] > latest['MA200']:
        signal = "BUY"
        col3.success("🟢 BUY")
    else:
        signal = "SELL"
        col3.error("🔴 SELL")

    # AI Prediction
    st.subheader("🤖 AI Prediction")
    if pred == 1:
        st.success("Next Day: UP 📈")
    else:
        st.error("Next Day: DOWN 📉")

    # Send alert
    if TOKEN and CHAT_ID:
        msg = f"{stock} Signal: {signal}"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": msg})

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200'))

    st.plotly_chart(fig, use_container_width=True)
