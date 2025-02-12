from datetime import datetime
import portfolio as p
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    try:
        API_KEY = 'keDH5lgSUzRw2em9oTcRdD9CHiHKiTaB'
        
        # Initialize with stocks
        initial_stocks = {
            'AAPL': {'shares': 10, 'purchase_date': datetime(2023, 10, 1)},
            'NVDA': {'shares': 5, 'purchase_date': datetime(2023, 10, 15)}
        }
        
        portfolio = p.Portfolio(api_key=API_KEY, initial_stocks=initial_stocks)
        
        # Add additional stock
        portfolio.add_stock('GOOGL', 2, datetime(2023, 10, 20))
        
        # Display portfolio information
        portfolio.display_portfolio()
        portfolio.display_yearly_values()
        portfolio.plot_portfolio_value()
        
    except Exception as e:
        logging.error(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()