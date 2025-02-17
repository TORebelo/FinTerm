import yfinance as yf
import requests
import json
import pandas as pd
import plotly.graph_objs as go
from ticker_cik import get_cik_from_ticker
import constants as constant

def get_sec_filings(cik, form_types=["10-K", "10-Q"], count=5):
    """Fetches the most recent SEC filings for a given CIK."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "Your Name (your@email.com)"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lança erro se a requisição falhar
        data = response.json()

        filings = data.get("filings", {}).get("recent", {})
        results = []

        for i in range(len(filings.get("accessionNumber", []))):
            if filings["form"][i] in form_types:
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}/{filings['primaryDocument'][i]}"
                
                results.append({
                    "Form Type": filings["form"][i],
                    "Filed Date": filings["filingDate"][i],
                    "Period of Report": filings.get("reportDate", ["N/A"])[i],
                    "URL": filing_url
                })

                if len(results) >= count:
                    break
        
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SEC filings: {e}")
        return []

import json
import yfinance as yf
import requests
import pandas as pd

def get_stock_info(ticker):
    """Fetch comprehensive stock and financial data from multiple sources."""
    
    # Get CIK from ticker (assuming get_cik_from_ticker is defined elsewhere)
    cik = get_cik_from_ticker(ticker)
    if not cik:
        print(f"Error: CIK not found for ticker {ticker}")
        return None
    
    # Yahoo Finance data
    stock = yf.Ticker(ticker)
    yf_info = stock.info

    # Polygon.io data
    polygon_url = f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={constant.API_KEY_POLYGON}"
    try:
        polygon_response = requests.get(polygon_url)
        polygon_data = polygon_response.json().get('results', {}) if polygon_response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        polygon_data = {}

    # Fetch SEC filings (assuming get_sec_filings is defined elsewhere)
    sec_filings = get_sec_filings(cik)

    # Fetch additional financial data
    balance_sheet = stock.balance_sheet if not stock.balance_sheet.empty else pd.DataFrame()
    cash_flow = stock.cashflow if not stock.cashflow.empty else pd.DataFrame()
    income_stmt = stock.income_stmt if not stock.income_stmt.empty else pd.DataFrame()

    # Organize the data
    info = {
        "General Information": {
            "Company Name": yf_info.get('longName', 'N/A'),
            "Ticker": ticker,
            "Industry": yf_info.get('industry', 'N/A'),
            "Sector": yf_info.get('sector', 'N/A'),
            "Country": yf_info.get('country', 'N/A'),
            "Website": yf_info.get('website', 'N/A'),
            "Description": 
            yf_info.get('longBusinessSummary', 'N/A')
            
        },
        "Market Data": {
            "Current Price": yf_info.get('currentPrice', 'N/A'),
            "Market Cap": yf_info.get('marketCap', 'N/A'),
            "52 Week High": yf_info.get('fiftyTwoWeekHigh', 'N/A'),
            "52 Week Low": yf_info.get('fiftyTwoWeekLow', 'N/A'),
            "Volume": yf_info.get('volume', 'N/A'),
            "Average Volume": yf_info.get('averageVolume', 'N/A'),
            "P/E Ratio": yf_info.get('trailingPE', 'N/A'),
            "Forward P/E": yf_info.get('forwardPE', 'N/A'),
            "Dividend Yield": f"{(yf_info.get('dividendYield', 0) * 100):.2f}%" if yf_info.get('dividendYield') else 'N/A'
        },
        "Financial Metrics": {
            "Revenue": yf_info.get('totalRevenue', 'N/A'),
            "Gross Profit": yf_info.get('grossProfits', 'N/A'),
            "Net Income": yf_info.get('netIncomeToCommon', 'N/A'),
            "EPS": yf_info.get('trailingEps', 'N/A'),
            "Forward EPS": yf_info.get('forwardEps', 'N/A'),
            "PEG Ratio": yf_info.get('pegRatio', 'N/A'),
            "Book Value": yf_info.get('bookValue', 'N/A'),
            "Price to Book": yf_info.get('priceToBook', 'N/A')
        },
        "Additional Information": {
            "Employees": yf_info.get('fullTimeEmployees', 'N/A'),
            "Founded": polygon_data.get('list_date', 'N/A'),
            "CEO": yf_info.get('companyOfficers', [{}])[0].get('name', 'N/A') if yf_info.get('companyOfficers') else 'N/A',
            "Next Earnings Date": yf_info.get('earningsTimestamp', 'N/A')
        },
        "Recent SEC Filings": sec_filings
    }

    # Convert the info dictionary to a formatted JSON string
    info_str = json.dumps(info, indent=2)

    # Save the full info to a JSON file
    with open(f"{ticker}_full_info.json", "w") as f:
        json.dump(info, f, indent=2)
    print(f"\nFull information for {ticker} has been saved to {ticker}_full_info.json")

    # Return the JSON string
    return info_str

def plot_stock_chart(ticker, period="1y"):
    """Plot an interactive stock chart using Plotly."""
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    # Create candlestick chart
    candlestick = go.Candlestick(
        x=history.index,
        open=history['Open'],
        high=history['High'],
        low=history['Low'],
        close=history['Close'],
        name="Price"
    )
    
    # Create volume bar chart
    volume = go.Bar(
        x=history.index,
        y=history['Volume'],
        name="Volume",
        yaxis="y2"
    )
    
    # Create moving averages
    ma50 = go.Scatter(
        x=history.index,
        y=history['Close'].rolling(window=50).mean(),
        name="50 Day MA",
        line=dict(color='orange')
    )
    
    ma200 = go.Scatter(
        x=history.index,
        y=history['Close'].rolling(window=200).mean(),
        name="200 Day MA",
        line=dict(color='red')
    )

    layout = go.Layout(
        title=f"{ticker} Stock Price",
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        xaxis=dict(title="Date"),
        height=600,
        width=1000
    )

    fig = go.Figure(data=[candlestick, volume, ma50, ma200], layout=layout)
    fig.show()


