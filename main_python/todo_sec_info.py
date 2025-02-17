import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
import json
import ticker_cik as ck

#TODO: Add function to get EDGAR filing information for a given ticker


def get_edgar_info(ticker: str) -> List[Dict[str, Any]]:
    """
    Retrieve EDGAR filing information for a given ticker.
    """
    cik = ck.get_cik_from_ticker(ticker)
    if not cik:
        return [{"error": f"CIK not found for ticker {ticker}"}]

    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=exclude&start=0&count=100&output=atom"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return [{"error": f"Failed to retrieve EDGAR data. Status code: {response.status_code}"}]

    soup = BeautifulSoup(response.content, 'xml')
    entries = soup.find_all('entry')

    filing_info = []
    for entry in entries:
        filing = {
            "title": entry.title.text,
            "link": entry.link['href'],
            "updated": entry.updated.text,
            "category": entry.category['term'],
            "accession_number": entry.id.text.split(":")[-1]
        }
        filing_info.append(filing)

    return filing_info

def get_filing_details(accession_number: str) -> Dict[str, Any]:
    """
    Retrieve detailed information for a specific filing.
    """
    url = f"https://www.sec.gov/Archives/edgar/data/{accession_number}-index.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to retrieve filing details. Status code: {response.status_code}"}

    soup = BeautifulSoup(response.content, 'html.parser')
    filing_details = {}

    # Extract filing date
    filing_date = soup.find('div', class_='formGrouping').find('div', class_='info').text.strip()
    filing_details['filing_date'] = filing_date

    # Extract available documents
    table = soup.find('table', class_='tableFile')
    if table:
        documents = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                doc = {
                    "document": cols[2].text.strip(),
                    "description": cols[1].text.strip(),
                    "link": f"https://www.sec.gov{cols[2].a['href']}" if cols[2].a else None
                }
                documents.append(doc)
        filing_details['documents'] = documents

    return filing_details

def main():
    ticker = input("Enter the ticker symbol (e.g., TSLA): ").upper()
    filings = get_edgar_info(ticker)

    if "error" in filings[0]:
        print(filings[0]["error"])
        return

    print(f"\nAvailable filings for {ticker}:")
    for i, filing in enumerate(filings, 1):
        print(f"{i}. {filing['title']} - {filing['updated'][:10]}")

    choice = int(input("\nEnter the number of the filing you want to view details for: "))
    if 1 <= choice <= len(filings):
        selected_filing = filings[choice - 1]
        details = get_filing_details(selected_filing['accession_number'])
        
        print(f"\nDetails for {selected_filing['title']}:")
        print(f"Filing Date: {details.get('filing_date', 'N/A')}")
        print("\nAvailable Documents:")
        for doc in details.get('documents', []):
            print(f"- {doc['description']}: {doc['link']}")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()