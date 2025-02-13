import yfinance as yf
import plotly.graph_objs as go

def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    print("get_stock_info function loaded successfully!")
    return stock.info

def plot_stock_chart(ticker, period="1y"):
    history = yf.Ticker(ticker).history(period=period)
    fig = go.Figure(data=[go.Candlestick(
        x=history.index,
        open=history['Open'],
        high=history['High'],
        low=history['Low'],
        close=history['Close']
    )])
    fig.show()
    