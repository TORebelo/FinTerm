from typing import List, Dict, Any, Optional
from core.http_client import HttpClient
from config import settings

class SECService:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK from ticker symbol"""
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            headers = {"User-Agent": settings.SEC_USER_AGENT}
            
            data = await self.http_client.make_request(url, headers=headers)
            
            if data:
                for key, item_info in data.items():
                    if item_info.get("ticker") == ticker.upper():
                        return str(item_info.get("cik_str")).zfill(10)
                        
        except Exception as e:
            print(f"Error fetching CIK for {ticker}: {e}")
            
        return None

    async def get_sec_filings_by_cik(
        self, 
        cik: str, 
        form_types: List[str] = None, 
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get SEC filings by CIK"""
        if not cik:
            return []
            
        if form_types is None:
            form_types = ["10-K", "10-Q"]

        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            headers = {"User-Agent": settings.SEC_USER_AGENT}
            
            data = await self.http_client.make_request(url, headers=headers)
            
            if not data or "filings" not in data or "recent" not in data["filings"]:
                return []

            filings = data["filings"]["recent"]
            results = []
            
            accession_numbers = filings.get("accessionNumber", [])
            forms = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            report_dates = filings.get("reportDate", [])
            primary_documents = filings.get("primaryDocument", [])

            for i in range(len(accession_numbers)):
                if forms[i] in form_types:
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_numbers[i].replace('-', '')}/{primary_documents[i]}"
                    results.append({
                        "formType": forms[i],
                        "filedDate": filing_dates[i],
                        "reportDate": report_dates[i] if i < len(report_dates) else "N/A",
                        "url": filing_url,
                        "accessionNumber": accession_numbers[i]
                    })
                    if len(results) >= count:
                        break
                        
            return results
            
        except Exception as e:
            print(f"Error fetching SEC filings for CIK {cik}: {e}")
            return []

    async def get_stock_sec_filings(
        self, 
        ticker: str, 
        form_types: List[str] = None, 
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get SEC filings for ticker"""
        cik = await self.get_cik_from_ticker(ticker)
        if not cik:
            return [{"error": f"CIK not found for ticker {ticker}"}]
            
        return await self.get_sec_filings_by_cik(cik, form_types, count)
