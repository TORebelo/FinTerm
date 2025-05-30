import httpx
import asyncio
from typing import Optional, Dict, Any
from config import settings

class HttpClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)
        self.retry_delay = settings.DEFAULT_RETRY_DELAY

    async def make_request(
        self, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        params: Optional[Dict[str, Any]] = None,
        retries: int = settings.MAX_RETRIES
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and exponential backoff"""
        last_exception = None
        
        for attempt in range(retries):
            try:
                response = await self.client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < retries - 1:
                    # Rate limited - exponential backoff
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                last_exception = e
                break
                
            except httpx.RequestError as e:
                last_exception = e
                if attempt < retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                break

        if last_exception:
            print(f"Failed to fetch {url} after {retries} attempts: {last_exception}")
            
        return None

    async def close(self):
        await self.client.aclose()
