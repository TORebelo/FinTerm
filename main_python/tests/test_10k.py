import requests

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"

def get_cik_from_ticker(ticker):
    headers = {"User-Agent": "Your Name (your@email.com)"}
    response = requests.get(TICKER_MAP_URL, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()

            # SEC file structure fix
            ticker_map = {item["ticker"]: str(item["cik_str"]).zfill(10) for item in data.values()}

            return ticker_map.get(ticker.upper(), None)

        except ValueError:
            print("Error: Unable to parse JSON response")
    else:
        print(f"Error: SEC API request failed with status code {response.status_code}")

    return None

# Example usage
ticker = "AAPL"
cik = get_cik_from_ticker(ticker)

if cik:
    print(f"CIK for {ticker}: {cik}")
else:
    print(f"CIK not found for {ticker}")

