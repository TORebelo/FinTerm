import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, request

class YahooFinanceChart:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.data = None
        self.info = None
        
    def fetch_data(self, period: str = "1y", interval: str = "1d"):
        """Fetch stock data and info"""
        self.data = self.stock.history(period=period, interval=interval)
        self.info = self.stock.info
        return self.data
    
    def calculate_macd(self, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        exp1 = self.data['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_rsi(self, periods=14):
        """Calculate RSI indicator"""
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def create_chart(self, period: str = "1y", interval: str = "1d"):
        """Create Yahoo Finance style chart"""
        # Fetch fresh data
        self.fetch_data(period, interval)
        
        # Create figure with secondary y-axis
        fig = make_subplots(rows=3, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           row_heights=[0.6, 0.2, 0.2])
        
        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=self.data.index,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='OHLC'
        ), row=1, col=1)
        
        # Add volume bars
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(self.data['Close'], self.data['Open'])]
        fig.add_trace(go.Bar(
            x=self.data.index,
            y=self.data['Volume'],
            marker_color=colors,
            name='Volume',
            opacity=0.5
        ), row=2, col=1)
        
        # Add MACD
        macd, signal, hist = self.calculate_macd()
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=macd,
            name='MACD',
            line=dict(color='#ff9800')
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=signal,
            name='Signal',
            line=dict(color='#2962ff')
        ), row=3, col=1)
        fig.add_trace(go.Bar(
            x=self.data.index,
            y=hist,
            name='Histogram',
            marker_color=['green' if val >= 0 else 'red' for val in hist]
        ), row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{self.ticker} Stock Price',
            yaxis_title='Stock Price (USD)',
            yaxis2_title='Volume',
            xaxis3_title='Date',
            template='plotly_dark',
            height=900,
            xaxis_rangeslider_visible=False,
            showlegend=True
        )
        
        # Update y-axes labels
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        return fig
    
    def show(self, period: str = "1y", interval: str = "1d"):
        """Display the chart"""
        fig = self.create_chart(period, interval)
        fig.show()
    
    def get_summary(self):
        """Get stock summary information"""
        if self.info is None:
            self.info = self.stock.info
        
        return {
            'name': self.info.get('longName', self.ticker),
            'sector': self.info.get('sector', 'N/A'),
            'industry': self.info.get('industry', 'N/A'),
            'current_price': self.info.get('currentPrice', 'N/A'),
            'market_cap': self.info.get('marketCap', 'N/A'),
            'pe_ratio': self.info.get('trailingPE', 'N/A'),
            'dividend_yield': self.info.get('dividendYield', 'N/A'),
            'volume': self.info.get('volume', 'N/A'),
            'avg_volume': self.info.get('averageVolume', 'N/A'),
            '52_week_high': self.info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': self.info.get('fiftyTwoWeekLow', 'N/A')
        }

# Flask Web Application
app = Flask(__name__)

@app.route('/')
def index():
    # Get parameters from URL with defaults
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    # Create HTML form with corrected formatting
    html_form = f'''
    <html>
        <head>
            <title>Stock Analysis</title>
            <style>
                body {{ 
                    font-family: Arial; 
                    background-color: #000000; 
                    color: white; 
                    padding: 20px; 
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: auto; 
                }}
                .form-container {{ 
                    margin-bottom: 20px; 
                    background-color: #1a1a1a; 
                    padding: 20px; 
                    border-radius: 5px; 
                }}
                .info-container {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 20px; 
                }}
                .info-box {{ 
                    background-color: #1a1a1a; 
                    padding: 15px; 
                    border-radius: 5px; 
                }}
                .info-label {{ 
                    color: #888; 
                    font-size: 0.9em; 
                }}
                .info-value {{ 
                    font-size: 1.1em; 
                    margin-top: 5px; 
                }}
                select, input {{ 
                    padding: 8px; 
                    margin: 5px; 
                    background-color: #333; 
                    color: white; 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                }}
                button {{ 
                    background-color: #0052cc; 
                    color: white; 
                    padding: 8px 15px; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer; 
                }}
                button:hover {{ 
                    background-color: #0047b3; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="form-container">
                    <form method="get">
                        <input type="text" name="ticker" value="{ticker}" placeholder="Enter stock symbol">
                        <select name="period">
                            <option value="1d" {"selected" if period == "1d" else ""}>1 Day</option>
                            <option value="5d" {"selected" if period == "5d" else ""}>5 Days</option>
                            <option value="1mo" {"selected" if period == "1mo" else ""}>1 Month</option>
                            <option value="3mo" {"selected" if period == "3mo" else ""}>3 Months</option>
                            <option value="6mo" {"selected" if period == "6mo" else ""}>6 Months</option>
                            <option value="1y" {"selected" if period == "1y" else ""}>1 Year</option>
                            <option value="2y" {"selected" if period == "2y" else ""}>2 Years</option>
                            <option value="5y" {"selected" if period == "5y" else ""}>5 Years</option>
                            <option value="max" {"selected" if period == "max" else ""}>Max</option>
                        </select>
                        <select name="interval">
                            <option value="1m" {"selected" if interval == "1m" else ""}>1 Minute</option>
                            <option value="5m" {"selected" if interval == "5m" else ""}>5 Minutes</option>
                            <option value="15m" {"selected" if interval == "15m" else ""}>15 Minutes</option>
                            <option value="1h" {"selected" if interval == "1h" else ""}>1 Hour</option>
                            <option value="1d" {"selected" if interval == "1d" else ""}>1 Day</option>
                            <option value="1wk" {"selected" if interval == "1wk" else ""}>1 Week</option>
                            <option value="1mo" {"selected" if interval == "1mo" else ""}>1 Month</option>
                        </select>
                        <button type="submit">Update Chart</button>
                    </form>
                </div>
    '''
    
    try:
        # Create chart instance
        chart = YahooFinanceChart(ticker)
        
        # Get stock info
        info = chart.get_summary()
        
        # Add stock info to HTML
        info_html = '''
                <div class="info-container">
                    <div class="info-box">
                        <div class="info-label">Price</div>
                        <div class="info-value">${:,.2f}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Market Cap</div>
                        <div class="info-value">${:,.0f}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">P/E Ratio</div>
                        <div class="info-value">{:,.2f}</div>
                    </div>
                    <div class="info-box">
                        <div class="info-label">Volume</div>
                        <div class="info-value">{:,.0f}</div>
                    </div>
                </div>
        '''.format(
            info['current_price'] if isinstance(info['current_price'], (int, float)) else 0,
            info['market_cap'] if isinstance(info['market_cap'], (int, float)) else 0,
            info['pe_ratio'] if isinstance(info['pe_ratio'], (int, float)) else 0,
            info['volume'] if isinstance(info['volume'], (int, float)) else 0
        )
        
        # Create and get chart
        fig = chart.create_chart(period=period, interval=interval)
        chart_html = fig.to_html(full_html=False)
        
        # Return complete page
        return html_form + info_html + chart_html + '</div></body></html>'
        
    except Exception as e:
        return html_form + f'<div style="color: red;">Error: {str(e)}</div></div></body></html>'

if __name__ == '__main__':
    print("Starting server... Open http://localhost:5000 in your browser")
    app.run(debug=True)