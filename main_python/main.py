from flask import Flask, render_template, request, jsonify
from datetime import datetime
from portfolio import Portfolio
from stock import get_stock_info, plot_stock_chart
import constants as constants 
import asyncio
import os

app = Flask(__name__ , template_folder=( './Web_tools/html'))

portfolio = Portfolio(constants.API_KEY_POLYGON)

@app.route('/')
def index():
    return render_template( 'main.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.json['command'].strip().lower()
    response = {}

    if command == "help":
        response['message'] = """
Commands:
  add <ticker> <shares> <YYYY-MM-DD> - Add a stock to the portfolio
  view <ticker>                      - View stock details and chart
  summary                            - Display portfolio summary
  news                               - Display market news
  benchmark <ticker>                 - Add a benchmark to compare against
  compare <ticker1> <ticker2>        - Compare two stocks
"""
    elif command.startswith("add"):
        try:
            _, ticker, shares, purchase_date = command.split()
            ticker = ticker.upper()
            shares = int(shares)
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
            asyncio.run(portfolio.add_stock(ticker, shares, purchase_date))
            response['message'] = f"Added {shares} shares of {ticker} purchased on {purchase_date.strftime('%Y-%m-%d')}."
        except ValueError as e:
            response['message'] = f"Invalid input: {e}"
        except Exception as e:
            response['message'] = f"Error adding stock: {e}"

    elif command.startswith("view"):
        try:
            _, ticker = command.split()
            ticker = ticker.upper()
            stock_info = get_stock_info(ticker)
            chart_data = plot_stock_chart(ticker)
            response['message'] = stock_info
            response['chart'] = chart_data
        except Exception as e:
            response['message'] = f"Error viewing stock: {e}"

    elif command == "summary":
        asyncio.run(portfolio.display_portfolio())
        total_value = asyncio.run(portfolio.get_total_value())
        response['message'] = f"Total Portfolio Value: ${total_value:.2f}"
        response['chart'] = portfolio.plot_portfolio_value()

    elif command == "news":
        # Implement a function to fetch market news
        response['message'] = "Fetching market news..."
        response['news'] = get_market_news()

    elif command.startswith("benchmark"):
        try:
            _, ticker = command.split()
            ticker = ticker.upper()
            # Implement a function to add and track a benchmark
            add_benchmark(ticker)
            response['message'] = f"Added {ticker} as a benchmark."
        except Exception as e:
            response['message'] = f"Error adding benchmark: {e}"

    elif command.startswith("compare"):
        try:
            _, ticker1, ticker2 = command.split()
            ticker1, ticker2 = ticker1.upper(), ticker2.upper()
            # Implement a function to compare two stocks
            comparison_data = compare_stocks(ticker1, ticker2)
            response['message'] = f"Comparing {ticker1} and {ticker2}"
            response['comparison'] = comparison_data
        except Exception as e:
            response['message'] = f"Error comparing stocks: {e}"

    else:
        response['message'] = "Unknown command. Type 'help' for a list of commands."

    return jsonify(response)

def get_market_news():
    # Implement this function to fetch market news
    # You can use a news API or web scraping
    pass

def add_benchmark(ticker):
    # Implement this function to add and track a benchmark
    pass

def compare_stocks(ticker1, ticker2):
    # Implement this function to compare two stocks
    pass

if __name__ == "__main__":
    app.run(debug=True)