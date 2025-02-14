import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from stock import get_stock_info, plot_stock_chart

def test_stock_info_and_chart():
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

    for ticker in tickers:
        print(f"\n{'='*50}")
        print(f"Testing stock info and chart for {ticker}")
        print(f"{'='*50}")

        # Fetch stock information
        info = get_stock_info(ticker)

        if info:
            # Print a summary of the information
            for section, details in info.items():
                print(f"\n{section}:")
                if isinstance(details, list):
                    for item in details[:3]:  # Print first 3 items for lists (e.g., SEC filings)
                        print(json.dumps(item, indent=2))
                    if len(details) > 3:
                        print("...")
                else:
                    for key, value in list(details.items())[:5]:  # Print first 5 items for dictionaries
                        print(f"  {key}: {value}")
                    if len(details) > 5:
                        print("  ...")

            # Save full info to a JSON file
            with open(f"{ticker}_full_info.json", "w") as f:
                json.dump(info, f, indent=2)
            print(f"\nFull information for {ticker} has been saved to {ticker}_full_info.json")

            # Plot the stock chart
            print(f"\nGenerating stock chart for {ticker}...")
            plot_stock_chart(ticker)
            print(f"Stock chart for {ticker} has been displayed.")

        else:
            print(f"Failed to retrieve information for {ticker}")

        print("\nPress Enter to continue to the next stock...")
        input()

if __name__ == "__main__":
    test_stock_info_and_chart()