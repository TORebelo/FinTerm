import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import time
import re
import os
import sys
from typing import List, Tuple, Optional
from datetime import datetime

# Add parent directory to sys.path for custom modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from ticker_cik import get_cik_from_ticker

# Set headers to avoid SEC blocking requests
HEADERS = {"User-Agent": "Your Name (your@email.com)"}  # Replace with your info

def get_sec_filings_edgar(ticker: str, form_type: str = "10-K", years: int = 10) -> List[Tuple[str, str]]:
    """
    Fetch SEC 10-K filings using the EDGAR search page.
    """
    cik = get_cik_from_ticker(ticker)
    if not cik:
        print(f"Error: CIK not found for ticker {ticker}")
        return []
    
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form_type}&dateb=&owner=exclude&count={years}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Error: EDGAR search request failed with status code {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.tableFile2 tr")[1:]  # Skip header row
    
    sec_urls = []
    for row in rows:
        cells = row.select("td")
        if len(cells) >= 5:
            filing_date = cells[3].text.strip()  # Filing date
            filing_url = "https://www.sec.gov" + cells[1].a["href"]  # Filing index page
            sec_urls.append((filing_url, filing_date))
    
    print(f"Found {len(sec_urls)} SEC {form_type} filings for {ticker}")
    return sec_urls

def get_primary_document_url(index_url: str) -> Optional[str]:
    """
    Extracts the main 10-K filing document from the SEC filing index page.
    """
    time.sleep(1)  # Prevent SEC rate limiting
    response = requests.get(index_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error: Unable to fetch index page {index_url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    doc_table = soup.find("table", {"class": "tableFile"})

    if not doc_table:
        print(f"Error: Could not find document table on {index_url}")
        return None

    for row in doc_table.find_all("tr")[1:]:  # Skip header row
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        doc_type = cols[3].text.strip().upper()
        doc_link = cols[2].find("a")["href"] if cols[2].find("a") else None

        if "10-K" in doc_type and doc_link:
            full_doc_url = "https://www.sec.gov" + doc_link
            print(f"Found 10-K document: {full_doc_url}")
            return full_doc_url

    print(f"Warning: No valid 10-K document found in {index_url}")
    return None


def extract_revenue(soup: BeautifulSoup) -> float:
    """
    Extracts revenue from XBRL/iXBRL SEC filings.
    """

    # Prioritize extracting revenue from iXBRL data
    xbrl_revenue_tags = [
        "us-gaap:Revenues",
        "us-gaap:SalesRevenueNet",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    ]
    
    for tag in xbrl_revenue_tags:
        xbrl_data = soup.find("ix:nonFraction", {"name": tag})
        if xbrl_data:
            revenue_str = xbrl_data.text.replace(",", "").strip()
            try:
                return float(revenue_str)
            except ValueError:
                print(f"⚠️ Warning: Found revenue '{revenue_str}' but couldn't convert to float.")

    print("⚠️ No revenue found in XBRL. Trying text-based fallback.")

    # Fallback: Use regex-based extraction for legacy filings
    text = soup.get_text()

    revenue_patterns = [
        r'Net sales\s*\$?([\d,]+)',
        r'Total net sales\s*\$?([\d,]+)',
        r'Net sales:\s*\$?([\d,]+)',
        r'Total net revenues?\s*\$?([\d,]+)',
        r'Total revenues?\s*\$?([\d,]+)',
        r'Net revenues?\s*\$?([\d,]+)',
    ]
    
    for pattern in revenue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            revenue_str = match.group(1).replace(',', '')
            try:
                return float(revenue_str)
            except ValueError:
                print(f"⚠️ Warning: Found revenue '{revenue_str}' but couldn't convert to float.")

    return None




def get_annual_financials(sec_urls):
    """
    Extract financial data (e.g., revenue) from SEC 10-K filings.
    """
    annual_data = []
    
    for index_url, filing_date in sec_urls:
        print(f"🔄 Processing filing from {filing_date}: {index_url}")
        primary_doc_url = get_primary_document_url(index_url)
        if not primary_doc_url:
            continue

        time.sleep(2)  # Prevent SEC rate limiting
        response = requests.get(primary_doc_url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ Error: Unable to fetch primary document from {primary_doc_url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        revenue = extract_revenue(soup)

        if revenue:
            annual_data.append({"URL": primary_doc_url, "Filing Date": filing_date, "Net Revenue": revenue})
            print(f"✅ Successfully extracted revenue: ${revenue:,.0f}")
        else:
            print(f"⚠️ Warning: Unable to extract revenue from {primary_doc_url}")

    return pd.DataFrame(annual_data)


def calculate_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate year-over-year revenue growth.
    """
    df["Filing Date"] = pd.to_datetime(df["Filing Date"])
    df = df.sort_values(by="Filing Date", ascending=True).reset_index(drop=True)
    
    df["YoY Growth"] = df["Net Revenue"].pct_change() * 100
    df["Year"] = df["Filing Date"].dt.year
    return df

def plot_revenue_and_growth(df: pd.DataFrame, ticker: str) -> None:
    """
    Plot revenue and YoY growth.
    """
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot YoY Growth
    ax1.bar(df["Year"], df["YoY Growth"], color='skyblue', alpha=0.7, label='YoY Growth (%)')
    ax1.set_xlabel("Year")
    ax1.set_ylabel("YoY Growth (%)", color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')

    # Add text labels for YoY Growth
    for i, v in enumerate(df["YoY Growth"]):
        if pd.notna(v):
            ax1.text(df["Year"].iloc[i], v, f'{v:.2f}%', ha='center', va='bottom', color='skyblue')

    # Create a second y-axis for Net Revenue
    ax2 = ax1.twinx()
    ax2.plot(df["Year"], df["Net Revenue"], color='orange', linewidth=2, marker='o', label='Net Revenue')
    ax2.set_ylabel("Net Revenue (USD)", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Add text labels for Net Revenue
    for i, v in enumerate(df["Net Revenue"]):
        if pd.notna(v):
            ax2.text(df["Year"].iloc[i], v, f'${v/1e9:.1f}B', ha='center', va='bottom', color='orange')

    plt.title(f"{ticker} Year-over-Year Revenue Growth and Net Revenue")
    fig.tight_layout()

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.show()

def financial_comparison(ticker: str, years: int = 10) -> None:
    """
    Main function to fetch, analyze, and plot financial data.
    """
    sec_urls = get_sec_filings_edgar(ticker, years=years)
    annual_financials = get_annual_financials(sec_urls)
    
    if annual_financials.empty:
        print(f"Error: No revenue data found for {ticker}")
        return
    
    comparison = calculate_yoy_growth(annual_financials)
    
    print(f"\nFinancial Comparison for {ticker}:")
    print(comparison[["Year", "Net Revenue", "YoY Growth"]].to_string(index=False))
    
    if not comparison.empty and comparison["YoY Growth"].notna().any():
        plot_revenue_and_growth(comparison, ticker)
    else:
        print("Unable to plot graph due to insufficient data.")

if __name__ == "__main__":
    ticker = input("Enter the stock ticker: ")
    financial_comparison(ticker)