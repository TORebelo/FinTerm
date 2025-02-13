import asyncio
from datetime import datetime
from ..main_python.portfolio import Portfolio

async def main():
    # Initialize portfolio with API key
    api_key = "keDH5lgSUzRw2em9oTcRdD9CHiHKiTaB"
    portfolio = Portfolio(api_key)

    # Add initial stocks
    await portfolio.add_stock("AAPL", 10, datetime(2020, 10, 1))
    await portfolio.add_stock("NVDA", 5, datetime(2022, 10, 1))

    # Display initial portfolio
    await portfolio.display_portfolio()

    # Add more stocks
    await portfolio.add_stock("MSFT", 8, datetime(2021, 5, 15))
    await portfolio.add_stock("GOOGL", 3, datetime(2023, 2, 1))

    # Display updated portfolio
    await portfolio.display_portfolio()

    # Display yearly values
    await portfolio.display_yearly_values()

    # Get current total value
    current_value = await portfolio.get_total_value()
    print(f"\nCurrent Total Portfolio Value: ${current_value:.2f}")

if __name__ == "__main__":
    asyncio.run(main())